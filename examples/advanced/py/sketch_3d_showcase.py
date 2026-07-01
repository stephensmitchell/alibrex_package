"""Port of "3D Sketch Showcase" AlibreScript example.

Creates one 3D sketch and adds every kind of 3D figure alibrex supports:
lines, an arc, a B-spline through points, a polyline (multiple line
segments), and a single point.
"""
from __future__ import annotations

import sys

from alibrex import connect, float_array, run_example
from _porting_utils import mm, new_part


def main() -> None:
    part = new_part("3DSketchShowcase")
    sk = part.Sketches3D.Add3DSketch("My3DSketch")

    sk.BeginChange()
    try:
        # A) Lines: single line from (0,0,0) to (10,0,5) mm.
        sk.Figures.AddLine(0.0, 0.0, 0.0, mm(10), 0.0, mm(5))

        # B) Arc by center-start-end:
        #    center (15,0,0), start (10,0,5), end (15,5,5).
        sk.Figures.AddCircularArcByCenterStartEnd(
            mm(15), 0.0,    mm(0),
            mm(10), 0.0,    mm(5),
            mm(15), mm(5),  mm(5),
        )

        # C) B-spline through 4 interpolation points: a 3D wave.
        bspline_pts = float_array([
            0.0,     mm(10),  0.0,
            mm(5),   mm(15),  mm(5),
            mm(10),  mm(15),  0.0,
            mm(15),  mm(20),  mm(10),
        ])
        sk.Figures.AddBsplineByInterpolation(bspline_pts)

        # D) Polyline: zig-zag from 4 corner points.
        poly_pts = float_array([
            mm(20),  0.0,     0.0,
            mm(25),  mm(5),   mm(5),
            mm(30),  0.0,     mm(10),
            mm(35),  mm(5),   mm(15),
        ])
        sk.Figures.AddPolyline(poly_pts)

        # E) Single reference point at (25,10,5).
        sk.Figures.AddPoint(mm(25), mm(10), mm(5))
    finally:
        sk.EndChange()

    print(f"3D sketch '{sk.Name}' contains {sk.Figures.Count} figures.")


if __name__ == "__main__":
    sys.exit(run_example(main))
