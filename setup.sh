#!/usr/bin/env bash
set -euo pipefail

# Optional: specify PYTHON_BIN or set CREATE_VENV=1 to create an external venv.
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ -n "${CREATE_VENV:-}" ]]; then
  VENV_DIR="${VENV_DIR:-$HOME/.venvs/v-JianzhangDong_25_12_03_case1}"
  mkdir -p "$(dirname "$VENV_DIR")"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  PYTHON_BIN="$VENV_DIR/bin/python"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt
