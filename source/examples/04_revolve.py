"""Example 04: revolve a profile to make a cylindrical part.

Sketches a rectangular profile, then revolves it 360° around the Y axis
to create a cylinder.
"""
from __future__ import annotations

import math
import sys

from alibrex import connect, run_example
def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Cylinder_Demo", False)

    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Profile")

    radius = 1.5
    height = 4.0
    sketch.BeginChange()
    try:
        figs = sketch.Figures
        figs.AddLine(0.0,    0.0, radius, 0.0)
        figs.AddLine(radius, 0.0, radius, height)
        figs.AddLine(radius, height, 0.0, height)
        figs.AddLine(0.0,    height, 0.0, 0.0)
    finally:
        sketch.EndChange()

    y_axis = part.DesignAxes.Item(1)

    feat = part.Features.AddRevolvedBoss(
        sketch,
        None,
        y_axis,
        math.radians(360.0),
        "Cylinder",
    )
    print(f"Revolved feature created: {feat.Name}")

if __name__ == "__main__":
    sys.exit(run_example(main))
