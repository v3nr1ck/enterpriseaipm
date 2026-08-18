# Lab F — Fine-tune, and find the data curve

**Time:** an afternoon · **Cost:** $0 on free Colab, or ~$2–5 rented
**Needs:** a GPU. Free Colab T4 is enough.

**Makes visible:** capability has a price, and the price is measurable in
examples.

Chapters 11 and 12. **This is the most operationally useful lab in the book.**

---

## Quickest way to run this

Double-click **`RUN-THIS-Windows.bat`** (Windows) or
**`RUN-THIS-Mac-Linux.command`** (Mac) in this folder. It builds the datasets
for Step 1. Nothing to install — this lab uses only the standard library.

*Mac: if it refuses to open, right-click it and choose Open, then Open again.
Only needed once.*

---

## What you're actually doing

Most writing treats fine-tuning as a shipping tactic. Here it's a **probe**.

You are going to train the same adapter at four dataset sizes and plot
performance against size. The *shape of that curve* tells you what to do next —
and it is the only cheap way to answer the question product managers get asked
constantly and answer by guessing: **how much labelled data would this take?**

The fine-tuned model is a byproduct. The curve is the deliverable.

---

## Step 1 — Build the dataset

```bash
cd lab-f-finetune
python make_dataset.py
```

Writes `data/train_20.jsonl`, `train_100`, `train_500`, `train_2000`, and one
`val.jsonl` held out from all of them.

Two design choices worth understanding, because if you adapt this to your own
task you need to preserve both:

**The training sets are nested.** `train_100` contains all of `train_20`. If
each size were a fresh random draw, part of what you measured would be luck in
the sample rather than the effect of size.

**One validation set, used for every size.** Otherwise you're measuring the
eval set as much as the model.

The task is deliberately a **rigid output format**, not a knowledge task:

```
<<BILLING|HIGH>>
summary: the card on file being declined silently
trigger: the overnight sync ran
escalate: yes
```

Format-following is what fine-tuning is genuinely good at — Chapter 10, it
lives in the instruction-tuning stage. It's also mechanically checkable, so
scoring involves no judgement calls.

**Do not substitute a knowledge task here.** Fine-tuning for knowledge
half-works and produces confident errors at the edges, which is the worst
possible outcome and a terrible lesson to take from your first run.

## Step 2 — Train, once per size

Use the **current Unsloth Colab notebook**, linked in `../CURRENT.md`.

I'm deliberately not pinning training code in this repo. Unsloth's notebooks are
updated far more often than I could keep a script working, and a stale training
script is the single most likely thing here to waste your afternoon. Use their
notebook, change the data file, run it four times.

Settings to keep constant across all four runs — this is the whole experiment,
so vary nothing else:

| Setting | Value |
|---|---|
| Base model | a 1B–4B instruct model (see `../CURRENT.md`) |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Epochs | 2 |
| Learning rate | 2e-4 |

Also run the **base model with no adapter** over the validation set. That's your
zero point, and without it the curve has no origin.

For each run, write predictions to `runs/<name>.jsonl`, one object per line:

```json
{"input": "<the ticket text>", "predicted": "<what the model produced>"}
```

Name them `base.jsonl`, `train_20.jsonl`, `train_100.jsonl`, and so on — the
scorer reads the size out of the filename.

## Step 3 — Score and read the curve

```bash
python score_outputs.py --curve runs/
```

Four mechanical checks, each worth 25%: header shape, header vocabulary valid,
header classification correct, overall structure. No LLM-as-judge, nothing to
argue about.

You get a per-run breakdown, an ASCII plot, and an interpretation.

---

## Reading the curve — four shapes, four decisions

**Already good at 20 examples, flat after.** The capability was latent. The
base model could always do this; it just needed to be shown the shape you
wanted. **Do not fine-tune.** Use few-shot prompting and go home. You just
saved a project.

**Climbs steeply, then flattens.** The good case. You found the plateau. The
answer to "how much data do we need" is now a number you measured in an
afternoon rather than a guess you defend for a quarter.

**Still climbing at the largest size.** You're underfeeding it. The slope tells
you roughly how much more data it wants, and the budget conversation becomes
arithmetic instead of an argument.

**Flat and bad everywhere.** The most valuable outcome in the book, and the
most counterintuitive. The capability isn't in the base model and adding
examples isn't reaching it. Go to retrieval, or a different base model, or
accept the task isn't learnable in this form. **You found out for a few dollars
in an afternoon instead of after a quarter of headcount.**

A caution the script also prints: an eval set of a hundred-odd rows carries a
few percent of sampling noise on its own. Differences under about 5% are not
differences.

---

## Step 4 — The probe (optional, and the most interesting part)

Take your best adapter and test it on things you **didn't** train on but that
are adjacent — a fifth severity level, a new area code, a slightly different
ticket phrasing.

- **Adjacent capability improves?** The model already had the underlying
  structure and you installed an access route. Worth building on.
- **Unchanged?** It memorised your examples without generalising. Expect to
  retrain every time requirements shift.
- **Got worse?** You found interference — your target behaviour is entangled
  with something else in the model's representation. That's a real, specific
  fact about what's inside, obtained empirically in an afternoon.

This is the closest a non-researcher gets to interpretability work, and it
directly informs whether a capability is a foundation or a liability.

---

## Then do it on your own task

The whole point. Swap in 200 rows of your own data with a checkable output
format, and run the same four sizes.

You will get a real number for a question your organisation currently answers
by guessing. That number is the most valuable thing in this repo.

---

## Troubleshooting

**Colab out of memory** — reduce `max_seq_length` to 512, batch size to 1, and
confirm 4-bit loading is on.

**Loss goes to zero immediately** — your task is too easy or the model is
memorising. With 20 examples and 2 epochs that's expected; look at the
validation score, not the loss.

**Every run scores identically** — you probably didn't actually change the
training file between runs. Check the filename in the notebook each time.

**Colab disconnects mid-run** — free tier has limits. Save adapters to Drive
after each run, or rent a GPU for two hours instead.
