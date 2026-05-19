"""Pipe-fitting cross-section profiles.

Profile-sketch generators used as sweep or revolve profiles for pipe
elbows, reducers, flanges, and so on. All distances in centimetres.

Profiles:
  - pipe_annulus(...)   — outer circle + inner circle (sweep profile
    for a constant-wall pipe).
  - reducer_half(...)   — half-section profile of an axisymmetric
    reducer; revolve 360° around the X-axis to make a reducer body.
  - flange_face(...)    — half-section profile of a slip-on flange face
    (without bolt holes); revolve 360°.
"""
from __future__ import annotations


def _polyline(figs, pts) -> None:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + [pts[0]]):
        figs.AddLine(x1, y1, x2, y2)


def pipe_annulus(sketch, *, od: float, wall: float,
                 cx: float = 0.0, cy: float = 0.0) -> None:
    """Pipe cross-section: outer circle + concentric inner circle.

    ``od`` outside diameter, ``wall`` wall thickness.
    """
    sketch.Figures.AddCircle(cx, cy, od / 2.0)
    sketch.Figures.AddCircle(cx, cy, (od - 2 * wall) / 2.0)


def reducer_half(sketch, *, od_in: float, od_out: float, length: float,
                 wall_in: float, wall_out: float | None = None,
                 cx: float = 0.0, cy: float = 0.0) -> None:
    """Half-profile of an axisymmetric concentric reducer.

    Revolve this profile 360° about the X-axis (Y=0) to make the
    reducer body. ``od_in`` and ``od_out`` are the two end outer
    diameters; ``length`` is the axial distance between them.
    ``wall_in`` is the wall thickness; ``wall_out`` defaults to the
    same value.
    """
    if wall_out is None:
        wall_out = wall_in
    ro_in  = od_in  / 2.0
    ri_in  = ro_in  - wall_in
    ro_out = od_out / 2.0
    ri_out = ro_out - wall_out
    pts = [
        (cx,                cy + ri_in),
        (cx,                cy + ro_in),
        (cx + length,       cy + ro_out),
        (cx + length,       cy + ri_out),
    ]
    _polyline(sketch.Figures, pts)


def flange_face(sketch, *, od: float, id_bore: float, hub_od: float,
                face_thk: float, hub_len: float,
                cx: float = 0.0, cy: float = 0.0) -> None:
    """Half-profile of a slip-on flange (no bolt holes).

    Revolve 360° about the X-axis (Y=0). ``od`` flange outer diameter,
    ``id_bore`` pipe bore, ``hub_od`` hub outer diameter, ``face_thk``
    flange-face thickness, ``hub_len`` total axial length from face to
    hub end.
    """
    r_id   = id_bore / 2.0
    r_hub  = hub_od / 2.0
    r_face = od / 2.0
    pts = [
        (cx,                       cy + r_id),
        (cx,                       cy + r_face),
        (cx + face_thk,            cy + r_face),
        (cx + face_thk,            cy + r_hub),
        (cx + hub_len,             cy + r_hub),
        (cx + hub_len,             cy + r_id),
    ]
    _polyline(sketch.Figures, pts)
