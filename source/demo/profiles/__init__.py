"""Parametric 2D profile library for alibrex demos.

Each submodule exposes generator functions that draw a fully-defined
cross-section into a given ``IADSketch``. All distances are in alibrex
internal units (centimetres). Helpers below convert from mm / inches.

Submodules:
  - steel   : structural shapes: I-beam, channel, equal-leg angle,
              rectangular hollow, circular hollow, T-section.
  - wood    : wood-trim cross-sections: baseboard, quarter-round,
              casing, simple crown molding.
  - threads : visual thread-tooth cross-sections: UN/metric, square,
              ACME, buttress.
  - pipe    : pipe-fitting profile primitives: pipe annulus,
              axisymmetric reducer half-profile, flange face.
"""
from __future__ import annotations

def mm(value: float) -> float:
    """Millimetres to centimetres (alibrex internal unit)."""
    return value / 10.0

def inches(value: float) -> float:
    """Inches to centimetres."""
    return value * 2.54
