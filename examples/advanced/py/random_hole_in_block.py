"""Port of "Random Hole in block" AlibreScript example.

Builds a 40 x 20 x 10 mm block, then sketches a 4 mm-radius circle at a
random location on the XY plane (clamped to keep the hole fully inside
the block's footprint) and cuts it through-all.

Differences from the original:
  * `MyPart.GetFace("Face<5>")` doesn't have an alibrex equivalent; we
    sketch directly on the XY plane and use a through-all cut with
    reversed=True so the cut bores up into the block.
  * Lengths are in centimetres (mm / 10), matching alibrex's internal unit.
"""
from __future__ import annotations

import random
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

WIDTH = mm(40.0)
HEIGHT = mm(20.0)
DEPTH = mm(10.0)
HOLE_R = mm(4.0)


def main() -> None:
    part = new_part("RandomHoleBlock")

    rect = sketch_rectangle(part, xy_plane(part), "RectSketch", 0.0, 0.0, WIDTH, HEIGHT)
    extrude_boss(part, rect, DEPTH, "Block")

    # Random hole center, clamped so the disk stays inside the block footprint.
    cx = random.uniform(HOLE_R, WIDTH - HOLE_R)
    cy = random.uniform(HOLE_R, HEIGHT - HOLE_R)

    hole_sk = sketch_circle(part, xy_plane(part), "RandomHoleSketch", cx, cy, HOLE_R)
    # reversed_=True so the cut bores up into the block (XY is the bottom face).
    extrude_cut_through(part, hole_sk, "RandomHole", reversed_=True)

    print(f"Block 40x20x10 mm.  Hole at (x={cx*10:.2f} mm, y={cy*10:.2f} mm)  r={HOLE_R*10:.2f} mm")


if __name__ == "__main__":
    sys.exit(run_example(main))
