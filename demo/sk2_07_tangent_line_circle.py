"""Sketch-2D demo 07 — make a line tangent to a circle.

Draws a circle and a line that *almost* touches it, then adds a
``TANGENT`` constraint between them. The line snaps to be tangent to
the circle — distance from circle center to line equals the radius.

Pass criteria:
  - Tangent constraint added.
  - Perpendicular distance from the circle's center to the line equals
    the radius (within 1e-3 cm).
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example


def _point_line_distance(px, py, x1, y1, x2, y2) -> float:
    """Perpendicular distance from point (px,py) to the line through (x1,y1)-(x2,y2)."""
    num = abs((x2 - x1) * (y1 - py) - (x1 - px) * (y2 - y1))
    den = math.hypot(x2 - x1, y2 - y1)
    return num / den


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_07_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "Tangent_LC")

    sk.BeginChange()
    try:
        circle = sk.Figures.AddCircle(0.0, 0.0, 2.0)         # circle r=2 at origin
        line   = sk.Figures.AddLine(-4.0, 2.5, 4.0, 2.5)     # line not yet tangent
    finally:
        sk.EndChange()

    print(f"Initial circle: c=({circle.Center.X}, {circle.Center.Y})  r={circle.Radius}")
    d0 = _point_line_distance(circle.Center.X, circle.Center.Y,
                              line.Start.X, line.Start.Y, line.End.X, line.End.Y)
    print(f"Initial center-line distance: {d0:.4f}  (line is {abs(d0 - circle.Radius):.4f} away from tangent)")

    sk.BeginChange()
    try:
        col = root.NewObjectCollector()
        col.Add(circle)
        col.Add(line)
        sk.SketchConstraints.AddConstraint(col, ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
    finally:
        sk.EndChange()

    d1 = _point_line_distance(circle.Center.X, circle.Center.Y,
                              line.Start.X, line.Start.Y, line.End.X, line.End.Y)
    print(f"Final center-line distance:   {d1:.4f}  (target = radius = {circle.Radius})")

    return report([
        ("center-line distance == radius",
            math.isclose(d1, circle.Radius, abs_tol=1e-3)),
        ("constraint added",
            sk.SketchConstraints.Count > 0),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
