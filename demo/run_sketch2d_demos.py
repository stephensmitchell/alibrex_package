"""Run the 2D fully-defined sketch demos (sk2_*.py)."""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SK2_SET = [
    "sk2_01_constraint_types.py",
    "sk2_02_fully_defined_rectangle.py",
    "sk2_03_fully_defined_circle.py",
    "sk2_04_fully_defined_triangle.py",
    "sk2_05_dimension_drives_geometry.py",
    "sk2_06_under_vs_fully.py",
    "sk2_07_tangent_line_circle.py",
    "sk2_08_tangent_two_circles.py",
    "sk2_09_fillet_arc.py",
    "sk2_10_slot_fully_defined.py",
    "sk2_11_three_tangent_arcs.py",
]


def main() -> int:
    results = []
    for name in SK2_SET:
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
