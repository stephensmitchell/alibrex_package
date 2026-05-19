"""Thread-tooth cross-sections.

Each generator draws **one tooth** of a thread profile in 2D. Sweep
the tooth along a helix to make a real thread, or just use these as
visual cross-sections for documentation. ``P`` is the thread pitch
(distance between adjacent teeth).

All in centimetres; origin is at the root of the tooth, peak along +Y.

Profiles:
  - un_metric(...)     — symmetric 60° (UN / ISO metric).
  - acme(...)          — 29° trapezoidal (ACME power-screw).
  - square_thread(...) — square / rectangular thread tooth.
  - buttress(...)      — asymmetric buttress thread (7° / 45°).
"""
from __future__ import annotations

import math


def _polyline(figs, pts) -> None:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + [pts[0]]):
        figs.AddLine(x1, y1, x2, y2)


def un_metric(sketch, *, P: float, cx: float = 0.0, cy: float = 0.0) -> None:
    """Symmetric 60° thread (UN / ISO metric). Sharp-V form.

    Tooth height = ``P * sqrt(3) / 2``. Truncation is left to the user
    if needed — this is the unrounded form.
    """
    height = P * math.sqrt(3) / 2.0
    pts = [
        (cx,           cy),
        (cx + P,       cy),
        (cx + P / 2.0, cy + height),
    ]
    _polyline(sketch.Figures, pts)


def acme(sketch, *, P: float, depth_ratio: float = 0.5,
         cx: float = 0.0, cy: float = 0.0) -> None:
    """ACME trapezoidal thread (29° included angle).

    ``depth_ratio`` is tooth height divided by pitch (default 0.5 —
    standard general-purpose ACME). Top flat width = ``P * 0.3707`` per
    the ACME standard.
    """
    height = P * depth_ratio
    half_angle_rad = math.radians(14.5)
    top_recess = height * math.tan(half_angle_rad)
    pts = [
        (cx,                       cy),
        (cx + P,                   cy),
        (cx + P - top_recess,      cy + height),
        (cx + top_recess,          cy + height),
    ]
    _polyline(sketch.Figures, pts)


def square_thread(sketch, *, P: float, depth_ratio: float = 0.5,
                  cx: float = 0.0, cy: float = 0.0) -> None:
    """Square (rectangular) thread tooth — 50/50 land/groove width by
    default. Flank angle is 0°."""
    height = P * depth_ratio
    width = P / 2.0
    pts = [
        (cx,                  cy),
        (cx + P,              cy),
        (cx + P,              cy + height),
        (cx + P - width / 2,  cy + height),
        (cx + P - width / 2,  cy),  # not used — fix below
    ]
    # Proper square-tooth perimeter: base[0..P], up at (P-quarter, 0..h),
    # across the top, down at (quarter, h..0), back to start.
    quarter = (P - width) / 2.0
    pts = [
        (cx,                 cy),
        (cx + P,             cy),
        (cx + P - quarter,   cy),
        (cx + P - quarter,   cy + height),
        (cx + quarter,       cy + height),
        (cx + quarter,       cy),
    ]
    _polyline(sketch.Figures, pts)


def buttress(sketch, *, P: float, depth_ratio: float = 0.5,
             pressure_angle_deg: float = 7.0, back_angle_deg: float = 45.0,
             cx: float = 0.0, cy: float = 0.0) -> None:
    """Asymmetric buttress thread tooth. The pressure flank (load-bearing
    side) is nearly perpendicular; the back flank is angled to ease
    manufacture."""
    height = P * depth_ratio
    front_offset = height * math.tan(math.radians(pressure_angle_deg))
    back_offset  = height * math.tan(math.radians(back_angle_deg))
    flat = P - front_offset - back_offset
    if flat < 0:
        # Pitch too tight for these angles at this depth — collapse to a peak.
        flat = 0.0
    pts = [
        (cx,                                 cy),
        (cx + P,                             cy),
        (cx + P - back_offset,               cy + height),
        (cx + P - back_offset - flat,        cy + height),
    ]
    _polyline(sketch.Figures, pts)
