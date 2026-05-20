"""Sketch-2D demo 06 - under-constrained vs fully-defined: side-by-side.

Builds two sketches in the same part:

  - sketch A: 4 lines drawn approximately as a rectangle, **no
    additional constraints** beyond the auto-coincident endpoints
    Alibre adds during draw.
  - sketch B: the same 4 lines, but with H/V + corner pin + width/
    height dimensions added - **fully defined**.

For each sketch, opens a parameter transaction that doesn't move any
parameter (a no-op regenerate) and then prints constraint + dimension
counts. The contrast makes the "fully defined" status concrete.

Pass criteria:
  - Both sketches have the same number of figures.
  - Sketch B has more constraints than A (the H/V + fix adds).
  - Sketch B has 2 dimensions; sketch A has 0.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example


def _draw_rect(sk, w: float, h: float):
    sk.BeginChange()
    try:
        bot   = sk.Figures.AddLine(0.0, 0.0, w,   0.0)
        right = sk.Figures.AddLine(w,   0.0, w,   h)
        top   = sk.Figures.AddLine(w,   h,   0.0, h)
        left  = sk.Figures.AddLine(0.0, h,   0.0, 0.0)
    finally:
        sk.EndChange()
    return bot, right, top, left


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_06_{tag}")
    root = connect()
    plane = part.DesignPlanes.Item(0)

    a = part.Sketches.AddSketch(None, plane, "RectA_under")
    _draw_rect(a, 5.0, 3.0)

    b = part.Sketches.AddSketch(None, plane, "RectB_fully")
    bot, right, top, left = _draw_rect(b, 5.0, 3.0)

    def add(sk, figs, ctype):
        col = root.NewObjectCollector()
        for f in figs:
            col.Add(f)
        return sk.SketchConstraints.AddConstraint(col, ctype)

    b.BeginChange()
    try:
        add(b, [bot],   ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add(b, [top],   ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add(b, [left],  ADSketchConstraintType.AD_CONSTRAINT_VERTICAL)
        add(b, [right], ADSketchConstraintType.AD_CONSTRAINT_VERTICAL)
        add(b, [bot.Start, b.OriginPoint], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        b.Dimensions.PlaceLinearDimension(bot,  5.0)
        b.Dimensions.PlaceLinearDimension(left, 3.0)
    finally:
        b.EndChange()

    a_constraints = a.SketchConstraints.Count
    a_dims = a.Dimensions.Count
    b_constraints = b.SketchConstraints.Count
    b_dims = b.Dimensions.Count

    print(f"Sketch A (under-constrained): {a.Figures.Count} figures, "
          f"{a_constraints} constraints, {a_dims} dimensions")
    print(f"Sketch B (fully defined)    : {b.Figures.Count} figures, "
          f"{b_constraints} constraints, {b_dims} dimensions")

    return report([
        ("same figure count",          a.Figures.Count == b.Figures.Count),
        ("B has more constraints",     b_constraints > a_constraints),
        ("A has zero dimensions",      a_dims == 0),
        ("B has 2 dimensions",         b_dims == 2),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
