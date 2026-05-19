"""Assembly demo 02 — ALIGN two muffler parts, verify movement.

Same scaffolding as ``asm_01`` but with an ALIGN constraint instead of
MATE. Mate makes the two planes coincide with opposite normals; Align
makes them coincide with the same normal direction. Either way the
solver should snap the non-anchored occurrence into the constrained
position.

Pass criteria:
  - Constraint count goes 0 -> 1.
  - Non-anchored occurrence's translation changed.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example


def _translation(occ) -> tuple[float, float, float]:
    flat = list(occ.WorldTransform.Array())
    return (flat[12], flat[13], flat[14])


def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "dished baffle plate.AD_PRT")

    tag = uuid.uuid4().hex[:6]
    root = connect()
    asm = root.CreateEmptyAssembly(f"Align_Asm_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(40.0, 25.0, 15.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    b_before = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"Before align: B={b_before}")

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))

    n_before = asm.AssemblyConstraints.Count
    asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_ALIGN_TYPE,
        None, False, "XYAlign", "",
    )
    n_after = asm.AssemblyConstraints.Count

    b_after = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"After align : B={b_after}")
    print(f"Constraint count: {n_before} -> {n_after}")

    return report([
        ("constraint added",      n_after == n_before + 1),
        ("B moved by constraint", b_before != b_after),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
