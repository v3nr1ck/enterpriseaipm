#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "============================================================"
echo "  Lab D - The interpolation walk"
echo "============================================================"
echo
echo "  Reuses Lab C's setup if you have already run Lab C."
echo

PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then
  echo "  Python is not installed."
  echo "  Install it from https://www.python.org/downloads/ then run this again."
  read -r -p "Press Enter to close." _; exit 1
fi

if [ -x "../lab-c-denoising/.venv/bin/python" ]; then
  echo "  Found Lab C's setup - reusing it."
  ../lab-c-denoising/.venv/bin/python interpolate.py
  read -r -p "Press Enter to close." _; exit 0
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "  First run - building this lab's own private Python setup..."
  $PY -m venv .venv || { echo "  Could not create the environment."; read -r -p "Press Enter." _; exit 1; }
fi
echo "  Checking this lab has what it needs..."
./.venv/bin/python -m pip install --quiet --upgrade pip
if ! ./.venv/bin/python -m pip install --quiet -r requirements.txt; then
  echo "  The download failed. Try again, or use colab.ipynb which needs no install."
  read -r -p "Press Enter to close." _; exit 1
fi
echo
./.venv/bin/python interpolate.py
echo
read -r -p "Finished. Press Enter to close." _
