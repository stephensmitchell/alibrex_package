"""Example 23 - build a 3D sketch (free-space curves).

3D sketches live in part-world coordinates, not on a 2D plane. Useful as
sweep paths and for laying out reference geometry that does not belong to
any single plane.

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
    # AlibreX 29 requires BeginChange/EndChange around figure additions -
    # 3D sketches included.
    sketch.BeginChange()
    try:
        figs = sketch.Figures

        # Plain points + free line
        figs.AddPoint(0.0, 0.0, 0.0)
        figs.AddPoint(0.0, 0.0, 3.0)
        figs.AddLine(0.0, 0.0, 0.0, 4.0, 0.0, 0.0)

        # Circular arc in the XY-Z=2 plane (using scalar overload)
        figs.AddCircularArcByCenterStartEnd(
            0.0, 0.0, 2.0,     # center
            1.0, 0.0, 2.0,     # start
            0.0, 1.0, 2.0,     # end (90 degrees)
        )

        # Polyline through 4 points - flat [x0,y0,z0,x1,y1,z1,...]
        poly_pts = float_array([
            4.0, 0.0, 0.0,
            4.0, 2.0, 0.0,
            4.0, 2.0, 3.0,
            6.0, 2.0, 3.0,
        ])
        # AddPolyline takes a `ref Array`, so the proxy returns (collector, modified_array)
        poly_result = figs.AddPolyline(poly_pts)
        poly = poly_result[0] if isinstance(poly_result, tuple) else poly_result
        print(f"AddPolyline produced {poly.Count} line segments.")

        # 3D B-spline through interpolation points
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
