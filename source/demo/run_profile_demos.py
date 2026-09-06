"""Run the profile-library demos (prof_*.py)."""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PROF_SET = [
    "prof_01_steel.py",
    "prof_02_wood.py",
    "prof_03_threads.py",
    "prof_04_pipe.py",
]

def main() -> int:
    results = []
    for name in PROF_SET:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"  [MISSING] {name}")
            results.append((name, 127))
            continue
        print(f"\n========== {name} ==========")
        rc = subprocess.call([sys.executable, path])
        results.append((name, rc))

    print("\n========== SUMMARY ==========")
    for name, rc in results:
        print(f"  [{'PASS' if rc == 0 else 'FAIL'}] {name}  (exit {rc})")
    failed = sum(1 for _, rc in results if rc != 0)
    print(f"\n{len(results) - failed} of {len(results)} demos passed.")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
