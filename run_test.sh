#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  PY="python"
fi

export MPLBACKEND=Agg
"$PY" auto_test.py "$@"
