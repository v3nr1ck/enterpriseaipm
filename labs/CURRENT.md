# CURRENT

**Everything on this page goes stale. This is the only file that does.**

The book contains no model names, no versions, and no prices, on purpose. They all
live here, where they can be corrected without reprinting anything.

**Last verified: August 2026.**

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
| Default | `Qwen/Qwen2.5-0.5B-Instruct` | Text-only, ~1GB, runs on CPU. Use this — Lab B needs raw next-token logits from a causal LM. |
| Do not use | `Qwen/Qwen3.5-0.8B` | Real model, but it is a **vision-language** checkpoint (`Qwen3_5ForConditionalGeneration`). `AutoModelForCausalLM` will fail or fight you. |
| Fallback | `Qwen/Qwen3-0.6B` | Also text-only. Use if 2.5 is gone. |

We use Hugging Face `transformers` rather than Ollama here, because we need raw
logits and Ollama's exposure of them has moved around between versions. If you'd
rather use Ollama and your version exposes `logprobs` on the OpenAI-compatible
endpoint, the lab README explains the swap.

## Labs C & D — Diffusion

| Role | Current pick | VRAM |
|---|---|---|
| Default | `runwayml/stable-diffusion-v1-5` | ~4GB |
| Faster | `stabilityai/sdxl-turbo` | ~7GB, 1–4 steps instead of 30 |
| Mirror, if the above 404s | `stable-diffusion-v1-5/stable-diffusion-v1-5` | ~4GB |

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

As of August 2026, a working set on the `gemma4` family:

```
gemma4:e4b-it-q8_0      # high precision
gemma4:e4b-it-q4_K_M    # the standard default
gemma4:e4b-it-q2_K      # where it breaks
```

The lab script takes the three tags as arguments, so you can substitute freely.
What matters is that you compare *the same model* at three precisions — which
model is almost irrelevant.

## Lab F — Fine-tuning

| Role | Current pick |
|---|---|
| Training library | `unsloth` — 2× faster, ~70% less VRAM, and has maintained free Colab notebooks |
| Base model | A 1B–4B **text** instruct model from the current Unsloth notebook. As of writing, `unsloth/Qwen3-4B-Instruct` or `unsloth/Qwen2.5-3B-Instruct`. Avoid natively multimodal Qwen3.5 checkpoints unless the notebook says they work. |
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
