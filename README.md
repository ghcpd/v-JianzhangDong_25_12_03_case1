# Dependency Maintenance & Test Harness

## Overview
| File | Purpose |
|------|---------|
| `requirements.txt` | Updated, pinned dependencies (secure & compatible) |
| `requirements_backup.txt` | Snapshot of the original dependencies |
| `report.json` | Summary of dependency issues and applied upgrades |
| `setup.sh` | Linux/macOS helper to install requirements (optional external venv) |
| `run_test.sh` | Linux/macOS test runner (delegates to `auto_test.py`, logs to `logs/test_run.log`) |
| `run_test.bat` | Windows test runner (delegates to `auto_test.py`, logs to `logs/test_run.log`) |
| `auto_test.py` | Auto-detects VS Code Python env (or creates external temp venv), installs deps, runs tests |
| `Dockerfile` | Containerized environment with dependencies and tests |
| `logs/test_run.log` | Test execution log (created at runtime) |

## Setup
### Linux/macOS
```bash
chmod +x setup.sh run_test.sh
./setup.sh         # installs deps into current interpreter; set CREATE_VENV=1 to isolate under ~/.venvs
```

### Windows
```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running Tests
### Linux/macOS
```bash
./run_test.sh                 # uses auto_test.py with --skip-install
```

### Windows
```bat
run_test.bat                  # uses auto_test.py with --skip-install
```

## Auto Test (VS Code-aware)
```bash
python auto_test.py            # uses VS Code-selected interpreter
python auto_test.py --isolate  # creates external venv in system temp dir
python auto_test.py --skip-install  # run tests with existing deps
```
```

## Docker
```bash
docker build -t dep-maint .
docker run --rm dep-maint
```

## Logs
- Test output is written to `logs/test_run.log` (created automatically).
- Inspect with `cat logs/test_run.log` (Linux/macOS) or `type logs\test_run.log` (Windows).
