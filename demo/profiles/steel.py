"""Steel structural cross-sections.

Each function takes ``(sketch, **params)`` and emits the figures
representing the cross-section's outline. Coordinates are placed
directly (no constraints needed) so the section is implicitly fully
defined. Caller is responsible for wrapping in BeginChange/EndChange
if multiple sections are added to the same sketch.

All dimensions in centimetres. Use the ``mm()`` helper in
``profiles.__init__`` to feed mm-spec dimensions.

Sections supplied:
  - i_beam(...)       — wide-flange I / W shape.
  - channel(...)      — C-section.
  - angle(...)        — equal- or unequal-leg L-section.
  - rhs(...)          — rectangular hollow section.
  - shs(...)          — square hollow section (specialisation of rhs).
  - chs(...)          — circular hollow section (round pipe).
  - tee(...)          — T-section.
"""
from __future__ import annotations


def _polyline(figs, pts) -> None:
    """Emit consecutive AddLine calls connecting ``pts`` (a closed loop)."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + [pts[0]]):
        figs.AddLine(x1, y1, x2, y2)


def i_beam(sketch, *, h: float, b: float, tw: float, tf: float,
           cx: float = 0.0, cy: float = 0.0) -> None:
    """Wide-flange I-beam (W-shape) centred on (cx, cy).

    ``h`` = total height, ``b`` = flange width, ``tw`` = web thickness,
    ``tf`` = flange thickness.
    """
    half_h = h / 2.0
    half_b = b / 2.0
    half_tw = tw / 2.0
    pts = [
        (cx - half_b, cy - half_h),                      # bottom-left
        (cx + half_b, cy - half_h),                      # bottom-right
        (cx + half_b, cy - half_h + tf),                 # top of bottom flange (right)
        (cx + half_tw, cy - half_h + tf),                # web join (right-bottom)
        (cx + half_tw, cy + half_h - tf),                # web join (right-top)
        (cx + half_b, cy + half_h - tf),                 # bottom of top flange (right)
        (cx + half_b, cy + half_h),                      # top-right
        (cx - half_b, cy + half_h),                      # top-left
        (cx - half_b, cy + half_h - tf),                 # bottom of top flange (left)
        (cx - half_tw, cy + half_h - tf),
        (cx - half_tw, cy - half_h + tf),
        (cx - half_b, cy - half_h + tf),
    ]
    _polyline(sketch.Figures, pts)


def channel(sketch, *, h: float, b: float, tw: float, tf: float,
            cx: float = 0.0, cy: float = 0.0) -> None:
    """C-channel section. Opening faces +X. Origin at the centroid of the
    bounding rectangle for convenience."""
    half_h = h / 2.0
    pts = [
        (cx,         cy - half_h),
        (cx + b,     cy - half_h),
        (cx + b,     cy - half_h + tf),
        (cx + tw,    cy - half_h + tf),
        (cx + tw,    cy + half_h - tf),
        (cx + b,     cy + half_h - tf),
        (cx + b,     cy + half_h),
        (cx,         cy + half_h),
    ]
    _polyline(sketch.Figures, pts)


def angle(sketch, *, leg_a: float, leg_b: float, t: float,
          cx: float = 0.0, cy: float = 0.0) -> None:
    """Equal- or unequal-leg L-section. Corner at (cx, cy), legs extend
    into +X and +Y."""
    pts = [
        (cx,             cy),
        (cx + leg_a,     cy),
        (cx + leg_a,     cy + t),
        (cx + t,         cy + t),
        (cx + t,         cy + leg_b),
        (cx,             cy + leg_b),
    ]
    _polyline(sketch.Figures, pts)


def rhs(sketch, *, w: float, h: float, t: float,
        cx: float = 0.0, cy: float = 0.0) -> None:
    """Rectangular hollow section (RHS). Outer rectangle + inner rectangle
    forming an annular cross-section."""
    half_w, half_h = w / 2.0, h / 2.0
    outer = [
        (cx - half_w, cy - half_h),
        (cx + half_w, cy - half_h),
        (cx + half_w, cy + half_h),
        (cx - half_w, cy + half_h),
    ]
    inner = [
        (cx - half_w + t, cy - half_h + t),
        (cx + half_w - t, cy - half_h + t),
        (cx + half_w - t, cy + half_h - t),
        (cx - half_w + t, cy + half_h - t),
    ]
    _polyline(sketch.Figures, outer)
    _polyline(sketch.Figures, inner)


def shs(sketch, *, side: float, t: float, cx: float = 0.0, cy: float = 0.0) -> None:
    """Square hollow section. Specialisation of rhs."""
    rhs(sketch, w=side, h=side, t=t, cx=cx, cy=cy)


def chs(sketch, *, od: float, t: float, cx: float = 0.0, cy: float = 0.0) -> None:
    """Circular hollow section (round pipe). Outer + inner circle."""
    sketch.Figures.AddCircle(cx, cy, od / 2.0)
    sketch.Figures.AddCircle(cx, cy, (od - 2 * t) / 2.0)


def tee(sketch, *, h: float, b: float, tw: float, tf: float,
        cx: float = 0.0, cy: float = 0.0) -> None:
    """T-section. Web extends downward from the centre of the top flange."""
    half_b = b / 2.0
    half_tw = tw / 2.0
    pts = [
        (cx - half_b,  cy + h - tf),
        (cx + half_b,  cy + h - tf),
        (cx + half_b,  cy + h),
        (cx - half_b,  cy + h),
        (cx - half_b,  cy + h - tf),    # back to top-flange left
        (cx - half_tw, cy + h - tf),    # step in to web
        (cx - half_tw, cy),             # web bottom-left
        (cx + half_tw, cy),             # web bottom-right
        (cx + half_tw, cy + h - tf),    # web top-right
    ]
    # The above closes onto the inside of the flange; trim to a clean loop.
    pts = [
        (cx - half_b,  cy + h),         # top-left
        (cx + half_b,  cy + h),         # top-right
        (cx + half_b,  cy + h - tf),    # under top-right corner
        (cx + half_tw, cy + h - tf),
        (cx + half_tw, cy),             # web bottom-right
        (cx - half_tw, cy),             # web bottom-left
        (cx - half_tw, cy + h - tf),
        (cx - half_b,  cy + h - tf),
    ]
    _polyline(sketch.Figures, pts)
