"""Example 23: build a 3D sketch (free-space curves).

3D sketches live in part-world coordinates, not on a 2D plane. Use them as
sweep paths and to lay out reference geometry that belongs to no single
plane.

Covers: IAD3DSketches.Add3DSketch, IAD3DSketchFigures.AddPoint, AddLine,
AddCircularArcByCenterStartEnd, AddPolyline, AddBsplineByInterpolation.
"""
from __future__ import annotations

import sys

from alibrex import IADPartSession, connect, run_example, float_array

def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("Sketch3D_Smoke", False)

    sketch = part.Sketches3D.Add3DSketch("FreeSpace")
    sketch.BeginChange()
    try:
        figs = sketch.Figures

        figs.AddPoint(0.0, 0.0, 0.0)
        figs.AddPoint(0.0, 0.0, 3.0)
        figs.AddLine(0.0, 0.0, 0.0, 4.0, 0.0, 0.0)

        figs.AddCircularArcByCenterStartEnd(
            0.0, 0.0, 2.0,
            1.0, 0.0, 2.0,
            0.0, 1.0, 2.0,
        )

        poly_pts = float_array([
            4.0, 0.0, 0.0,
            4.0, 2.0, 0.0,
            4.0, 2.0, 3.0,
            6.0, 2.0, 3.0,
        ])
        poly_result = figs.AddPolyline(poly_pts)
        poly = poly_result[0] if isinstance(poly_result, tuple) else poly_result
        print(f"AddPolyline produced {poly.Count} line segments.")

        spline_pts = float_array([
            0.0, -3.0, 0.0,
            2.0, -3.0, 1.0,
            4.0, -3.0, 3.0,
            6.0, -3.0, 1.5,
            8.0, -3.0, 0.0,
        ])
        figs.AddBsplineByInterpolation(spline_pts)
    finally:
        sketch.EndChange()

    print(f"Part '{part.Name}' has {part.Sketches3D.Count} 3D sketch(es), "
          f"{sketch.Figures.Count} figure(s) in '{sketch.Name}'.")

if __name__ == "__main__":
    sys.exit(run_example(main))
