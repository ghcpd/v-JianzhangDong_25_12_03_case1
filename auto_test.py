import argparse
import os
import sys
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).parent
REQ_FILE = ROOT / "requirements.txt"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"


def debug(msg: str):
    print(f"[auto_test] {msg}")


def in_project_path(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


def ensure_python(isolate: bool = False) -> Path:
    """Return a python interpreter path to use.

    Priority:
    1) VS Code-selected interpreter (sys.executable)
    2) If isolation requested or the interpreter lives inside the project dir, create a temp venv outside the project.
    """
    current_py = Path(sys.executable)
    if not current_py:
        raise RuntimeError("No active Python interpreter detected. Please select an interpreter in VS Code.")

    if isolate or in_project_path(current_py):
        venv_dir = Path(tempfile.gettempdir()) / "v_JianzhangDong_25_12_03_case1_venv"
        python_bin = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "python"
        if not python_bin.exists():
            debug(f"Creating external venv at {venv_dir}")
            subprocess.run([current_py, "-m", "venv", str(venv_dir)], check=True)
        return python_bin

    return current_py


def install_requirements(python_bin: Path):
    debug("Upgrading pip and installing requirements")
    subprocess.run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(python_bin), "-m", "pip", "install", "-r", str(REQ_FILE)], check=True)


def run_tests(python_bin: Path) -> int:
    tests_dir = ROOT / "tests"
    test_files = sorted(tests_dir.glob("*.py"))
    if not test_files:
        debug("No test files found.")
        return 0

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    with LOG_FILE.open("w", encoding="utf-8") as log:
        for test_file in test_files:
            debug(f"Running {test_file}")
            log.write(f"=== Running {test_file.name} ===\n")
            result = subprocess.run(
                [str(python_bin), str(test_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )
            log.write(result.stdout)
            log.write("\n")
            log.flush()
            if result.returncode != 0:
                debug(f"Test failed: {test_file}")
                return result.returncode
    debug("All tests completed.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Auto-detect environment, install deps, and run tests.")
    parser.add_argument(
        "--isolate",
        action="store_true",
        help="Force creation/use of an external virtual environment in the system temp directory.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installing requirements (assume already installed).",
    )
    args = parser.parse_args()

    python_bin = ensure_python(isolate=args.isolate)
    if not args.skip_install:
        install_requirements(python_bin)
    rc = run_tests(python_bin)
    sys.exit(rc)


if __name__ == "__main__":
    main()
