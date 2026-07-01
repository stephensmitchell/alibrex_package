"""Sketch-2D demo 08: two circles tangent to each other.

Two circles tangent externally satisfy:
    distance_between_centers == r1 + r2

Draws two circles whose centers are too far apart, then adds a tangent
constraint. Verifies the center distance equals the sum of radii.

Pass criteria:
  - Tangent constraint added.
  - Center-to-center distance equals (r1 + r2) within 1e-3 cm.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_08_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "TangentCircles")

    sk.BeginChange()
    try:
        c1 = sk.Figures.AddCircle(0.0, 0.0, 2.0)
        c2 = sk.Figures.AddCircle(6.0, 0.0, 1.0)   # centers 6 apart, sum of radii is 3, not tangent
    finally:
        sk.EndChange()

    dx, dy = c2.Center.X - c1.Center.X, c2.Center.Y - c1.Center.Y
    d0 = math.hypot(dx, dy)
    print(f"Initial: c1=({c1.Center.X}, {c1.Center.Y}) r={c1.Radius}; "
          f"c2=({c2.Center.X}, {c2.Center.Y}) r={c2.Radius}; "
          f"d={d0:.4f}  (r1+r2={c1.Radius + c2.Radius:.4f})")

    sk.BeginChange()
    try:
        col = root.NewObjectCollector()
        col.Add(c1)
        col.Add(c2)
        sk.SketchConstraints.AddConstraint(col, ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
    finally:
        sk.EndChange()

    dx, dy = c2.Center.X - c1.Center.X, c2.Center.Y - c1.Center.Y
    d1 = math.hypot(dx, dy)
    r_sum = c1.Radius + c2.Radius
    print(f"Final  : d={d1:.4f}  (r1+r2={r_sum:.4f})")

    return report([
        ("constraint added",                 sk.SketchConstraints.Count > 0),
        ("centers separated by (r1 + r2)",   math.isclose(d1, r_sum, abs_tol=1e-3)),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
