"""Run the configuration-API demo batch (cfg_*.py)."""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CFG_SET = [
    "cfg_01_add_and_switch.py",
    "cfg_02_suppress_feature_per_config.py",
    "cfg_03_lock_state.py",
    "cfg_04_iterate_and_report.py",
]

def main() -> int:
    results = []
    for name in CFG_SET:
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
