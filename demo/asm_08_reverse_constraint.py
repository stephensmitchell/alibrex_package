"""Assembly demo 08: same MATE constraint with isReversed=True flips offset side.

Compares two assemblies built from identical inputs except for the
``isReversed`` flag on the mate constraint. With ``isReversed=False``
the constraint solver places B on one side of A; with ``True`` it
flips to the other side. A non-zero mate offset makes that side change
observable in B's translation.

Pass criteria:
  - Both assemblies build with 1 constraint each.
  - B's Z translation lands on opposite sides of A's XY plane.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example

OFFSET = 10.0


def _build(root, tag: str, reversed_: bool):
    asm = root.CreateEmptyAssembly(f"Reverse_{'T' if reversed_ else 'F'}_{tag}")
    geo = asm.GeometryFactory
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 25.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True
    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))
    asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_MATE_TYPE,
        OFFSET, reversed_, f"MateXY_{'R' if reversed_ else 'F'}", "MateOffset",
    )
    return asm


def _translation(occ) -> tuple[float, float, float]:
    flat = list(occ.WorldTransform.Array())
    return (flat[12], flat[13], flat[14])


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    root = connect()

    asm_f = _build(root, tag, reversed_=False)
    pos_f = _translation(asm_f.RootOccurrence.Occurrences.Item(1))
    n_f = asm_f.AssemblyConstraints.Count

    asm_r = _build(root, tag, reversed_=True)
    pos_r = _translation(asm_r.RootOccurrence.Occurrences.Item(1))
    n_r = asm_r.AssemblyConstraints.Count

    print(f"isReversed=False -> B translation = {pos_f}")
    print(f"isReversed=True  -> B translation = {pos_r}")

    opposite_sides = pos_f[2] * pos_r[2] < 0.0

    return report([
        ("1 constraint in F build", n_f == 1),
        ("1 constraint in R build", n_r == 1),
        ("B offset side flips",     opposite_sides),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
