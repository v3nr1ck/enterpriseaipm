# Lab A — Walk the space

**Time:** 20–30 minutes · **Cost:** $0 · **Needs:** any laptop, 8GB RAM, no GPU

**Makes visible:** structure exists in the space without anyone putting it there.

Chapters 1 and 2.

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
.\.venv\Scripts\python.exe walk_the_space.py
```

```bash
./.venv/bin/python walk_the_space.py
```

Calling the interpreter by path is deliberate. It needs no `activate`, so
PowerShell's execution policy cannot block it, and there is no way to silently
install into the wrong environment — which is what `source .venv/bin/activate`
does on Windows, where it fails without stopping the script that follows.

First run downloads a ~90MB model. Once only.

**No-install route:** open `colab.ipynb` in Google Colab. Nothing to install,
nothing to uninstall, works on a locked-down work laptop.

---

## Part one — the similarity matrix

```bash
python walk_the_space.py
```

Sixteen words go in. A 16×16 similarity matrix comes out, plus each word's
nearest neighbours.

**What to actually do with the output** — not just read it:

1. Find the three obvious clusters (animals, colours, emotions). Confirm they
   cluster. That's the boring part and it takes ten seconds.
2. **Go to the four trap words: `bank`, `light`, `charge`, `spring`.** Each is
   at least two different words wearing one spelling. Look at where each one
   landed. The model got no context, so it had to produce a single vector
   averaging every sense it knows. Which sense won? Why that one?
3. Read the RANDOM BASELINE section carefully. It reports what two *random*
   vectors score against each other, and the answer is essentially zero with a
   very small spread. This is the number that should recalibrate you: against
   that baseline, a similarity of 0.4 is not "somewhat similar," it is twelve
   standard deviations off random.

Then run it on your own words:

```bash
python walk_the_space.py --words invoice refund chargeback dispute latency
```

Use vocabulary from your actual product. Find a pair that your product treats
as unrelated but the model puts close together — or the reverse.

## Part two — word arithmetic

Included in the same run. `king − man + woman = ?` and three others.

**Some of these will fail.** That is the finding, not a bug. Spend your time on
the failures: they tell you which properties the model encoded as clean linear
directions and which it didn't, and that is a map of what the model can and
can't do for you.

The clean king/queen result you have read about a hundred times came from older
*word-level* models. Modern sentence-embedding models are contextual, and with
no context the arithmetic gets messy. The underlying claim — directions carry
meaning — holds. The party trick is oversold. Both things are true, and a book
that tells you only the first one is selling you something.

## Part three — cluster your own data

**This is the one that changes how you think.** Everything above was warm-up.

```bash
python cluster_your_data.py                                  # sample data
python cluster_your_data.py --csv mine.csv --column body     # YOUR data
```

Export 100+ rows of real text from your own work: support tickets, feature
requests, sales call notes, churn survey responses, anything. One column of
text, saved as UTF-8 CSV.

You did not define categories. You did not label a single row. You did not
train anything. The clusters were already there, in the geometry, and k-means
just noticed.

**Now the actual lab, which is not the script:** pull up however your company
currently categorizes that same data. Put the two side by side.

- Where did the machine **split** something your taxonomy merges?
- Where did it **merge** something your taxonomy splits?
- For each disagreement: which one is wrong? Sometimes the machine. Often not.

Then look at the rows the script flags as **least central**. Those are the
items that don't really belong to any cluster, which in my experience is
reliably where the real edge cases live — and where your taxonomy is quietly
failing today.

That comparison is the deliverable. If you do one thing from this lab in the
next week, do it on data your team argues about.

---

## Troubleshooting

**`ModuleNotFoundError: sentence_transformers`** — you are running a different
Python from the one you installed into. Check which:

```powershell
.\.venv\Scripts\python.exe ..\verify_setup.py
```

If that reports a conda or system Python rather than the `.venv`, your packages
went elsewhere. Install with the venv's interpreter explicitly, not bare `pip`.

**Download fails / SSL errors on a corporate network** — a proxy is probably
intercepting. Use the Colab notebook instead; don't fight the proxy.

**`UnicodeDecodeError` on your CSV** — Excel saved it as something other than
UTF-8. Save As → **CSV UTF-8**.

**Clusters look like nonsense** — check you pointed `--column` at the right
column. If your rows are very short (under about five words), embeddings have
little to work with; try a column with more text in it.
