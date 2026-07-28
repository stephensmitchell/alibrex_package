"""Port of "Cylinder Shared Edge" AlibreScript example.

Given two faces on the active part, finds the edge they share by
matching the (X, Y, Z) coordinates of each edge's vertices. If no part
is open or the active part has no body, the script builds a small
revolved cylinder so it always has shareable face pairs to inspect.

Differences from the original:
  * AlibreScript's ``GetFace("Face<1>")`` is replaced by index access on
    ``part.Bodies.Item(0).Faces``.
  * The example pairs the first two faces by default. Pass
    ``--faces I J`` to choose other indices.
"""
from __future__ import annotations

import argparse
import sys

from alibrex import IADFace, run_example
from _porting_utils import mm, part_or_open, sketch_rectangle, xy_plane

def _seed_demo_cylinder(part) -> None:
    """Sketch a profile + revolve it 360° to give the part a real body."""
    import math
    profile = sketch_rectangle(part, xy_plane(part), "Profile", 0.0, 0.0, mm(15), mm(40))
    y_axis = part.DesignAxes.Item(1)
    part.Features.AddRevolvedBoss(profile, None, y_axis, math.radians(360.0), "DemoCylinder")

def shared_edge(face_a: IADFace, face_b: IADFace):
    """Return the edge shared by face_a and face_b, or None."""
    edges_a = face_a.Edges
    edges_b = face_b.Edges
    for i in range(edges_a.Count):
        ea = edges_a.Item(i)
        va = {(ea.StartVertex.Point.X, ea.StartVertex.Point.Y, ea.StartVertex.Point.Z),
              (ea.EndVertex.Point.X,   ea.EndVertex.Point.Y,   ea.EndVertex.Point.Z)}
        for j in range(edges_b.Count):
            eb = edges_b.Item(j)
            vb = {(eb.StartVertex.Point.X, eb.StartVertex.Point.Y, eb.StartVertex.Point.Z),
                  (eb.EndVertex.Point.X,   eb.EndVertex.Point.Y,   eb.EndVertex.Point.Z)}
            if va == vb:
                return ea
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--faces", type=int, nargs=2, default=[0, 1],
                        help="Two face indices on body 0 (default: 0 1)")
    args = parser.parse_args()

    part = part_or_open("SharedEdgeDemo")
    if part.Bodies.Count == 0:
        _seed_demo_cylinder(part)

    faces = part.Bodies.Item(0).Faces
    i, j = args.faces
    if not (0 <= i < faces.Count and 0 <= j < faces.Count):
        print(f"Face indices {i}, {j} out of range (have {faces.Count} face(s)).")
        return 1

    fa = faces.Item(i)
    fb = faces.Item(j)
    edge = shared_edge(fa, fb)
    if edge is None:
        print(f"No shared edge between face {i} and face {j}.")
    else:
        sv = edge.StartVertex.Point
        ev = edge.EndVertex.Point
        print(f"Shared edge between face {i} and face {j}:")
        print(f"  start: ({sv.X:.4f}, {sv.Y:.4f}, {sv.Z:.4f})")
        print(f"  end:   ({ev.X:.4f}, {ev.Y:.4f}, {ev.Z:.4f})")
    return 0

if __name__ == "__main__":
    sys.exit(run_example(main))
