"""CRUD demo 04: extrude a box, query topology, verify Euler counts.

For a solid rectangular box the topology is known exactly:
  - 1 body
  - 6 faces
  - 12 edges
  - 8 vertices

Creates a fresh part so the counts are predictable and no user document
is modified.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    run_example,
)

def main() -> int:
    part = fresh_part(f"CRUD04_Box_{uuid.uuid4().hex[:6]}")
    print(f"[info] Created demo part: {part.Name!r}.")

    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "CRUD04_Base")
    sk.BeginChange()
    try:
        figs = sk.Figures
        figs.AddLine(0.0, 0.0, 3.0, 0.0)
        figs.AddLine(3.0, 0.0, 3.0, 2.0)
        figs.AddLine(3.0, 2.0, 0.0, 2.0)
        figs.AddLine(0.0, 2.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 1.0, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "CRUD04_Box", "CRUD04_Depth", "",
    )

    bodies_count = part.Bodies.Count
    faces = part.Bodies.Item(0).Faces.Count
    edges = part.Bodies.Item(0).Edges.Count
    try:
        verts = part.Bodies.Item(0).Vertices.Count   # type: ignore[attr-defined]
        vertex_source = "Body.Vertices"
    except AttributeError:
        verts = 2 + edges - faces
        vertex_source = "Euler V=2+E-F"

    print(f"Bodies   : {bodies_count}  (expect 1)")
    print(f"Faces    : {faces}              (expect 6)")
    print(f"Edges    : {edges}              (expect 12)")
    print(f"Vertices : {verts}              (expect 8)  [{vertex_source}]")

    return report([
        ("1 body",     bodies_count == 1),
        ("6 faces",    faces == 6),
        ("12 edges",   edges == 12),
        ("8 vertices", verts == 8),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
