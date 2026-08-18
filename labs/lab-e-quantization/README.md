# Lab E — Watch it degrade

**Time:** 45 minutes · **Cost:** $0 · **Needs:** 16GB RAM, no GPU required

**Makes visible:** quality is a purchasable dial, and a degraded model sounds
exactly as confident as a good one.

Chapter 9.

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

Install Ollama: <https://ollama.com/download>

Then start it and leave it running in its own terminal:

```bash
ollama serve
```

No Python dependencies beyond the standard library. This lab deliberately uses
nothing but `urllib`, so there is nothing to install and nothing to break.

---

## Choosing your three tags

**Do not trust a hardcoded model tag.** They change constantly and vary per
model. Check what exists right now:

- Browse `https://ollama.com/library/<model>/tags`
- `../CURRENT.md` has a working set as of August 2026

You want **the same model at three precisions** — high, standard, and
aggressive. Something like q8_0, q4_K_M, q2_K.

Holding the model constant is non-negotiable; that is what isolates precision
from capability. But **which** model you pick is not arbitrary either: below
about 8B, 2-bit tends to destroy the model outright rather than degrade it, so
you see a cliff instead of the confident-wrongness this lab is about.

```bash
ollama pull llama3.1:8b-instruct-q8_0
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull llama3.1:8b-instruct-q2_K
```

That is ~16.6GB. For a ~6.5GB alternative that shows a *collapse* rather than
confident wrongness, substitute `qwen2.5:3b-instruct` throughout — see
`../CURRENT.md` for what each choice demonstrates.

Check the download sizes as they come down. That ratio — roughly 4:2:1 — *is*
the lab's premise made concrete before you've run anything.

---

## Run it

One line — do not split it. The `\` continuation character is bash;
PowerShell uses a backtick and will error on `\`.

```bash
python compare_quants.py --tags llama3.1:8b-instruct-q8_0 llama3.1:8b-instruct-q4_K_M llama3.1:8b-instruct-q2_K
```

Thirteen prompts across four categories, every model, temperature 0 so the
comparison is like for like. The script pre-flights which models are actually
pulled and tells you before it starts, rather than failing forty minutes in.

**On the token cap.** Answers are capped at 512 generated tokens
(`--max-tokens`), and anything that hits the cap is marked
`[truncated at 512 tokens]`. Read that marker carefully, because it means two
different things:

- On a **hard reasoning prompt at high precision**, it just means a long
  answer. Not a defect.
- On a **heavily quantised model**, it often means the model never emitted a
  stop token at all. Below its viability threshold a model can degenerate into
  repeated digits and stray characters and run until something stops it. That
  is not a bug in the script — it is the most vivid thing in this lab.

The cap exists because without it a single collapsed model can generate for
longer than the entire rest of the lab takes.

---

## What you should find

The degradation is **not uniform**, and the *order* in which things break is
the finding.

Here is a real run. `llama3.1:8b-instruct`, same prompts, same seed, only the
precision changing:

| Task | q8_0 | q4_K_M | q2_K | Breaks at |
|---|---|---|---|---|
| Capital of France, Moby-Dick author, Berlin Wall year | ✓ | ✓ | ✓ | never |
| Bare JSON array, 12-word summary, single-word reply | ✓ | ✓ | ✓ | never |
| Third President of the United States | ✓ | ✓ | **✗** | q4 → q2 |
| Bloop/Razzie syllogism | ✓ | **✗** | **✗** | **q8 → q4** |

Read the last column, because it is the whole lab. **Reasoning broke one full
step earlier than anything else.** The logic question was already wrong at
q4_K_M — the quantization most people ship without thinking about it — while
every recall and formatting task was still perfect and stayed perfect two
levels further down.

And look at *how* it fails. At q8 the model answers "No" and explains that the
premises do not license the conclusion. At q4 it answers "Yes" and justifies
itself by invoking the "transitive property." At q2 it answers "Yes" and cites
"transitive inference." The wrong answers are fluent, confident, correctly
punctuated, and reference a real logical principle that simply does not apply.
Nothing in the prose signals that anything has degraded.

The edge-recall failure has the same character: `John Adams` for the third
President. He *was* a president — the second. It is an off-by-one from a
half-remembered list, delivered in exactly the tone of the correct answers.

**That is the finding.** If you had tested only on recall and formatting — which
is what a quick smoke test looks like — you would have shipped q4 and concluded
it was fine.

### One prompt is not evidence

The `recall_edge` set also contains a genuine caution. Asked who the second
person to walk on the Moon was:

| q8_0 | q4_K_M | q2_K |
|---|---|---|
| Pete Conrad ✗ | Buzz Aldrin ✓ | Alan Bean ✗ |

That is **not** monotonic — the highest-precision model got it wrong and the
middle one got it right. All three answers name real Apollo astronauts who
really did walk on the Moon; the model is picking from roughly the right list
and ordering it badly, and small numerical changes reshuffle that pick almost
arbitrarily.

So do not build a conclusion on one prompt. Score the whole set, write the
numbers down, and look at the pattern across categories. A single flipped
answer is noise. **The pattern — reasoning first, then edge facts, with easy
recall and formatting untouched — is signal.**

Also: only attribute a failure to quantization when the **same model at higher
precision gets it right**. Some failures are just the base model's ceiling.
That comparison is the only thing that isolates the variable, and it is why
this lab insists on one model at several precisions rather than several
different models.

### Below a certain size, it does not degrade — it dies

`qwen2.5:3b-instruct-q2_K` does not produce degraded prose. It produces
repeated digits and stray CJK characters and never emits a stop token. A 3B
model at 2-bit is past its viability threshold. That is a real and useful
result — it tells you the "quality dial" has a floor you can fall through —
but it is a *different* lesson from the confident-wrongness above, and you need
a model with more headroom (8B or larger) to see that one.

**Score them yourself.** Write numbers in a file. Do not skip this by
eyeballing the output and forming an impression — an impression is exactly the
failure mode this lab exists to inoculate you against. Use
`../eval-template/eval_template.csv`.

---

## The actual point

Here is the thing you can only get by doing this rather than reading it:

**The degraded model sounds exactly as confident as the good one.** It is
fluent. It is well-formed. It is wrong. There is no hedging, no shift in tone,
no signal anywhere in the prose that anything is amiss.

And the villain is not the obvious one. The 2-bit model is easy to catch — on a
small enough model it stops producing language at all. The dangerous result is
**q4_K_M**, which is the default nearly everyone ships: it answered every
recall and formatting prompt perfectly, and got the logic question confidently
wrong. It looks fine precisely where you would think to look, and fails where
you would not.

Notice what follows. If you had smoke-tested it on recall and formatting — which
is what a smoke test *is* — you would have shipped it and concluded it was fine.

Once you've watched that happen in your own terminal, you will never again
accept "it seemed fine in testing" as evidence about a model swap, a quantization
change, or a vendor's silent update. That reflex is worth more than everything
else in this lab.

---

## Optional: the memory trade

Run `ollama ps` while a model is loaded to see its actual memory footprint.

Then check the rule from Chapter 9 for yourself: **a bigger model at 4 bits
usually beats a smaller model at 8 bits in the same memory budget.** Pull a
larger model at q4 with roughly the same footprint as your smaller one at q8,
and run both through these same prompts.

Capacity is worth more than precision over a surprisingly wide range. That one
finding will change how you size a local deployment.

---

## Troubleshooting

**`Can't reach Ollama`** — `ollama serve` isn't running, or it's on a different
port. Pass `--host http://localhost:11434`.

**404 on a tag** — that quantization doesn't exist for that model. Check the
tags page. Not every model ships every quant, and q2 in particular is often
missing for small models.

**Very slow** — expected on CPU. These are small models; give it time. Reduce
the prompt set by editing `prompts.json` if you're impatient.

**All three give identical answers** — you may have pulled three tags that
resolve to the same underlying file. Run `ollama list` and compare the sizes and
digests. If they match, the tags are aliases.
