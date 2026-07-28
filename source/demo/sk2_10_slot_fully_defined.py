"""Sketch-2D demo 10: fully constrain a "slot" (2 lines + 2 semicircle arcs).

A slot is the classic CAD shape for bolt-clearance, key-ways, etc.:
two parallel lines capped by two semicircle arcs. We fully define it
by:

  - Coincident at each of the four arc-to-line endpoint joins.
  - Horizontal constraint on both straight sides.
  - Tangent constraints between each line and each adjacent arc.
  - Equal radius between the two arcs.
  - One sketch-origin pin on the left arc's center.
  - Two dimensions: slot length (centre-to-centre) and slot width
    (= 2 * arc radius via the radial dim on either arc).

Pass criteria:
  - The two arcs end up at equal radius == slot width / 2.
  - The line lengths == slot length (centre-to-centre).
  - The two top-line endpoints sit on the same Y.
  - Origin is one of the arc centres.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

SLOT_LENGTH = 8.0
SLOT_WIDTH = 2.0
RADIUS = SLOT_WIDTH / 2.0

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_10_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "Slot")

    sk.BeginChange()
    try:
        top = sk.Figures.AddLine(0.2, 1.1, 7.8, 1.05)
        bot = sk.Figures.AddLine(0.1, -1.05, 7.9, -1.1)
        larc = sk.Figures.AddCircularArcByCenterStartEnd(
            0.0, 0.0,
            0.2, 1.1,
            0.1, -1.05,
        )
        rarc = sk.Figures.AddCircularArcByCenterStartEnd(
            8.0, 0.0,
            7.9, -1.1,
            7.8, 1.05,
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
        add([top.Start, larc.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([top.End,   rarc.End],   ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([bot.Start, larc.End],   ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([bot.End,   rarc.Start], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        add([top], ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add([bot], ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL)
        add([larc, rarc], ADSketchConstraintType.AD_CONSTRAINT_EQUAL)
        add([top, larc], ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([top, rarc], ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([bot, larc], ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([bot, rarc], ADSketchConstraintType.AD_CONSTRAINT_TANGENT)
        add([larc.Center, sk.OriginPoint], ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT)
        sk.Dimensions.PlaceLinearDimension(larc.Center, rarc.Center, SLOT_LENGTH)
        sk.Dimensions.PlaceRadialDimension(larc, RADIUS)
    finally:
        sk.EndChange()

    print(f"Left arc:  center=({larc.Center.X:.4f}, {larc.Center.Y:.4f})  r={larc.Radius:.4f}")
    print(f"Right arc: center=({rarc.Center.X:.4f}, {rarc.Center.Y:.4f})  r={rarc.Radius:.4f}")
    print(f"Left arc endpoints:  start=({larc.Start.X:.4f}, {larc.Start.Y:.4f})  "
          f"end=({larc.End.X:.4f}, {larc.End.Y:.4f})")
    print(f"Right arc endpoints: start=({rarc.Start.X:.4f}, {rarc.Start.Y:.4f})  "
          f"end=({rarc.End.X:.4f}, {rarc.End.Y:.4f})")
    print(f"Top line:  start=({top.Start.X:.4f}, {top.Start.Y:.4f})  "
          f"end=({top.End.X:.4f}, {top.End.Y:.4f})")
    print(f"Bot line:  start=({bot.Start.X:.4f}, {bot.Start.Y:.4f})  "
          f"end=({bot.End.X:.4f}, {bot.End.Y:.4f})")

    centre_distance = math.hypot(
        rarc.Center.X - larc.Center.X,
        rarc.Center.Y - larc.Center.Y,
    )

    return report([
        ("left arc centred at origin",
            math.isclose(larc.Center.X, 0.0, abs_tol=1e-3)
            and math.isclose(larc.Center.Y, 0.0, abs_tol=1e-3)),
        ("equal radii",                   math.isclose(larc.Radius, rarc.Radius, abs_tol=1e-3)),
        ("radius matches dim",            math.isclose(larc.Radius, RADIUS, abs_tol=1e-3)),
        ("centre-to-centre == length",    math.isclose(centre_distance, SLOT_LENGTH, abs_tol=1e-3)),
        ("top line horizontal",           math.isclose(top.Start.Y, top.End.Y, abs_tol=1e-3)),
        ("bot line horizontal",           math.isclose(bot.Start.Y, bot.End.Y, abs_tol=1e-3)),
        ("top above bot",                 top.Start.Y > bot.Start.Y),
        ("left arc top-to-bottom",        larc.Start.Y > larc.Center.Y and larc.End.Y < larc.Center.Y),
        ("right arc bottom-to-top",       rarc.Start.Y < rarc.Center.Y and rarc.End.Y > rarc.Center.Y),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
