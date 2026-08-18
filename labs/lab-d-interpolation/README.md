# Lab D — The interpolation walk

**Time:** 45 minutes · **Cost:** $0 local, ~$1–2 rented
**Needs:** same as Lab C

**Makes visible:** the space is continuous and navigable — the model is not
retrieving, it is moving.

Chapters 3 and 6. **This is the most convincing artifact in the book.** If you
do only one lab, do this one.

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

Same dependencies as Lab C. **Reuse Lab C's venv** rather than building a second
4GB one — just call its interpreter by path.

**Run these one line at a time.** Do not paste the fence lines.

### Windows (PowerShell), reusing Lab C

```powershell
..\lab-c-denoising\.venv\Scripts\python.exe interpolate.py
```

### macOS / Linux, reusing Lab C

```bash
../lab-c-denoising/.venv/bin/python interpolate.py
```

### If you skipped Lab C

Build a venv here first, then use it for every command below:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe interpolate.py
```

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python interpolate.py
```

Every `python` below means whichever of those interpreters you chose.

---

## Part one — the walk

```bash
python interpolate.py
```

Two prompts, conceptually distant:

- A: *a medieval stone castle in heavy fog*
- B: *a chrome sports car on a salt flat at noon*

Both get encoded to vectors. Then ten images are generated at evenly spaced
points along the line between those two vectors, **same seed throughout**, into
`output/walk/`.

View them in order.

**What you get is a morph, not a crossfade.** Frame 5 is not frame 0 and frame
9 overlaid at 50% opacity. It's a single coherent image of one thing that is
halfway between two concepts: stone gone metallic, fog thinning into haze over
salt, crenellation becoming aerodynamics.

**Why this is the proof.** If the model were a lookup table of memorised
images, the midpoints would be garbage, or they would snap abruptly from one
endpoint to the other. They don't. The space is continuous and meaning varies
smoothly across it. That's what navigating means, and it's why "it's just
copying its training data" is wrong as a description of the mechanism.

Every frame in the middle is an image of something that has no name.

Try your own pair:

```bash
python interpolate.py --a "a cast iron skillet" --b "a jellyfish" --frames 12
```

Distant, concrete nouns work best. Abstract prompts give mushy walks.

## Part two — close the loop

```bash
python interpolate.py --classify
```

This takes the frames you just **generated** and **recognises** them, using
CLIP, against the two original prompts.

Watch the middle frames come back near-equal on both — flagged as ambiguous —
because that is genuinely where they sit.

You have now generated a point and then read off its coordinates, with the same
machinery pointed in opposite directions. Generation picked an address and
built what belongs there. Recognition read the address something arrived at.

**That's Chapter 3's entire thesis, executed end to end, in about 45 minutes.**

## Part three — linear vs spherical (optional, 5 minutes)

```bash
python interpolate.py --linear
```

By default the script walks the *sphere* between the two vectors rather than
cutting straight through. Here's why that matters, and it's a nice piece of
high-dimensional intuition:

The straight line between two vectors dips toward the origin in the middle —
in the code's own test, magnitude drops by nearly 30% at the midpoint. Vectors
near the origin are shorter than anything the model saw in training, so the
midpoints can come out washed out or incoherent. Spherical interpolation keeps
the magnitude constant the whole way across.

Run both and compare the middle frames. Sometimes the difference is obvious,
sometimes not. Either way you now know why the option exists.

---

## Troubleshooting

**Midpoints are mush** — your two prompts are probably too close, or too
abstract. Use distant, concrete nouns.

**`prompt_embeds` errors** — you've swapped in an SDXL-class model, which has
two text encoders and needs `pooled_prompt_embeds` as well. Stick with SD 1.5
for this lab; that's exactly why it's the default.

**CLIP download fails** — the `--classify` step pulls a separate ~600MB model.
Skip it if you're bandwidth-limited; the walk itself is the main event.

**Out of memory** — `--frames 5 --steps 15`.
