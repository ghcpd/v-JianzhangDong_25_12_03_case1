#!/usr/bin/env bash
set -euo pipefail

# Use the selected Python interpreter and run the auto_test runner
python auto_test.py "$@"
