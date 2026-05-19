"""Port of AlibreScript ``Tool-Cutting.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/tool-cutting

Simulates a lathe cutter making helical passes around a cylinder. The
original creates a list of *named* reference planes via
``P.AddPlane(plane, axis, angle)``; AlibreX uses
``DesignPlanes.CreateAtAngleToPlane(planeOcc, plane, axisOcc, axis,
angle, name)`` for the same thing.
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
MM = 0.1
DIAMETER  = 20  * MM
LENGTH    = 100 * MM
CUTTER_R  = 5   * MM / 2
STEP_DEG  = 10
TOTAL_DEG = 1440
START_X   = 10 * MM


def _extrude_cut_through(part, sketch, name: str):
    return part.Features.AddExtrudedCutout(
        sketch, 0.0, ADPartFeatureEndCondition.AD_THROUGH_ALL,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, name, "Depth", "",
    )


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Cylinder", False)

    # Cylinder on XY
    xy = part.DesignPlanes.Item(0)
    yz = part.DesignPlanes.Item(1)
    z_axis = part.DesignAxes.Item(2)   # default Z axis index

    cross = part.Sketches.AddSketch(None, xy, "Cross-Section")
    cross.Figures.AddCircle(0.0, 0.0, DIAMETER / 2)
    part.Features.AddExtrudedBoss(
        cross, LENGTH, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Cylinder", "Depth", "",
    )

    # Build planes around Z, 0..180 degrees stepping by STEP_DEG (mirrored)
    num_planes = 180 // STEP_DEG
    planes = []
    for i in range(num_planes):
        ang = i * STEP_DEG
        p = part.DesignPlanes.CreateAtAngleToPlane(
            None, yz, None, z_axis, float(ang), f"P{ang}",
        )
        planes.append(p)
    planes.extend(planes)   # mirror duplicate as in the original
    total_planes = len(planes)

    x_step = 0.0
    for step in range(TOTAL_DEG // STEP_DEG):
        angle = step * STEP_DEG
        norm = angle % 360
        x_step += angle * 0.001 * MM
        r = DIAMETER / 2
        if norm < 90:
            x, y = -(START_X + x_step),  r
        elif norm == 90:
            x, y = -r, -(START_X + x_step)
        elif norm < 180:
            x, y = (START_X + x_step), -r
        elif norm < 270:
            x, y = -(START_X + x_step), -r
        elif norm == 270:
            x, y = r, -(START_X + x_step)
        else:
            x, y = (START_X + x_step), r

        sk = part.Sketches.AddSketch(None, planes[step % total_planes], f"S{angle}")
        sk.Figures.AddCircle(x, y, CUTTER_R)
        _extrude_cut_through(part, sk, f"Cut{angle}")
    print(f"Performed {TOTAL_DEG // STEP_DEG} cuts.")


if __name__ == "__main__":
    sys.exit(run_example(main))
