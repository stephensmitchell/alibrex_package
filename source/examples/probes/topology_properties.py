"""Probe the BRep topology tree of the active part.

For each body, probe the body itself + a sample of faces, edges, and
vertices. Each face/edge gets its ``GetExtents`` bounding-box read so
the out-param marshalling pattern is exercised.
"""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_object

def main() -> None:
    root = connect()
    part = require_active_part(root)

    print(f"Bodies count: {part.Bodies.Count}")
    for bi in range(part.Bodies.Count):
        body = part.Bodies.Item(bi)
        probe_object(body, f"Body[{bi}]")

        print(f"\n  Body[{bi}].Faces.Count = {body.Faces.Count}")
        for fi in range(min(3, body.Faces.Count)):
            face = body.Faces.Item(fi)
            probe_object(face, f"Body[{bi}].Face[{fi}]")
            try:
                lo, hi = face.GetExtents()
                print(f"    GetExtents -> ({lo.X:.3f},{lo.Y:.3f},{lo.Z:.3f}) "
                      f"({hi.X:.3f},{hi.Y:.3f},{hi.Z:.3f})")
            except Exception as exc:  # noqa: BLE001
                print(f"    GetExtents -> <{type(exc).__name__}: {exc}>")

        print(f"\n  Body[{bi}].Edges.Count = {body.Edges.Count}")
        for ei in range(min(3, body.Edges.Count)):
            edge = body.Edges.Item(ei)
            probe_object(edge, f"Body[{bi}].Edge[{ei}]")
            try:
                p_start = edge.StartVertex.Point
                p_end = edge.EndVertex.Point
                print(f"    start=({p_start.X:.3f},{p_start.Y:.3f},{p_start.Z:.3f}) "
                      f"end=({p_end.X:.3f},{p_end.Y:.3f},{p_end.Z:.3f})")
            except Exception as exc:  # noqa: BLE001
                print(f"    vertex read failed: {exc}")

        print(f"\n  Body[{bi}].Vertices.Count = {body.Vertices.Count}")
        for vi in range(min(3, body.Vertices.Count)):
            v = body.Vertices.Item(vi)
            probe_object(v, f"Body[{bi}].Vertex[{vi}]")

if __name__ == "__main__":
    sys.exit(run_example(main))
