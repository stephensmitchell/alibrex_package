"""CRUD demo 11: equal-distance edge chamfer on the top 4 edges of a box.

Pipeline: block (6 x 4 x 2) -> chamfer the 4 highest-Z edges by 0.3 cm.

A chamfered top yields a box with 10 faces total (6 originals + 4 new
chamfer faces). Each chamfer replaces 1 edge with 3 edges (the chamfer
boundary curves), so edge count grows.

Verifies:
  - 2 features (boss + chamfer).
  - 1 body, 10 faces, edge count grew.
  - STL exports > 1 KB.
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report, stl_size
from alibrex import (
    ADEdgeChamferType,
    connect,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CHAMFER = 0.3


def main() -> int:
    root = connect()
    part = fresh_part(f"CRUD11_Chamfer_{uuid.uuid4().hex[:6]}")

    extrude_block(part, 6.0, 4.0, 2.0, "Block")
    edges_before = part.Bodies.Item(0).Edges.Count

    # Don't cache body: S2 in KNOWN_ISSUES.md (body proxies go stale).
    edges = part.Bodies.Item(0).Edges
    scored = []
    for i in range(edges.Count):
        e = edges.Item(i)
        z = 0.5 * (e.StartVertex.Point.Z + e.EndVertex.Point.Z)
        scored.append((z, e))
    scored.sort(key=lambda t: t[0], reverse=True)

    edges_col = root.NewObjectCollector()
    for _, e in scored[:4]:
        edges_col.Add(e)

    part.Features.AddEdgeChamferFeature(
        edges_col,
        ADEdgeChamferType.AD_EQUAL_DISTANCE,
        CHAMFER, CHAMFER, 0.0,
        True,
        "", "", "",
        "TopChamfer",
    )

    fc = part.FeatureCount
    bodies = part.Bodies.Count
    faces_after = part.Bodies.Item(0).Faces.Count
    edges_after = part.Bodies.Item(0).Edges.Count
    size = stl_size(part, os.path.join(HERE, f"crud_11_{part.Name}"))

    print(f"Features : {fc}     (expect 2)")
    print(f"Bodies   : {bodies} (expect 1)")
    print(f"Faces    : {faces_after}  (expect 10)")
    print(f"Edges    : {edges_before} -> {edges_after}  (expect growth)")
    print(f"STL bytes: {size:,}")

    return report([
        ("2 features",      fc == 2),
        ("single body",     bodies == 1),
        ("10 faces",        faces_after == 10),
        ("edge count grew", edges_after > edges_before),
        ("STL >= 1 KB",     size >= 1024),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
