"""Port of AlibreScript ``Triangle.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/triangle

Draws a right triangle with angles 90/15/75 on the XY plane.

Notes
-----
AlibreScript uses millimetres by default; AlibreX uses centimetres
internally. The original ``Adjacent = 100.0`` mm becomes 10.0 cm here.
"""
from __future__ import annotations

import math
import sys
from alibrex import connect, run_example
THETA_DEG = 15.0
ADJACENT_CM = 10.0   # 100 mm in the original


def main() -> None:
    opp = ADJACENT_CM * math.tan(math.radians(THETA_DEG))

    p1 = (0.0, 0.0)
    p2 = (ADJACENT_CM, 0.0)
    p3 = (ADJACENT_CM, opp)

    root = connect()
    part = root.CreateEmptyPart("Foo", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Shape")

    sketch.Figures.AddLine(*p1, *p2)
    sketch.Figures.AddLine(*p2, *p3)
    sketch.Figures.AddLine(*p3, *p1)

    print(f"Triangle vertices: {p1}, {p2}, {p3}")


if __name__ == "__main__":
    sys.exit(run_example(main))
