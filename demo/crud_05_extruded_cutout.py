"""CRUD demo 05: extruded boss + extruded cutout, verify body topology.

Pipeline: block (60 x 40 x 20) -> cut a 20 x 20 hole through the top.

Verifies:
  - Feature count = 2 after both operations.
  - Body count stays 1 (cutout subtracts from existing body, doesn't add).
  - Face count = 10 (6 original + 4 inside walls of the hole).
  - STL exports > 1 KB.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report, sketch_rectangle, stl_size
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    part = fresh_part(f"CRUD05_Cutout_{uuid.uuid4().hex[:6]}")

    extrude_block(part, 6.0, 4.0, 2.0, "Base")
    fc_after_boss = part.FeatureCount

    # Cut a 2x2 square hole through the top: sketch lives on top face's plane (XY+depth).
    # Easiest: sketch on the top design plane offset upwards isn't necessary; sketch on XY
    # then cut downward via reversed normal. Simpler: cut from XY through full block depth.
    xy = part.DesignPlanes.Item(0)
    cut_sk = sketch_rectangle(part, xy, "CutSketch", 2.0, 2.0, x0=2.0, y0=1.0)
    part.Features.AddExtrudedCutout(
        cut_sk,
        2.0,                                       # depth (cuts through block)
        ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL,
        None, None, False,
        None, False,
        "Cutout", "CutDepth", "",
    )
    fc_after_cut = part.FeatureCount

    bodies = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    size = stl_size(part, os.path.join(HERE, f"crud_05_{part.Name}"))

    print(f"Features      : {fc_after_boss} after boss, {fc_after_cut} after cutout")
    print(f"Bodies        : {bodies}")
    print(f"Faces         : {faces}  (expect 10)")
    print(f"STL bytes     : {size:,}")

    return report([
        ("boss added",       fc_after_boss == 1),
        ("cutout added",     fc_after_cut  == 2),
        ("single body",      bodies == 1),
        ("10 faces",         faces == 10),
        ("STL >= 1 KB",      size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
