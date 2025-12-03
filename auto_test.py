"""
Auto-test runner that uses the active Python interpreter (selected in VSCode) or creates
an external venv in the system temp/cache directory if no venv is active.

Behavior:
- If running inside a virtualenv (sys.prefix != sys.base_prefix), use that environment.
- Otherwise create a timestamped venv under the system temp folder and use it (not inside the project).
- Install packages from requirements.txt (no-cache-dir) and run tests in tests/.
- Write combined output to logs/test_run.log and return non-zero exit code if any test fails.
"""
import os
import sys
import subprocess
import tempfile
import venv
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"


def run_command(cmd, env=None, capture=False):
    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=env, capture_output=capture, text=True)
    return proc


def create_external_venv():
    ts = int(time.time())
    tmpdir = Path(tempfile.gettempdir()) / f"v-JianzhangDong_test_env_{ts}"
    venv.create(tmpdir, with_pip=True)
    return tmpdir


def install_requirements(python_exe):
    cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
    p = run_command(cmd)
    if p.returncode != 0:
        raise SystemExit(p.returncode)
    # Prefer binary wheels to avoid building heavy packages from source on Windows
    cmd = [
        str(python_exe),
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--prefer-binary",
        "-r",
        str(ROOT / "requirements.txt"),
    ]
    p = run_command(cmd)
    if p.returncode != 0:
        # If prefer-binary failed (pip may still try to build some packages), try a per-package binary-only fallback
        print("Initial install failed; attempting binary-only installation for known heavy packages (numpy, scipy, lxml)...")
        fallback_pkgs = ["numpy", "scipy", "lxml"]
        for pkg in fallback_pkgs:
            pkg_spec = None
            # find pinned version in requirements.txt
            for line in open(ROOT / "requirements.txt", encoding="utf-8"):
                if line.strip().startswith(pkg + "=="):
                    pkg_spec = line.strip()
                    break
            if pkg_spec:
                cmd2 = [str(python_exe), "-m", "pip", "install", "--no-cache-dir", "--only-binary=:all:", pkg_spec]
                try:
                    p2 = run_command(cmd2)
                    if p2.returncode == 0:
                        print(f"Binary-only install succeeded for {pkg}")
                        continue
                except Exception as ex:
                    print(f"Binary-only install failed for {pkg}: {ex}")
        # after fallbacks, re-run main install to pick up remaining packages (if any)
        p3 = run_command(cmd)
        if p3.returncode != 0:
            raise SystemExit(p3.returncode)


def run_tests(python_exe):
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        print("No tests/ directory found; nothing to run.")
        return 0

    test_files = sorted(p for p in tests_dir.glob("*.py") if p.is_file())
    overall_rc = 0
    with open(LOG_FILE, "w", encoding="utf-8") as fh:
        for t in test_files:
            cmd = [str(python_exe), str(t)]
            env = os.environ.copy()
            # Ensure the project root is on PYTHONPATH so 'app' imports resolve
            existing = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(ROOT) + (os.pathsep + existing if existing else "")
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
            fh.write(f"=== Running {t.name} ===\n")
            fh.write(proc.stdout)
            fh.write(proc.stderr)
            fh.write(f"=== Exit code: {proc.returncode} ===\n\n")
            if proc.returncode != 0:
                overall_rc = proc.returncode
    print(f"Test results written to {LOG_FILE}")
    return overall_rc


def main():
    # If running inside a virtualenv, use current interpreter. Otherwise create external venv.
    in_venv = getattr(sys, "real_prefix", None) is not None or sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        python_exe = Path(sys.executable)
        print(f"Using active virtual environment: {python_exe}")
    else:
        print("No active virtualenv detected; creating an external temp venv.")
        tmp_env = create_external_venv()
        python_exe = tmp_env / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")

    # If running on a Python version with poor wheel support (e.g., 3.14+ at time of writing),
    # prefer to run tests inside the Docker image (python:3.11) when docker is available.
    py_major, py_minor = sys.version_info[:2]
    if py_major == 3 and py_minor >= 14:
        print("Warning: Python 3.14 detected — many packages may not provide prebuilt wheels for this version yet. Attempting local install; if it fails, please use Docker, conda or install Visual Studio Build Tools.")

    install_requirements(python_exe)
    rc = run_tests(python_exe)
    if rc != 0:
        print(f"Some tests failed (exit code {rc}). See {LOG_FILE} for details.")
    else:
        print("All tests passed.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
