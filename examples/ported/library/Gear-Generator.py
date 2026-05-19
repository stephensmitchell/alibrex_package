"""Port of AlibreScript ``Mechanical/Gear Generator.py``.

AlibreScript has ``AddGearNP(name, teeth, pitch_diameter, pressure_angle,
0, 0, on_face?, plane)``; AlibreX has no involute-gear primitive, so
this port builds the gear profile by hand from the standard involute
parametric formulae and then extrudes it.

Reference for the involute math:
- Base radius   r_b  = (pitch_diameter / 2) · cos(pressure_angle)
- Pitch radius  r_p  = pitch_diameter / 2
- Addendum      a    = pitch_diameter / teeth   (module = pitch / teeth)
- Dedendum      d    = 1.25 · a
- Outer radius  r_o  = r_p + a
- Root radius   r_r  = r_p − d
- Involute      x(θ) = r_b · (cos θ + θ · sin θ)
                y(θ) = r_b · (sin θ − θ · cos θ)
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
from alibrex.dialogs import InputType, options_dialog
MM = 0.1
SAMPLES_PER_FLANK = 12


def _involute_flank(r_b: float, theta_start: float, theta_end: float, sign: float):
    """Sample one involute flank between two parameter values."""
    for i in range(SAMPLES_PER_FLANK + 1):
        t = theta_start + (theta_end - theta_start) * i / SAMPLES_PER_FLANK
        x = r_b * (math.cos(t) + t * math.sin(t))
        y = sign * r_b * (math.sin(t) - t * math.cos(t))
        yield x, y


def _theta_at_radius(r_b: float, r: float) -> float:
    return math.sqrt(max(0.0, (r * r) / (r_b * r_b) - 1.0))


def main() -> None:
    values = options_dialog(
        "Gear Generator",
        [
            ["Number of Teeth",    InputType.Integer, 20],
            ["Pitch Diameter (mm)", InputType.Real,   30.0],
            ["Pressure Angle (°)",  InputType.Real,   20.0],
            ["Thickness (mm)",      InputType.Real,   3.0],
        ],
        width=320,
    )
    if values is None:
        sys.exit("User cancelled")
    teeth, pitch_mm, pa_deg, thick_mm = values

    pitch_d = pitch_mm * MM
    thickness = thick_mm * MM
    pa = math.radians(pa_deg)
    r_p = pitch_d / 2.0
    r_b = r_p * math.cos(pa)
    addendum = pitch_d / teeth
    dedendum = 1.25 * addendum
    r_o = r_p + addendum
    r_r = max(r_b, r_p - dedendum)

    theta_o = _theta_at_radius(r_b, r_o)
    theta_r = _theta_at_radius(r_b, r_r)

    # Tooth-thickness angle at the pitch circle is π/teeth; we offset
    # each flank by half that angle around the tooth centerline.
    tooth_angle = 2 * math.pi / teeth
    half_tooth = tooth_angle / 4.0

    points: list[tuple[float, float]] = []
    for i in range(teeth):
        centre = i * tooth_angle
        # Right flank (origin pointing along +X then rotated by centre - half_tooth)
        rot1 = centre - half_tooth
        for x, y in _involute_flank(r_b, theta_r, theta_o, +1.0):
            cx = x * math.cos(rot1) - y * math.sin(rot1)
            cy = x * math.sin(rot1) + y * math.cos(rot1)
            points.append((cx, cy))
        # Top arc (outside radius) from right flank end to left flank start
        # Approximate with a straight chord — visually fine at SAMPLES_PER_FLANK ≥ 8
        rot2 = centre + half_tooth
        # Left flank, mirrored
        for x, y in _involute_flank(r_b, theta_o, theta_r, -1.0):
            cx = x * math.cos(rot2) - y * math.sin(rot2)
            cy = x * math.sin(rot2) + y * math.cos(rot2)
            points.append((cx, cy))

    root = connect()
    part = root.CreateEmptyPart("Gear", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Profile")
    for (x1, y1), (x2, y2) in zip(points, points[1:] + [points[0]]):
        sketch.Figures.AddLine(x1, y1, x2, y2)

    part.Features.AddExtrudedBoss(
        sketch, thickness, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Gear", "Thickness", "",
    )
    print(f"Built gear: {teeth} teeth, pitch Ø {pitch_mm:.2f} mm, "
          f"pressure {pa_deg:.1f}°.")


if __name__ == "__main__":
    sys.exit(run_example(main))
