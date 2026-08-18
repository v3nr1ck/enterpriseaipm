# Troubleshooting

This file grows from reader reports. If you hit something not listed, email me
your OS, Python version, and the full error text — that's how it gets added.

---

## Start here

**Run the preflight before anything else.** From inside a lab folder, with the
interpreter you intend to use:

```powershell
.\.venv\Scripts\python.exe ..\verify_setup.py
```

```bash
./.venv/bin/python ../verify_setup.py
```

It tells you which Python is actually running, whether that is a venv, whether
the lab's packages import, and whether the lab's models still exist upstream.
Three of the four most common failures show up there immediately.

---

## The four that catch almost everyone

**1. You pasted the code fences.**
```
ash : The term 'ash' is not recognized as the name of a cmdlet
```
You copied a whole markdown block, triple backticks and all. The ```` ```bash ````
line is markdown, not a command. Copy the lines *between* the fences, one at a
time.

**2. You are in `cmd.exe`, not PowerShell.**
```
The system cannot find the path specified.
```
A `cmd` prompt looks like `C:\Users\you>`; PowerShell looks like
`PS C:\Users\you>`. In `cmd` the separator is `&&`, not `;` — paste a
PowerShell one-liner into `cmd` and it swallows the whole thing as one path.
Type `powershell` and press Enter, or run each line separately.

**3. `source .venv/bin/activate` failed and you kept going.**
```
source : The term 'source' is not recognized...
```
This is the expensive one. `source` is bash; on Windows that line always fails.
If you continue past it, the venv is not active and `pip install` goes to
whatever Python is on your PATH — often Anaconda's `base` environment, where it
can break unrelated packages. The labs avoid this entirely by calling the venv's
interpreter by path. Never use `activate`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Check where you actually are — this must print a path ending in `.venv`:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.prefix)"
```

**4. The model id went stale.**
```
OSError: <name> is not a local folder and is not a valid model identifier
```
Not your fault. Model repos get renamed and retired. Check
[CURRENT.md](CURRENT.md) for the current id and pass it with `--model`. Note
that Hugging Face returns **401**, not 404, for a repo that does not exist — it
does not confirm whether private repos are there. A 401 on a public model id
means it is gone, not that you need to log in.

---

## Install problems

**`ModuleNotFoundError` right after installing**
Almost always the wrong interpreter, not a failed install — see #3 above. Run
`verify_setup.py`; if it reports a conda or system Python, your packages went
somewhere else.

**`pip: command not found`**
Try `python -m pip` instead. On macOS/Linux you may need `python3` and
`python3 -m pip`.

**SSL / certificate errors during pip or model download**
A corporate proxy is intercepting HTTPS. Use Google Colab instead of fighting
it. This is not a lab problem and solving it teaches you nothing about AI.

**`torch` install is enormous / fails on disk space**
It's ~2GB, and with CUDA support more. Use Colab for Labs B, C, D.

**Apple Silicon: torch installs but is slow or errors**
Make sure you have a recent torch. MPS support has improved a lot and old
versions are flaky. `--device cpu` will confirm whether the code path works at
all before you debug the accelerator.

---

## Model download problems

**404 / repo not found**
The model name changed. This is expected over time — check `CURRENT.md` and
substitute any model of the same size class. **Nothing in any lab depends on a
specific model.** That's by design.

**Download starts then stalls**
Usually a flaky CDN. Re-run; Hugging Face and Ollama both resume partial
downloads.

**"You need to agree to share your contact information"**
Some models are gated on Hugging Face. Either accept on their website and
`huggingface-cli login`, or pick an ungated model. `CURRENT.md`'s defaults are
ungated.

---

## Lab-specific

### Lab A
- **Clusters look random** — check `--column` points at the right column, and
  that your rows have more than about five words each.
- **`UnicodeDecodeError`** — re-save the CSV as **CSV UTF-8** from Excel.

### Lab B
- **Extremely slow** — CPU generation. Reduce `--steps 3 --top-n 5`. You're
  reading a distribution, not writing an essay.
- **Wanting to use Ollama** — see the note in the lab README; logprob support
  varies by version.

### Lab C / D
- **CUDA out of memory** — lower `--steps`, use `--frames 5` in Lab D, or rent.
  Attention slicing is already on for CUDA.
- **All images identical across a seed sweep** — you passed `--seed`, which
  fixes the start. That's the point of the *other* sweeps; the seed sweep
  overrides it internally.
- **`prompt_embeds` shape errors in Lab D** — you swapped in an SDXL model,
  which needs a second encoder's pooled embeddings. Stay on SD 1.5 here.
- **Black images** — MPS on some torch versions, or a safety checker on a
  different model. Try `--device cpu` to isolate.

### Lab E
- **`Can't reach Ollama`** — run `ollama serve` in a separate terminal.
- **Tag 404** — that quantization doesn't exist for that model. Small models
  often have no q2 build. Check the tags page.
- **All three quants give identical output** — run `ollama list` and compare
  digests; the tags may be aliases of one file.

### Lab F
- **Colab OOM** — `max_seq_length=512`, batch size 1, confirm 4-bit loading.
- **Curve is not monotonic** — normal. Sampling noise on a small eval set is
  worth several percent. Differences under ~5% aren't differences.
- **Scorer says "rows need 'input' and 'predicted' keys"** — your prediction
  file has different key names. Rename them; the error prints what it found.
- **All runs score the same** — you probably didn't change the training file
  between runs.

---

## Windows specifically

**"Running scripts is disabled on this system"**
PowerShell blocks `Activate.ps1` by default. Either
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, or skip
activation and call the venv interpreter directly:
`.\.venv\Scripts\python.exe script.py`. The second always works.

**`python` opens the Microsoft Store**
That's the Windows stub. Use `py` instead.

**`curl` behaves strangely**
In PowerShell `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe`.

**Long path / filename too long during pip install**
Unzip to a short path like `C:\labs`, or enable long paths (needs admin — see
SETUP.md).

**`ollama serve` says the port is already in use**
The desktop app already has it running in the tray. Skip the command.

**torch installs but `cuda.is_available()` is False**
You got the CPU-only wheel. Reinstall from the CUDA index — see SETUP.md.

**C: drive fills up**
Model caches live in `%USERPROFILE%\.cache\huggingface`. Set `$env:HF_HOME` to
another drive.

---

## General

**"It worked yesterday and doesn't today"**
If it's a generation difference, that may be Lab B's actual lesson (near-ties
plus batching non-determinism). If it's an import or download error, something
in the ecosystem updated — check `CURRENT.md`.

**A lab's output doesn't match what the README describes**
Tell me. Either the model landscape moved or the README is wrong, and both are
worth fixing.
