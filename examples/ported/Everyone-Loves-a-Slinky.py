"""Port of AlibreScript ``Everyone-Loves-a-Slinky.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/everyone-loves-a-slinky

Generates the slinky helix as a 3D B-spline through 437 interpolation
points sampled from the original parametric formula. tkinter collects
the dialog inputs (see ``_dialogs.py``).
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
        "Everyone Loves a Slinky",
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

    print(f"Angle Increment        = {angle_inc:f}")
    print(f"Loop Scale             = {loop_scale:f}")
    print(f"Height Scale           = {height_scale:f}")
    print(f"Major Helix Width      = {width_scale:f}")
    print(f"Turn Density           = {turn_density:d}")

    points: list[float] = []
    angle = 0.0
    for _ in range(437):
        x = (width_scale + loop_scale * math.cos(angle * turn_density)) * math.cos(angle)
        y = (width_scale + loop_scale * math.cos(angle * turn_density)) * math.sin(angle)
        z = height_scale * angle + loop_scale * math.sin(angle * turn_density)
        points.extend([x, y, z])
        angle += angle_inc

    root = connect()
    part = root.CreateEmptyPart("Slinky", False)
    path = part.Sketches3D.Add3DSketch("Path")
    path.Figures.AddBsplineByInterpolation(float_array(points))
    print(f"Built 3D B-spline path with {len(points) // 3} interpolation points.")


if __name__ == "__main__":
    sys.exit(run_example(main))
