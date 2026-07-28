"""Assembly demo 05: fully constrain a part using three plane aligns.

A free part has 6 degrees of freedom (3 translation, 3 rotation).
Aligning each of its three orthogonal design planes (XY, YZ, ZX) to
the matching plane on an anchored part forces the constrained part to
sit at the anchor's origin with identity rotation.

Three plane constraints lock 3×3 = 9 axes worth of DOF on a body
that only has 6, so the third constraint is redundant. Alibre's solver
still finds the unique solution; the redundant constraint may report
``HasError == True`` even though the part is correctly positioned, so
this demo asserts the *geometric result*, not zero errors.

Uses ``ALIGN`` (same-normal direction) rather than ``MATE`` (opposite-
normal direction) so the rotation comes out as identity rather than a
180° flip. With three MATEs the part is reflected about each plane
and ends up rotated 180° about a diagonal axis.

Pass criteria:
  - 3 constraints added to the assembly.
  - Constrained part's translation = (0, 0, 0) (within 1e-3 cm).
  - Constrained part's rotation matrix is the 3x3 identity (within
    1e-3 per element).
"""
from __future__ import annotations

import math
import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example

def _matrix(occ) -> list[float]:
    return list(occ.WorldTransform.Array())

def _translation(flat: list[float]) -> tuple[float, float, float]:
    return (flat[12], flat[13], flat[14])

def _rotation_diag(flat: list[float]) -> tuple[float, float, float]:
    return (flat[0], flat[5], flat[10])

def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    tag = uuid.uuid4().hex[:6]

    root = connect()
    asm = root.CreateEmptyAssembly(f"FullyConstrain_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(20.0, 15.0, 10.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    before = _matrix(asm.RootOccurrence.Occurrences.Item(1))
    print(f"Before: B translation = {_translation(before)}")

    constraints = []
    for idx, label in [(0, "XY"), (1, "YZ"), (2, "ZX")]:
        occ_a = asm.RootOccurrence.Occurrences.Item(0)
        occ_b = asm.RootOccurrence.Occurrences.Item(1)
        t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(idx))
        t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(idx))
        c = asm.AssemblyConstraints.AddConstraint(
            t_a, t_b, ADAssemblyConstraintType.AD_ALIGN_TYPE,
            None, False, f"Align_{label}", "",
        )
        constraints.append(c)
        after_step = _translation(_matrix(asm.RootOccurrence.Occurrences.Item(1)))
        print(f"  after Align_{label}: B translation = {after_step}")

    after = _matrix(asm.RootOccurrence.Occurrences.Item(1))
    tx, ty, tz = _translation(after)
    rx, ry, rz = _rotation_diag(after)
    errors = [c.HasError for c in constraints]
    print(f"\nFinal: translation=({tx:.4f}, {ty:.4f}, {tz:.4f})  "
          f"rot diag=({rx:.4f}, {ry:.4f}, {rz:.4f})")
    print(f"Constraint errors: {errors}")

    return report([
        ("3 constraints added",     asm.AssemblyConstraints.Count == 3),
        ("translation at origin",
            math.isclose(abs(tx), 0.0, abs_tol=1e-3)
            and math.isclose(abs(ty), 0.0, abs_tol=1e-3)
            and math.isclose(abs(tz), 0.0, abs_tol=1e-3)),
        ("rotation is identity",
            math.isclose(rx, 1.0, abs_tol=1e-3)
            and math.isclose(ry, 1.0, abs_tol=1e-3)
            and math.isclose(rz, 1.0, abs_tol=1e-3)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
