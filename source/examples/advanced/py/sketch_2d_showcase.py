"""Port of "2D Sketch Showcase" AlibreScript example.

One 2D sketch on XY plane with every shape alibrex supports: lines,
rectangle, circle, arc by center-start-end, ellipse, elliptic arc,
polygon (drawn as N inscribed line segments), polyline, B-spline.

alibrex has no direct equivalent of AlibreScript's ``AddPolygon``, so
this draws an N-sided polygon as line segments inscribed in the diameter.
"""
from __future__ import annotations

import math
import sys

from alibrex import connect, float_array, run_example
from _porting_utils import mm, new_part, xy_plane

def main() -> None:
    part = new_part("Sketch2DShowcase")
    sk = part.Sketches.AddSketch(None, xy_plane(part), "MultiShapeSketch")

    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0,    0.0,   mm(30), 0.0)
        sk.Figures.AddLine(mm(30), 0.0,   mm(30), mm(10))
        sk.Figures.AddLine(mm(30), mm(10), 0.0,   mm(10))
        sk.Figures.AddLine(0.0,    mm(10), 0.0,   0.0)
        sk.Figures.AddRectangle(mm(35), 0.0, mm(45), mm(5))

        sk.Figures.AddCircle(mm(70), mm(5), mm(5))

        sk.Figures.AddCircularArcByCenterStartEnd(
            mm(95), mm(5),
            mm(90), mm(5),
            mm(95), mm(10),
        )

        sk.Figures.AddEllipse(mm(120), mm(5), mm(10), 0.5, 0.0)

        sk.Figures.AddEllipticArc(
            mm(150), mm(5),
            mm(10),  0.5,
            mm(140), mm(5),
            mm(150), mm(10),
            0.0,
        )

        cx, cy, r, sides = mm(180), mm(5), mm(7.5), 6
        prev = (cx + r, cy)
        for i in range(1, sides + 1):
            a = 2 * math.pi * i / sides
            cur = (cx + r * math.cos(a), cy + r * math.sin(a))
            sk.Figures.AddLine(prev[0], prev[1], cur[0], cur[1])
            prev = cur

        poly_pts = [
            (0.0,    mm(30)),
            (mm(10), mm(40)),
            (mm(20), mm(30)),
            (mm(30), mm(40)),
            (mm(40), mm(30)),
        ]
        for (x1, y1), (x2, y2) in zip(poly_pts, poly_pts[1:]):
            sk.Figures.AddLine(x1, y1, x2, y2)

        spline_pts = float_array([
            0.0,    mm(50),
            mm(10), mm(60),
            mm(20), mm(55),
            mm(30), mm(65),
        ])
        sk.Figures.AddBsplineByInterpolation(spline_pts)
    finally:
        sk.EndChange()

    print(f"2D sketch '{sk.Name}' contains {sk.Figures.Count} figures.")

if __name__ == "__main__":
    sys.exit(run_example(main))
