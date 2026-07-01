"""Example 20: walk the BRep topology of the active part.

For each solid body: report Lumps/Shells/Faces/Edges/Vertices counts and
print the first few faces and edges with their underlying surface/curve
type. Useful for verifying that the typed stubs surface the inspection
API correctly.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example, require_active_part
def main() -> None:
    root = connect()
    part = require_active_part(root)

    n = part.Bodies.Count
    print(f"Part '{part.Name}' has {n} solid body(ies).")

    for bi in range(n):
        body = part.Bodies.Item(bi)
        print(f"\nBody[{bi}]  topology={body.TopologyType}")
        print(f"  Lumps={body.Lumps.Count}  Shells={body.Shells.Count}  "
              f"Faces={body.Faces.Count}  Edges={body.Edges.Count}  "
              f"Vertices={body.Vertices.Count}")

        # Sample up to 5 faces
        for fi in range(min(5, body.Faces.Count)):
            face = body.Faces.Item(fi)
            try:
                surf_kind = type(face.Geometry).__name__
                lower, upper = face.GetExtents()
                extents = (f"  bbox=({lower.X:.2f},{lower.Y:.2f},{lower.Z:.2f})"
                           f"->({upper.X:.2f},{upper.Y:.2f},{upper.Z:.2f})")
            except Exception as exc:
                surf_kind = f"<{type(exc).__name__}>"
                extents = ""
            print(f"  Face[{fi}]: surface={surf_kind}{extents}")

        # Sample up to 5 edges with endpoint coordinates
        for ei in range(min(5, body.Edges.Count)):
            edge = body.Edges.Item(ei)
            sv = edge.StartVertex.Point
            ev = edge.EndVertex.Point
            print(f"  Edge[{ei}]: ({sv.X:6.3f},{sv.Y:6.3f},{sv.Z:6.3f}) -> "
                  f"({ev.X:6.3f},{ev.Y:6.3f},{ev.Z:6.3f})")


if __name__ == "__main__":
    sys.exit(run_example(main))
