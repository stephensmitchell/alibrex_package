"""CRUD demo 08 - loft between two square sections, verify.

A frustum lofted from a 4cm square to a 1.5cm square has:
  - 6 faces (1 bottom, 1 top, 4 trapezoidal sides).
  - 12 edges (4 bottom, 4 top, 4 vertical).
  - 8 vertices.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import fresh_part, report, sketch_rectangle, stl_size
from alibrex import (
    ADLoftGuideType,
    connect,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    root = connect()
    part = fresh_part(f"CRUD08_Loft_{uuid.uuid4().hex[:6]}")

    xy = part.DesignPlanes.Item(0)
    top_plane = part.DesignPlanes.CreateAtOffsetToPlane(None, xy, 3.0, "TopPlane")

    base = sketch_rectangle(part, xy,        "Base", 4.0, 4.0, x0=-2.0, y0=-2.0)
    top  = sketch_rectangle(part, top_plane, "Top",  1.5, 1.5, x0=-0.75, y0=-0.75)

    sections = root.NewObjectCollector()
    sections.Add(base)
    sections.Add(top)

    part.Features.AddLoftBoss(
        sections,
        None, None, None,
        None,
        ADLoftGuideType.AD_NONE,
        False, False, False, False,
        "Loft",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    edges = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_08_{part.Name}"))

    print(f"Features : {fc}     (expect 1)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces}  (expect 6)")
    print(f"Edges    : {edges}  (expect 12)")
    print(f"STL bytes: {size:,}")

    return report([
        ("feature added", fc == 1),
        ("single body",   bodies == 1),
        ("6 faces",       faces == 6),
        ("12 edges",      edges == 12),
        ("STL >= 1 KB",   size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
