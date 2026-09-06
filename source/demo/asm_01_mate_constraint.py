"""Assembly demo 01: MATE two muffler parts together, verify movement.

Drops two on-disk muffler parts (cylinder + choke tube) into a fresh
assembly at different positions, then adds a MATE constraint between
their XY planes. Reads each occurrence's translation before and after;
the constraint solver should snap the non-anchored occurrence onto the
anchored one along the mated axis.

Pass criteria:
  - Two file-backed occurrences in the new assembly.
  - The non-anchored occurrence's pre-mate translation differs from its
    post-mate translation (the solver moved it).
  - ``AssemblyConstraints.Count`` increments by one.
  - The anchored occurrence's translation is unchanged.
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
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    for p in (part_a, part_b):
        if not os.path.exists(p):
            print(f"Missing muffler part: {p}")
            return 1

    tag = uuid.uuid4().hex[:6]
    root = connect()
    asm = root.CreateEmptyAssembly(f"Mate_Asm_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(50.0, 30.0, 20.0))

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_a.IsAnchored = True

    a_before = _translation(asm.RootOccurrence.Occurrences.Item(0))
    b_before = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"Before: A={a_before}  B={b_before}")

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))

    n_before = asm.AssemblyConstraints.Count
    asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_MATE_TYPE,
        None, False, "XYMate", "",
    )
    n_after = asm.AssemblyConstraints.Count

    a_after = _translation(asm.RootOccurrence.Occurrences.Item(0))
    b_after = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"After : A={a_after}  B={b_after}")
    print(f"Constraint count: {n_before} -> {n_after}")

    return report([
        ("2 occurrences",         asm.RootOccurrence.Occurrences.Count == 2),
        ("constraint added",      n_after == n_before + 1),
        ("anchor unchanged",      a_before == a_after),
        ("B moved by constraint", b_before != b_after),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
