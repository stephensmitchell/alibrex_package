"""CRUD demo 10 — constant-radius fillet on every edge of a box.

A box has 12 edges. Filleting all of them yields a body with:
  - more faces than the original (each edge becomes a curved face).
  - more edges than the original (each fillet introduces 2 boundary curves).

Verifies:
  - 2 features (boss + fillet).
  - 1 body, face count grew, edge count grew.
  - STL exports > 1 KB.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report, stl_size
from alibrex import connect, run_example

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    root = connect()
    part = fresh_part(f"CRUD10_Fillet_{uuid.uuid4().hex[:6]}")

    extrude_block(part, 4.0, 3.0, 2.0, "Block")
    faces_before = part.Bodies.Item(0).Faces.Count
    edges_before = part.Bodies.Item(0).Edges.Count

    # Don't cache body — S2 in KNOWN_ISSUES.md (body proxies go stale).
    edges = part.Bodies.Item(0).Edges
    edges_col = root.NewObjectCollector()
    for i in range(edges.Count):
        edges_col.Add(edges.Item(i))

    part.Features.AddConstantRadiusFilletFeature(
        edges_col,
        0.3,        # radius (cm)
        True,       # tangent-propagate
        "",
        "AllEdgeFillets",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces_after = part.Bodies.Item(0).Faces.Count
    edges_after = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_10_{part.Name}"))

    print(f"Features : {fc}     (expect 2)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces_before} -> {faces_after}  (expect growth)")
    print(f"Edges    : {edges_before} -> {edges_after}  (expect growth)")
    print(f"STL bytes: {size:,}")

    return report([
        ("2 features",      fc == 2),
        ("single body",     bodies == 1),
        ("face count grew", faces_after > faces_before),
        ("edge count grew", edges_after > edges_before),
        ("STL >= 1 KB",     size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
