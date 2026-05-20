"""Assembly demo 04 - build a sub-assembly, place it inside a parent.

Pipeline:
  1. Build a *sub-assembly* with two muffler parts inside it.
  2. Save it to disk.
  3. Build a *parent* assembly that includes the sub-assembly twice
     plus one bare part - exercising a 3-level hierarchy.

Pass criteria:
  - Sub-assembly file is on disk.
  - Parent assembly has 3 children at the root.
  - Two of those children are themselves assembly occurrences (each
    holding 2 children).
  - Total leaf-part count under the parent is 5 (2 sub-asm copies x 2
    + 1 bare).
"""
from __future__ import annotations

import os
import sys
import tempfile
import uuid

from _demo_utils import MUFFLER_DIR, report, walk_occurrences
from alibrex import connect, run_example


def main() -> int:
    folder = tempfile.mkdtemp(prefix="alibrex_subasm_")
    tag = uuid.uuid4().hex[:6]

    part_a = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube support block.AD_PRT")
    part_c = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")

    root = connect()

    # --- 1. Build the sub-assembly ----------------------------------------
    sub_name = f"Sub_{tag}"
    sub = root.CreateEmptyAssembly(sub_name)
    sub_geo = sub.GeometryFactory
    a_obj: object = part_a
    b_obj: object = part_b
    sub.RootOccurrence.Occurrences.Add(a_obj, sub_geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    sub.RootOccurrence.Occurrences.Add(b_obj, sub_geo.CreateTranslationTransformByXYZ(10.0, 0.0, 0.0))
    folder_ref: object = folder
    sub.SaveAs(folder_ref, sub_name)
    sub_path = os.path.join(folder, f"{sub_name}.AD_ASM")
    print(f"Sub-assembly saved: {sub_path}  (exists={os.path.exists(sub_path)})")
    sub.Close(False)

    # --- 2. Build the parent assembly -------------------------------------
    parent = root.CreateEmptyAssembly(f"Parent_{tag}")
    geo = parent.GeometryFactory
    sub_obj: object = sub_path
    c_obj: object = part_c
    parent.RootOccurrence.Occurrences.Add(sub_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    parent.RootOccurrence.Occurrences.Add(sub_obj, geo.CreateTranslationTransformByXYZ(50.0, 0.0, 0.0))
    parent.RootOccurrence.Occurrences.Add(c_obj,   geo.CreateTranslationTransformByXYZ(0.0, 30.0, 0.0))

    root_occ = parent.RootOccurrence
    top_count = root_occ.Occurrences.Count
    print(f"Parent root has {top_count} child occurrences:")

    leaf_count = 0
    sub_asm_count = 0
    def visit(occ, depth):
        nonlocal leaf_count, sub_asm_count
        print(" " * (depth + 1) + f"- {occ.Name}  (children={occ.Occurrences.Count})")
        if occ.Occurrences.Count == 0:
            leaf_count += 1
        elif depth == 0:
            sub_asm_count += 1
    walk_occurrences(root_occ, visit)

    print(f"\nLeaves: {leaf_count}, top-level sub-assemblies: {sub_asm_count}")

    return report([
        ("sub-assembly on disk", os.path.exists(sub_path)),
        ("3 children at root",   top_count == 3),
        ("2 sub-assemblies",     sub_asm_count == 2),
        ("5 leaf parts total",   leaf_count == 5),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
