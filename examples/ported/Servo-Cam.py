"""Port of AlibreScript ``Servo-Cam.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/servo-cam

Builds a slotted oval base, an annular hub, then cuts the slots through
both. AlibreScript values were in millimetres; converted to centimetres.
Face lookup uses an index (``Bodies.Item(0).Faces``) rather than
``GetFace('Face<13>')``, since AlibreX has no name-based lookup for
topology.
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
MM = 0.1
majorwidth  = 13.763 * MM
minorwidth  =  6.260 * MM
height      =  7.000 * MM
slotwidth   =  3.000 * MM
baseheight  =  2.000 * MM
servoheight =  4.000 * MM
servoinside =  4.200 * MM


def _stadium(figs, length: float, h: float) -> None:
    figs.AddLine(-length/2, -h/2,  length/2, -h/2)
    figs.AddLine(-length/2,  h/2,  length/2,  h/2)
    figs.AddCircularArcByCenterStartEnd( length/2, 0.0,  length/2, -h/2,  length/2,  h/2)
    figs.AddCircularArcByCenterStartEnd(-length/2, 0.0, -length/2,  h/2, -length/2, -h/2)


def _slot(figs, x_outer: float, x_inner: float, h: float) -> None:
    """Draw a slot: top + bottom straight lines, semicircular caps at each end.

    ``CircularArcByCenterStartEnd`` sweeps CCW from start to end, so pick
    the cap orientation from the slot's side. On the +X
    half, the outer cap bulges to +X (start at -h/2, end at +h/2). On
    the -X half, the same start/end ordering bulges the wrong way
    (toward the origin): flip start/end so the cap still bulges away.
    """
    figs.AddLine(x_inner, -h/2,  x_outer, -h/2)
    figs.AddLine(x_inner,  h/2,  x_outer,  h/2)
    if x_outer >= 0:
        outer_s, outer_e = (-h/2,  h/2)
        inner_s, inner_e = ( h/2, -h/2)
    else:
        outer_s, outer_e = ( h/2, -h/2)
        inner_s, inner_e = (-h/2,  h/2)
    figs.AddCircularArcByCenterStartEnd(x_outer, 0.0, x_outer, outer_s, x_outer, outer_e)
    figs.AddCircularArcByCenterStartEnd(x_inner, 0.0, x_inner, inner_s, x_inner, inner_e)


def _extrude(part, sketch, name: str, depth: float, is_cut: bool):
    fn = part.Features.AddExtrudedCutout if is_cut else part.Features.AddExtrudedBoss
    return fn(
        sketch, depth, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, name, "Depth", "",
    )


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("GripperCam", False)
    xy = part.DesignPlanes.Item(0)

    base = part.Sketches.AddSketch(None, xy, "Base")
    _stadium(base.Figures, majorwidth, height)
    _slot(base.Figures,  majorwidth/2,  minorwidth/2, slotwidth)
    _slot(base.Figures, -majorwidth/2, -minorwidth/2, slotwidth)
    _extrude(part, base, "Base", baseheight, is_cut=False)

    # Top face = highest-Z face on body[0]. Don't cache the body proxy
    # (S2). GetExtents has two out params (S-NA, KNOWN_ISSUES section
    # P1); pass None placeholders and unpack the returned tuple.
    faces = part.Bodies.Item(0).Faces
    best_idx, best_z = -1, -1e9
    for i in range(faces.Count):
        try:
            lo, hi = faces.Item(i).GetExtents()
        except Exception:
            continue
        z = (lo.Z + hi.Z) / 2.0
        if z > best_z:
            best_z = z
            best_idx = i
    if best_idx < 0:
        raise RuntimeError("Could not find top face of base.")
    top_face = part.Bodies.Item(0).Faces.Item(best_idx)

    servo = part.Sketches.AddSketch(None, top_face, "Servo")
    servo.Figures.AddCircle(0.0, 0.0, 9.0 * MM / 2)
    servo.Figures.AddCircle(0.0, 0.0, servoinside / 2)
    _extrude(part, servo, "Servo", servoheight, is_cut=False)

    holes = part.Sketches.AddSketch(None, xy, "Holes")
    _slot(holes.Figures,  majorwidth/2,  minorwidth/2, slotwidth)
    _slot(holes.Figures, -majorwidth/2, -minorwidth/2, slotwidth)
    _extrude(part, holes, "Holes", baseheight + servoheight, is_cut=True)


if __name__ == "__main__":
    sys.exit(run_example(main))
