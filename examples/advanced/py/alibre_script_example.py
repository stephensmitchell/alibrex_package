"""Port of "Alibre Script Example": the canonical AlibreScript starter.

Creates a 50 x 20 x 10 mm base block then cuts a Ø10 mm hole at (25, 10).

Differences from the original:
  * AlibreScript's ``GetFace("Face<3>")`` is replaced by a through-all
    cut from the XY plane with reversed=True (drills up into the block).
  * Diameters become radii (alibrex.AddCircle takes radius).
  * Distances are in centimetres.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example
from _porting_utils import (
    extrude_boss,
    extrude_cut_through,
    mm,
    new_part,
    sketch_circle,
    sketch_rectangle,
    xy_plane,
)


def main() -> None:
    part = new_part("Example Part")

    base = sketch_rectangle(part, xy_plane(part), "Sketch1", 0.0, 0.0, mm(50), mm(20))
    extrude_boss(part, base, mm(10), "Base-Block")

    hole_sk = sketch_circle(part, xy_plane(part), "HoleSketch", mm(25), mm(10), mm(5))
    extrude_cut_through(part, hole_sk, "HoleCut", reversed_=True)

    print(f"Created '{part.Name}' with one base extrusion and one through-hole.")


if __name__ == "__main__":
    sys.exit(run_example(main))
