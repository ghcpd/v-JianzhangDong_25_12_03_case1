#!/usr/bin/env bash
set -euo pipefail

echo "Installing project requirements into the active Python environment..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements.txt

echo "Installation complete. Use run_test.sh to execute tests or auto_test.py for automatic test runs."
