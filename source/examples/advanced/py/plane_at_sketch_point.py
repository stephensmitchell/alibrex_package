"""Port of "Plane at Sketch Point" AlibreScript example.

Builds a 50 x 50 x 10 mm block, then creates a reference plane that's
parallel to XY and passes through the top centre of the block.

Differences from the original:
  * AlibreScript's ``GetFace("Face<5>")`` + 2D->global conversion is
    replaced by computing the world position directly (the top face of
    a +Z extrusion is at z = block_depth).
  * AlibreScript's ``AddPlane(name, normal_vec, origin_pt)`` (general
    "plane from a normal and a point") is rebuilt here as an offset
    plane parallel to XY at z = block_depth, which is what the original
    wanted given a normal of [0, 0, 1].
"""
from __future__ import annotations

import sys

from alibrex import run_example
from _porting_utils import (
    extrude_boss,
    mm,
    part_or_open,
    sketch_rectangle,
    xy_plane,
)

def main() -> int:
    part = part_or_open("PlaneAtPointPart")

    base = sketch_rectangle(part, xy_plane(part), "BaseSketch", 0.0, 0.0, mm(50), mm(50))
    extrude_boss(part, base, mm(10), "BaseExtrusion")

    plane_at_point = part.DesignPlanes.CreateAtOffsetToPlane(
        None, xy_plane(part), mm(10), "PlaneAtPoint",
    )
    print(f"Created plane '{plane_at_point.Name}' parallel to XY at z = 10 mm.")
    print(f"Total design planes on '{part.Name}': {part.DesignPlanes.Count}")
    return 0

if __name__ == "__main__":
    sys.exit(run_example(main))
