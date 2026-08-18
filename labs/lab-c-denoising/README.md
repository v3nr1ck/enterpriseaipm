# Lab C — Denoise in public

**Time:** 45–60 minutes · **Cost:** $0 local, ~$1 rented
**Needs:** 6GB VRAM, or Apple Silicon with 16GB unified, or a rented GPU

**Makes visible:** generation is a walk from noise, not a lookup.

Chapter 5.

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
.\.venv\Scripts\python.exe denoise_in_public.py
```

```bash
./.venv/bin/python denoise_in_public.py
```

Calling the interpreter by path is deliberate. It needs no `activate`, so
PowerShell's execution policy cannot block it, and there is no way to silently
install into the wrong environment — which is what `source .venv/bin/activate`
does on Windows, where it fails without stopping the script that follows.

First run downloads ~4GB of model weights. Once only.

**No GPU?** See `../SETUP.md` for renting one for an hour (about $0.35–0.69).
An RTX 4090 or an A5000 is plenty. Do not rent an H100 for this.

**CPU-only** works but is genuinely painful — several minutes per image. If
you're going that route, use `--steps 8` and accept ugly results; you're
looking at the *sequence*, not the quality.

---

## Why an old model

The default is Stable Diffusion 1.5, from 2022. There are far better generators
now and we are not using them on purpose:

- One text encoder instead of two, which makes the Lab D interpolation about
  fifteen lines instead of fifty.
- Runs on 4GB of VRAM.
- Every mechanism in Chapter 5 is present and visible.

This is the teaching model, not the quality model. Newer families want 10–12GB
minimum and complicate the code without changing a single thing you're meant to
learn. Go look at current models afterwards, separately.

---

## Part one — the walk

```bash
python denoise_in_public.py
```

Generates one image and saves a PNG at **every** denoising step into
`output/trace/`.

Now open that folder and scan the files in order. This is the lab. It is not
complicated and it doesn't need to be.

**The thing nobody tells you in advance: notice how early the composition is
fixed.** Within the first fifth of the steps — before there's anything you'd
call detail — the overall structure is already committed. Everything after is
refinement inside a decision that has already been made.

That has a direct product consequence. If a generation is going to come out
wrong in composition, it was wrong within the first few steps, and adding steps
at the end will not save it.

## Part two — three sweeps

**Step count.** Where does it stop improving?

```bash
python denoise_in_public.py --sweep-steps
```

Same seed, same prompt, at 2/5/10/20/35/50 steps. Line them up. Somewhere
between 20 and 35 the returns stop. That point is your quality/cost frontier,
measured rather than guessed — and it is the same *shape* of curve you'll meet
again in Lab F with training examples on the x-axis instead of steps.

**Guidance.** What CFG scale actually does.

```bash
python denoise_in_public.py --sweep-guidance
```

At 1.0 the model wanders wherever it likes and barely registers your words. At
7.5 you get adherence with natural results. At 25 it's contorted and
oversaturated — you amplified the text direction so hard that you pushed the
latent outside the region where the decoder produces anything sane.

You are watching a vector subtraction get multiplied. That slider is in every
image UI on earth and almost nobody using it knows what it's doing.

**Seeds.** Same words, different starting point.

```bash
python denoise_in_public.py --sweep-seeds
```

Every one of those images got identical instructions. All the variation comes
from where the walk started.

Keep that distinction: **"the prompt was ambiguous" and "the walk started
somewhere else" are different diagnoses with different fixes**, and teams
confuse them constantly. If seeds vary wildly on a prompt you thought was
specific, that tells you the prompt is underconstraining the region — which is
a prompt problem. If they're all similar and all wrong, that's a model problem.

---

## Troubleshooting

**CUDA out of memory** — add `--steps 15`, or use
`stabilityai/sdxl-turbo` with `--steps 4`, or rent a GPU. The script already
enables attention slicing on CUDA.

**`safety_checker` warnings** — expected and harmless; it's disabled
deliberately so it can't silently blank an image mid-sweep and confuse your
comparison.

**Model 404s** — Hugging Face repo IDs get renamed. `../CURRENT.md` lists the
current ID and a mirror.

**macOS: very slow or black images** — MPS support varies by torch version.
Try `--device cpu` to confirm the pipeline works at all, then upgrade torch.

**Images are all noise** — you're looking at early steps. Check `final.png`.
