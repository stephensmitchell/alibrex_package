"""Port of "Reference Geometry Showcase" AlibreScript example.

Builds a 40x20x10 block, then creates two reference planes:
  1. ``PlaneAngleXY`` - rotated 30 degrees from XY around the Y-axis.
  2. ``PlaneFrom3Points`` - defined by three corner points of the block.

Differences from the original:
  * AlibreScript's ``AddPlane(name, plane, axis, angle)`` becomes
    alibrex's ``IADDesignPlanes.CreateAtAngleToPlane``.
  * AlibreScript's ``AddPlane(name, [x1,y1,z1], [x2,y2,z2], [x3,y3,z3])``
    becomes ``IADDesignPlanes.CreateBy3Points`` - points must be real
    ``IADPoint`` objects, built via the session's GeometryFactory.
  * AlibreScript's ``AddAxis(name, plane1, plane2)`` doesn't have a
    direct alibrex equivalent on the design-axes collection; we skip
    the axis-from-intersection step in this port.
"""
from __future__ import annotations

import sys

from alibrex import run_example
from _porting_utils import (
    extrude_boss,
    mm,
    part_or_open,
    sketch_rectangle,
    xy_plane,
)


def main() -> int:
    part = part_or_open("ReferenceGeometryShowcase")

    # Step 1: 40 x 20 x 10 mm base block.
    base_sketch = sketch_rectangle(part, xy_plane(part), "BaseSketch",
                                   0.0, 0.0, mm(40), mm(20))
    extrude_boss(part, base_sketch, mm(10), "BaseExtrusion")
    print("Step 1: 40x20x10 mm block.")

    # Step 2: Angled plane (30 degrees from XY around the Y-axis).
    xy = xy_plane(part)
    y_axis = part.DesignAxes.Item(1)
    angled_plane = part.DesignPlanes.CreateAtAngleToPlane(
        None, xy, None, y_axis, 30.0, "PlaneAngleXY",
    )
    print(f"Step 2: created '{angled_plane.Name}' at 30 degrees to XY around Y-axis.")

    # Step 3: Plane from three non-coplanar corner points.
    # Note: `IADDesignPlanes.CreateBy3Points` in AlibreX 29 BETA-2 raises
    # "Cannot create plane with Collinear points" regardless of the actual
    # input points - verified by trying half a dozen obviously-non-collinear
    # triples. Treated as an upstream bug for now; the call is wrapped in
    # try/except so this script still demonstrates the working pieces.
    try:
        geo = part.GeometryFactory
        p1 = geo.CreatePoint(0.0,    0.0,    0.0)
        p2 = geo.CreatePoint(mm(40), 0.0,    0.0)
        p3 = geo.CreatePoint(0.0,    mm(20), mm(10))
        three_pt = part.DesignPlanes.CreateBy3Points(
            None, p1, None, p2, None, p3, "PlaneFrom3Points",
        )
        print(f"Step 3: created '{three_pt.Name}' from three corner points.")
    except Exception as exc:  # noqa: BLE001
        print(f"Step 3: SKIPPED - upstream AlibreX bug ({type(exc).__name__}).")

    print(f"Total design planes on '{part.Name}': {part.DesignPlanes.Count}")
    return 0


if __name__ == "__main__":
    sys.exit(run_example(main))
