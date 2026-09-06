"""Port of AlibreScript ``Bolt-Creator.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/bolt-creator

The original used ``S.AddPolygon`` (no AlibreX equivalent) for the hex
recess. This port expands the hexagon into six explicit line segments.
The ``AddPlane(plane, offset)`` for the shoulder maps to
``DesignPlanes.CreateAtOffsetToPlane``.
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
MM = 0.1
HEAD_RADIUS  = 10.0 * MM
HEAD_HEIGHT  =  5.0 * MM
SHAFT_RADIUS =  5.0 * MM
SHAFT_LEN    = 20.0 * MM
HEX_INCIRCLE_DIAMETER = 5.0 * MM
HEX_DEPTH    =  3.0 * MM

def _hexagon(sketch, cx: float, cy: float, incircle_dia: float) -> None:
    exterior = incircle_dia / math.cos(math.pi / 6)
    r = exterior / 2.0
    pts = [(cx + r * math.cos(2*math.pi*i/6), cy + r * math.sin(2*math.pi*i/6))
           for i in range(6)]
    for i in range(6):
        x1, y1 = pts[i]
        x2, y2 = pts[(i+1) % 6]
        sketch.Figures.AddLine(x1, y1, x2, y2)

def _extrude(part, sketch, name: str, depth: float, is_cut: bool):
    fn = part.Features.AddExtrudedCutout if is_cut else part.Features.AddExtrudedBoss
    return fn(
        sketch, depth, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, name, "Depth", "",
    )

def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("My Part", False)

    xy = part.DesignPlanes.Item(0)
    head = part.Sketches.AddSketch(None, xy, "Head")
    head.Figures.AddCircle(0.0, 0.0, HEAD_RADIUS)
    _extrude(part, head, "Bolt Head", HEAD_HEIGHT, is_cut=False)

    head_bottom = part.DesignPlanes.CreateAtOffsetToPlane(
        None, xy, HEAD_HEIGHT, "Head Bottom",
    )
    shoulder = part.Sketches.AddSketch(None, head_bottom, "Shoulder")
    shoulder.Figures.AddCircle(0.0, 0.0, SHAFT_RADIUS)
    _extrude(part, shoulder, "Bolt Shoulder", SHAFT_LEN, is_cut=False)

    hex_sk = part.Sketches.AddSketch(None, xy, "Hex")
    _hexagon(hex_sk, 0.0, 0.0, HEX_INCIRCLE_DIAMETER)
    _extrude(part, hex_sk, "Hex Recess", HEX_DEPTH, is_cut=True)

if __name__ == "__main__":
    sys.exit(run_example(main))
