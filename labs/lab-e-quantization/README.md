# Lab E — Watch it degrade

**Time:** 45 minutes · **Cost:** $0 · **Needs:** 16GB RAM, no GPU required

**Makes visible:** quality is a purchasable dial, and a degraded model sounds
exactly as confident as a good one.

Chapter 9.

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
aggressive. Something like q8_0, q4_K_M, q2_K. Which model barely matters; the
comparison is the point.

```bash
ollama pull gemma4:e4b-it-q8_0
ollama pull gemma4:e4b-it-q4_K_M
ollama pull gemma4:e4b-it-q2_K
```

Check the download sizes as they come down. That ratio — roughly 4:2:1 — *is*
the lab's premise made concrete before you've run anything.

---

## Run it

```bash
python compare_quants.py --tags gemma4:e4b-it-q8_0 \
                                gemma4:e4b-it-q4_K_M \
                                gemma4:e4b-it-q2_K
```

Nine prompts across three categories, all three models, temperature 0 so the
comparison is like for like. The script pre-flights which models are actually
pulled and tells you before it starts, rather than failing forty minutes in.

---

## What you should find

The degradation is **not uniform**, and the pattern is the finding:

| Category | Behaviour |
|---|---|
| **Recall** | Survives all the way down. A 2-bit model still knows the capital of France. |
| **Format-following** | Degrades in the middle. Constraints get dropped one at a time — it obeys three of your four rules. |
| **Reasoning** | Breaks first and breaks hardest. Multi-step arithmetic and logic go before anything else. |

**Score them yourself.** Write numbers in a file. Do not skip this by
eyeballing the output and forming an impression — an impression is exactly the
failure mode this lab exists to inoculate you against. Use
`../eval-template/eval_template.csv`.

---

## The actual point

Here is the thing you can only get by doing this rather than reading it:

**The 2-bit model sounds exactly as confident as the 8-bit one.** It is fluent.
It is well-formed. It is wrong. There is no hedging, no degradation in tone, no
signal in the prose that anything is amiss.

And notice: if you had only tested it on the recall prompts, you would have
concluded it was fine and shipped it.

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
