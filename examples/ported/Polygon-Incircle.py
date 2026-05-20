"""Port of AlibreScript ``Polygon-Incircle.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/polygon-incircle

Sketches a regular *n*-gon whose inscribed circle has the given diameter,
then extrudes it. AlibreScript has ``S.AddPolygon(cx,cy,d,n,False)`` -
AlibreX has no polygon helper, so we lay down *n* line segments
explicitly.
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
# 100 mm / 10 mm extrusion in the original; AlibreX expects cm.
INCIRCLE_DIAMETER_CM = 10.0
SIDES = 6
EXTRUDE_DEPTH_CM = 1.0


def add_polygon(sketch, cx: float, cy: float, exterior_dia: float, n: int) -> None:
    r = exterior_dia / 2.0
    pts = [
        (cx + r * math.cos(2 * math.pi * i / n),
         cy + r * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        sketch.Figures.AddLine(x1, y1, x2, y2)


def main() -> None:
    exterior = INCIRCLE_DIAMETER_CM / math.cos(math.pi / SIDES)

    root = connect()
    part = root.CreateEmptyPart("Hex", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Hexagon")
    add_polygon(sketch, 0.0, 0.0, exterior, SIDES)

    part.Features.AddExtrudedBoss(
        sketch, EXTRUDE_DEPTH_CM, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Hex Head", "Depth", "",
    )
    print(f"Created {SIDES}-gon with incircle diameter {INCIRCLE_DIAMETER_CM} cm.")


if __name__ == "__main__":
    sys.exit(run_example(main))
