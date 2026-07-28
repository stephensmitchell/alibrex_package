"""CRUD demo 02: parameter create/update/read-back on a demo part.

Creates a fresh part and extrudes a small block so there's a Depth
parameter to drive.

Pass criteria:
  - A user parameter 'CRUD02_Stretch' is created.
  - After committing 'Depth = CRUD02_Stretch * 2' with Stretch=1.0, the
    Depth parameter on the extrusion reads ~2.0.
  - After bumping Stretch to 2.5, Depth reads ~5.0 after RegenerateAll.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import part_or_open, report
from alibrex import (
    ADDirectionType,
    ADParameterType,
    ADPartFeatureEndCondition,
    run_example,
)

def _find(params, name):
    for i in range(params.Count):
        p = params.Item(i)
        if p.Name == name:
            return p
    return None

def _equation_matches(actual: str, expected: str) -> bool:
    return "".join(actual.split()) == "".join(expected.split())

def _set_parameter_state(part, stretch_name: str, stretch_value: float,
                         depth_name: str, depth_equation: str | None = None) -> None:
    params = part.Parameters
    params.OpenParameterTransaction()
    try:
        stretch = _find(params, stretch_name)
        if stretch is None:
            raise KeyError(f"Parameter {stretch_name!r} not found")
        stretch.Value = stretch_value
        if depth_equation is not None:
            depth = _find(params, depth_name)
            if depth is None:
                raise KeyError(f"Parameter {depth_name!r} not found")
            depth.Equation = depth_equation
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()

def _ensure_extrusion_with_named_depth(part, depth_name: str) -> None:
    """If the part has no extrusion that owns a parameter called *depth_name*,
    add one so the demo has something to drive."""
    params = part.Parameters
    if _find(params, depth_name) is not None:
        return
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, f"CRUD02_Base_{uuid.uuid4().hex[:6]}")
    sk.BeginChange()
    try:
        figs = sk.Figures
        figs.AddLine(0.0, 0.0, 4.0, 0.0)
        figs.AddLine(4.0, 0.0, 4.0, 2.0)
        figs.AddLine(4.0, 2.0, 0.0, 2.0)
        figs.AddLine(0.0, 2.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 1.5, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        f"CRUD02_Block_{uuid.uuid4().hex[:6]}",
        depth_name, "",
    )

def main() -> int:
    part = part_or_open("CRUD02_ParamDrive")
    depth_name = "CRUD02_Depth"
    stretch_name = "CRUD02_Stretch"
    _ensure_extrusion_with_named_depth(part, depth_name)

    params = part.Parameters
    params.NewParameter(stretch_name, ADParameterType.AD_DISTANCE)
    stretch_found = _find(params, stretch_name) is not None
    depth = _find(params, depth_name)
    if depth is None:
        print(f"[FAIL] '{depth_name}' parameter missing after extrusion")
        return 1

    expected_equation = f"{stretch_name} * 2"
    _set_parameter_state(part, stretch_name, 1.0, depth_name, expected_equation)
    depth_after_1 = _find(part.Parameters, depth_name).Value

    _set_parameter_state(part, stretch_name, 2.5, depth_name)
    depth_param = _find(part.Parameters, depth_name)
    depth_after_2 = depth_param.Value
    depth_equation = depth_param.Equation

    print(f"Stretch param created : {stretch_found}")
    print(f"Depth equation        : {depth_equation!r}")
    print(f"Stretch=1.0  ->  Depth = {depth_after_1:.4f}  (expect ~2.0)")
    print(f"Stretch=2.5  ->  Depth = {depth_after_2:.4f}  (expect ~5.0)")

    return report([
        ("stretch created", stretch_found),
        ("equation set",    _equation_matches(depth_equation, expected_equation)),
        ("depth=2.0",       math.isclose(depth_after_1, 2.0, abs_tol=1e-6)),
        ("depth=5.0",       math.isclose(depth_after_2, 5.0, abs_tol=1e-6)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
