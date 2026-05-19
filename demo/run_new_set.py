"""Run only the muffler-driven demos (crud_13..crud_18).

Skips the older crud_01..crud_12 suite (those exercise part-feature
CRUD using fresh empty parts). The muffler demos open the bundled
``muffler/0_Muffler_Assembly.AD_ASM`` and operate on its real
occurrence tree.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

NEW_SET = [
    "crud_13_muffler_walk.py",
    "crud_14_muffler_bom.py",
    "crud_15_muffler_suppress_toggle.py",
    "crud_16_muffler_interference.py",
    "crud_17_muffler_world_transforms.py",
    "crud_18_muffler_export.py",
]


def main() -> int:
    results = []
    for name in NEW_SET:
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
