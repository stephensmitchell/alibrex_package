"""CRUD demo 03 - add component occurrences to the active assembly, verify.

Uses the active assembly if one is open; otherwise opens a fresh empty
assembly. Adds three empty-part occurrences at three different
translations, then queries the tree back.

Pass criteria:
  - RootOccurrence.Occurrences.Count grows by exactly 3.
  - Each added occurrence is locatable by name in the children list.
  - CheckInterference runs and returns a result (count >= 0).
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import assembly_or_open, report
from alibrex import run_example


def main() -> int:
    asm = assembly_or_open("CRUD03_Assembly")
    geo = asm.GeometryFactory
    root_occ = asm.RootOccurrence

    before = root_occ.Occurrences.Count
    tag = uuid.uuid4().hex[:6]
    layout = [
        (f"CRUD03_A_{tag}", 0.0, 0.0, 0.0, False),
        (f"CRUD03_B_{tag}", 5.0, 0.0, 0.0, False),
        (f"CRUD03_C_{tag}", 2.5, 4.0, 0.0, True),
    ]
    for name, x, y, z, is_sheet in layout:
        xform = geo.CreateTranslationTransformByXYZ(x, y, z)
        root_occ.Occurrences.AddEmptyPart(name, is_sheet, xform)

    after = root_occ.Occurrences.Count
    child_names = [
        root_occ.Occurrences.Item(i).Name
        for i in range(after)
    ]
    # Alibre may append a "<n>" suffix to occurrence names - match by prefix.
    found = {
        name for name, *_ in layout
        if any(cn == name or cn.startswith(name) for cn in child_names)
    }

    try:
        result = asm.CheckInterference(None, None)
        interferences = result[0] if isinstance(result, tuple) else result
        interference_count = interferences.Count
        interference_ok = interference_count >= 0
    except Exception as exc:  # noqa: BLE001
        interference_count = -1
        interference_ok = False
        print(f"[warn] CheckInterference failed: {type(exc).__name__}: {exc}")

    print(f"Occurrences   : {before} -> {after}")
    print(f"Added names   : {sorted(n for n, *_ in layout)}")
    print(f"Found in tree : {sorted(found)}")
    print(f"Interferences : {interference_count}")

    return report([
        ("3 occurrences added", after == before + 3),
        ("all names present",   len(found) == 3),
        ("interference query",  interference_ok),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
