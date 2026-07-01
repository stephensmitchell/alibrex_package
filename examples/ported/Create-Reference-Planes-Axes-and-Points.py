"""Port of AlibreScript ``Create-Reference-Planes-Axes-and-Points.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/create-reference-planes-axes-and-points

Mapping (original mm to AlibreX cm, ÷ 10):

- ``P.AddPlane(name, base, offset)``           : ``DesignPlanes.CreateAtOffsetToPlane(None, base, offset, name)``
- ``P.AddPoint(name, x, y, z)``                : ``DesignPoints.CreatePoint(x, y, z, name)``
- ``P.AddAxis(name, [x1,y1,z1], [x2,y2,z2])``  : create two design points, then ``DesignAxes.CreateBy2Points``
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example
def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("My Part", False)
    xy = part.DesignPlanes.Item(0)

    top = part.DesignPlanes.CreateAtOffsetToPlane(None, xy,  10.0, "Top Plane")
    bot = part.DesignPlanes.CreateAtOffsetToPlane(None, xy, -10.0, "Bottom Plane")
    print(f"Created offset planes: {top.Name}, {bot.Name}")

    pts_on_bot = [
        ( 5.0,  5.0, -10.0),
        ( 5.0, -5.0, -10.0),
        (-5.0, -5.0, -10.0),
        (-5.0,  5.0, -10.0),
    ]
    refs = [
        part.DesignPoints.CreatePoint(x, y, z, f"Ref {i+1}")
        for i, (x, y, z) in enumerate(pts_on_bot)
    ]
    center_top = part.DesignPoints.CreatePoint(0.0, 0.0, 10.0, "TopCenter")

    for i, p in enumerate(refs, start=1):
        part.DesignAxes.CreateBy2Points(None, p, None, center_top, f"Axis {i}")

    print(f"Added {len(refs)} reference points and 4 axes converging on TopCenter.")


if __name__ == "__main__":
    sys.exit(run_example(main))
