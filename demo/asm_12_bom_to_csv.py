"""Assembly demo 12 - write the muffler's bill of materials to a CSV.

Walks the muffler assembly tree, tallies leaf parts by base name
(stripping the ``<N>`` instance suffix), and writes the result to a
``.csv`` file. This is the typical kickoff for any "feed our PLM /
inventory / cost system from a CAD assembly" workflow.

Pass criteria:
  - CSV file is written and >= 200 bytes.
  - CSV has a header row plus one row per distinct part.
  - Total count column sums to the assembly's leaf-part count.
"""
from __future__ import annotations

import csv
import os
import re
import sys
import tempfile
import time
from collections import Counter

from _demo_utils import open_muffler, report, walk_occurrences
from alibrex import run_example

_INSTANCE_SUFFIX = re.compile(r"<\d+>$")


def base_name(name: str) -> str:
    return _INSTANCE_SUFFIX.sub("", name).strip()


def main() -> int:
    asm = open_muffler()

    counts: Counter[str] = Counter()
    paths: dict[str, str] = {}
    def visit(occ, _depth):
        if occ.Occurrences.Count == 0:
            n = base_name(occ.Name)
            counts[n] += 1
            try:
                paths.setdefault(n, occ.DesignSession.FilePath or "")
            except Exception:
                paths.setdefault(n, "")
    walk_occurrences(asm.RootOccurrence, visit)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(tempfile.gettempdir(), f"muffler_bom_{stamp}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["part_name", "quantity", "source_file"])
        for name, n in counts.most_common():
            writer.writerow([name, n, paths.get(name, "")])

    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    total = sum(counts.values())
    print(f"Wrote BOM: {out_path}  ({size:,} bytes)")
    print(f"  {len(counts)} distinct parts, {total} total leaf occurrences")

    # Read back to verify row count.
    with open(out_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    data_rows = rows[1:]
    summed = sum(int(r[1]) for r in data_rows)

    return report([
        ("CSV on disk >= 200 bytes", size >= 200),
        ("header + N data rows",     len(rows) == 1 + len(counts)),
        ("quantities sum matches",   summed == total),
        ("non-zero parts",           total >= 15),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
