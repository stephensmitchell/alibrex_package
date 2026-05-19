"""Example 22 — exercise the full 2D sketch-figure surface.

Creates one sketch per primitive family so each `IADSketchFigures.Add*`
method gets a smoke test. No extrude — open the part and inspect the
sketches visually. All coordinates are in centimeters.

Covers: AddSketchPoint, AddLine, AddRectangle, AddCircle,
AddCircularArcByCenterStartAngle, AddCircularArcByCenterStartEnd,
AddCircularArcBy3Points, AddEllipse, AddEllipseBy3Points,
AddEllipticArc, AddBsplineByInterpolation.
"""
from __future__ import annotations

import math
import sys

from alibrex import IADPartSession, connect, run_example, float_array


def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("Sketch2D_Smoke", False)
    xy = part.DesignPlanes.Item(0)

    # --- Points + line + rectangle
    sk1 = part.Sketches.AddSketch(None, xy, "Points_Lines_Rect")
    sk1.BeginChange()
    try:
        sk1.Figures.AddSketchPoint(0.0, 0.0)
        sk1.Figures.AddSketchPoint(1.0, 0.0)
        sk1.Figures.AddLine(0.0, 0.5, 3.0, 0.5)
        rect_lines = sk1.Figures.AddRectangle(2.0, 1.0, 5.0, 2.5)
    finally:
        sk1.EndChange()
    print(f"AddRectangle returned a collector with {rect_lines.Count} segments.")

    # --- Circles + three arc constructors
    sk2 = part.Sketches.AddSketch(None, xy, "Circles_Arcs")
    sk2.BeginChange()
    try:
        sk2.Figures.AddCircle(0.0, 0.0, 1.0)
        sk2.Figures.AddCircle(3.0, 0.0, 0.6)
        # arc by center + start + angle (radians? right-hand rule)
        sk2.Figures.AddCircularArcByCenterStartAngle(
            6.0, 0.0,    # center
            7.0, 0.0,    # start
            math.pi,     # +180 degrees
        )
        sk2.Figures.AddCircularArcByCenterStartEnd(
            0.0, -3.0, 1.0, -3.0, 0.0, -2.0,
        )
        sk2.Figures.AddCircularArcBy3Points(
            3.0, -3.0, 4.0, -3.0, 3.0, -2.0,
        )
    finally:
        sk2.EndChange()

    # --- Ellipses + elliptic arc
    sk3 = part.Sketches.AddSketch(None, xy, "Ellipses")
    sk3.BeginChange()
    try:
        sk3.Figures.AddEllipse(
            0.0, 0.0,
            2.0,           # major axis length
            0.5,           # minor / major ratio
            0.0,           # rotation
        )
        sk3.Figures.AddEllipseBy3Points(
            5.0, 0.0,
            7.0, 0.0,      # major axis end
            5.0, 0.7,      # minor axis end
        )
        sk3.Figures.AddEllipticArc(
            0.0, -4.0,
            1.5,
            0.6,
            1.5, -4.0,     # start
            0.0, -2.8,     # end
            0.0,
        )
    finally:
        sk3.EndChange()

    # --- B-spline through interpolation points (flat [x0,y0,x1,y1,...] array)
    sk4 = part.Sketches.AddSketch(None, xy, "Spline")
    pts = float_array([
        0.0, 0.0,
        1.0, 1.5,
        2.5, 0.5,
        4.0, 2.0,
        5.5, 0.0,
    ])
    sk4.BeginChange()
    try:
        sk4.Figures.AddBsplineByInterpolation(pts)
    finally:
        sk4.EndChange()

    print(f"Part '{part.Name}' now has {part.Sketches.Count} sketches.")


if __name__ == "__main__":
    sys.exit(run_example(main))
