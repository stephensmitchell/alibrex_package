"""Assembly demo 08 - same MATE constraint with isReversed=True flips the part.

Compares two assemblies built from identical inputs except for the
``isReversed`` flag on the mate constraint. With ``isReversed=False``
the constraint solver places B on one side of A; with ``True`` it
flips to the other side. The rotation diagonal of B's WorldTransform
records this flip.

Pass criteria:
  - Both assemblies build with 1 constraint each.
  - The Z-row of B's rotation matrix has opposite signs in the two
    assemblies (the part is flipped relative to A's plane).
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example


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
        None, reversed_, f"MateXY_{'R' if reversed_ else 'F'}", "",
    )
    return asm


def _row_z(occ) -> tuple[float, float, float]:
    flat = list(occ.WorldTransform.Array())
    # Column-major: the 3rd row is at indices 2, 6, 10 (XX, YX, ZX) for a row?
    # The rotation diagonal in column-major is at indices 0, 5, 10. Z-axis
    # direction in the local frame is the 3rd column: indices 8, 9, 10.
    return (flat[8], flat[9], flat[10])


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    root = connect()

    asm_f = _build(root, tag, reversed_=False)
    z_f = _row_z(asm_f.RootOccurrence.Occurrences.Item(1))
    n_f = asm_f.AssemblyConstraints.Count

    asm_r = _build(root, tag, reversed_=True)
    z_r = _row_z(asm_r.RootOccurrence.Occurrences.Item(1))
    n_r = asm_r.AssemblyConstraints.Count

    print(f"isReversed=False -> Z column of B's rotation = {z_f}")
    print(f"isReversed=True  -> Z column of B's rotation = {z_r}")

    flipped = abs(z_f[2] + z_r[2]) < abs(z_f[2] - z_r[2])

    return report([
        ("1 constraint in F build", n_f == 1),
        ("1 constraint in R build", n_r == 1),
        ("B is flipped (Zz sign)",  flipped),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
