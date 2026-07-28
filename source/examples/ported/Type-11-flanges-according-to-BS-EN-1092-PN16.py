"""Port of AlibreScript ``Type-11-flanges-according-to-BS-EN-1092-PN16.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/type-11-flanges-according-to-bs-en-1092-pn16

Generates a BS/EN-1092 PN16 Type-11 flange by revolving a polyline and
cutting bolt holes around a bolt circle. Same simplifications as the
hollow-profile ports: explicit polyline (no ``Polyline()`` helper),
holes laid out around a circle directly without face-name lookup. Bolt-
hole cut depth is the flange thickness through-all rather than the
fragile face-based original.
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
from alibrex.dialogs import InputType, options_dialog
MM = 0.1

DN_DATA = {
    10:  [90, 14, 35, 6,  4, 17.2, 28, 40, 2, 60, 14, 4],
    15:  [95, 14, 35, 6,  4, 21.3, 32, 45, 2, 65, 14, 4],
    20:  [105, 14, 38, 6, 4, 26.9, 39, 58, 2, 75, 14, 4],
    25:  [115, 16, 38, 6, 4, 33.7, 46, 68, 2, 85, 14, 4],
    32:  [140, 16, 40, 6, 6, 42.4, 56, 78, 2, 100, 18, 4],
    40:  [150, 16, 42, 7, 6, 48.3, 64, 88, 2, 110, 18, 4],
    50:  [165, 18, 45, 8, 6, 60.3, 75, 102, 2, 125, 18, 4],
    65:  [185, 18, 45, 10, 6, 76.1, 90, 122, 2, 145, 18, 4],
    80:  [200, 20, 50, 10, 8, 88.9, 105, 138, 2, 160, 18, 8],
    100: [220, 20, 52, 12, 8, 114.3, 131, 158, 2, 180, 18, 8],
    150: [285, 22, 55, 12, 10, 168.3, 192, 212, 2, 240, 22, 8],
}

def main() -> None:
    sizes = sorted(DN_DATA)
    values = options_dialog(
        "Flange Generator (BS/EN-1092 PN16)",
        [
            ["DN Size", InputType.StringList, [f"DN{x}" for x in sizes], "DN50"],
        ],
    )
    if values is None:
        sys.exit("User cancelled")
    dn = sizes[values[0]]
    D, C2, H2, H3, R, A, N1, d1, f1, K, L, N = DN_DATA[dn]

    DN_v = dn * MM
    D_v, C2_v, H2_v, H3_v = D*MM, C2*MM, H2*MM, H3*MM
    A_v, N1_v, d1_v, f1_v, K_v, L_v = A*MM, N1*MM, d1*MM, f1*MM, K*MM, L*MM
    R_v = R * MM

    root = connect()
    part = root.CreateEmptyPart(f"DN{dn} Flange PN16", False)

    xy = part.DesignPlanes.Item(0)
    y_axis = part.DesignAxes.Item(1)
    profile = part.Sketches.AddSketch(None, xy, "Profile")
    pts = [
        (DN_v/2,  0.0),
        (d1_v/2,  0.0),
        (d1_v/2,  f1_v),
        (D_v/2,   f1_v),
        (D_v/2,   C2_v),
        (N1_v/2,  C2_v),
        (A_v/2,   H2_v - H3_v),
        (A_v/2,   H2_v),
        (DN_v/2,  H2_v),
        (DN_v/2,  0.0),
    ]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        profile.Figures.AddLine(x1, y1, x2, y2)
    part.Features.AddRevolvedBoss(profile, None, y_axis, math.radians(360.0), "Body")

    xz = part.DesignPlanes.Item(2)
    holes = part.Sketches.AddSketch(None, xz, "Holes")
    for i in range(N):
        ang = (360.0 / N) * i
        cx = math.sin(math.radians(ang)) * K_v / 2.0
        cy = math.cos(math.radians(ang)) * K_v / 2.0
        holes.Figures.AddCircle(cx, cy, L_v / 2.0)
    part.Features.AddExtrudedCutout(
        holes, C2_v, ADPartFeatureEndCondition.AD_THROUGH_ALL,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Flange Holes", "Depth", "",
    )
    print(f"Built DN{dn} PN16 Type-11 flange with {N} bolt holes.")

if __name__ == "__main__":
    sys.exit(run_example(main))
