# Project environment and test helpers 🔧

This repository now includes updated, secure dependency pins and helper scripts to replicate/test the environment across platforms.

## Files added or modified ✅

- `requirements_backup.txt` — backup of the original `requirements.txt` before changes.
- `requirements.txt` — updated to secure, stable versions pinned for reproducible installs.
- `report.json` — a simplified report listing which packages were updated, original versions, and reasons.
- `Dockerfile` — minimal container recipe to reproduce the environment.
- `setup.sh` — installs `requirements.txt` into the active Python environment (Linux/macOS).
- `run_test.sh` — wrapper that runs `auto_test.py` (Linux/macOS).
- `run_test.bat` — wrapper for Windows to run `auto_test.py`.
- `auto_test.py` — automatic test-runner that uses the active VSCode Python environment or a temporary external venv (not inside the project). It installs requirements and runs all `tests/*.py`, writing output to `logs/test_run.log`.

## How to set up the environment

### Linux / macOS

1. Make sure your active Python interpreter is the one you want to use in VSCode.
2. Run the installer script (this installs packages directly into the active environment):

```bash
./setup.sh
```

3. Run tests:

```bash
./run_test.sh
```

Or run manually with the test runner (this will write logs to `logs/test_run.log`):

```bash
python auto_test.py
```

If you prefer a completely isolated temporary virtual environment outside the repo (safer for CI), run:

```bash
python auto_test.py --temp-venv
```

### Windows

1. Open a PowerShell shell using your VSCode-selected Python environment.
2. Install packages:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

3. Run tests:

```powershell
run_test.bat
```

Or run `python auto_test.py` directly.

### Docker

Build and run a container that mirrors the environment:

```bash
docker build -t repo-tests:latest .
docker run -it --rm repo-tests:latest /bin/bash
```

Inside the container, the environment will have `requirements.txt` dependencies installed.

## Test logs

- Test output is recorded at `logs/test_run.log`.

## Notes and reasoning

- I picked patch or minor upgrades to keep compatibility while addressing known vulnerabilities (e.g., older `requests` and `pyyaml` versions). See `report.json` for the full list of changes and reasons.
- The `auto_test.py` script intentionally avoids creating a venv inside the project folder. If the active interpreter is inside the project directory, it will create a temporary external venv.
