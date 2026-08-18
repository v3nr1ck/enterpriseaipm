# Latent Space — Labs

Companion code for *Latent Space: A Product Manager's Guide to How AI Actually Works*
by James Venrick.

**Live at [enterpriseaipm.com/labs](https://www.enterpriseaipm.com/labs).**
Source: [github.com/v3nr1ck/enterpriseaipm](https://github.com/v3nr1ck/enterpriseaipm).

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

See [SETUP.md](SETUP.md). The short version:

```bash
git clone https://github.com/v3nr1ck/enterpriseaipm.git
cd enterpriseaipm/labs
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
# no root requirements file — install per lab
#   cd lab-a-embeddings && pip install -r requirements.txt
```

Each lab has its own extra requirements, installed per-lab, so you never download
a 2GB library for a lab that doesn't need one.

**On a locked-down work laptop?** Labs A, B, and F have Google Colab paths that
need nothing installed. C and D can run on a rented GPU. Only E really wants a
local install. See SETUP.md for the no-install routes.

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
3. Open an issue. Include your OS, your Python version (`python --version`), and
   the full error text. Failures reported by readers are how TROUBLESHOOTING.md
   gets written.

---

## License

Code: MIT. Do what you like with it.
Book text: © James Venrick, all rights reserved.
