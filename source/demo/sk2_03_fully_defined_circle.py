"""Sketch-2D demo 03: fully constrain a circle (center fixed + diameter dim).

A circle has 3 degrees of freedom (Cx, Cy, R). Pinning the center to
the sketch origin removes 2; adding a diameter dimension removes the
third. The circle is now fully constrained.

Pass criteria:
  - One circle sketched with a sloppy center and radius.
  - After FIX on the center point and a diametric dimension, the circle
    reads back center=(0,0) and the requested diameter.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

DIAM = 4.0

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_03_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "Circle")

    sk.BeginChange()
    try:
        circle = sk.Figures.AddCircle(0.7, 0.3, 1.7)
    finally:
        sk.EndChange()
    print(f"Initial: center=({circle.Center.X}, {circle.Center.Y})  radius={circle.Radius}")

    sk.BeginChange()
    try:
        col = root.NewObjectCollector()
        col.Add(circle.Center)
        col.Add(sk.OriginPoint)
        sk.SketchConstraints.AddConstraint(col, ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        sk.Dimensions.PlaceDiametricDimension(circle, DIAM)
    finally:
        sk.EndChange()

    cx, cy, r = circle.Center.X, circle.Center.Y, circle.Radius
    print(f"Final  : center=({cx}, {cy})  radius={r}  diameter={2*r}")

    return report([
        ("center at origin (X=0)",   math.isclose(cx, 0.0, abs_tol=1e-3)),
        ("center at origin (Y=0)",   math.isclose(cy, 0.0, abs_tol=1e-3)),
        ("diameter matches",         math.isclose(2*r, DIAM, abs_tol=1e-3)),
        ("dimension added",          sk.Dimensions.Count == 1),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
