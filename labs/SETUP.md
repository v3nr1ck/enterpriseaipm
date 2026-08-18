# Setup

Read this once. Each lab's README repeats the parts it needs.

---

## What you need

| Lab | Python | GPU | Disk | Install size |
|---|---|---|---|---|
| A | 3.9+ | no | ~500MB | small |
| B | 3.9+ | no | ~4GB | torch (~2GB) |
| C, D | 3.9+ | 6GB VRAM, or rent | ~8GB | torch + diffusers |
| E | 3.9+ | no | ~15GB models | none (Ollama app) |
| F | 3.9+ | yes — free Colab is fine | small locally | none locally |

Python 3.9 or newer. Check with `python --version`. On some systems the command
is `python3`.

---

## The three routes

### 1. Just run it (recommended, and what most readers should do)

Unzip the download, open a lab folder, and double-click
**`RUN-THIS-Windows.bat`** or **`RUN-THIS-Mac-Linux.command`**. It handles
Python, the environment, and the install for you, and explains what to do if
Python is missing.

Everything below is for people who would rather drive it themselves.

### 2. Local install by hand

**Run these one line at a time.** Do not paste the fence lines.

**Windows (PowerShell)**

```powershell
cd latent-space-labs\lab-a-embeddings
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe walk_the_space.py
```

**macOS / Linux**

```bash
cd latent-space-labs/lab-a-embeddings
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python walk_the_space.py
```

The labs call the venv's interpreter by path instead of using `activate`. This
is not stylistic. `activate` is the step that fails silently: on Windows the
bash form `source .venv/bin/activate` errors, and if you keep going, `pip`
installs into whatever Python is on your PATH — commonly Anaconda's base
environment, where it can break unrelated packages. Calling the interpreter
directly makes that failure impossible.

**Check which environment you are actually in** at any point:

```
python verify_setup.py
```

Run it from a lab folder with that lab's interpreter. It reports the Python in
use, whether it is a venv, what is installed, and whether the lab's models
resolve.

**Use a virtual environment per lab.** They have conflicting-ish dependency
weights and you do not want a 2GB torch install for Lab A, which doesn't need
it. Labs C and D can share one.

### 3. Google Colab (nothing installed)

Labs A, B, and C ship a self-contained `colab.ipynb`. Each notebook carries
the lab's code inside it, so there is nothing to clone and nothing to upload
besides the notebook itself. This is the right answer if:

- your work laptop is locked down and you can't install things
- you don't want 8GB of ML libraries on your machine
- you tried route 1 and hit a wall

Colab gives you a free GPU (T4, ~15GB VRAM), which is enough for every lab
here including the fine-tune.

### 4. Rented GPU (Labs C, D, F)

You need this only if you want to run diffusion locally and have no GPU.

1. Make an account at RunPod (or any equivalent — nothing here is
   RunPod-specific).
2. Deploy a **Pod**, not Serverless.
3. Pick an **RTX 4090** or **RTX A5000**. Roughly $0.35–0.69/hr.
   **Do not rent an H100.** It costs four times as much and you will not
   perceive any difference on these workloads.
4. Choose a PyTorch template. It comes with torch and CUDA already set up.
5. Connect via the web terminal or JupyterLab.
6. Upload the lab folder (or re-download the zip on the pod), `pip install -r requirements.txt`, run the lab.
7. **Terminate the pod when you're done.**

### The storage trap — read this bit

**A stopped pod still bills for storage.** Network volumes start around
$0.07/GB/month and accrue whether or not the pod is running.

**Terminate, don't stop.** Copy anything you want off the pod first.

This is the single most common way people get a surprise GPU bill, and it is
entirely avoidable by knowing it exists.

---

## Windows / PowerShell

Every lab works on Windows. The commands differ enough to be worth spelling out,
because the failure modes are different too.

### Quickstart

```powershell
cd latent-space-labs\lab-a-embeddings
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python walk_the_space.py
```

Use `py` rather than `python` to launch. Windows ships a `python.exe` stub that
opens the Microsoft Store instead of running anything, and `py` skips it.

### "Running scripts is disabled on this system"

The most common Windows wall. PowerShell blocks script execution by default, so
`Activate.ps1` refuses to run. Fix it for your user only — no admin needed:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

If your organisation locks execution policy by group policy, you cannot override
it. Two ways around:

```powershell
.\.venv\Scripts\activate.bat          # the .bat works when .ps1 is blocked
.\.venv\Scripts\python.exe walk_the_space.py   # or skip activation entirely
```

That last line is the reliable escape hatch: call the venv's interpreter
directly and never activate anything.

### Line continuation

The labs' multi-line commands use `\`, which is bash. In PowerShell the
continuation character is a backtick:

```powershell
python compare_quants.py --tags llama3.1:8b-instruct-q8_0 `
                                llama3.1:8b-instruct-q4_K_M `
                                llama3.1:8b-instruct-q2_K
```

Or just put it on one line, which is what I'd do.

### Paths

Forward slashes work fine in Python arguments on Windows — `--csv data/mine.csv`
is fine. It's only the shell commands that need backslashes.

If a path contains spaces, quote it:

```powershell
python cluster_your_data.py --csv "C:\Users\me\My Data\tickets.csv" --column text
```

### Other Windows-specific gotchas

**`ollama serve` says the port is in use** — the Ollama desktop app is already
running it in the tray. Skip `ollama serve` entirely; it's already up. Check
with:

```powershell
curl.exe http://localhost:11434/api/tags
```

Use `curl.exe`, not `curl` — bare `curl` is an alias for `Invoke-WebRequest` in
PowerShell and takes different arguments.

**Long path errors during pip install** — torch has deeply nested paths. Enable
long paths:

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
```

That one does need admin. If you don't have it, clone the repo somewhere short
like `C:\labs` instead of a deep folder under Documents.

**Model downloads go to your C: drive and fill it** — Hugging Face caches under
`%USERPROFILE%\.cache\huggingface`. Redirect it if C: is small:

```powershell
$env:HF_HOME = "D:\hf-cache"
```

Set it in the same session before running the lab, or add it to your user
environment variables to make it stick.

**CUDA not detected on a machine that has an NVIDIA GPU** — the default pip
`torch` is CPU-only on some Windows setups. Reinstall with the CUDA build:

```powershell
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Verify:

```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

**Git isn't installed** — download the repo as a ZIP from GitHub and extract it.
Nothing in these labs needs git.

---

## Corporate laptop workarounds

**Can't install Python.** Use Colab. Labs A, B, C work fully; D can run
there too with a runtime change to GPU.

**pip fails with SSL errors.** A proxy is intercepting HTTPS. Ask IT for the
proxy cert, or just use Colab. Don't burn an afternoon on this — it isn't the
lab.

**Downloads blocked.** Hugging Face and Ollama both pull from CDNs that some
corporate firewalls block. Colab again, or your personal machine.

**No admin rights.** `python -m venv` doesn't need admin. `pip install --user`
also works. Ollama does need an install, so Lab E is the one that may be
genuinely blocked; everything else has a route.

---

## Verifying your setup

```bash
python -c "import sys; print(sys.version)"
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

For Ollama:

```bash
ollama --version
curl http://localhost:11434/api/tags
```

If that curl returns JSON, Ollama is running and Lab E will work.

---

## If you get stuck

Check `TROUBLESHOOTING.md`, then email me with your OS, Python version,
and the full error text. Reported failures are how TROUBLESHOOTING.md grows.
