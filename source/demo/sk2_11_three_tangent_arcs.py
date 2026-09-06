"""Sketch-2D demo 11: three arcs smoothly joined (tangent-continuous spline).

Builds three circular arcs whose endpoints are coincident and whose
tangent vectors line up at each junction. The result is a
``C1``-continuous curve made entirely of circular pieces: the kind of
shape you'd put inside a cam profile, ducting transition, or pipe bend.

Pass criteria:
  - 2 coincident constraints (end of arc N -> start of arc N+1).
  - 2 tangent constraints (between consecutive arcs).
  - Arc 1 end == Arc 2 start (coincident worked).
  - Arc 2 end == Arc 3 start.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_11_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "ChainArcs")

    sk.BeginChange()
    try:
        a = sk.Figures.AddCircularArcByCenterStartEnd(
            0.0, 0.0,
            2.0, 0.0,
            0.0, 2.0,
        )
        b = sk.Figures.AddCircularArcByCenterStartEnd(
            0.0, 4.0,
            0.0, 2.0,
            -2.0, 4.0,
        )
        c = sk.Figures.AddCircularArcByCenterStartEnd(
            -4.0, 4.0,
            -2.0, 4.0,
            -4.0, 6.0,
        )
    finally:
        sk.EndChange()

    def add(figs, ctype):
        col = root.NewObjectCollector()
        for f in figs:
            col.Add(f)
        return sk.SketchConstraints.AddConstraint(col, ctype)

    sk.BeginChange()
    try:
        add([a.End, b.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([b.End, c.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([a, b],            ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([b, c],            ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
    finally:
        sk.EndChange()

    print(f"a.End  =({a.End.X:.4f}, {a.End.Y:.4f})   b.Start=({b.Start.X:.4f}, {b.Start.Y:.4f})")
    print(f"b.End  =({b.End.X:.4f}, {b.End.Y:.4f})   c.Start=({c.Start.X:.4f}, {c.Start.Y:.4f})")

    return report([
        ("a.End == b.Start (X)", math.isclose(a.End.X, b.Start.X, abs_tol=1e-3)),
        ("a.End == b.Start (Y)", math.isclose(a.End.Y, b.Start.Y, abs_tol=1e-3)),
        ("b.End == c.Start (X)", math.isclose(b.End.X, c.Start.X, abs_tol=1e-3)),
        ("b.End == c.Start (Y)", math.isclose(b.End.Y, c.Start.Y, abs_tol=1e-3)),
        ("4 new constraints",    sk.SketchConstraints.Count >= 4),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
