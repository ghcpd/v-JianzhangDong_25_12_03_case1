#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

# Create venv OUTSIDE project to avoid committing large env folders.
VENVS_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/oswe_envs"
mkdir -p "$VENVS_ROOT"
VENV_DIR="$VENVS_ROOT/v-JianzhangDong_25_12_03_case1"

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Virtualenv created at $VENV_DIR"
echo "Activate with: source $VENV_DIR/bin/activate"
