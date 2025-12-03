#!/usr/bin/env bash
set -euo pipefail

# Create an external venv in a system cache location (not inside the project)
ENV_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/v-JianzhangDong_25_12_03_env"
python3 -m venv "$ENV_DIR"
"$ENV_DIR/bin/python" -m pip install --upgrade pip
"$ENV_DIR/bin/python" -m pip install --no-cache-dir -r requirements.txt

echo "Environment created at $ENV_DIR"
echo "To use it: source $ENV_DIR/bin/activate"
