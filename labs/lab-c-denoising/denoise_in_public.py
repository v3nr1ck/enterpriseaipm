"""
Lab C: watch the walk.

Generation is not retrieval and it is not one-shot construction. It is a walk
that starts at random noise and steps toward the region of latent space where
real images live. This script saves every step so you can look at the walk.

Run:  python denoise_in_public.py
      python denoise_in_public.py --prompt "a lighthouse in a storm" --steps 30
      python denoise_in_public.py --sweep-steps      # quality/cost frontier
      python denoise_in_public.py --sweep-guidance   # what CFG actually does
      python denoise_in_public.py --sweep-seeds      # same words, different start

Outputs land in ./output/. Look at them in order.
"""

import argparse
import os
import sys

DEFAULT_PROMPT = "a stone castle on a cliff in heavy fog, dramatic light"


def load_pipeline(model_id, device_pref=None):
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError:
        sys.exit(
            "Missing dependencies. Run:\n"
            "  pip install -r requirements.txt\n"
            "See ../SETUP.md for the rented-GPU route if you have no GPU."
        )

    # pick a device
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
        print("WARNING: no GPU found. This will run on CPU and be very slow")
        print("         (several minutes per image). Consider --steps 8, or")
        print("         see ../SETUP.md for renting a GPU for an hour.\n")

    print(f"Loading {model_id} on {device} ...")
    print("(First run downloads ~4GB. Once only.)\n")

    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=dtype, safety_checker=None, requires_safety_checker=False
    )
    pipe = pipe.to(device)
    pipe.set_progress_bar_config(disable=True)
    if device == "cuda":
        pipe.enable_attention_slicing()   # lower peak VRAM, small speed cost
    return torch, pipe, device


def decode_latent(pipe, latents, torch):
    """
    Turn a latent into a viewable image.

    This is the VAE decoder from Chapter 3 — the second half of the
    encoder/decoder pair. Every 'progress' frame you have ever seen in an
    image generator is a latent pushed through this.
    """
    with torch.no_grad():
        scaled = latents / pipe.vae.config.scaling_factor
        image = pipe.vae.decode(scaled.to(pipe.vae.dtype)).sample
    image = (image / 2 + 0.5).clamp(0, 1)
    image = image.cpu().permute(0, 2, 3, 1).float().numpy()
    return pipe.numpy_to_pil(image)[0]


def generate_with_trace(torch, pipe, prompt, steps, guidance, seed, outdir):
    """Generate one image, saving a PNG at every denoising step."""
    os.makedirs(outdir, exist_ok=True)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    saved = []

    def on_step(pipe_ref, step, timestep, kwargs):
        # Not every scheduler runs exactly num_inference_steps callbacks. SD
        # 1.5's default PNDM scheduler runs one extra, so trust the scheduler's
        # own timestep count rather than what we asked for — otherwise the
        # progress line reads "step 7/6".
        total = len(getattr(pipe_ref.scheduler, "timesteps", [])) or steps
        latents = kwargs["latents"]
        img = decode_latent(pipe_ref, latents, torch)
        path = os.path.join(outdir, f"step_{step + 1:03d}.png")
        img.save(path)
        saved.append(path)
        print(f"  step {step + 1:>3}/{total}  ->  {os.path.basename(path)}")
        return kwargs

    print(f'Prompt: "{prompt}"')
    print(f"Steps: {steps}   Guidance: {guidance}   Seed: {seed}\n")
    print("Saving every step. Watch the fog resolve.\n")

    result = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
        callback_on_step_end=on_step,
        callback_on_step_end_tensor_inputs=["latents"],
    )
    final = os.path.join(outdir, "final.png")
    result.images[0].save(final)
    print(f"\n  final          ->  {final}")
    return saved


def sweep_steps(torch, pipe, prompt, guidance, seed, outdir):
    """Same seed and prompt at increasing step counts. Find the plateau."""
    os.makedirs(outdir, exist_ok=True)
    print("Step-count sweep: where does it stop improving?\n")
    for n in (2, 5, 10, 20, 35, 50):
        g = torch.Generator(device="cpu").manual_seed(seed)
        img = pipe(prompt=prompt, num_inference_steps=n,
                   guidance_scale=guidance, generator=g).images[0]
        path = os.path.join(outdir, f"steps_{n:02d}.png")
        img.save(path)
        print(f"  {n:>2} steps -> {os.path.basename(path)}")
    print("\n  Line them up. Somewhere between 20 and 35 the returns stop.")
    print("  That point is your quality/cost frontier, measured rather than")
    print("  guessed — and it is the same shape of curve you will meet again")
    print("  in Lab F, where the axis is training examples instead of steps.")


def sweep_guidance(torch, pipe, prompt, steps, seed, outdir):
    """CFG scale is a vector multiplication. Here is what it looks like."""
    os.makedirs(outdir, exist_ok=True)
    print("Guidance sweep: watch it go from ignoring you to overcooking.\n")
    for g_scale in (1.0, 3.0, 7.5, 15.0, 25.0):
        g = torch.Generator(device="cpu").manual_seed(seed)
        img = pipe(prompt=prompt, num_inference_steps=steps,
                   guidance_scale=g_scale, generator=g).images[0]
        path = os.path.join(outdir, f"guidance_{g_scale:04.1f}.png")
        img.save(path)
        print(f"  cfg {g_scale:>4.1f} -> {os.path.basename(path)}")
    print("\n  At 1.0 the model wanders wherever it likes — your words barely")
    print("  register. At 7.5 you get adherence with natural results. At 25")
    print("  it is contorted and oversaturated, because you amplified the")
    print("  text direction so hard that you pushed the latent outside the")
    print("  region where the decoder produces anything sane.")
    print("\n  You are watching a vector get multiplied.")


def sweep_seeds(torch, pipe, prompt, steps, guidance, outdir, n=6):
    """Fixed prompt, different starting noise."""
    os.makedirs(outdir, exist_ok=True)
    print("Seed sweep: same words, different starting point.\n")
    for s in range(n):
        g = torch.Generator(device="cpu").manual_seed(1000 + s)
        img = pipe(prompt=prompt, num_inference_steps=steps,
                   guidance_scale=guidance, generator=g).images[0]
        path = os.path.join(outdir, f"seed_{1000 + s}.png")
        img.save(path)
        print(f"  seed {1000 + s} -> {os.path.basename(path)}")
    print("\n  Every one of those got identical instructions. The variation")
    print("  is entirely in where the walk started.")
    print()
    print("  This distinction matters in practice: 'the prompt was ambiguous'")
    print("  and 'the walk started somewhere else' are different diagnoses")
    print("  with different fixes, and people confuse them constantly.")


def main():
    p = argparse.ArgumentParser(description="Lab C: watch the denoising walk.")
    p.add_argument("--model", default="stable-diffusion-v1-5/stable-diffusion-v1-5",
                   help="see ../CURRENT.md")
    p.add_argument("--prompt", default=DEFAULT_PROMPT)
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--guidance", type=float, default=7.5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="output")
    p.add_argument("--device", default=None, choices=[None, "cuda", "mps", "cpu"])
    p.add_argument("--sweep-steps", action="store_true")
    p.add_argument("--sweep-guidance", action="store_true")
    p.add_argument("--sweep-seeds", action="store_true")
    args = p.parse_args()

    torch, pipe, device = load_pipeline(args.model, args.device)

    if args.sweep_steps:
        sweep_steps(torch, pipe, args.prompt, args.guidance, args.seed,
                    os.path.join(args.out, "sweep_steps"))
    elif args.sweep_guidance:
        sweep_guidance(torch, pipe, args.prompt, args.steps, args.seed,
                       os.path.join(args.out, "sweep_guidance"))
    elif args.sweep_seeds:
        sweep_seeds(torch, pipe, args.prompt, args.steps, args.guidance,
                    os.path.join(args.out, "sweep_seeds"))
    else:
        generate_with_trace(torch, pipe, args.prompt, args.steps,
                            args.guidance, args.seed,
                            os.path.join(args.out, "trace"))
        print()
        print("=" * 70)
        print("NOW LOOK AT THEM IN ORDER")
        print("=" * 70)
        print(f"  Open {os.path.join(args.out, 'trace')} and scan step_001 onward.")
        print()
        print("  The thing nobody tells you in advance: notice HOW EARLY the")
        print("  composition is fixed. Within the first fifth of the steps —")
        print("  before there is anything you would call detail — the overall")
        print("  layout is already committed. Everything after that is")
        print("  refinement inside a decision that has already been made.")
        print()
        print("  Then run the three sweeps:")
        print("    python denoise_in_public.py --sweep-steps")
        print("    python denoise_in_public.py --sweep-guidance")
        print("    python denoise_in_public.py --sweep-seeds")
        print()


if __name__ == "__main__":
    main()
