"""
Lab E: watch it degrade.

Same model, three precisions, same prompts. The finding is not that
quantization costs quality — you knew that from reading. The finding is the
*shape* of the loss: easy tasks survive all the way down, reasoning falls apart
first, and the broken model sounds exactly as confident as the good one.

Run:  ollama serve                       # in another terminal
      python compare_quants.py --tags gemma4:e4b-it-q8_0 \
                                      gemma4:e4b-it-q4_K_M \
                                      gemma4:e4b-it-q2_K

Check ../CURRENT.md for tags that exist today. Or browse:
      https://ollama.com/library/<model>/tags
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_HOST = "http://localhost:11434"


def load_prompts(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def ollama_generate(host, model, prompt, timeout=180):
    """Call Ollama's /api/generate at temperature 0 so we compare like for like."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "seed": 42},
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        if e.code == 404:
            raise SystemExit(
                f"\nOllama doesn't have '{model}'.\n"
                f"  ollama pull {model}\n"
                f"If that fails, the tag no longer exists — check\n"
                f"  https://ollama.com/library\n"
                f"and see ../CURRENT.md.\n"
            )
        raise SystemExit(f"Ollama returned HTTP {e.code}: {detail}")
    except urllib.error.URLError:
        raise SystemExit(
            f"\nCan't reach Ollama at {host}.\n"
            "  Is it running? Start it with:  ollama serve\n"
            "  Install: https://ollama.com/download\n"
        )
    return body.get("response", "").strip(), time.time() - started


def check_model_present(host, model):
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=10) as resp:
            names = {m["name"] for m in json.loads(resp.read()).get("models", [])}
    except Exception:
        return None
    return model in names or f"{model}:latest" in names


def main():
    p = argparse.ArgumentParser(description="Lab E: watch quantization degrade.")
    p.add_argument("--tags", nargs="+", required=True,
                   help="three tags of the SAME model at different quants")
    p.add_argument("--prompts", default="prompts.json")
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--max-chars", type=int, default=280,
                   help="truncate printed answers to keep the table readable")
    args = p.parse_args()

    if len(args.tags) < 2:
        sys.exit("Give at least two tags to compare. Three is better.")

    prompts = load_prompts(args.prompts)

    # pre-flight: tell the reader what's missing BEFORE running anything long
    print("Checking which models are pulled ...")
    missing = []
    for tag in args.tags:
        present = check_model_present(args.host, tag)
        if present is None:
            sys.exit(
                f"\nCan't reach Ollama at {args.host}.\n"
                "  Start it with:  ollama serve\n"
            )
        print(f"  {'found  ' if present else 'MISSING'}  {tag}")
        if not present:
            missing.append(tag)
    if missing:
        print("\nPull them first:")
        for tag in missing:
            print(f"  ollama pull {tag}")
        sys.exit(1)
    print()

    results = {}
    for category, items in prompts.items():
        print("=" * 74)
        print(f"CATEGORY: {category.upper()}")
        print("=" * 74)
        for item in items:
            print(f"\nPROMPT: {item['prompt']}")
            if item.get("answer"):
                print(f"EXPECTED: {item['answer']}")
            print()
            for tag in args.tags:
                text, secs = ollama_generate(args.host, tag, item["prompt"])
                short = text.replace("\n", " ")
                if len(short) > args.max_chars:
                    short = short[:args.max_chars] + " ..."
                print(f"  [{tag}]  ({secs:.1f}s)")
                print(f"    {short}")
                results.setdefault(tag, {}).setdefault(category, []).append(text)
            print()

    print("=" * 74)
    print("HOW TO READ THIS")
    print("=" * 74)
    print("  Score them yourself. Do not skip this by eyeballing — write a")
    print("  number in a file. Anything else and you are doing vibes.")
    print()
    print("  What you should find:")
    print()
    print("  RECALL      survives all the way down. A 2-bit model still knows")
    print("              the capital of France.")
    print("  REASONING   breaks first, and breaks hardest. Multi-step")
    print("              arithmetic and logic go before anything else.")
    print("  FORMAT      degrades in the middle — constraints get dropped")
    print("              one at a time rather than all at once.")
    print()
    print("  Now the part that matters, and the reason this lab exists:")
    print()
    print("  The 2-bit model sounds EXACTLY as confident as the 8-bit one.")
    print("  It is fluent. It is well-formed. It is wrong. If you had only")
    print("  tested it on the recall prompts, you would have shipped it and")
    print("  concluded it was fine.")
    print()
    print("  Once you have seen that in your own terminal, you will never")
    print("  again accept 'it seemed fine in testing' as evidence about a")
    print("  model swap. That is the whole lab.")
    print()


if __name__ == "__main__":
    main()
