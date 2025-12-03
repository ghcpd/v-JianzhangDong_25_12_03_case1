#!/usr/bin/env python
"""Test harness with environment management for VS Code-selected Python.

Requirements:
- Does **not** create a venv inside the project directory.
- Uses the active VS Code interpreter (`sys.executable`).
- If dependencies are missing or install fails, creates a **temporary external** venv.
- Executes all test scripts in `tests/` and logs output to `logs/test_run.log`.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).parent
TEST_DIR = ROOT / "tests"
DEFAULT_PATTERNS = ["case_*.py", "test_*.py"]
ARTIFACTS = ["tmp.csv", "plot.png"]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "test_run.log"
REQUIREMENTS = ROOT / "requirements.txt"


def discover_tests(patterns: Iterable[str] = DEFAULT_PATTERNS) -> List[Path]:
    tests: List[Path] = []
    for pat in patterns:
        tests.extend(sorted(TEST_DIR.glob(pat)))
    # Deduplicate while preserving order
    unique: List[Path] = []
    seen = set()
    for t in tests:
        if t not in seen:
            unique.append(t)
            seen.add(t)
    return unique


def run_test(path: Path, env: dict | None = None) -> tuple[int, str, str]:
    """Run a single test file using the current interpreter."""
    cmd = [env.get("PYTHON_EXECUTABLE", sys.executable), str(path)] if env else [sys.executable, str(path)]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def cleanup_artifacts():
    for name in ARTIFACTS:
        p = ROOT / name
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


def get_external_venv_path() -> Path:
    cache_root = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_root / "oswe_envs" / "v-JianzhangDong_25_12_03_case1"


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_deps(python_exec: str) -> str:
    """Install requirements into the provided interpreter. Return the interpreter path.

    If installation fails (e.g., permissions), create an external venv and install there.
    """

    def pip_install(py: str) -> bool:
        try:
            subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            subprocess.run([py, "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    if pip_install(python_exec):
        return python_exec

    # Fallback to external venv
    venv_dir = get_external_venv_path()
    venv_dir.mkdir(parents=True, exist_ok=True)
    py_path = venv_python(venv_dir)
    if not py_path.exists():
        subprocess.run([python_exec, "-m", "venv", str(venv_dir)], check=True)
    if not pip_install(str(py_path)):
        raise RuntimeError("Failed to install dependencies in external venv")
    return str(py_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run test scripts in the tests directory")
    parser.add_argument("tests", nargs="*", help="Specific test files or glob patterns to run")
    parser.add_argument(
        "-k", "--keyword", action="append", help="Run tests matching this substring (can be repeated)"
    )
    parser.add_argument("--list", action="store_true", help="List discovered tests and exit")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument(
        "--use-current", action="store_true", help="Force using current interpreter without creating an external venv"
    )
    parser.add_argument(
        "--force-temp-env", action="store_true", help="Always create/use a temp external venv (not inside project)"
    )
    args = parser.parse_args(argv)

    patterns = args.tests if args.tests else DEFAULT_PATTERNS
    discovered = []
    for pat in patterns:
        # Allow direct file path as well as glob
        direct = ROOT / pat
        if direct.exists():
            discovered.append(direct)
        else:
            discovered.extend(discover_tests([pat]))

    # De-duplicate and normalize
    tests = []
    seen = set()
    for t in discovered:
        t = t.resolve()
        if t not in seen:
            seen.add(t)
            tests.append(t)

    # Apply keyword filters
    if args.keyword:
        def match_keywords(path: Path) -> bool:
            name = path.name
            return any(k.lower() in name.lower() for k in args.keyword)
        tests = [t for t in tests if match_keywords(t)]

    if not tests:
        print("No tests found.")
        return 1

    if args.list:
        for t in tests:
            print(t.relative_to(ROOT))
        return 0

    # Prepare environment for matplotlib headless runs
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("PYTHONPATH", str(ROOT))
    env.setdefault("MPLCONFIGDIR", str((ROOT / ".mplconfig")))

    # Ensure mpl config dir exists
    try:
        (ROOT / ".mplconfig").mkdir(exist_ok=True)
    except OSError:
        pass

    # Ensure logs directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / ".mplconfig").mkdir(exist_ok=True)

    # Prepare interpreter/deps
    if args.force_temp_env:
        # Always create/use external venv
        external_py = venv_python(get_external_venv_path())
        if not external_py.exists():
            subprocess.run([sys.executable, "-m", "venv", str(get_external_venv_path())], check=True)
        py_exec = ensure_deps(str(external_py))
    else:
        py_exec = sys.executable
        if not args.use_current:
            py_exec = ensure_deps(py_exec)

    env["PYTHON_EXECUTABLE"] = py_exec

    results = []
    with LOG_FILE.open("w", encoding="utf-8") as log:
        def log_print(msg: str = ""):
            print(msg)
            print(msg, file=log)

        log_print(f"Using Python: {py_exec}")
        log_print(f"Requirements: {REQUIREMENTS}")
        log_print("\nDiscovered tests:")
        for t in tests:
            log_print(f" - {t.relative_to(ROOT)}")

        log_print("\nRunning tests...\n")

        for test in tests:
            cleanup_artifacts()
            rel = test.relative_to(ROOT)
            log_print(f"=== Running {rel} ===")
            code, out, err = run_test(test, env=env)
            if out:
                log_print(out.rstrip("\n"))
            if err:
                log_print(err.rstrip("\n"))
            status = "PASSED" if code == 0 else "FAILED"
            log_print(f"--- {rel} {status} (exit={code}) ---")
            results.append((rel, code))
            if code != 0 and args.fail_fast:
                break

        failures = [r for r in results if r[1] != 0]
        log_print("\nSummary:")
        for rel, code in results:
            log_print(f" - {rel}: {'OK' if code == 0 else f'FAIL(' + str(code) + ')'}")
        if failures:
            log_print(f"\n{len(failures)} test(s) failed.")
            return 1
        log_print(f"\nAll {len(results)} test(s) passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
