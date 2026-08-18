# Latent Space — Labs

Companion code for *Latent Space: A Product Manager's Guide to How AI Actually Works*.

**Everything volatile lives in [CURRENT.md](CURRENT.md)** — model names, versions,
approximate costs. The book deliberately avoids printing those, because they go
stale. If a command in a lab fails, check CURRENT.md first, then
[TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## What these labs are for

Each lab exists to make one abstract idea physically visible. **None of them is a
recipe for shipping anything.** You are not building a product here. You are
looking at a mechanism directly so that you stop having to take anyone's word for
how it behaves.

If you finish a lab and think "that was small," that's correct. The size is the
point. The insight is not.

| Lab | What it makes visible | Time | Cost | Floor hardware |
|---|---|---|---|---|
| [A](lab-a-embeddings/) | Structure exists in the space without anyone labeling it | 20–30 min | $0 | Any laptop, 8GB RAM |
| [B](lab-b-sampling/) | There is no decision, only a distribution | 30 min | $0 | Any laptop, 8GB RAM |
| [C](lab-c-denoising/) | Generation is a walk from noise | 45–60 min | $0–1 | 6GB VRAM, or rent |
| [D](lab-d-interpolation/) | The space is continuous and navigable | 45 min | $0–2 | 6GB VRAM, or rent |
| [E](lab-e-quantization/) | Quality is a purchasable dial | 45 min | $0 | 16GB RAM |
| [F](lab-f-finetune/) | Capability has a price measured in examples | An afternoon | $2–5 | Free Colab, or rent |

Total spend if you do all six and use free Colab where offered: **under $5.**

---

## Order

A and B first, in that order. They install almost nothing and they establish the
two ideas everything else builds on — a space with structure in it, and sampling
from a distribution.

After that, C and D go together (D reuses C's setup), and E and F are independent.

---

## Setup

**You do not need GitHub, git, or a terminal.**

1. Unzip the file you downloaded.
2. Open the folder for the lab you want — start with `lab-a-embeddings`.
3. Double-click **`RUN-THIS-Windows.bat`** (Windows) or
   **`RUN-THIS-Mac-Linux.command`** (Mac).

That is the whole setup. The launcher finds Python, builds a private setup for
that lab the first time you run it, and then runs the lab. A window opens and
stays open so you can read the output.

If Python is not installed, the launcher tells you exactly what to download and
which box to tick in the installer. (It is "Add Python to PATH", on the first
screen, and it is easy to miss.)

**Mac note:** the first time you open a `.command` file, macOS may refuse
because it was downloaded from the internet. Right-click it and choose **Open**,
then **Open** again in the dialog. You only do this once per file.

### If you would rather type commands

Each lab's README has the exact commands for Windows and for Mac/Linux, one
line at a time. There is no top-level install: **each lab has its own
`requirements.txt` and its own private environment**, so you never download a
2GB library for a lab that does not need one. Labs C and D share one; Labs E
and F install nothing at all.

### If something goes wrong

Run the preflight. It reports which Python you are using, whether the lab's
packages are installed, and whether the lab's models still exist:

```
python verify_setup.py
```

Then see [TROUBLESHOOTING.md](TROUBLESHOOTING.md), which opens with the four
problems that catch almost everyone.

**On a locked-down work laptop?** Labs A, B, and C ship a `colab.ipynb` that
runs in Google Colab with nothing installed on your machine at all — the
notebook carries the lab's code inside it, so you upload one file and press
Run All. Lab F's training runs in Colab too (see its README). Lab E needs
Ollama locally and has no no-install route. See SETUP.md.

---

## A word on the code

These scripts are written to be *read*, not reused. They are longer and more
explicit than they need to be, they avoid clever abstractions, and they print
their intermediate state constantly — because the printing is the lab. If a
script looks like it's doing something the long way, it is, deliberately.

Nothing here is production code and none of it should be treated as such.

---

## When something breaks

1. Check [CURRENT.md](CURRENT.md) — a model name has probably changed.
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — someone has probably hit it.
3. Still stuck? Email me with your OS, your Python version, and the full error
   text — copy the whole thing, not a summary of it. Reader reports are how
   TROUBLESHOOTING.md gets written.

---

## License

Code: MIT. Do what you like with it.
Book text: © James Venrick, all rights reserved.
