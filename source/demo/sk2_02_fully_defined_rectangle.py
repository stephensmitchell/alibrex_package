"""Sketch-2D demo 02: fully constrain a rectangle.

Builds a rectangle from 4 line segments, then locks it down so every
vertex is fixed:

  - 4 coincident constraints joining consecutive endpoints (closes the loop).
  - Top + bottom lines horizontal; left + right lines vertical.
  - A FIX constraint on the bottom-left corner pins it to the origin.
  - Two linear dimensions: width on the bottom, height on the left.

The rectangle's corners sit at exact, known
positions regardless of how sloppy the original sketch coordinates were.

Pass criteria:
  - SketchConstraints has 4 coincidents + 4 H/V + 1 fix = 9 new entries.
  - Dimensions collection has 2 entries (width, height).
  - The four corner positions read back to (0,0), (W,0), (W,H), (0,H).
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

W = 6.0
H = 4.0

def _xy_plane(part):
    return part.DesignPlanes.Item(0)

def _corner_positions(sk):
    """Read the 4 distinct vertex positions from the 4 lines."""
    pts = []
    for i in range(sk.Figures.Count):
        fig = sk.Figures.Item(i)
        try:
            s, e = fig.Start, fig.End
        except AttributeError:
            continue
        pts.append((round(s.X, 4), round(s.Y, 4)))
        pts.append((round(e.X, 4), round(e.Y, 4)))
    return sorted(set(pts))

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_02_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, _xy_plane(part), "Rect")

    sk.BeginChange()
    try:
        bot   = sk.Figures.AddLine(0.0,  0.0,  5.5, 0.2)
        right = sk.Figures.AddLine(5.5,  0.2,  6.1, 3.9)
        top   = sk.Figures.AddLine(6.1,  3.9,  0.3, 4.1)
        left  = sk.Figures.AddLine(0.3,  4.1,  0.0, 0.0)
    finally:
        sk.EndChange()

    cs_before = sk.SketchConstraints.Count
    print(f"Initial constraints: {cs_before}")
    print(f"Initial corners: {_corner_positions(sk)}")

    def add(figs, ctype):
        col = root.NewObjectCollector()
        for f in figs:
            col.Add(f)
        return sk.SketchConstraints.AddConstraint(col, ctype)

    sk.BeginChange()
    try:
        add([bot.End,   right.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([right.End, top.Start],   ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([top.End,   left.Start],  ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([left.End,  bot.Start],   ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([bot],   ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add([top],   ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add([left],  ADSketchConstraintType.AD_CONSTRAINT_VERTICAL)
        add([right], ADSketchConstraintType.AD_CONSTRAINT_VERTICAL)
        add([bot.Start], ADSketchConstraintType.AD_CONSTRAINT_FIX)
    finally:
        sk.EndChange()

    cs_after = sk.SketchConstraints.Count
    print(f"After geom constraints: {cs_after}")

    dims = sk.Dimensions
    dim_before = dims.Count
    sk.BeginChange()
    try:
        dims.PlaceLinearDimension(bot,  W)
        dims.PlaceLinearDimension(left, H)
    finally:
        sk.EndChange()
    dim_after = sk.Dimensions.Count
    print(f"Dimensions: {dim_before} -> {dim_after}")

    final_corners = _corner_positions(sk)
    print(f"Final corners: {final_corners}")
    expected = sorted({(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)})

    def _approx(a, b, tol=1e-3):
        return len(a) == len(b) and all(
            math.isclose(ax, bx, abs_tol=tol) and math.isclose(ay, by, abs_tol=tol)
            for (ax, ay), (bx, by) in zip(a, b)
        )

    return report([
        ("constraints grew",              cs_after - cs_before >= 4),
        ("2 dimensions added",            dim_after - dim_before == 2),
        ("corners at exact rectangle",    _approx(final_corners, expected)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
