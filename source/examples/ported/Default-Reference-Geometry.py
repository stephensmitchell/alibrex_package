"""Port of AlibreScript ``Default-Reference-Geometry.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/default-reference-geometry

Prints the default reference geometry of a fresh part. AlibreScript
exposes ``P.XYPlane / YZPlane / ZXPlane / XAxis / YAxis / ZAxis / Origin``
as named attributes; AlibreX collects them in ``DesignPlanes``,
``DesignAxes``, and ``DesignPoints`` and indexes by position.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example
def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Test", False)

    print(f"Part: {part.Name}\n")

    print(f"DesignPlanes ({part.DesignPlanes.Count}):")
    for i in range(part.DesignPlanes.Count):
        plane = part.DesignPlanes.Item(i)
        print(f"  [{i}] {plane.Name}")

    print(f"\nDesignAxes ({part.DesignAxes.Count}):")
    for i in range(part.DesignAxes.Count):
        axis = part.DesignAxes.Item(i)
        print(f"  [{i}] {axis.Name}")

    print(f"\nDesignPoints ({part.DesignPoints.Count}):")
    for i in range(part.DesignPoints.Count):
        point = part.DesignPoints.Item(i)
        print(f"  [{i}] {point.Name}")

if __name__ == "__main__":
    sys.exit(run_example(main))
