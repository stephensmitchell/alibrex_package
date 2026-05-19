"""CRUD demo 06 — revolve a profile to make a cylinder, verify topology.

A solid cylinder has exactly 3 faces (top cap, bottom cap, lateral curved
surface) and 2 circular edges (top + bottom rims).

Verifies:
  - 1 feature, 1 body.
  - 3 faces, 2 edges.
  - STL exports > 1 KB.

Note: AlibreX 29's ``AddRevolvedBoss`` takes the revolve angle in
**radians**, not degrees. Passing ``360.0`` produces a "near-full" tube
(5 faces / 9 edges) — use ``math.radians(360)`` instead.
"""
from __future__ import annotations

import math
import os
import sys
import uuid

from _demo_utils import fresh_part, report, sketch_rectangle, stl_size
from alibrex import run_example

HERE = os.path.dirname(os.path.abspath(__file__))
RADIUS, HEIGHT = 1.5, 4.0


def main() -> int:
    part = fresh_part(f"CRUD06_Cylinder_{uuid.uuid4().hex[:6]}")

    xy = part.DesignPlanes.Item(0)
    profile = sketch_rectangle(part, xy, "Profile", RADIUS, HEIGHT)
    y_axis = part.DesignAxes.Item(1)

    part.Features.AddRevolvedBoss(
        profile,
        None,
        y_axis,
        math.radians(360.0),     # radians! 360.0 gives a tube.
        "Cylinder",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    edges = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_06_{part.Name}"))

    print(f"Features : {fc}     (expect 1)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces}  (expect 3 — top, bottom, side)")
    print(f"Edges    : {edges}  (expect 2 — top + bottom circles)")
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
