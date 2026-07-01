"""Wood-trim cross-sections.

Functions emit fully-defined cross-sections in centimetres. Origin
convention: profile sits in the +X / +Y quadrant with its "wall" face
along X = 0 (so an extrude along Z mounts to a vertical wall).

Sections:
  - baseboard(...)     : stepped baseboard with a decorative top.
  - quarter_round(...) : quarter circle filler.
  - casing(...)        : simple stepped casing (window/door trim).
  - crown(...)         : basic cove-and-step crown molding profile.
"""
from __future__ import annotations

import math


def _polyline(figs, pts) -> None:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + [pts[0]]):
        figs.AddLine(x1, y1, x2, y2)


def baseboard(sketch, *, h: float, t: float, cap_h: float = 0.5,
              cx: float = 0.0, cy: float = 0.0) -> None:
    """Baseboard with a thin top cap step.

    ``h`` total height, ``t`` thickness at the base, ``cap_h`` height of
    the decorative top cap (the cap projects ``t`` deep).
    """
    cap_step = t * 0.6
    pts = [
        (cx,                cy),                       # back-bottom
        (cx + t,            cy),                       # front-bottom
        (cx + t,            cy + h - cap_h),           # front, up to cap base
        (cx + cap_step,     cy + h - cap_h),           # step back
        (cx + cap_step,     cy + h),                   # top of cap
        (cx,                cy + h),                   # back-top
    ]
    _polyline(sketch.Figures, pts)


def quarter_round(sketch, *, r: float,
                  cx: float = 0.0, cy: float = 0.0) -> None:
    """Quarter circle filling the bottom-left of an inside corner."""
    sketch.Figures.AddLine(cx, cy, cx + r, cy)                   # bottom edge
    sketch.Figures.AddLine(cx, cy, cx,     cy + r)               # back edge
    sketch.Figures.AddCircularArcByCenterStartEnd(
        cx, cy,
        cx + r, cy,
        cx, cy + r,
    )


def casing(sketch, *, h: float, t: float, recess: float = 0.3,
           cx: float = 0.0, cy: float = 0.0) -> None:
    """Stepped door / window casing: flat against wall, two steps in front.

    ``h`` total height, ``t`` thickness at the back, ``recess`` how
    much each step recesses.
    """
    step1_y = h * 0.4
    step2_y = h * 0.7
    pts = [
        (cx,                cy),
        (cx + t,            cy),
        (cx + t,            cy + step1_y),
        (cx + t - recess,   cy + step1_y),
        (cx + t - recess,   cy + step2_y),
        (cx + t - 2*recess, cy + step2_y),
        (cx + t - 2*recess, cy + h),
        (cx,                cy + h),
    ]
    _polyline(sketch.Figures, pts)


def crown(sketch, *, h: float, projection: float, cove_r: float | None = None,
          cx: float = 0.0, cy: float = 0.0) -> None:
    """Simple crown molding profile.

    A back-wall edge, a top edge, and a cove (concave quarter-arc)
    between them. ``h`` is total height (along Y), ``projection`` is
    how far the crown sticks out from the wall along X. ``cove_r``
    defaults to ``min(h, projection) * 0.8``.
    """
    if cove_r is None:
        cove_r = min(h, projection) * 0.8

    # Wall edge (back), then step out to start of cove, then arc, then top.
    p_wall_bottom = (cx,                       cy)
    p_cove_start  = (cx + projection - cove_r, cy)
    cove_center   = (cx + projection - cove_r, cy + cove_r)
    p_cove_end    = (cx + projection,          cy + cove_r)
    p_top_right   = (cx + projection,          cy + h)
    p_top_left    = (cx,                       cy + h)

    figs = sketch.Figures
    figs.AddLine(*p_wall_bottom, *p_cove_start)             # bottom run
    figs.AddCircularArcByCenterStartEnd(
        cove_center[0], cove_center[1],
        p_cove_start[0], p_cove_start[1],
        p_cove_end[0],   p_cove_end[1],
    )
    figs.AddLine(*p_cove_end,    *p_top_right)              # right edge up
    figs.AddLine(*p_top_right,   *p_top_left)               # top
    figs.AddLine(*p_top_left,    *p_wall_bottom)            # wall-side close
