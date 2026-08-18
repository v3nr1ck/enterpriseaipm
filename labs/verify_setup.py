r"""
Preflight check. Run this before asking why a lab doesn't work.

Run:  python verify_setup.py
      python verify_setup.py --lab b
      python verify_setup.py --no-network

Run it with the SAME interpreter you intend to run the lab with. That is the
whole point: it tells you which Python you are actually using, which is the
thing that goes wrong most often and is invisible when it does.

  Windows:  .\.venv\Scripts\python.exe verify_setup.py
  macOS/Linux:  ./.venv/bin/python verify_setup.py
"""

import argparse
import importlib
import json
import os
import sys
import urllib.error
import urllib.request

OK = "  OK   "
BAD = "  FAIL "
WARN = "  WARN "

# Package requirements per lab. Import name first, pip name second where they differ.
LAB_PACKAGES = {
    "a": [("sentence_transformers", "sentence-transformers"),
          ("sklearn", "scikit-learn"),
          ("numpy", "numpy")],
    "b": [("torch", "torch"),
          ("transformers", "transformers"),
          ("accelerate", "accelerate")],
    "c": [("torch", "torch"),
          ("diffusers", "diffusers"),
          ("transformers", "transformers"),
          ("PIL", "pillow")],
    "d": [("torch", "torch"),
          ("diffusers", "diffusers"),
          ("transformers", "transformers"),
          ("PIL", "pillow")],
    "e": [],   # stdlib only, needs Ollama running
    "f": [],   # stdlib only, training happens in Colab
}

# Models each lab pulls from Hugging Face. Keep in sync with CURRENT.md.
LAB_MODELS = {
    "a": ["sentence-transformers/all-MiniLM-L6-v2"],
    "b": ["Qwen/Qwen2.5-0.5B-Instruct"],
    "c": ["stable-diffusion-v1-5/stable-diffusion-v1-5"],
    "d": ["stable-diffusion-v1-5/stable-diffusion-v1-5"],
    "e": [],
    "f": [],
}

# Ollama tags Lab E needs. Keep in sync with CURRENT.md.
LAB_E_TAGS = [
    "qwen2.5:3b-instruct-q8_0",
    "qwen2.5:3b-instruct-q4_K_M",
    "qwen2.5:3b-instruct-q2_K",
]

OLLAMA_HOST = "http://localhost:11434"


def detect_lab():
    """Guess which lab we're in from the folder name."""
    here = os.path.basename(os.path.abspath(".")).lower()
    for key in LAB_PACKAGES:
        if here.startswith("lab-" + key + "-"):
            return key
    return None


def check_python(needs_venv=True):
    """The check that matters most: which interpreter is this, and is it a venv?

    needs_venv is False for labs that install nothing (E, F), where running
    from a global or conda Python is perfectly fine.
    """
    print("PYTHON")
    print("    executable : %s" % sys.executable)
    print("    version    : %s" % sys.version.split()[0])
    print("    prefix     : %s" % sys.prefix)

    problems = 0

    if sys.version_info < (3, 9):
        print(BAD + "Python 3.9+ required. This is %d.%d."
              % (sys.version_info[0], sys.version_info[1]))
        problems += 1
    else:
        print(OK + "Python version is new enough.")

    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    prefix_low = sys.prefix.lower()
    is_conda = ("conda" in prefix_low or "miniforge" in prefix_low
                or os.environ.get("CONDA_DEFAULT_ENV") not in (None, ""))

    if in_venv:
        print(OK + "Running inside a virtual environment.")
    elif not needs_venv:
        print(OK + "Not a venv, but this lab installs nothing - that is fine.")
    elif is_conda:
        print(BAD + "NOT in a venv - this is a conda environment (%s)."
              % (os.environ.get("CONDA_DEFAULT_ENV") or "base"))
        print("         Installing lab packages here can break unrelated conda")
        print("         packages. Build a venv in the lab folder and use its")
        print("         interpreter by path. See ../SETUP.md.")
        problems += 1
    else:
        print(BAD + "NOT in a virtual environment - this is a global Python.")
        print("         See ../SETUP.md; every lab expects a per-lab venv.")
        problems += 1

    return problems


def check_packages(lab):
    print("\nPACKAGES (lab %s)" % lab.upper())
    pkgs = LAB_PACKAGES.get(lab, [])
    if not pkgs:
        print(OK + "This lab needs nothing beyond the standard library.")
        return 0

    problems = 0
    for import_name, pip_name in pkgs:
        try:
            mod = importlib.import_module(import_name)
        except ImportError:
            print(BAD + "%s is missing." % pip_name)
            problems += 1
            continue
        version = getattr(mod, "__version__", "?")
        print(OK + "%s %s" % (pip_name, version))

    if problems:
        print("\n         Install them with THIS interpreter:")
        print("           %s -m pip install -r requirements.txt" % sys.executable)
    return problems


def check_models(lab, timeout=10):
    """Ask Hugging Face whether the model ids in this lab still exist."""
    models = LAB_MODELS.get(lab, [])
    if not models:
        return 0
    print("\nMODELS (lab %s)" % lab.upper())
    problems = 0
    for repo in models:
        url = "https://huggingface.co/api/models/%s" % repo
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "latent-space-labs"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp.read(1)
            print(OK + "%s" % repo)
        except urllib.error.HTTPError as e:
            # HF returns 401 for repos that do not exist, to avoid confirming
            # whether a private repo is there. Treat 401 and 404 the same.
            if e.code in (401, 404):
                print(BAD + "%s does not exist on Hugging Face." % repo)
                print("         The model id has gone stale. Check ../CURRENT.md")
                print("         for a current replacement and pass it with --model.")
                problems += 1
            else:
                print(WARN + "%s returned HTTP %d." % (repo, e.code))
        except urllib.error.URLError as e:
            print(WARN + "Could not reach Hugging Face (%s)." % e.reason)
            print("         Offline, or a proxy is in the way. If the model is")
            print("         already cached locally the lab will still run.")
            return problems
    return problems


def check_ollama(timeout=5):
    print("\nOLLAMA (lab E)")
    try:
        with urllib.request.urlopen(OLLAMA_HOST + "/api/tags", timeout=timeout) as resp:
            body = json.loads(resp.read())
    except Exception:
        print(BAD + "Ollama is not answering on %s." % OLLAMA_HOST)
        print("         Install it from https://ollama.com/download, then run")
        print("         'ollama serve' in its own terminal and leave it open.")
        return 1

    have = set()
    for m in body.get("models", []):
        name = m.get("name", "")
        have.add(name)
        if ":" in name:
            have.add(name)
    print(OK + "Ollama is running (%d model(s) pulled)." % len(body.get("models", [])))

    problems = 0
    for tag in LAB_E_TAGS:
        if tag in have or (tag + ":latest") in have:
            print(OK + "%s" % tag)
        else:
            print(WARN + "%s not pulled yet." % tag)
            print("         ollama pull %s" % tag)
            problems += 1
    return problems


def main():
    p = argparse.ArgumentParser(description="Preflight check for the latent-space labs.")
    p.add_argument("--lab", help="a b c d e f. Guessed from the folder name if omitted.")
    p.add_argument("--no-network", action="store_true",
                   help="skip the Hugging Face and Ollama checks")
    args = p.parse_args()

    lab = (args.lab or detect_lab() or "").lower().strip()

    print("=" * 68)
    print("LATENT-SPACE LABS - PREFLIGHT")
    print("=" * 68)

    needs_venv = bool(LAB_PACKAGES.get(lab)) if lab in LAB_PACKAGES else True
    problems = check_python(needs_venv)

    if not lab:
        print("\n" + WARN + "Could not tell which lab this is.")
        print("         Run this from inside a lab folder, or pass --lab b.")
        print("\nThe Python check above is the important one either way.")
        return 0 if problems == 0 else 1

    if lab not in LAB_PACKAGES:
        print("\n" + BAD + "Unknown lab '%s'. Use one of: a b c d e f." % lab)
        return 1

    problems += check_packages(lab)

    if not args.no_network:
        problems += check_models(lab)
        if lab == "e":
            problems += check_ollama()

    print("\n" + "=" * 68)
    if problems == 0:
        print("All checks passed. Run the lab.")
    else:
        print("%d problem(s) above. Fix them top to bottom - the first one" % problems)
        print("usually causes the rest.")
    print("=" * 68)
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
