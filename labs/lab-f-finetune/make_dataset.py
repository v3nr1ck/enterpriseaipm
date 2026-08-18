"""
Lab F, step one: build the dataset.

We generate a task with a rigid, unusual output format. That choice is
deliberate:

  - Format-following is what fine-tuning is genuinely good at (Chapter 10:
    it lives in the instruction-tuning stage).
  - It is mechanically checkable, so you can score the result without
    judgement calls.
  - The base model will be visibly bad at it, so the delta is unmissable.

Do NOT pick a knowledge task here. Fine-tuning for knowledge half-works and
produces confident errors at the edges, which is the worst possible outcome
and a bad lesson to learn from your first run.

Run:  python make_dataset.py                 # writes train/val at every size
      python make_dataset.py --sizes 20 100 500 2000
"""

import argparse
import json
import os
import random

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
AREAS = ["BILLING", "AUTH", "PERFORMANCE", "DATA", "UI", "INTEGRATION"]

TEMPLATES = [
    ("Customer reports {sym} when {ctx}.", "{area}", "{sev}"),
    ("Multiple users seeing {sym} since {ctx}.", "{area}", "{sev}"),
    ("{sym} — started after {ctx}.", "{area}", "{sev}"),
    ("Escalation: {sym}. Context: {ctx}.", "{area}", "{sev}"),
    ("Ticket describes {sym} occurring when {ctx}.", "{area}", "{sev}"),
]

SYMPTOMS = {
    "BILLING": [("a duplicate charge on the monthly invoice", "CRITICAL"),
                ("the invoice PDF failing to download", "MEDIUM"),
                ("a refund not appearing after two weeks", "HIGH"),
                ("VAT number missing from the receipt", "LOW"),
                ("the card on file being declined silently", "HIGH")],
    "AUTH": [("the SSO redirect looping back to login", "CRITICAL"),
             ("password reset emails never arriving", "HIGH"),
             ("two-factor codes arriving several minutes late", "MEDIUM"),
             ("the session expiring after ten minutes", "MEDIUM"),
             ("a confusing error message on failed login", "LOW")],
    "PERFORMANCE": [("the dashboard taking over 60 seconds to load", "HIGH"),
                    ("exports timing out above 1000 rows", "HIGH"),
                    ("the whole app freezing on long lists", "CRITICAL"),
                    ("search results taking about 8 seconds", "MEDIUM"),
                    ("a slightly slow initial page paint", "LOW")],
    "DATA": [("records silently reverting to an older version", "CRITICAL"),
             ("a CSV import dropping the final row", "HIGH"),
             ("timestamps showing in the wrong timezone", "MEDIUM"),
             ("duplicate entries after a sync", "HIGH"),
             ("a column header being mislabelled", "LOW")],
    "UI": [("the save button being invisible on small screens", "HIGH"),
           ("a modal that cannot be dismissed", "CRITICAL"),
           ("misaligned table columns", "LOW"),
           ("a tooltip covering the field it describes", "MEDIUM"),
           ("dark mode not applying to one panel", "LOW")],
    "INTEGRATION": [("the webhook firing twice per event", "HIGH"),
                    ("the API returning 500s on every third call", "CRITICAL"),
                    ("a Slack notification arriving without a link", "LOW"),
                    ("OAuth tokens expiring a day early", "HIGH"),
                    ("rate limits being hit at half the documented level", "MEDIUM")],
}

CONTEXTS = [
    "the latest release went out", "they switched to the new plan",
    "their team grew past 50 seats", "the overnight sync ran",
    "they enabled the beta flag", "traffic peaked on Monday morning",
    "they migrated from the legacy workspace", "the mobile app updated",
]


def make_example(rng):
    area = rng.choice(AREAS)
    symptom, severity = rng.choice(SYMPTOMS[area])
    ctx = rng.choice(CONTEXTS)
    template = rng.choice(TEMPLATES)[0]
    ticket = template.format(sym=symptom, ctx=ctx)

    # The rigid target format. Base models will not produce this shape
    # unprompted — that is the point.
    target = (
        f"<<{area}|{severity}>>\n"
        f"summary: {symptom}\n"
        f"trigger: {ctx}\n"
        f"escalate: {'yes' if severity in ('HIGH', 'CRITICAL') else 'no'}"
    )
    return {
        "instruction": (
            "Classify this support ticket. Respond in the exact house format "
            "and nothing else."
        ),
        "input": ticket,
        "output": target,
    }


def main():
    p = argparse.ArgumentParser(description="Lab F: build the dataset.")
    p.add_argument("--sizes", nargs="+", type=int, default=[20, 100, 500, 2000],
                   help="training set sizes for the data curve")
    p.add_argument("--val-size", type=int, default=120)
    p.add_argument("--out", default="data")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)

    # one held-out set, used for EVERY training size — otherwise the curve
    # measures the eval set as much as the model
    val = [make_example(rng) for _ in range(args.val_size)]
    val_inputs = {e["input"] for e in val}
    val_path = os.path.join(args.out, "val.jsonl")
    with open(val_path, "w", encoding="utf-8") as fh:
        for e in val:
            fh.write(json.dumps(e) + "\n")
    print(f"  wrote {val_path}  ({len(val)} held-out examples)")

    biggest = max(args.sizes)
    pool = []
    guard = 0
    while len(pool) < biggest and guard < biggest * 50:
        e = make_example(rng)
        guard += 1
        if e["input"] not in val_inputs:      # no leakage into training
            pool.append(e)

    for n in sorted(args.sizes):
        subset = pool[:n]                     # nested, so bigger sets contain smaller
        path = os.path.join(args.out, f"train_{n}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for e in subset:
                fh.write(json.dumps(e) + "\n")
        print(f"  wrote {path}  ({len(subset)} examples)")

    print()
    print("  The training sets are nested: train_100 contains all of train_20.")
    print("  That matters. If each size were a fresh random draw, part of what")
    print("  you measured would be luck in the sample rather than the effect")
    print("  of size.")
    print()
    print("Next: read README.md, then run the training in the Unsloth Colab")
    print("notebook linked in ../CURRENT.md — once per size — and score each")
    print("result with score_outputs.py.")
    print()


if __name__ == "__main__":
    main()
