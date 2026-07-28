"""Sketch-2D demo 09: proper sketch fillet at a corner.

Models the CAD-fillet pattern: two lines trimmed back from a
corner, joined by an arc tangent to each, with the arc's endpoints
coincident with the trimmed line ends. The radius is set by a radial
dimension; the corner geometry is otherwise fully defined.

Geometry:

                              + (6, 4)
                              |
                              |  vertical line
                              |
                       (6, 1) +-.    <- arc.End
                              .  )
                              .  )  fillet arc, r = 1
                              . /
       horizontal line        (5, 0) <- arc.Start
       +----------------------+
       (0, 0)                 (5, 0)

Pass criteria:
  - Arc tangent to both lines (distance center-to-line == radius).
  - horiz.End coincident with arc.Start.
  - vert.Start coincident with arc.End.
  - Radius equals the value passed to ``PlaceRadialDimension`` (1.0 cm).
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

RADIUS = 1.0

def _point_line_distance(px, py, x1, y1, x2, y2) -> float:
    num = abs((x2 - x1) * (y1 - py) - (x1 - px) * (y2 - y1))
    den = math.hypot(x2 - x1, y2 - y1)
    return num / den

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_09_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "FilletCorner")

    sk.BeginChange()
    try:
        horiz = sk.Figures.AddLine(0.0, 0.0, 5.0, 0.0)
        vert  = sk.Figures.AddLine(6.0, 1.0, 6.0, 4.0)
        arc   = sk.Figures.AddCircularArcByCenterStartEnd(
            4.9, 1.1,
            5.0, 0.0,
            6.0, 1.0,
        )
    finally:
        sk.EndChange()

    def add(figs, ctype):
        col = root.NewObjectCollector()
        for f in figs:
            col.Add(f)
        return sk.SketchConstraints.AddConstraint(col, ctype)

    sk.BeginChange()
    try:
        add([horiz.Start, sk.OriginPoint], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([horiz], ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add([vert],  ADSketchConstraintType.AD_CONSTRAINT_VERTICAL)
        add([arc.Start, horiz.End],  ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([arc.End,   vert.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([arc, horiz], ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([arc, vert],  ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        sk.Dimensions.PlaceLinearDimension(horiz, 5.0)
        sk.Dimensions.PlaceLinearDimension(vert,  3.0)
        sk.Dimensions.PlaceRadialDimension(arc,   RADIUS)
    finally:
        sk.EndChange()

    print(f"horiz: start=({horiz.Start.X:.4f}, {horiz.Start.Y:.4f})  "
          f"end=({horiz.End.X:.4f}, {horiz.End.Y:.4f})")
    print(f"vert : start=({vert.Start.X:.4f}, {vert.Start.Y:.4f})  "
          f"end=({vert.End.X:.4f}, {vert.End.Y:.4f})")
    print(f"arc  : start=({arc.Start.X:.4f}, {arc.Start.Y:.4f})  "
          f"end=({arc.End.X:.4f}, {arc.End.Y:.4f})  r={arc.Radius:.4f}")

    d_h = _point_line_distance(arc.Center.X, arc.Center.Y,
                               horiz.Start.X, horiz.Start.Y,
                               horiz.End.X,   horiz.End.Y)
    d_v = _point_line_distance(arc.Center.X, arc.Center.Y,
                               vert.Start.X, vert.Start.Y,
                               vert.End.X,   vert.End.Y)
    print(f"distances: horiz={d_h:.4f}, vert={d_v:.4f}, radius={arc.Radius:.4f}")

    return report([
        ("arc tangent to horiz",       math.isclose(d_h, arc.Radius, abs_tol=1e-3)),
        ("arc tangent to vert",        math.isclose(d_v, arc.Radius, abs_tol=1e-3)),
        ("radius matches dim",         math.isclose(arc.Radius, RADIUS, abs_tol=1e-3)),
        ("horiz.End == arc.Start (X)", math.isclose(horiz.End.X, arc.Start.X, abs_tol=1e-3)),
        ("horiz.End == arc.Start (Y)", math.isclose(horiz.End.Y, arc.Start.Y, abs_tol=1e-3)),
        ("arc.End == vert.Start (X)",  math.isclose(arc.End.X, vert.Start.X, abs_tol=1e-3)),
        ("arc.End == vert.Start (Y)",  math.isclose(arc.End.Y, vert.Start.Y, abs_tol=1e-3)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
