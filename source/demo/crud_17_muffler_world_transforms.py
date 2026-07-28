"""CRUD demo 17: read every leaf occurrence's WorldTransform on the muffler.

Walks the muffler tree, reads ``WorldTransform`` for each leaf part,
extracts the translation component, and prints a position summary.
This pattern populates a BOM / CSV / dump for downstream tooling.

Pass criteria:
  - Every leaf reports a usable WorldTransform.
  - Different occurrences end up at different world positions (the
    assembly isn't a stack of identical-transform parts).
"""
from __future__ import annotations

import sys

from _demo_utils import open_muffler, report, walk_occurrences
from alibrex import run_example

def _translation_of(occ) -> tuple[float, float, float] | None:
    """Read the (Tx, Ty, Tz) translation from ``occ.WorldTransform``.

    ``IADTransformation.Array()`` returns the homogeneous matrix as a
    16-double flat ``System.Array`` in row-major order; the translation
    is the 4th column.
    """
    try:
        flat = list(occ.WorldTransform.Array())
    except Exception:
        return None
    if len(flat) == 16:
        return (flat[12], flat[13], flat[14])
    if len(flat) == 12:
        return (flat[9], flat[10], flat[11])
    return None

def main() -> int:
    asm = open_muffler()
    positions: list[tuple[str, tuple[float, float, float] | None]] = []
    def visit(occ, _depth):
        if occ.Occurrences.Count == 0:
            positions.append((occ.Name, _translation_of(occ)))
    walk_occurrences(asm.RootOccurrence, visit)

    print(f"World translations of {len(positions)} leaf occurrence(s):\n")
    print(f"{'name':<40s}  {'Tx':>10s}  {'Ty':>10s}  {'Tz':>10s}")
    print("-" * 80)
    usable = 0
    distinct = set()
    for name, t in positions:
        if t is None:
            print(f"{name:<40s}  {'-':>10s}  {'-':>10s}  {'-':>10s}")
        else:
            usable += 1
            distinct.add(tuple(round(v, 4) for v in t))
            print(f"{name:<40s}  {t[0]:>10.4f}  {t[1]:>10.4f}  {t[2]:>10.4f}")

    print(f"\n{usable}/{len(positions)} transforms read OK; {len(distinct)} distinct positions.")
    return report([
        ("all leaves report a transform",   usable == len(positions)),
        (">= 5 distinct positions",         len(distinct) >= 5),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
