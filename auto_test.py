#!/usr/bin/env python3
"""
auto_test.py

Automatic test runner that installs dependencies into the active Python environment
selected by VSCode (via sys.executable). If the active environment is the project
folder (e.g. a venv inside the project) the script will create an isolated external
venv in the system temporary directory to avoid adding environment folders to the repo.

The script runs every Python file in the tests/ directory and writes results to
logs/test_run.log.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
LOG_FILE = LOGS / "test_run.log"
REQUIREMENTS = ROOT / "requirements.txt"


def run_cmd(cmd, capture=False, env=None, cwd=None):
    if capture:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=cwd)
    return subprocess.run(cmd, env=env, cwd=cwd)


def pip_available(python_exe):
    try:
        r = run_cmd([python_exe, "-m", "pip", "--version"], capture=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def ensure_env(use_temp_venv=False):
    """Return (python_exec, pip_exec, cleanup_fn) where cleanup_fn is None or callable"""
    python_exec = sys.executable
    cleanup = None

    # Avoid creating a venv inside the project (don't pollute repo). If the
    # active interpreter path is within the project, create a new external venv.
    if use_temp_venv or Path(python_exec).resolve().is_relative_to(ROOT):
        tempdir = tempfile.mkdtemp(prefix="autotest_venv_")
        venv_dir = Path(tempdir) / "venv"
        print(f"Creating external venv at {venv_dir}")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
        if os.name == "nt":
            p = venv_dir / "Scripts" / "python.exe"
        else:
            p = venv_dir / "bin" / "python"

        python_exec = str(p)

        def cleanup_fn():
            try:
                shutil.rmtree(tempdir)
            except Exception:
                pass

        cleanup = cleanup_fn

    pip_exec = python_exec
    if not pip_available(python_exec):
        raise RuntimeError(f"pip not available for interpreter {python_exec}")

    return python_exec, pip_exec, cleanup


def install_requirements(python_exec, require_file):
    print("Installing requirements from:", require_file)
    subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    subprocess.check_call([python_exec, "-m", "pip", "install", "-r", str(require_file)])


def run_tests(python_exec, tests_dir, out_log):
    tests = sorted(tests_dir.glob("*.py"))
    if not tests:
        out_log.write("No tests found in directory: {}\n".format(tests_dir))
        return 0

    overall_rc = 0
    for t in tests:
        out_log.write("\n=== RUNNING: {} ===\n".format(t.name))
        out_log.flush()
        print("Running test:", t)
        r = subprocess.run([python_exec, str(t)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out_log.write(r.stdout)
        out_log.write("\n--- RETURN CODE: {} ---\n".format(r.returncode))
        out_log.flush()
        if r.returncode != 0:
            overall_rc = r.returncode

    return overall_rc


def main():
    pars = argparse.ArgumentParser()
    pars.add_argument("--temp-venv", action="store_true", help="Always create a temporary external venv for testing")
    args = pars.parse_args()

    LOGS.mkdir(exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as out_log:
        out_log.write("Auto test run: active interpreter: {}\n".format(sys.executable))

        python_exec, pip_exec, cleanup = ensure_env(use_temp_venv=args.temp_venv)
        out_log.write(f"Using python: {python_exec}\n")

        try:
            install_requirements(python_exec, REQUIREMENTS)
            rc = run_tests(python_exec, ROOT / "tests", out_log)
            out_log.write("\nSummary: exit code {}\n".format(rc))
        except subprocess.CalledProcessError as e:
            out_log.write("Install or test run failed: {}\n".format(e))
            rc = getattr(e, "returncode", 1)

        finally:
            if cleanup is not None:
                out_log.write("Cleaning up temporary environment\n")
                cleanup()

    print(f"Test run done. Log written to {LOG_FILE}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
