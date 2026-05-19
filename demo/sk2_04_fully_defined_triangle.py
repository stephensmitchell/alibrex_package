"""Sketch-2D demo 04 — fully constrain a triangle by SSS (3 side lengths).

Builds a triangle from 3 lines, closes the loop with 3 coincidents,
pins one vertex to the sketch origin + makes one side horizontal,
then dimensions all three sides. SSS is the simplest fully-defined
specification for a triangle (3 lengths + 3 free DOF removed by
pinning origin + one side along the X-axis).

Pass criteria:
  - 3 dimensions added.
  - The three vertex positions read back match a 3-4-5 right triangle:
    (0,0), (4,0), and one of (0,3) / (0,-3) (Alibre may flip).
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_04_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "Triangle")

    # Sloppy 3-4-5 sketched as 3 lines closing into a loop.
    sk.BeginChange()
    try:
        base = sk.Figures.AddLine(0.1, 0.05, 4.2, -0.1)    # base (~4)
        hyp  = sk.Figures.AddLine(4.2, -0.1, 0.05, 3.1)    # hypotenuse (~5)
        leg  = sk.Figures.AddLine(0.05, 3.1, 0.1, 0.05)    # vertical leg (~3)
    finally:
        sk.EndChange()

    def add(figs, ctype):
        col = root.NewObjectCollector()
        for f in figs:
            col.Add(f)
        return sk.SketchConstraints.AddConstraint(col, ctype)

    sk.BeginChange()
    try:
        # Close the loop explicitly (Alibre also auto-adds these).
        add([base.End,  hyp.Start],  ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([hyp.End,   leg.Start],  ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([leg.End,   base.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        # Pin the base's start to the origin and make the base horizontal.
        add([base.Start, sk.OriginPoint], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([base], ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        # SSS — 3 length dimensions.
        sk.Dimensions.PlaceLinearDimension(base, 4.0)
        sk.Dimensions.PlaceLinearDimension(leg,  3.0)
        sk.Dimensions.PlaceLinearDimension(hyp,  5.0)
    finally:
        sk.EndChange()

    pts = set()
    for fig in (base, hyp, leg):
        s, e = fig.Start, fig.End
        pts.add((round(s.X, 3), round(s.Y, 3)))
        pts.add((round(e.X, 3), round(e.Y, 3)))
    pts_sorted = sorted(pts)
    print(f"Final vertices: {pts_sorted}")
    print(f"Dimensions: {sk.Dimensions.Count}")

    # Expected: (0,0), (4,0), and one of (0, +3) / (0, -3) — Alibre may
    # choose either side of the X-axis.
    has_origin = (0.0, 0.0) in pts_sorted
    has_base_end = (4.0, 0.0) in pts_sorted
    has_apex = (0.0, 3.0) in pts_sorted or (0.0, -3.0) in pts_sorted

    return report([
        ("3 dimensions added",    sk.Dimensions.Count == 3),
        ("origin vertex present", has_origin),
        ("base-end at (4, 0)",    has_base_end),
        ("apex at (0, +-3)",      has_apex),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
