# Lab B — Watch it choose

**Time:** 30 minutes · **Cost:** $0 · **Needs:** any laptop, 8GB RAM

**Makes visible:** there is no decision, only a distribution.

Chapter 4.

---

## Quickest way to run this

Double-click **`RUN-THIS-Windows.bat`** (Windows) or
**`RUN-THIS-Mac-Linux.command`** (Mac) in this folder. It sets everything up
the first time and then runs the lab. Nothing else needed.

*Mac: if it refuses to open, right-click it and choose Open, then Open again.
Only needed once.*

Prefer to type the commands yourself? Carry on below.

---

## Setup

**Run these one line at a time.** Do not paste the fence lines (the triple
backticks) — they are markdown, not commands. Pasting a whole block at once is
the single most common way this lab fails before it starts.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### Verify before you continue

This must print a path ending in `.venv`:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.prefix)"
```

```bash
./.venv/bin/python -c "import sys; print(sys.prefix)"
```

If it prints a conda path, a system Python, or anything else, **stop**. Your
packages installed into the wrong environment and nothing below will work.

### Running the lab

Every `python` in this README means the venv's interpreter:

```powershell
.\.venv\Scripts\python.exe watch_it_choose.py
```

```bash
./.venv/bin/python watch_it_choose.py
```

Calling the interpreter by path is deliberate. It needs no `activate`, so
PowerShell's execution policy cannot block it, and there is no way to silently
install into the wrong environment — which is what `source .venv/bin/activate`
does on Windows, where it fails without stopping the script that follows.

This installs torch, which is a ~2GB download. If that's a problem, use
`colab.ipynb` instead — same lab, nothing installed.

---

## Part one — tokens

Runs automatically at the start of every invocation.

You'll see your prompt broken into the units the model actually processes, and
then `strawberry` and `unbelievable` broken up the same way.

Note that none of `strawberry`'s tokens is the letter `r`. When someone on your
team demonstrates that a model can't count letters, reverse a string, or catch
a typo — this is why. It's a representation problem. No prompt fixes it.

Note also the leading spaces: `' Paris'` and `'Paris'` are different tokens
with different IDs and slightly different behaviour.

## Part two — the distribution

```bash
python watch_it_choose.py
```

At every generation step you get the top ten candidate tokens, their
probabilities, their raw logits, and what fraction of *all* probability mass
those ten hold.

Three things to look for:

**Where it's certain and where it isn't.** After "The capital of France is" the
distribution is a spike — one token holds nearly everything. Mid-sentence in
open prose it's flat across dozens of plausible options. You will start to
develop a feel for which parts of an output were near-forced and which were
near-arbitrary, and that feel transfers directly to knowing which parts of a
model's answer you can lean on.

**What temperature does to the shape.** Run all three and compare:

```bash
python watch_it_choose.py --temperature 0.2
python watch_it_choose.py --temperature 0.8
python watch_it_choose.py --temperature 1.5
```

Watch the tail thicken. Temperature is not a creativity dial in any meaningful
sense; it is a flatness dial on a probability distribution, and you are
watching it flatten.

**A confident prompt versus an open one.**

```bash
python watch_it_choose.py --prompt "The capital of France is"
python watch_it_choose.py --prompt "My favourite thing about Tuesday is"
```

## Part three — the branch points

```bash
python watch_it_choose.py --near-ties
```

This walks 25 steps at temperature 0 and flags every step where the top two
tokens are within 3% of each other.

Each one of those is a place where two different outputs were nearly equally
likely. In production, requests get batched together on the GPU, and
floating-point addition isn't associative, so the arithmetic can come out
fractionally differently from run to run. At a near-tie, that difference flips
which token wins.

**This is why temperature 0 is not deterministic in practice**, even though it
is in theory. If you have ever sat in a meeting where someone said "but it
worked yesterday," this is sometimes literally the reason.

---

## Using Ollama instead

Ollama is easier to install than torch, but its exposure of raw logits has
moved between versions, which is why this lab uses `transformers` by default.

If your Ollama version supports `logprobs` on the OpenAI-compatible endpoint,
you can swap it in: point an OpenAI client at `http://localhost:11434/v1`, set
`logprobs=True` and `top_logprobs=10`, and read the same numbers off the
response. Check your version's docs first — if the field isn't there, don't
fight it, just use the default path.

---

## Troubleshooting

**Download is enormous / disk full** — torch plus a small model is ~4GB. Use
Colab.

**Very slow on CPU** — expected. The default model is small enough to tolerate
it, but reduce `--steps 3` and `--top-n 5` if you're impatient. You're reading
the distribution, not generating an essay.

**Model name 404s** — the tag changed. See `../CURRENT.md` for the current
pick and substitute any small instruct model; nothing in this lab depends on
which one.
