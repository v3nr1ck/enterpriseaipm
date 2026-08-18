"""
Lab D: the interpolation walk.

The most convincing artifact in the book. Generate images at ten evenly spaced
points along the straight line between two prompt embeddings, same seed
throughout. If the space were a lookup table of memorised images, the midpoints
would be garbage. They are not. They are coherent images of things that have
no name.

That smoothness is the proof that the model is navigating, not retrieving.

Run:  python interpolate.py
      python interpolate.py --a "a medieval stone castle in fog" \
                            --b "a chrome sports car on a salt flat"
      python interpolate.py --frames 16 --classify

Outputs land in ./output/walk/.
"""

import argparse
import os
import sys

PROMPT_A = "a medieval stone castle in heavy fog"
PROMPT_B = "a chrome sports car on a salt flat at noon"


def load_pipeline(model_id, device_pref=None):
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError:
        sys.exit("Missing dependencies. Run: pip install -r requirements.txt")

    if device_pref:
        device = device_pref
    elif torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    dtype = torch.float16 if device == "cuda" else torch.float32
    if device == "cpu":
        print("WARNING: CPU only. Expect several minutes per frame.")
        print("         Try --frames 5, or rent a GPU (see ../SETUP.md).\n")

    print(f"Loading {model_id} on {device} ...\n")
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=dtype, safety_checker=None, requires_safety_checker=False
    ).to(device)
    pipe.set_progress_bar_config(disable=True)
    if device == "cuda":
        pipe.enable_attention_slicing()
    return torch, pipe, device


def embed_prompt(torch, pipe, text):
    """
    Text -> vector, using the pipeline's own CLIP text encoder.

    This is the encoder half of CLIP from Chapter 6. The vector it returns
    lives in a space shared with images, which is the entire reason a
    sentence can specify a location among pictures.
    """
    tok = pipe.tokenizer(
        text,
        padding="max_length",
        max_length=pipe.tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt",
    )
    with torch.no_grad():
        out = pipe.text_encoder(tok.input_ids.to(pipe.device))[0]
    return out


def lerp(a, b, t):
    """Straight line between two vectors. t=0 gives a, t=1 gives b."""
    return a * (1.0 - t) + b * t


def slerp(torch, a, b, t):
    """
    Spherical interpolation — walks along the surface of the sphere rather
    than cutting through the middle of it.

    Worth knowing why this exists: in high dimensions, the straight line
    between two unit vectors dips toward the origin, where vectors are
    shorter and less like anything the model saw in training. Slerp keeps
    the magnitude constant the whole way across. Sometimes it gives
    noticeably better midpoints. Try both with --linear.
    """
    a_flat = a.flatten().float()
    b_flat = b.flatten().float()
    a_norm = a_flat / a_flat.norm()
    b_norm = b_flat / b_flat.norm()
    dot = torch.clamp((a_norm * b_norm).sum(), -1.0, 1.0)
    theta = torch.acos(dot)
    if theta.abs() < 1e-4:
        return lerp(a, b, t)
    sin_theta = torch.sin(theta)
    w_a = torch.sin((1.0 - t) * theta) / sin_theta
    w_b = torch.sin(t * theta) / sin_theta
    return (a * w_a + b * w_b).to(a.dtype)


def walk(torch, pipe, text_a, text_b, frames, steps, guidance, seed,
         outdir, use_slerp=True):
    os.makedirs(outdir, exist_ok=True)

    emb_a = embed_prompt(torch, pipe, text_a)
    emb_b = embed_prompt(torch, pipe, text_b)
    print(f"Each prompt is now a tensor of shape {tuple(emb_a.shape)}.")
    print("Two points. We are about to walk the line between them.\n")

    paths = []
    for i in range(frames):
        t = i / (frames - 1) if frames > 1 else 0.0
        emb = (slerp(torch, emb_a, emb_b, torch.tensor(t))
               if use_slerp else lerp(emb_a, emb_b, t))

        generator = torch.Generator(device="cpu").manual_seed(seed)
        img = pipe(
            prompt_embeds=emb,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]

        path = os.path.join(outdir, f"frame_{i:02d}_t{t:.2f}.png")
        img.save(path)
        paths.append(path)
        pct_a, pct_b = (1 - t) * 100, t * 100
        print(f"  frame {i:>2}  {pct_a:>5.1f}% A / {pct_b:>5.1f}% B  ->  "
              f"{os.path.basename(path)}")

    return paths


def classify_midpoints(paths, text_a, text_b):
    """
    Close the loop: take the frames you just GENERATED and RECOGNISE them,
    with the same CLIP machinery, against the two original prompts.

    Generation picked an address and built what belongs there.
    Recognition reads the address something arrived at.
    Same map. That is Chapter 3, executed end to end.
    """
    try:
        import torch
        from PIL import Image
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        print("\n(Skipping classification: needs transformers + pillow.)")
        return

    print("\n" + "=" * 70)
    print("NOW RECOGNISE WHAT YOU JUST GENERATED")
    print("=" * 70)
    name = "openai/clip-vit-base-patch32"
    print(f"Loading {name} ...\n")
    model = CLIPModel.from_pretrained(name)
    proc = CLIPProcessor.from_pretrained(name)

    print(f"  A = {text_a!r}")
    print(f"  B = {text_b!r}\n")
    print(f"  {'frame':<26}{'sim to A':>10}{'sim to B':>10}   verdict")
    print("  " + "-" * 62)

    for path in paths:
        img = Image.open(path)
        inputs = proc(text=[text_a, text_b], images=img,
                      return_tensors="pt", padding=True)
        with torch.no_grad():
            out = model(**inputs)
        probs = out.logits_per_image.softmax(dim=1)[0]
        pa, pb = probs[0].item(), probs[1].item()
        verdict = "A" if pa > 0.6 else ("B" if pb > 0.6 else "-- ambiguous --")
        print(f"  {os.path.basename(path):<26}{pa:>9.1%}{pb:>10.1%}   {verdict}")

    print()
    print("  Look at the middle frames. The ones marked ambiguous are images")
    print("  of something with no name, and CLIP scores them near-equally")
    print("  because that is genuinely where they sit.")
    print()
    print("  You generated a point, then read off its coordinates, using the")
    print("  same machinery in both directions.")
    print()


def main():
    p = argparse.ArgumentParser(description="Lab D: the interpolation walk.")
    p.add_argument("--model", default="runwayml/stable-diffusion-v1-5")
    p.add_argument("--a", default=PROMPT_A)
    p.add_argument("--b", default=PROMPT_B)
    p.add_argument("--frames", type=int, default=10)
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--guidance", type=float, default=7.5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="output")
    p.add_argument("--device", default=None, choices=[None, "cuda", "mps", "cpu"])
    p.add_argument("--linear", action="store_true",
                   help="use straight-line interpolation instead of spherical")
    p.add_argument("--classify", action="store_true",
                   help="run CLIP over the frames afterwards")
    args = p.parse_args()

    if args.frames < 2:
        sys.exit("--frames needs to be at least 2.")

    torch, pipe, device = load_pipeline(args.model, args.device)
    outdir = os.path.join(args.out, "walk")

    print(f'  A: "{args.a}"')
    print(f'  B: "{args.b}"')
    print(f"  {args.frames} frames, "
          f"{'linear' if args.linear else 'spherical'} interpolation, "
          f"seed {args.seed} throughout\n")

    paths = walk(torch, pipe, args.a, args.b, args.frames, args.steps,
                 args.guidance, args.seed, outdir, use_slerp=not args.linear)

    if args.classify:
        classify_midpoints(paths, args.a, args.b)

    print("=" * 70)
    print("WHAT TO LOOK FOR")
    print("=" * 70)
    print(f"  Open {outdir} and view the frames in order.")
    print()
    print("  It is not a crossfade. Frame 5 is not frame 0 and frame 9")
    print("  overlaid at 50% each — it is a coherent image of a single thing")
    print("  that is halfway between two concepts. Stone that has gone")
    print("  metallic. Fog thinning into haze over salt.")
    print()
    print("  If the model were retrieving memorised images, the midpoints")
    print("  would be garbage or would snap between the two ends. They")
    print("  don't. The space is continuous, and meaning varies smoothly")
    print("  across it, which means the model is navigating.")
    print()
    print("  Then: python interpolate.py --classify")
    print()


if __name__ == "__main__":
    main()
