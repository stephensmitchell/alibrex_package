"""Port of AlibreScript ``Creating-a-3D-Sketch-with-a-Spline-and-an-Arc.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/creating-a-3d-sketch-with-a-spline-and-an-arc

Mixes a 3D B-spline and a 3D arc on the same 3D sketch. Original values
were in inches; converted to centimetres (×2.54).

AlibreScript note: ``AddArcCenterStartEnd`` is *clockwise*, achieved by
swapping start/end. AlibreX's
``AddCircularArcByCenterStartEnd(center, start, end)`` follows the same
shorter-arc convention, so the swap idiom carries over.
"""
from __future__ import annotations

import sys
from pathlib import Path
from alibrex import connect, run_example, float_array


IN = 2.54


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("My Part", False)
    path = part.Sketches3D.Add3DSketch("Path")

    spline_pts_in = [
        0.6, -0.6625,  0.0,
        0.6, -0.6625, -0.2175,
        0.6, -0.8125, -0.6795,
    ]
    path.Figures.AddBsplineByInterpolation(
        float_array(v * IN for v in spline_pts_in)
    )

    # Arc - original: clockwise by start/end swap
    path.Figures.AddCircularArcByCenterStartEnd(
        -5.6634 * IN, -3.92 * IN,   -0.6795 * IN,
         0.6    * IN, -7.0275 * IN, -0.6795 * IN,
         0.6    * IN, -0.8125 * IN, -0.6795 * IN,
    )
    print("Created 3D sketch with B-spline + arc.")


if __name__ == "__main__":
    sys.exit(run_example(main))
