#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "============================================================"
echo "  Lab F - Build the dataset"
echo "============================================================"
echo
echo "  Needs nothing installed. Runs in seconds."
echo

PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then
  echo "  Python is not installed."
  echo "  Install it from https://www.python.org/downloads/ then run this again."
  read -r -p "Press Enter to close." _; exit 1
fi

$PY make_dataset.py
echo
read -r -p "Finished. Press Enter to close." _
