"""Port of AlibreScript ``Helical-spring.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/helical-spring
(same body as ``Everyone-Loves-a-Slinky.py`` on the help site)

Uses tkinter for inputs.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from alibrex import connect, run_example
from alibrex.dialogs import InputType, options_dialog
from alibrex import float_array


def main() -> None:
    values = options_dialog(
        "Helical spring",
        [
            ["Angle Increment",         InputType.Real,    0.05],
            ["Loop Scale",              InputType.Real,    0.8],
            ["Height Scale",            InputType.Real,    1.0],
            ["Major Helix Width Scale", InputType.Real,    2.0],
            ["Turn Density",            InputType.Integer, 25],
        ],
    )
    if values is None:
        sys.exit("User cancelled")
    angle_inc, loop_scale, height_scale, width_scale, turn_density = values

    points: list[float] = []
    angle = 0.0
    for _ in range(437):
        x = (width_scale + loop_scale * math.cos(angle * turn_density)) * math.cos(angle)
        y = (width_scale + loop_scale * math.cos(angle * turn_density)) * math.sin(angle)
        z = height_scale * angle + loop_scale * math.sin(angle * turn_density)
        points.extend([x, y, z])
        angle += angle_inc

    root = connect()
    part = root.CreateEmptyPart("Helical spring", False)
    path = part.Sketches3D.Add3DSketch("Path")
    path.Figures.AddBsplineByInterpolation(float_array(points))


if __name__ == "__main__":
    sys.exit(run_example(main))
