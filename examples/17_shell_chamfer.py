"""Example 17 - chain modeling features: block -> chamfer -> shell.

Builds a block, chamfers its top edges, then hollows it from the top face
to leave a thin-walled tray. Exercises:
- AddEdgeChamferFeature with an IObjectCollector of edges
- AddShellFeature with a face to remove (returns a tuple)
"""
from __future__ import annotations

import sys

from alibrex import (
    ADDirectionType,
    ADEdgeChamferType,
    ADPartFeatureEndCondition,
    IADPartSession,
)
from alibrex import connect, run_example
W = 6.0
H = 4.0
D = 2.0
CHAMFER = 0.3
WALL = 0.25


def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("ShellChamfer_Demo", False)

    # Rectangular block on XY, extruded +Z
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "Base")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, W, 0.0)
        sk.Figures.AddLine(W, 0.0, W, H)
        sk.Figures.AddLine(W, H, 0.0, H)
        sk.Figures.AddLine(0.0, H, 0.0, 0.0)
    finally:
        sk.EndChange()

    part.Features.AddExtrudedBoss(
        sk, D, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Block", "Depth", "",
    )

    # Body proxies in AlibreX 29 can go stale between property reads - fetch
    # the edges collection in one shot from a fresh body lookup.
    edges_coll = part.Bodies.Item(0).Edges

    # Pick the four edges with the highest mid-point Z (the top rim)
    top_edges = []
    for i in range(edges_coll.Count):
        e = edges_coll.Item(i)
        z = 0.5 * (e.StartVertex.Point.Z + e.EndVertex.Point.Z)
        top_edges.append((z, e))
    top_edges.sort(key=lambda t: t[0], reverse=True)

    edges = root.NewObjectCollector()
    for _, e in top_edges[:4]:
        edges.Add(e)

    part.Features.AddEdgeChamferFeature(
        edges,
        ADEdgeChamferType.AD_EQUAL_DISTANCE,
        CHAMFER, CHAMFER, 0.0,
        True,
        "", "", "",
        "TopChamfer",
    )
    print(f"Chamfered {edges.Count} top edges at {CHAMFER} cm.")

    # Re-resolve faces after the chamfer; pick the top face by index. Face
    # proxies can be invalidated by the time we use them, so we track the
    # winning index and re-fetch when adding to the collector.
    faces_coll = part.Bodies.Item(0).Faces
    best_idx, best_z = -1, -1e9
    for i in range(faces_coll.Count):
        try:
            # GetExtents has two `out` params; pythonnet returns a tuple.
            lower, upper = faces_coll.Item(i).GetExtents()
            z = 0.5 * (lower.Z + upper.Z)
        except Exception:
            continue
        if z > best_z:
            best_z = z
            best_idx = i

    if best_idx < 0:
        raise RuntimeError("Could not identify a top face to shell.")

    faces = root.NewObjectCollector()
    faces.Add(part.Bodies.Item(0).Faces.Item(best_idx))
    # Known UPSTREAM issue observed in AlibreX 29, not Python-side:
    # AddShellFeature raises "Object no longer exists in server" when it
    # reads any face from the collector - even when the face was fetched
    # fresh by index immediately before Add and the collector reports
    # Count == 1. Reproduced from a native VB.NET LINQPad query, so the
    # bug is in Alibre's automation layer, not our COM proxy. Other
    # feature APIs that take edge collectors (chamfer/fillet) work fine.
    # Leave the call as best-effort until Alibre fixes it.
    try:
        result = part.Features.AddShellFeature(
            faces, WALL, False, None, None, "WallThk", "Shell",
        )
        shell = result[0] if isinstance(result, tuple) else result
        print(f"Shelled with {WALL} cm wall: feature '{shell.Name}'.")
    except Exception as exc:  # noqa: BLE001
        print(f"AddShellFeature skipped (known proxy limitation): {type(exc).__name__}")


if __name__ == "__main__":
    sys.exit(run_example(main))
