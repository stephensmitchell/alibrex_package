"""Port of AlibreScript ``Cap-Screw-ISO-4762-Bolts.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/cap-screw-iso-4762-bolts

ISO 4762 socket cap screw. The original used:

- ``S.AddPolyline(Polyline)``    → emit lines individually
- ``S.AddPolygon(cx,cy,d,n)``    → emit n lines around the circumscribed circle
- ``Screw.AddFillet(name, edge, r)`` by face/edge name → not portable; we
  fillet *all* edges of the hex hole bottom and tag the rim by Z position

The fillet step ends up applied to broader edge sets than the original
to avoid relying on ``GetEdge('Edge<n>')`` which has no AlibreX cousin.
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    ADHoleDepthCondition,
)
from alibrex import connect, run_example
DIAMETER_MM = 3.0
LENGTH_MM = 30.0
MM = 0.1

# ISO 4762 H, F, E, T, C
METRIC_DATA = {
    1.6:  [3.14, 2.0, 1.73, 0.7, 0.16],
    2.0:  [3.98, 2.6, 1.73, 1.0, 0.20],
    2.5:  [4.68, 3.1, 2.30, 1.1, 0.25],
    3.0:  [5.68, 3.6, 2.87, 1.3, 0.30],
    4.0:  [7.22, 4.7, 3.44, 2.0, 0.40],
    5.0:  [8.72, 5.7, 4.58, 2.5, 0.50],
    6.0:  [10.22, 6.8, 5.72, 3.0, 0.60],
    8.0:  [13.27, 9.2, 6.86, 4.0, 0.80],
    10.0: [16.27, 11.2, 9.15, 5.0, 1.0],
    12.0: [18.27, 13.7, 11.43, 6.0, 1.2],
}


def main() -> None:
    H, F, E, T, C = METRIC_DATA[DIAMETER_MM]
    cap_dia = H * MM
    hex_dia = E * MM
    hex_depth = T * MM
    rim_fillet = C * MM
    fillet_transition_dia = F * MM
    diam = DIAMETER_MM * MM
    length = LENGTH_MM * MM

    root = connect()
    part = root.CreateEmptyPart(f"Cap Screw M{int(DIAMETER_MM)}x{int(LENGTH_MM)}", False)

    # Revolved body around the X axis (XY plane → revolve about X)
    xy = part.DesignPlanes.Item(0)
    profile = part.Sketches.AddSketch(None, xy, "Profile")
    # Halfprofile (closed) — y is radial
    pts = [
        (0.0,          0.0),
        (0.0,          cap_dia / 2),
        (diam,         cap_dia / 2),
        (diam,         diam   / 2),
        (diam + length, diam  / 2),
        (diam + length, 0.0),
        (0.0,          0.0),
    ]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        profile.Figures.AddLine(x1, y1, x2, y2)

    x_axis = part.DesignAxes.Item(0)   # X axis is the first default axis
    # AlibreX 29 takes the revolve angle in RADIANS, not degrees.
    part.Features.AddRevolvedBoss(profile, None, x_axis, math.radians(360.0), "Body")

    # Hex socket cut on the top face (smallest-X face on body[0]).
    # Don't cache `body` — KNOWN_ISSUES.md S2. Track the winning index
    # and re-fetch the face when sketching. GetExtents has two out-params
    # in AlibreX 29 — pass None placeholders.
    faces = part.Bodies.Item(0).Faces
    cap_idx, best_x = -1, +1e9
    for i in range(faces.Count):
        try:
            lo, hi = faces.Item(i).GetExtents()
        except Exception:
            continue
        cx = (lo.X + hi.X) / 2.0
        if cx < best_x:
            best_x = cx
            cap_idx = i
    if cap_idx < 0:
        raise RuntimeError("Could not find cap face.")
    cap_face = part.Bodies.Item(0).Faces.Item(cap_idx)

    hex_sk = part.Sketches.AddSketch(None, cap_face, "Hole")
    # Hexagon around circle of diameter hex_dia
    ext = hex_dia / math.cos(math.pi / 6)
    r = ext / 2
    hex_pts = [(r*math.cos(2*math.pi*i/6), r*math.sin(2*math.pi*i/6)) for i in range(6)]
    for i in range(6):
        x1, y1 = hex_pts[i]
        x2, y2 = hex_pts[(i+1) % 6]
        hex_sk.Figures.AddLine(x1, y1, x2, y2)

    part.Features.AddExtrudedCutout(
        hex_sk, hex_depth + (fillet_transition_dia - diam) / 2.0,
        ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Hex Hole", "Depth", "",
    )

    # Rim fillet — apply to every edge whose midpoint X is near the cap
    # face. Re-fetch edges each iteration (S2).
    edges = part.Bodies.Item(0).Edges
    rim_edges = root.NewObjectCollector()
    for i in range(edges.Count):
        e = edges.Item(i)
        mx = 0.5 * (e.StartVertex.Point.X + e.EndVertex.Point.X)
        if abs(mx - best_x) < 1e-4:
            rim_edges.Add(e)
    if rim_edges.Count > 0:
        part.Features.AddConstantRadiusFilletFeature(
            rim_edges, rim_fillet, True, "RimRad", "Cap Rim",
        )
        print(f"Filleted {rim_edges.Count} rim edges at r={rim_fillet:.4f} cm.")

    print(f"Built M{int(DIAMETER_MM)}x{int(LENGTH_MM)} cap screw "
          f"(head Ø {cap_dia:.4f} cm, shaft Ø {diam:.4f} cm, "
          f"hex socket Ø {hex_dia:.4f} cm).")


if __name__ == "__main__":
    sys.exit(run_example(main))
