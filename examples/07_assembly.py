"""Example 07 - walk an assembly tree and check for interferences.

Recursively prints occurrences and runs an interference check between all
top-level pairs.
"""
from __future__ import annotations

import sys

from alibrex import IADOccurrence, connect, run_example, require_active_assembly
def walk(occ: IADOccurrence, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}- {occ.Name}")
    n = 1
    for i in range(occ.Occurrences.Count):
        n += walk(occ.Occurrences.Item(i), depth + 1)
    return n


def main() -> None:
    root = connect()
    asm = require_active_assembly(root)

    print(f"Assembly: {asm.Name}\n")
    total = walk(asm.RootOccurrence)
    print(f"\nTotal occurrences: {total}")

    if asm.RootOccurrence.Occurrences.Count < 2:
        print("Need at least 2 children for interference check.")
        return

    g1 = root.NewObjectCollector()
    g2 = root.NewObjectCollector()
    g1.Add(asm.RootOccurrence.Occurrences.Item(0))
    for i in range(1, asm.RootOccurrence.Occurrences.Count):
        g2.Add(asm.RootOccurrence.Occurrences.Item(i))

    interferences, _, _ = asm.CheckInterference(g1, g2)
    print(f"\nInterferences found: {interferences.Count}")
    for i in range(interferences.Count):
        intf = interferences.Item(i)
        print(f"  {intf.Part1.Name}  <->  {intf.Part2.Name}   vol={intf.InterferenceVolume:.4f}")


if __name__ == "__main__":
    sys.exit(run_example(main))
