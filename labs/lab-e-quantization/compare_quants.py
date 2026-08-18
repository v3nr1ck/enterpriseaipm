"""
Lab E: watch it degrade.

Same model, three precisions, same prompts. The finding is not that
quantization costs quality — you knew that from reading. The finding is the
*shape* of the loss, and the order things break in. Measured on
llama3.1:8b-instruct: reasoning is already wrong at q4_K_M, edge facts go at
q2_K, and easy recall plus format-following survive all the way down. Nothing
in the tone of the output tells you which you are looking at.

Two cautions. A wrong answer is not automatically a quantization effect - only
count it when the SAME model at higher precision gets it right. And one prompt
is not evidence: individual edge facts flip non-monotonically. Score the set.

Run:  ollama serve            # in another terminal, left running

      python compare_quants.py --tags llama3.1:8b-instruct-q8_0 llama3.1:8b-instruct-q4_K_M llama3.1:8b-instruct-q2_K

The --tags list goes on ONE line. A trailing backslash is bash continuation
and is a syntax error in PowerShell.

Check ../CURRENT.md for tags that exist today. Or browse:
      https://ollama.com/library/<model>/tags
"""

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.request

DEFAULT_HOST = "http://localhost:11434"


def load_prompts(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def ollama_generate(host, model, prompt, timeout=600, max_tokens=512):
    """Call Ollama's /api/generate at temperature 0 so we compare like for like.

    Returns (text, seconds, hit_cap). hit_cap is True when the model was still
    generating when it ran into num_predict. On a hard reasoning prompt that
    just means a long answer; on a model quantised past its viability
    threshold it means the model never chose to stop at all.
    """
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        # num_predict is a safety cap, not a style choice. A model quantised
        # past its viability threshold often never emits a stop token — it
        # degenerates into repeated digits and stray CJK and runs to the
        # context limit. Uncapped, one prompt can take longer than the entire
        # rest of the lab. That failure to terminate is itself a finding, so
        # we surface it below rather than hiding it.
        "options": {"temperature": 0, "seed": 42, "num_predict": max_tokens},
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
    except urllib.error.URLError as e:
        # A read timeout arrives wrapped in URLError on some Python builds and
        # bare on others. Either way it means the model is still loading, not
        # that Ollama is down — hand back None and let the caller carry on.
        if isinstance(getattr(e, "reason", None), (socket.timeout, TimeoutError)):
            return None, time.time() - started, False
        raise SystemExit(
            f"\nCan't reach Ollama at {host}.\n"
            "  Is it running? Start it with:  ollama serve\n"
            "  Install: https://ollama.com/download\n"
        )
    except (socket.timeout, TimeoutError):
        return None, time.time() - started, False
    hit_cap = body.get("done_reason") == "length"
    return body.get("response", "").strip(), time.time() - started, hit_cap


def safe_print(text):
    """Print model output without dying on the Windows console.

    A heavily quantised model will happily emit tokens from another script
    entirely — Chinese, Cyrillic, emoji. That is a finding, not an error, so
    we must not crash on it: the default Windows console codepage is cp1252
    and cannot encode most of it. Replace what won't encode and carry on.
    """
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding))


def warm_up(host, model, timeout=900):
    """Force Ollama to load the model before we time anything against it.

    Swapping quantisations evicts the previous model from memory, so the first
    request against each tag pays the whole load cost. Without this the first
    prompt of every tag looks artificially slow, and on a machine with other
    large models resident it can blow past any sane per-request timeout.
    """
    payload = json.dumps({"model": model, "prompt": "hi", "stream": False,
                          "options": {"num_predict": 1}}).encode()
    req = urllib.request.Request(
        f"{host}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        return True
    except Exception:
        return False


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
    p.add_argument("--max-tokens", type=int, default=512,
                   help="cap on generated tokens per prompt; a model quantised "
                        "past its viability threshold may never stop on its own")
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

    # Ask every prompt of one model before moving to the next. Ollama holds a
    # limited number of models in memory, so interleaving tags would evict and
    # reload on nearly every request — 27 model loads instead of 3, and a cold
    # load of a 3B model can take minutes. We collect first, print after.
    flat = [(category, item)
            for category, items in prompts.items()
            for item in items]

    answers = {}   # (tag, category, index) -> (text, seconds)
    results = {}
    for tag in args.tags:
        print(f"Running {len(flat)} prompts against {tag} ...")
        warm_up(args.host, tag)
        for n, (category, item) in enumerate(flat):
            text, secs, hit_cap = ollama_generate(
                args.host, tag, item["prompt"], max_tokens=args.max_tokens)
            answers[(tag, category, n)] = (text, secs, hit_cap)
            results.setdefault(tag, {}).setdefault(category, []).append(text or "")
        print("  done\n")

    last_category = None
    for n, (category, item) in enumerate(flat):
        if category != last_category:
            print("=" * 74)
            print(f"CATEGORY: {category.upper()}")
            print("=" * 74)
            last_category = category
        print(f"\nPROMPT: {item['prompt']}")
        if item.get("answer"):
            print(f"EXPECTED: {item['answer']}")
        print()
        for tag in args.tags:
            text, secs, hit_cap = answers[(tag, category, n)]
            if text is None:
                print(f"  [{tag}]  (timed out after {secs:.0f}s)")
                print("    -- no response --")
                continue
            short = text.replace("\n", " ")
            if len(short) > args.max_chars:
                short = short[:args.max_chars] + " ..."
            cap_note = f"  [truncated at {args.max_tokens} tokens]" if hit_cap else ""
            print(f"  [{tag}]  ({secs:.1f}s){cap_note}")
            safe_print(f"    {short}")
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
