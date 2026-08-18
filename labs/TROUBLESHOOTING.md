# Troubleshooting

This file grows from reader reports. If you hit something not listed, open an
issue with your OS, Python version, and the full error — that's how it gets
added.

---

## Install problems

**`ModuleNotFoundError` right after installing**
The virtual environment isn't active. You'll see `(.venv)` in your prompt when
it is. Re-run the activate line.

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
Clone to a short path like `C:\labs`, or enable long paths (needs admin — see
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
