"""Run every crud_*.py demo in this folder and report a summary.

Each demo prints its own PASS/FAIL and exits 0 (pass) or 1 (fail). This
runner aggregates results.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def main() -> int:
    scripts = sorted(
        f for f in os.listdir(HERE)
        if f.startswith("crud_") and f.endswith(".py")
    )
    results = []
    for s in scripts:
        path = os.path.join(HERE, s)
        print(f"\n========== {s} ==========")
        rc = subprocess.call([sys.executable, path])
        results.append((s, rc))

    print("\n========== SUMMARY ==========")
    for s, rc in results:
        print(f"  [{'PASS' if rc == 0 else 'FAIL'}] {s}  (exit {rc})")
    failed = sum(1 for _, rc in results if rc != 0)
    print(f"\n{len(results) - failed} of {len(results)} demos passed.")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
