"""Port of AlibreScript ``Midplane-Extrusion.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/midplane-extrusion

Extrudes a circle symmetrically about its sketch plane. AlibreScript's
``Part.EndCondition.MidPlane`` maps to ``ADPartFeatureEndCondition.AD_MID_PLANE``.
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
RADIUS_CM = 0.9       # 9 mm in the original
EXTRUDE_LEN_CM = 1.0  # 10 mm


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Test", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Shape")
    sketch.Figures.AddCircle(0.0, 0.0, RADIUS_CM)

    part.Features.AddExtrudedBoss(
        sketch, EXTRUDE_LEN_CM, ADPartFeatureEndCondition.AD_MID_PLANE,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Cyl", "Depth", "",
    )
    print(f"Mid-plane cylinder: total length {EXTRUDE_LEN_CM} cm "
          f"(±{EXTRUDE_LEN_CM/2:.3f} cm about XY).")


if __name__ == "__main__":
    sys.exit(run_example(main))
