"""Example 18: mass / volume / surface area / inertia of the active part.

Reads `IADPartSession.PhysicalProperties` at AD_HIGH accuracy and prints
the full set of scalar and vector results. Run with any part open.
"""
from __future__ import annotations

import sys

from alibrex import (
    ADAccuracySetting,
    ADDirectionType,
    ADPartFeatureEndCondition,
    connect,
    run_example,
    require_active_part,
)

def _active_or_new_part(root):
    try:
        return require_active_part(root)
    except RuntimeError:
        return root.CreateEmptyPart("PhysProps_Demo", False)

def _ensure_body(part) -> None:
    if part.Bodies.Count > 0:
        return
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "AutoBase")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 3.0, 0.0)
        sk.Figures.AddLine(3.0, 0.0, 3.0, 2.0)
        sk.Figures.AddLine(3.0, 2.0, 0.0, 2.0)
        sk.Figures.AddLine(0.0, 2.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 1.0, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "AutoBlock", "AutoDepth", "",
    )

def main() -> None:
    root = connect()
    part = _active_or_new_part(root)
    _ensure_body(part)

    props = part.PhysicalProperties(ADAccuracySetting.AD_HIGH)

    print(f"Part: {part.Name}")
    try:
        material_repr = repr(props.Material)
    except Exception as exc:  # noqa: BLE001
        material_repr = f"<unavailable: {type(exc).__name__}>"
    print(f"Material:      {material_repr}")
    print(f"Volume:        {props.Volume:.4f} cm^3")
    print(f"Mass:          {props.Mass:.4f}  (mass units = {part.DesignProperties.MassUnits})")
    print(f"Surface area:  {props.SurfaceArea:.4f} cm^2")
    print(f"Faces / Edges / Vertices: {props.FacesCount} / {props.EdgesCount} / {props.VerticesCount}")

    cx, cy, cz = props.GetCenterOfGravity()
    print(f"Center of gravity: ({cx:.4f}, {cy:.4f}, {cz:.4f}) cm")

    pmin, pmax = props.GetExtents()
    print(f"Bounding box: "
          f"min ({pmin.X:.3f}, {pmin.Y:.3f}, {pmin.Z:.3f})  "
          f"max ({pmax.X:.3f}, {pmax.Y:.3f}, {pmax.Z:.3f}) cm")

    ixx, iyy, izz, iyz, izx, ixy = props.GetMomentsOfInertia()
    print("Moments of inertia (about COG):")
    print(f"  Ixx={ixx:.4e}  Iyy={iyy:.4e}  Izz={izz:.4e}")
    print(f"  Iyz={iyz:.4e}  Izx={izx:.4e}  Ixy={ixy:.4e}")

    p1, p2, p3 = props.GetPrincipalMomentsOfInertia()
    print(f"Principal moments: ({p1:.4e}, {p2:.4e}, {p3:.4e})")

if __name__ == "__main__":
    sys.exit(run_example(main))
