# Lab A — Walk the space

**Time:** 20–30 minutes · **Cost:** $0 · **Needs:** any laptop, 8GB RAM, no GPU

**Makes visible:** structure exists in the space without anyone putting it there.

Chapters 1 and 2.

---

## Setup

```bash
cd lab-a-embeddings
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

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

**`ModuleNotFoundError: sentence_transformers`** — the venv isn't active, or
`pip install -r requirements.txt` didn't finish. Re-run it and read the output.

**Download fails / SSL errors on a corporate network** — a proxy is probably
intercepting. Use the Colab notebook instead; don't fight the proxy.

**`UnicodeDecodeError` on your CSV** — Excel saved it as something other than
UTF-8. Save As → **CSV UTF-8**.

**Clusters look like nonsense** — check you pointed `--column` at the right
column. If your rows are very short (under about five words), embeddings have
little to work with; try a column with more text in it.
