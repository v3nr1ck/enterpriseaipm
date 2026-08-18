"""
Lab F, step three: score the outputs and draw the curve.

This is the point of the whole lab. Not the fine-tuned model — the CURVE.
Its shape tells you what to do next, and it is the only cheap way to answer
"how much labelled data would this take?" with a number instead of a guess.

Scoring is mechanical on purpose: no judgement, no LLM-as-judge, nothing to
argue about. Four checks, each worth 25%.

Run:  python score_outputs.py --predictions runs/base.jsonl
      python score_outputs.py --curve runs/           # all of them, plotted

Each predictions file is JSONL with at least: {"input": ..., "predicted": ...}
Get one by running your fine-tuned model over data/val.jsonl.
"""

import argparse
import glob
import json
import os
import re
import sys

HEADER = re.compile(r"^<<([A-Z]+)\|([A-Z]+)>>$", re.M)
AREAS = {"BILLING", "AUTH", "PERFORMANCE", "DATA", "UI", "INTEGRATION"}
SEVS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"{path} line {i} is not valid JSON: {e}")
    return rows


def score_one(predicted, expected):
    """
    Four independent checks. Each is either right or wrong — no partial credit,
    no interpretation.
    """
    checks = {}

    # 1. does it have the header line at all, in the right shape?
    m = HEADER.search(predicted or "")
    checks["header_shape"] = bool(m)

    # 2. are the two header fields drawn from the allowed vocabularies?
    checks["header_valid"] = bool(m and m.group(1) in AREAS and m.group(2) in SEVS)

    # 3. does it match the expected classification?
    em = HEADER.search(expected)
    checks["header_correct"] = bool(m and em and m.groups() == em.groups())

    # 4. are all four required lines present, in order, and nothing else?
    want = ["<<", "summary:", "trigger:", "escalate:"]
    lines = [l.strip() for l in (predicted or "").strip().splitlines() if l.strip()]
    checks["structure"] = (
        len(lines) == 4
        and all(lines[i].startswith(want[i]) for i in range(4))
    )

    return checks


def score_file(path):
    rows = load_jsonl(path)
    if not rows:
        sys.exit(f"{path} is empty.")
    missing = [k for k in ("input", "predicted") if k not in rows[0]]
    if missing:
        sys.exit(
            f"{path} rows need 'input' and 'predicted' keys "
            f"(missing: {', '.join(missing)}).\n"
            f"Found keys: {', '.join(rows[0].keys())}"
        )

    # expected output: from the row itself, or from val.jsonl by input match
    if "output" not in rows[0]:
        val_path = os.path.join("data", "val.jsonl")
        if not os.path.exists(val_path):
            sys.exit("Rows have no 'output' and data/val.jsonl is missing.")
        lookup = {r["input"]: r["output"] for r in load_jsonl(val_path)}
        for r in rows:
            r["output"] = lookup.get(r["input"], "")

    totals = {}
    for r in rows:
        for k, v in score_one(r.get("predicted", ""), r.get("output", "")).items():
            totals[k] = totals.get(k, 0) + (1 if v else 0)

    n = len(rows)
    pct = {k: v / n for k, v in totals.items()}
    pct["OVERALL"] = sum(pct.values()) / len(pct)
    return n, pct


def print_report(name, n, pct):
    print(f"  {name}   ({n} examples)")
    for k in ("header_shape", "header_valid", "header_correct", "structure"):
        bar = "#" * int(pct[k] * 30)
        print(f"    {k:<18}{pct[k]:>7.1%}  {bar}")
    print(f"    {'OVERALL':<18}{pct['OVERALL']:>7.1%}")
    print()


def draw_curve(points):
    """
    ASCII plot. No matplotlib dependency for the thing that matters most.
    points: list of (n_examples, overall_score)
    """
    if len(points) < 2:
        print("  Need at least two runs to draw a curve.")
        return
    points = sorted(points)
    height = 12
    print()
    print("  score")
    for row in range(height, -1, -1):
        threshold = row / height
        line = f"  {threshold:>5.0%} |"
        for _, score in points:
            line += "  #  " if score >= threshold else "     "
        print(line)
    print("        +" + "-----" * len(points))
    print("         " + "".join(f"{n:^5}" for n, _ in points))
    print("         " + " examples".center(5 * len(points)))
    print()


def interpret(points):
    points = sorted(points)
    first, last = points[0][1], points[-1][1]
    gain_total = last - first
    # "still climbing?" is a question about the FINAL leg of the curve —
    # comparing against the middle point would call a clean plateau a climb.
    prev = points[-2][1] if len(points) > 1 else first
    gain_late = last - prev
    # normalise by how much the data actually grew on that final leg
    n_prev, n_last = points[-2][0], points[-1][0]
    doublings = 1.0
    if n_prev > 0 and n_last > n_prev:
        import math
        doublings = max(1.0, math.log2(n_last / n_prev))
    gain_per_doubling = gain_late / doublings

    print("=" * 70)
    print("READING THE CURVE")
    print("=" * 70)
    print()
    print("  Four shapes, four different decisions:\n")

    # Thresholds are deliberately loose. With a 120-row eval set, sampling
    # noise alone is worth several percent, so tight thresholds would report
    # "inconclusive" on curves that are actually perfectly readable.
    if first > 0.80:
        verdict = (
            "ALREADY GOOD AT THE SMALLEST SIZE, FLAT AFTER.\n"
            "  The capability was latent — the base model could always do this,\n"
            "  it just needed to be shown the shape you wanted.\n"
            "  DO NOT FINE-TUNE. Use few-shot prompting and go home.\n"
            "  You just saved a project."
        )
    elif gain_total > 0.15 and gain_per_doubling < 0.04:
        verdict = (
            "CLIMBS STEEPLY, THEN FLATTENS. The good case.\n"
            "  You have found the plateau. The answer to 'how much data do we\n"
            "  need' is now a number you measured in an afternoon, rather than\n"
            "  a guess you defend for a quarter."
        )
    elif gain_per_doubling > 0.04:
        verdict = (
            "STILL CLIMBING AT THE LARGEST SIZE.\n"
            "  You are underfeeding it. The task needs more data than you have\n"
            "  collected, and the slope tells you roughly how much more.\n"
            "  The data-collection budget conversation is now arithmetic\n"
            "  instead of an argument."
        )
    elif last < 0.5:
        verdict = (
            "FLAT AND BAD EVERYWHERE. The most valuable outcome here.\n"
            "  The capability is not in the base model and adding examples is\n"
            "  not reaching it. Either the knowledge isn't in the space (go to\n"
            "  retrieval), or you need a different base model, or the task is\n"
            "  not learnable in this form.\n"
            "  Whichever it is, you found out for a few dollars in an\n"
            "  afternoon instead of after a quarter of headcount."
        )
    else:
        verdict = (
            "SOMEWHERE BETWEEN THE CLEAN SHAPES.\n"
            "  Add more sizes and re-run before drawing a conclusion. Curves\n"
            "  with three points lie."
        )

    print("  YOUR CURVE: " + verdict)
    print()
    print("  Sanity check before you believe any of this: an eval set of a")
    print("  hundred-odd rows carries a few percent of sampling noise on its")
    print("  own. Differences smaller than about 5% are not differences.")
    print()
    print(f"  smallest set: {points[0][0]:>5} examples -> {first:.1%}")
    print(f"  largest set:  {points[-1][0]:>5} examples -> {last:.1%}")
    print(f"  final leg: {n_prev} -> {n_last} examples, {gain_late:+.1%}")
    print(f"  gain per doubling of data at the end: {gain_per_doubling:+.1%}")
    print()


def main():
    p = argparse.ArgumentParser(description="Lab F: score outputs, draw the curve.")
    p.add_argument("--predictions", help="one JSONL file of predictions")
    p.add_argument("--curve", help="a directory of them, named train_<N>.jsonl "
                                   "plus optionally base.jsonl")
    args = p.parse_args()

    if not args.predictions and not args.curve:
        sys.exit("Give --predictions <file> or --curve <directory>.")

    if args.predictions:
        n, pct = score_file(args.predictions)
        print()
        print_report(os.path.basename(args.predictions), n, pct)
        return

    files = sorted(glob.glob(os.path.join(args.curve, "*.jsonl")))
    if not files:
        sys.exit(f"No .jsonl files in {args.curve}")

    print()
    print("=" * 70)
    print("SCORES")
    print("=" * 70)
    print()

    points = []
    for path in files:
        n, pct = score_file(path)
        name = os.path.basename(path)
        print_report(name, n, pct)
        m = re.search(r"(\d+)", name)
        if m:
            points.append((int(m.group(1)), pct["OVERALL"]))
        elif "base" in name.lower():
            points.append((0, pct["OVERALL"]))

    if points:
        draw_curve(points)
        interpret(points)


if __name__ == "__main__":
    main()
