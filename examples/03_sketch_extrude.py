"""Example 03 - sketch a rectangle on the XY plane and extrude it.

Demonstrates the core modeling pipeline:
    plane -> sketch -> figures -> feature

Units throughout the API are centimeters internally regardless of UI display.
"""
from __future__ import annotations

import sys

from alibrex import (
    ADPartFeatureEndCondition,
    ADDirectionType,
    IADPartSession,
)
from alibrex import connect, run_example
WIDTH_CM = 5.0     # X
HEIGHT_CM = 3.0    # Y
DEPTH_CM = 1.0     # extrude depth in Z


def add_rectangle(part: IADPartSession, w: float, h: float) -> None:
    # XY plane is conventionally the first design plane on a fresh part
    xy_plane = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy_plane, "RectSketch")
    figs = sketch.Figures
    figs.AddLine(0.0, 0.0,  w,   0.0)
    figs.AddLine(w,   0.0,  w,   h  )
    figs.AddLine(w,   h,    0.0, h  )
    figs.AddLine(0.0, h,    0.0, 0.0)


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("RectExtrude_Demo", False)

    add_rectangle(part, WIDTH_CM, HEIGHT_CM)

    sketch = part.Sketches.Item(part.Sketches.Count - 1)
    feat = part.Features.AddExtrudedBoss(
        sketch,
        DEPTH_CM,                                  # depth
        ADPartFeatureEndCondition.AD_TO_DEPTH,     # end condition
        None, None, 0.0,                           # to-geometry (unused for blind)
        ADDirectionType.AD_ALONG_NORMAL,           # direction
        None, None, False,                         # direction overrides
        None, False,                               # draft angle
        "Block",                                   # feature name
        "Depth", "",                               # parameter names
    )
    print(f"Created extrusion '{feat.Name}' on part '{part.Name}'.")
    print(f"Feature count: {part.FeatureCount}")


if __name__ == "__main__":
    sys.exit(run_example(main))
