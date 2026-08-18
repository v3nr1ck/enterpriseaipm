#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "============================================================"
echo "  Lab E - Watch it degrade"
echo "============================================================"
echo
echo "  Needs Ollama installed and running."
echo

PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python
if [ -z "$PY" ]; then
  echo "  Python is not installed."
  echo "  Install it from https://www.python.org/downloads/ then run this again."
  read -r -p "Press Enter to close." _; exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "  Ollama is not installed. Get it from https://ollama.com/download"
  read -r -p "Press Enter to close." _; exit 1
fi
if ! curl -s -m 5 http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "  Ollama is installed but not running. Start it, then run this again."
  read -r -p "Press Enter to close." _; exit 1
fi
echo "  This lab needs ~16GB of models pulled first - see README.md"
echo
$PY compare_quants.py --tags llama3.1:8b-instruct-q8_0 llama3.1:8b-instruct-q4_K_M llama3.1:8b-instruct-q2_K
echo
read -r -p "Finished. Press Enter to close." _
