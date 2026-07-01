"""Assembly demo 07: angle constraint between two part planes.

Adds an ``AD_ANGLE_TYPE`` constraint with a parameterised angle so the
two part planes end up at the requested angle to each other. Like the
revolve angle (S9 in KNOWN_ISSUES.md), the parameter is interpreted in
**radians**: pass ``math.radians(degrees)``.

Pass criteria:
  - Constraint count goes 0 -> 1.
  - Constraint reports type AD_ANGLE_TYPE.
  - HasError is False.
"""
from __future__ import annotations

import math
import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example

ANGLE_DEG = 30.0


def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "dished baffle plate.AD_PRT")
    tag = uuid.uuid4().hex[:6]

    root = connect()
    asm = root.CreateEmptyAssembly(f"Angle_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(40.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))

    n_before = asm.AssemblyConstraints.Count
    c = asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_ANGLE_TYPE,
        math.radians(ANGLE_DEG), False, "Angle30", "AngleParam",
    )
    n_after = asm.AssemblyConstraints.Count
    print(f"Constraint count: {n_before} -> {n_after}")
    print(f"Type: {c.ConstraintType}, HasError: {c.HasError}")

    return report([
        ("constraint added",  n_after == n_before + 1),
        ("type is angle",     int(c.ConstraintType) == int(ADAssemblyConstraintType.AD_ANGLE_TYPE)),
        ("no error",          not bool(c.HasError)),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
