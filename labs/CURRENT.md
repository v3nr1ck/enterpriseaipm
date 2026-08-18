# CURRENT

**Everything on this page goes stale. This is the only file that does.**

The book contains no model names, no versions, and no prices, on purpose. They all
live here, where they can be corrected without reprinting anything.

**Last verified: 18 August 2026** — every model id and tag on this page was checked
against the live Hugging Face and Ollama registries on that date.

If you are reading this more than about six months after that date and something
doesn't work, the model name has probably changed. Substitute a current equivalent
of the same size class — the labs teach mechanisms, and mechanisms don't care which
specific model you point them at.

---

## Lab A — Embeddings

| Role | Current pick | Why |
|---|---|---|
| Default | `sentence-transformers/all-MiniLM-L6-v2` | 90MB, 384 dims, runs on CPU in seconds. Not the best model available; it is the best *teaching* model because nothing about it is slow enough to obscure the point. |
| Step up | `BAAI/bge-m3` | ~2GB, much stronger retrieval quality, multilingual. Use if you want the clustering in Part Three to be sharper. |

The word-arithmetic section (king − man + woman) works most cleanly on older
*word-level* models, `glove-wiki-gigaword-100` via `gensim`. Modern sentence
embedding models are contextual and the arithmetic is messier on them. **This is
covered in the lab and the messiness is part of the lesson** — don't "fix" it.

## Lab B — Sampling

| Role | Current pick | Notes |
|---|---|---|
| Default | `Qwen/Qwen2.5-0.5B-Instruct` | ~1GB download, runs on CPU. Small enough that CPU-only generation is tolerable. |
| Step up | `Qwen/Qwen3-1.7B` | ~3.4GB. Sharper distributions, still CPU-tolerable. |
| Fallback | `Qwen/Qwen3-0.6B` | Smallest current option. Use if the above are gone. |

We use Hugging Face `transformers` rather than Ollama here, because we need raw
logits and Ollama's exposure of them has moved around between versions. If you'd
rather use Ollama and your version exposes `logprobs` on the OpenAI-compatible
endpoint, the lab README explains the swap.

## Labs C & D — Diffusion

| Role | Current pick | VRAM |
|---|---|---|
| Default | `stable-diffusion-v1-5/stable-diffusion-v1-5` | ~4GB |
| Faster | `stabilityai/sdxl-turbo` | ~7GB, 1–4 steps instead of 30 |
| Lighter | `stabilityai/sd-turbo` | ~2.5GB, 1–4 steps |

The old `runwayml/stable-diffusion-v1-5` id was retired; it still 307-redirects to
the canonical repo above, but point at the canonical name directly.

**Why an old model?** SD 1.5 is from 2022 and there are far better generators now.
We use it anyway because it has one text encoder instead of two, which makes the
Lab D interpolation about fifteen lines instead of fifty, and because it runs on
4GB of VRAM. This is the teaching model, not the quality model. Newer families
(SD 3.5, FLUX) want 10–12GB minimum and complicate the code without changing a
single thing you're meant to learn.

If you want to see what current models produce, do that separately, after the lab.

## Lab E — Quantization

Quantization tags change constantly and vary per model. **Do not trust a hardcoded
tag.** Check the live tag list before running:

- Browse `https://ollama.com/library/<model>/tags`
- Or run `ollama show <model> --modelfile` after pulling

As of August 2026, two verified ladders. **Which you pick changes what the lab
shows**, so pick deliberately:

**Recommended — `llama3.1:8b-instruct`** (~16.6GB for all three). At 2-bit this
model stays fluent and well-formed but gets edge facts confidently wrong, which
is the lesson the lab is built around:

```
llama3.1:8b-instruct-q8_0      # high precision
llama3.1:8b-instruct-q4_K_M    # the standard default
llama3.1:8b-instruct-q2_K      # fluent, confident, wrong
```

**Cheaper — `qwen2.5:3b-instruct`** (~6.5GB for all three). Shows a different
result: at 2-bit a 3B model does not degrade, it collapses into repeated digits
and stray CJK and never stops generating. Useful, but it is a viability-cliff
demo, not a confident-wrongness demo:

```
qwen2.5:3b-instruct-q8_0
qwen2.5:3b-instruct-q4_K_M
qwen2.5:3b-instruct-q2_K       # collapses entirely
```

**The `gemma4` family no longer publishes anything below q4_K_M**, so it cannot
be used for this lab at all — there is no low-precision end to the ladder.

Verified 18 August 2026: the q4_K_M and q2_K tags of both families above were
pulled and run. `llama3.1:8b-instruct-q8_0` was not pulled; it is listed on the
assumption that q8 is no worse than q4.

The lab script takes the tags as arguments, so you can substitute freely. What
matters absolutely is that you compare *the same model* at different
precisions — that is the only way to isolate quantization from base capability.

The model is **not** irrelevant, though, which is a correction to earlier
advice here. Size determines whether you see graceful degradation or a cliff,
and a model that is simply bad at a task will be bad at it at every precision.

## Lab F — Fine-tuning

| Role | Current pick |
|---|---|
| Training library | `unsloth` — 2× faster, ~70% less VRAM, and has maintained free Colab notebooks |
| Base model | A 1B–4B instruct model. As of writing, `unsloth/Qwen3-4B-Instruct-2507` or similar |
| Free compute | Google Colab free tier (T4, ~15GB VRAM) fits a 4-bit 7B comfortably |

Unsloth maintains its own notebooks at `https://unsloth.ai/docs` and they are
updated far more often than this repo. **Prefer their current notebook over any
pinned code here** — use our `make_dataset.py` to build the data and the data-curve
protocol in the lab README, then run the training in their notebook.

---

## Rented GPUs

RunPod pod rates, list price, checked August 2026. These move:

| GPU | VRAM | Secure Cloud | Community Cloud |
|---|---|---|---|
| RTX A5000 | 24GB | ~$0.27/hr | — |
| A40 | 48GB | ~$0.44/hr | ~$0.35/hr |
| RTX 4090 | 24GB | ~$0.69/hr | ~$0.34/hr |
| A100 PCIe | 80GB | ~$1.39/hr | — |
| H100 PCIe | 80GB | ~$2.89/hr | — |

For every lab here, **an RTX 4090 or an A5000 is more than enough.** Do not rent an
H100 for these. You will not go faster in any way you can perceive, and you will
pay four times as much.

### The storage trap

**A stopped pod still bills for storage.** Network volumes start around
$0.07/GB/month and accrue whether or not the pod is running. If you finish a lab
and stop the pod, you are still paying.

**Terminate. Don't stop.** Move anything you want to keep off the pod first.

This is the single most common way people are surprised by a GPU bill, and it is
entirely avoidable.

---

## Changelog

| Date | Change |
|---|---|
| Aug 2026 | Initial version. |
