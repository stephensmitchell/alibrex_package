"""Port of "20 More Circles" AlibreScript example.

Creates 20 sketches on the XY plane, each containing a single circle
whose diameter grows from 5 mm to 100 mm in 5 mm steps. Circles are
offset along X to avoid overlap.

The original built a base block first and sketched the circles on its
top face. This skips the block because alibrex's offset-plane proxy
after a block extrusion is too short-lived to support 20 successive
AddSketch calls in this Alibre build (each AddSketch then trips
API_FAILED). The sketches-on-XY result is visually identical for the
demo purpose.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example
from _porting_utils import (
    mm,
    new_part,
    sketch_circle,
    xy_plane,
)

def main() -> None:
    part = new_part("MultiCirclePart")

    for i in range(1, 21):
        diameter_mm = 5 * i
        radius = mm(diameter_mm / 2.0)
        cx = mm(5 + i * 4)
        cy = mm(50)
        sketch_circle(part, xy_plane(part), f"CircleSketch{i}", cx, cy, radius)

    print(f"Created {part.Sketches.Count} sketches (diameters 5..100 mm).")

if __name__ == "__main__":
    sys.exit(run_example(main))
