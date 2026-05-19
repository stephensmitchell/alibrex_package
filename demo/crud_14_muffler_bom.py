"""CRUD demo 14 — bill of materials from the muffler assembly.

Walks the muffler tree and tallies leaf parts by base name (stripping
the ``<N>`` instance suffix Alibre appends). Output is sorted by count.

Pass criteria:
  - 'choke tube' appears 3 times (one per choke tube assembly).
  - 'cylinder' appears once.
  - 'choke tube support block' appears 6 times (2 per choke tube assy × 3).
  - 'elliptical head' appears at least 2 times.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

from _demo_utils import open_muffler, report, walk_occurrences
from alibrex import run_example


_INSTANCE_SUFFIX = re.compile(r"<\d+>$")


def base_name(name: str) -> str:
    return _INSTANCE_SUFFIX.sub("", name).strip()


def main() -> int:
    asm = open_muffler()
    counts: Counter[str] = Counter()
    def visit(occ, _depth):
        if occ.Occurrences.Count == 0:                # leaf part
            counts[base_name(occ.Name)] += 1
    walk_occurrences(asm.RootOccurrence, visit)

    print(f"Bill of materials for '{asm.Name}':")
    print(f"{'count':>5s}  part")
    print("-" * 50)
    for name, n in counts.most_common():
        print(f"{n:>5d}  {name}")
    print(f"{'total':>5s}  {sum(counts.values())}")

    return report([
        ("3x choke tube",                       counts.get("choke tube", 0) == 3),
        ("1x cylinder",                         counts.get("cylinder", 0) == 1),
        ("6x choke tube support block",         counts.get("choke tube support block", 0) == 6),
        (">= 2x elliptical head",               counts.get("elliptical head", 0) >= 2),
        ("BOM non-empty",                       sum(counts.values()) >= 15),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
