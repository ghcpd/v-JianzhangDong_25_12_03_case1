# Dependency Maintenance & Test Harness

## Overview

Generated artifacts:
- `requirements_backup.txt` — backup of original dependency pins.
- `requirements.txt` — updated, secure, and compatible pins.
- `report.json` — summary of dependency issues & upgrades.
- `setup.sh` — Linux/macOS setup script (creates venv outside project).
- `run_test.sh` — Linux/macOS test runner using active Python.
- `run_test.bat` — Windows test runner using active Python.
- `auto_test.py` — environment-aware test harness; installs deps (outside project if needed) and logs to `logs/test_run.log`.
- `Dockerfile` — containerized environment with dependencies installed.
- `logs/test_run.log` — test execution log (created on demand).

## Prerequisites
- Python **>=3.9** (3.11+ recommended).
- `pip` available in PATH.
- VS Code: select desired interpreter (Ctrl+Shift+P → "Python: Select Interpreter").

## Setup (Linux/macOS)
```bash
./setup.sh
```
- Creates venv under `${XDG_CACHE_HOME:-$HOME/.cache}/oswe_envs/v-JianzhangDong_25_12_03_case1`.
- Installs dependencies from `requirements.txt`.

## Run Tests
### Linux/macOS
```bash
./run_test.sh
```

### Windows
```bat
run_test.bat
```

Both call `python auto_test.py`, which:
- Uses the selected VS Code interpreter by default.
- Installs/updates dependencies into that interpreter; on failure, creates a temp venv **outside** the project.
- Executes all `tests/*.py` (matching `case_*.py` and `test_*.py`).
- Writes results to `logs/test_run.log` and mirrors to stdout.

### `auto_test.py` options
```bash
python auto_test.py --list           # list discovered tests
python auto_test.py -k case_1        # filter tests by keyword
python auto_test.py tests/case_1.py  # run specific test file
python auto_test.py --use-current    # never create external env; install into current
python auto_test.py --force-temp-env # always use external temp env
```

## Docker
```bash
docker build -t oswe-case1 .
docker run --rm oswe-case1
```
- Uses `python:3.12-slim`, installs dependencies, runs `auto_test.py` by default.

## Logs
- Test logs: `logs/test_run.log`
- Matplotlib config: `.mplconfig/` (auto-created)

## Notes
- No virtual environments are created inside the project root.
- Update `requirements.txt` and rerun `setup.sh` / `auto_test.py` to refresh dependencies.
