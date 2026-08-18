"""
Lab B: watch the model choose.

There is no decision inside a language model. There is a probability
distribution over every token it knows, and a sampling procedure that draws
from it. This script exposes both.

Run:  python watch_it_choose.py
      python watch_it_choose.py --prompt "The capital of France is"
      python watch_it_choose.py --temperature 1.4
      python watch_it_choose.py --near-ties
"""

import argparse
import sys

PROMPTS = [
    "The capital of France is",
    "The best thing about working in product management is",
]


def load(model_name):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        sys.exit(
            "Missing dependencies. Run:\n"
            "  pip install -r requirements.txt\n"
            "This lab needs torch and transformers (~2GB). See ../SETUP.md\n"
            "for the Colab route if you'd rather not install locally."
        )
    print(f"Loading {model_name} ...")
    print("(First run downloads the model. See ../CURRENT.md.)\n")
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float32
    )
    model.eval()
    return torch, tok, model


def show_tokenization(tok, text):
    """Before anything else: the model does not see words."""
    ids = tok.encode(text, add_special_tokens=False)
    pieces = [tok.decode([i]) for i in ids]
    print("=" * 70)
    print("FIRST, THE TOKENS")
    print("=" * 70)
    print(f'  Input: "{text}"')
    print(f"  Becomes {len(ids)} tokens:")
    print("   ", " | ".join(repr(p) for p in pieces))
    print()
    print("  Note the leading spaces attached to words. ' Paris' and 'Paris'")
    print("  are different tokens with different IDs.")
    print()

    # the strawberry demonstration
    for word in ("strawberry", "unbelievable"):
        wid = tok.encode(word, add_special_tokens=False)
        wp = [tok.decode([i]) for i in wid]
        print(f'  "{word}" -> {len(wid)} token(s): {" | ".join(repr(p) for p in wp)}')
    print()
    print("  The model cannot see letters. Asking it to count the r's in")
    print("  'strawberry' asks it to reason about the internal composition of")
    print("  symbols it was never shown. It is a representation problem, and")
    print("  no amount of prompting fixes a representation problem.")
    print()


def step_report(torch, tok, model, prompt, temperature, top_n, steps):
    """Generate token by token, printing the distribution at each step."""
    ids = tok.encode(prompt, return_tensors="pt")
    generated = []

    print("=" * 70)
    print(f"GENERATING AT TEMPERATURE {temperature}")
    print("=" * 70)
    print(f'  Prompt: "{prompt}"\n')

    for step in range(steps):
        with torch.no_grad():
            out = model(ids)
        logits = out.logits[0, -1, :]          # scores for EVERY token, this position

        # the softmax from Chapter 1, with temperature applied
        if temperature <= 0:
            probs = torch.zeros_like(logits)
            probs[int(torch.argmax(logits).item())] = 1.0
        else:
            probs = torch.softmax(logits / temperature, dim=-1)

        top = torch.topk(probs, top_n)
        print(f"  Step {step + 1}: after \"{prompt}{''.join(generated)}\"")
        print(f"    {'token':<16}{'prob':>9}   {'raw logit':>10}")
        for rank in range(top_n):
            tid = top.indices[rank].item()
            p = top.values[rank].item()
            bar = "#" * max(1, int(p * 34))
            print(f"    {repr(tok.decode([tid]))[:15]:<16}{p:>8.3%}   "
                  f"{logits[tid].item():>10.2f}  {bar}")

        # what fraction of all probability sits in the top few?
        head = top.values.sum().item()
        print(f"    -> top {top_n} hold {head:.1%} of all probability; "
              f"the other {len(probs) - top_n:,} tokens share {1 - head:.1%}")

        # sample
        if temperature <= 0:
            nxt = torch.topk(probs, 1).indices
        else:
            nxt = torch.multinomial(probs, num_samples=1)
        piece = tok.decode(nxt)
        generated.append(piece)
        print(f"    -> sampled: {piece!r}\n")

        ids = torch.cat([ids, nxt.unsqueeze(0)], dim=1)

    print(f'  Result: "{prompt}{"".join(generated)}"')
    print()


def find_near_ties(torch, tok, model, prompt, steps=25, threshold=0.03):
    """
    Find the branch points: steps where the top two tokens are close enough
    that a rounding difference could flip them. These are exactly where
    'but it worked yesterday' comes from.
    """
    ids = tok.encode(prompt, return_tensors="pt")
    print("=" * 70)
    print("NEAR-TIES: WHERE REPRODUCIBILITY GOES TO DIE")
    print("=" * 70)
    print(f"  Walking {steps} steps at temperature 0 (always take the top token).")
    print(f"  Flagging any step where the top two are within {threshold:.0%}.\n")

    found = 0
    text = prompt
    for step in range(steps):
        with torch.no_grad():
            logits = model(ids).logits[0, -1, :]
        probs = torch.softmax(logits, dim=-1)
        top = torch.topk(probs, 2)
        gap = (top.values[0] - top.values[1]).item()
        a, b = tok.decode(top.indices[0:1]), tok.decode(top.indices[1:2])

        if gap < threshold:
            found += 1
            print(f"  Step {step + 1:>2}  gap {gap:.4f}   "
                  f"{a!r} ({top.values[0]:.3f})  vs  {b!r} ({top.values[1]:.3f})")

        nxt = top.indices[0:1]
        text += tok.decode(nxt)
        ids = torch.cat([ids, nxt.unsqueeze(0)], dim=1)

    print()
    if found:
        print(f"  Found {found} near-tie(s) in {steps} steps.")
        print()
        print("  At each of those, two different outputs were nearly equally")
        print("  likely. In production, requests get batched on the GPU and")
        print("  floating-point addition isn't associative, so the arithmetic")
        print("  can come out fractionally differently run to run. At a step")
        print("  like these, that difference flips which token wins.")
        print()
        print("  This is why temperature 0 is not deterministic in practice,")
        print("  even though it is in theory.")
    else:
        print("  No near-ties this time. Try a more open-ended prompt —")
        print('  factual completions tend to be confident all the way through.')
    print()


def main():
    p = argparse.ArgumentParser(description="Lab B: watch the model choose.")
    p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct",
                   help="see ../CURRENT.md")
    p.add_argument("--prompt", default=None)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--steps", type=int, default=6)
    p.add_argument("--near-ties", action="store_true",
                   help="hunt for branch points instead of generating")
    args = p.parse_args()

    torch, tok, model = load(args.model)
    prompt = args.prompt or PROMPTS[0]

    show_tokenization(tok, prompt)

    if args.near_ties:
        find_near_ties(torch, tok, model, args.prompt or PROMPTS[1])
        return

    step_report(torch, tok, model, prompt, args.temperature, args.top_n, args.steps)

    print("=" * 70)
    print("NOW TRY THESE")
    print("=" * 70)
    print("  Same prompt, three temperatures — watch the distribution flatten:")
    print("    python watch_it_choose.py --temperature 0.2")
    print("    python watch_it_choose.py --temperature 0.8")
    print("    python watch_it_choose.py --temperature 1.5")
    print()
    print("  A confident prompt vs an open-ended one:")
    print('    python watch_it_choose.py --prompt "The capital of France is"')
    print('    python watch_it_choose.py --prompt "My favourite thing about Tuesday is"')
    print()
    print("  The branch points where reproducibility breaks:")
    print("    python watch_it_choose.py --near-ties")
    print()


if __name__ == "__main__":
    main()
