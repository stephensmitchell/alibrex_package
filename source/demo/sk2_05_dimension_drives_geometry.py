"""Sketch-2D demo 05: change a dimension parameter, geometry resizes.

Builds the fully-constrained rectangle from sk2_02, then mutates the
width dimension's *parameter* via the parameter-transaction API.
Because every other DOF is pinned, the corners shift in lockstep with
the new width.

The canonical "parametric design" workflow:

    1. Build geometry fully constrained.
    2. Expose dimensions as named parameters.
    3. Edit parameters: geometry updates everywhere it's used.

Pass criteria:
  - After setting width = 10.0, the right-side corners' X are 10.0.
  - After setting width =  3.0, the right-side corners' X are 3.0.
  - The left-side corners stay at X = 0.0 (they're pinned to origin).
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

W0, H0 = 6.0, 4.0

def _xs(sk) -> tuple[float, ...]:
    xs = set()
    for i in range(sk.Figures.Count):
        fig = sk.Figures.Item(i)
        try:
            xs.add(round(fig.Start.X, 4))
            xs.add(round(fig.End.X, 4))
        except AttributeError:
            continue
    return tuple(sorted(xs))

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_05_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "ParamRect")

    sk.BeginChange()
    try:
        bot   = sk.Figures.AddLine(0.0, 0.0, W0, 0.0)
        right = sk.Figures.AddLine(W0,  0.0, W0, H0)
        top   = sk.Figures.AddLine(W0,  H0,  0.0, H0)
        left  = sk.Figures.AddLine(0.0, H0,  0.0, 0.0)
    finally:
        sk.EndChange()

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
        add([bot.Start, sk.OriginPoint], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        width_dim = sk.Dimensions.PlaceLinearDimension(bot,  W0)
        sk.Dimensions.PlaceLinearDimension(left, H0)
    finally:
        sk.EndChange()

    width_param = width_dim.Parameter
    print(f"Initial width parameter: {width_param.Name} = {width_param.Value}")
    print(f"Initial X positions: {_xs(sk)}")

    def set_width(new_w: float) -> tuple[float, ...]:
        params = part.Parameters
        params.OpenParameterTransaction()
        try:
            width_param.Value = new_w
            params.CloseParameterTransaction()
        except Exception:
            params.CancelParameterTransaction()
            raise
        part.RegenerateAll()
        return _xs(sk)

    xs_at_10 = set_width(10.0)
    print(f"After W=10: X = {xs_at_10}")
    xs_at_3 = set_width(3.0)
    print(f"After W=3:  X = {xs_at_3}")

    return report([
        ("W=10 right edge at 10", 10.0 in xs_at_10),
        ("W=10 left edge at 0",   0.0 in xs_at_10),
        ("W=3 right edge at 3",   3.0 in xs_at_3),
        ("W=3 left edge at 0",    0.0 in xs_at_3),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
