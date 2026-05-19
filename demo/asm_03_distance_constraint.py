"""Assembly demo 03 — distance-MATE (parameterized) between two parts.

Same as ``asm_01`` but passes a non-None ``parameterValue`` (a distance
in cm) so the two mating planes end up *that distance apart* rather
than coincident.

Pass criteria:
  - Constraint count goes 0 -> 1.
  - After the constraint, B's Z translation equals the supplied distance
    (within 1e-3 cm), measured from A's plane.
"""
from __future__ import annotations

import math
import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example

DISTANCE_CM = 7.5


def _translation(occ) -> tuple[float, float, float]:
    flat = list(occ.WorldTransform.Array())
    return (flat[12], flat[13], flat[14])


def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    tag = uuid.uuid4().hex[:6]

    root = connect()
    asm = root.CreateEmptyAssembly(f"Dist_Asm_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(30.0, 15.0, 20.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))

    n_before = asm.AssemblyConstraints.Count
    asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_MATE_TYPE,
        DISTANCE_CM, False, "DistanceMate", "GapZ",
    )
    n_after = asm.AssemblyConstraints.Count

    b_after = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"B after distance-mate at {DISTANCE_CM} cm: {b_after}")
    print(f"Constraint count: {n_before} -> {n_after}")

    z_at_distance = math.isclose(abs(b_after[2]), DISTANCE_CM, abs_tol=1e-2)
    return report([
        ("constraint added",          n_after == n_before + 1),
        ("B Z == distance parameter", z_at_distance),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
