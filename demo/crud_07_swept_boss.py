"""CRUD demo 07: sweep a circular profile along a straight path.

A constant-section sweep along a straight line gives the same topology
as a cylinder: 3 faces (start cap, end cap, lateral surface), 2 edges.

Verifies:
  - 1 feature, 1 body.
  - 3 faces, 2 edges.
  - STL exports > 1 KB.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import fresh_part, report, sketch_circle, stl_size
from alibrex import (
    ADPartFeatureEndCondition,
    connect,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PATH_LEN, R = 4.0, 0.4


def main() -> int:
    root = connect()
    part = fresh_part(f"CRUD07_Sweep_{uuid.uuid4().hex[:6]}")

    xy = part.DesignPlanes.Item(0)
    yz = part.DesignPlanes.Item(1)

    # Path on XY: a line from origin in +X direction.
    path = part.Sketches.AddSketch(None, xy, "Path")
    path.BeginChange()
    try:
        path.Figures.AddLine(0.0, 0.0, PATH_LEN, 0.0)
    finally:
        path.EndChange()

    profile = sketch_circle(part, yz, "Profile", 0.0, 0.0, R)

    paths = root.NewObjectCollector()
    paths.Add(path)

    part.Features.AddSweptBoss(
        profile, paths,
        True,                                      # rigid profile
        ADPartFeatureEndCondition.AD_ENTIRE_PATH,  # sweep doesn't take depth
        None, None, 0.0,
        None, False,
        "Sweep",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    edges = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_07_{part.Name}"))

    print(f"Features : {fc}     (expect 1)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces}  (expect 3)")
    print(f"Edges    : {edges}  (expect 2)")
    print(f"STL bytes: {size:,}")

    return report([
        ("feature added", fc == 1),
        ("single body",   bodies == 1),
        ("3 faces",       faces == 3),
        ("2 edges",       edges == 2),
        ("STL >= 1 KB",   size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
