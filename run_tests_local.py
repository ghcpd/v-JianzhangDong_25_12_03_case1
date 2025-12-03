#!/usr/bin/env python3
"""
Run the script-style tests in tests/ with project root on sys.path and write a
combined log to logs/test_run.log. This avoids running pytest and executes the
scripts as standalone programs while ensuring 'app' package imports work.
"""
import sys
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
LOG = LOGS / "test_run.log"

tests = [ROOT / 'tests' / 'case_1.py', ROOT / 'tests' / 'case_2.py', ROOT / 'tests' / 'case_3.py']

def main():
    # Ensure project root is first in sys.path so 'app' is importable
    sys.path.insert(0, str(ROOT))

    with open(LOG, 'w', encoding='utf-8') as out:
        out.write(f"Active interpreter: {sys.executable}\n")
        overall_rc = 0
        for t in tests:
            out.write('\n' + '='*20 + f" RUNNING: {t.name} " + '='*20 + '\n')
            try:
                runpy.run_path(str(t), run_name='__main__')
                out.write(f"{t.name}: SUCCESS\n")
            except Exception as e:
                out.write(f"{t.name}: FAILURE\n")
                out.write("" + str(e) + '\n')
                overall_rc = 1

        out.write('\nSUMMARY: exit_code=' + str(overall_rc) + '\n')

    print(f"Wrote logs to {LOG}")
    sys.exit(overall_rc)


if __name__ == '__main__':
    main()
