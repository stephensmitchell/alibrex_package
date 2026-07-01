"""CRUD demo 12: drill a through-all hole in a block, verify topology.

Pipeline: block (6 x 4 x 2) -> sketch a single point on XY -> drill a
0.5 cm-diameter through-all hole at that point.

A through-hole in a box adds 1 cylindrical inner face and 2 circular
edges (top + bottom rims of the hole). So expected: 7 faces, 14 edges.

Verifies:
  - 2 features (boss + hole).
  - 1 body, 7 faces, 14 edges.
  - STL exports > 1 KB.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report, stl_size
from alibrex import (
    ADHoleDepthCondition,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    part = fresh_part(f"CRUD12_Hole_{uuid.uuid4().hex[:6]}")

    extrude_block(part, 6.0, 4.0, 2.0, "Block")

    xy = part.DesignPlanes.Item(0)
    pt_sk = part.Sketches.AddSketch(None, xy, "HoleCenter")
    pt_sk.BeginChange()
    try:
        pt_sk.Figures.AddSketchPoint(3.0, 2.0)  # center of the top face
    finally:
        pt_sk.EndChange()

    # The hole sketch sits on XY (z=0) which is the *bottom* of the +Z-extruded
    # block. The default direction (reversed=False) drills -Z, away from the
    # block. Pass reversed=True so the bore goes into the part.
    part.Features.AddSimpleHole(
        pt_sk,
        0.0,                                       # depth (ignored for through-all)
        0.5,                                       # diameter
        True,                                      # reversed -> drill +Z into the block
        None,
        ADHoleDepthCondition.AD_HOLE_THROUGH_ALL,
        None, None, 0.0,
        "ThroughHole",
        "",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    edges = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_12_{part.Name}"))

    print(f"Features : {fc}     (expect 2)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces}  (expect 7 - 6 box + 1 hole)")
    print(f"Edges    : {edges}  (expect 14 - 12 box + 2 hole rims)")
    print(f"STL bytes: {size:,}")

    return report([
        ("2 features",   fc == 2),
        ("single body",  bodies == 1),
        ("7 faces",      faces == 7),
        ("14 edges",     edges == 14),
        ("STL >= 1 KB",  size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
