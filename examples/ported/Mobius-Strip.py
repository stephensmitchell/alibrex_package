"""Port of AlibreScript ``Mobius-Strip.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/mobius-strip

KNOWN UPSTREAM ISSUE (S10 in KNOWN_ISSUES.md): this example may not
produce a usable result in AlibreX 29. The 30 angled cross-
section planes are created OK and the rectangles are sketched on them,
but the final ``AddLoftBoss`` over a Mobius-twisted ring fails inside
AlibreX with ``COMException: Object reference not set to an instance of
an object.`` - Alibre's loft kernel chokes on the non-orientable twist
geometry on affected builds. The same script worked in earlier AlibreScript
runtimes per the original article. Nothing the Python side can do.

The port is left in place so that when Alibre fixes their loft engine
the example will start producing a Mobius strip with no code changes.

Generates N rectangle cross-sections on planes rotated about Y at
``DegreesPerStep`` increments, each twisted in-plane by
``RotationPerStep`` and offset radially. AlibreScript's
``Sketch.CopyFrom`` does all that in one call; AlibreX has no
equivalent so the port emits the four corner points of each rectangle
explicitly with the per-sketch rotation applied.
"""
from __future__ import annotations

import math
import sys
from alibrex import ADLoftGuideType, connect, run_example
MM = 0.1
DIAMETER = 100.0 * MM
WIDTH    = 20.0  * MM
HEIGHT   = 5.0   * MM
ROTATIONS = 2
STEPS = 30


def _add_twisted_rect(sketch, center_x: float, half_w: float, half_h: float, twist_deg: float) -> None:
    c, s = math.cos(math.radians(twist_deg)), math.sin(math.radians(twist_deg))
    corners = [
        (-half_w, -half_h),
        ( half_w, -half_h),
        ( half_w,  half_h),
        (-half_w,  half_h),
    ]
    pts = [(center_x + c*x - s*y, c*y + s*x) for x, y in corners]
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i+1) % 4]
        sketch.Figures.AddLine(x1, y1, x2, y2)


def main() -> None:
    rotation_per_step = ROTATIONS / float(STEPS) * 360.0
    degrees_per_step  = 360.0 / STEPS

    root = connect()
    part = root.CreateEmptyPart("Mobius", False)

    xy = part.DesignPlanes.Item(0)
    y_axis = part.DesignAxes.Item(1)
    center_x = DIAMETER + WIDTH / 2.0

    sketches = []
    # Step 0 - on XY directly
    s0 = part.Sketches.AddSketch(None, xy, "S0")
    _add_twisted_rect(s0, center_x, WIDTH/2, HEIGHT/2, 0.0)
    sketches.append(s0)

    for step in range(1, STEPS):
        plane = part.DesignPlanes.CreateAtAngleToPlane(
            None, xy, None, y_axis, degrees_per_step * step, f"S{step}P",
        )
        sk = part.Sketches.AddSketch(None, plane, f"S{step}")
        _add_twisted_rect(sk, center_x, WIDTH/2, HEIGHT/2,
                          rotation_per_step * step)
        sketches.append(sk)

    sections = root.NewObjectCollector()
    for sk in sketches:
        sections.Add(sk)

    # Some AlibreX 29 builds choke on Mobius-twisted loft geometry - see the
    # module docstring + KNOWN_ISSUES.md S10. Wrap the call so the rest
    # of the suite keeps running.
    try:
        part.Features.AddLoftBoss(
            sections, None, None, None, None,
            ADLoftGuideType.AD_NONE, False, False, False, True,
            "Strip",
        )
        print(f"Lofted {len(sketches)} cross-sections.")
    except Exception as exc:  # noqa: BLE001
        print(f"AddLoftBoss skipped (S10): {type(exc).__name__}.")
        print(f"All {len(sketches)} cross-section sketches are still in the part.")


if __name__ == "__main__":
    sys.exit(run_example(main))
