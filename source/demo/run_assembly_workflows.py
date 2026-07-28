"""Run the assembly-workflow demo batch (asm_*.py).

Covers MATE, ALIGN, distance-mate, and sub-assembly construction. All
demos use parts from the bundled muffler folder so they don't fabricate
synthetic geometry.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ASM_SET = [
    "asm_01_mate_constraint.py",
    "asm_02_align_constraint.py",
    "asm_03_distance_constraint.py",
    "asm_04_sub_assembly.py",
    "asm_05_fully_constrain.py",
    "asm_06_suppress_constraint.py",
    "asm_07_angle_constraint.py",
    "asm_08_reverse_constraint.py",
    "asm_09_delete_constraint.py",
    "asm_10_fully_defined_verify.py",
    "asm_11_flexible_subassembly.py",
    "asm_12_bom_to_csv.py",
]

def main() -> int:
    results = []
    for name in ASM_SET:
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
