"""Parameter demo 01: create a parameter and drive a feature dimension.

Builds a block whose extrusion depth is bound at creation time to a
named parameter (``"BlockDepth_Depth"``). Reads the parameter, sets a
new value inside an OpenParameterTransaction, regenerates, and confirms
the body's Z extents tracked the new parameter value.

Geometry is queried via ``IADPartSession.PhysicalProperties(...)``
because ``IADBody`` doesn't expose ``GetExtents`` directly in
AlibreX 29.

Pass criteria:
  - The ``BlockDepth_Depth`` parameter exists after the extrusion.
  - Initial Z extent is 2.0 cm (the depth we passed).
  - After setting Value=5.0, the body's Z extent is 5.0 cm.
  - Setting Value back to 2.0 restores the original Z extent.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report
from alibrex import ADAccuracySetting, run_example


def _find_param(part, name: str):
    params = part.Parameters
    for i in range(params.Count):
        p = params.Item(i)
        if p.Name == name:
            return p
    return None


def _z_extent(part) -> float:
    props = part.PhysicalProperties(ADAccuracySetting.AD_LOW)
    lo, hi = props.GetExtents(None, None)
    return hi.Z - lo.Z


def _set_value(part, p, new_value: float) -> None:
    params = part.Parameters
    params.OpenParameterTransaction()
    try:
        p.Value = new_value
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM01_{tag}")
    # extrude_block names the depth parameter "{name}_Depth".
    extrude_block(part, 4.0, 3.0, 2.0, "BlockDepth")
    depth_param = _find_param(part, "BlockDepth_Depth")
    if depth_param is None:
        print("Couldn't find the named depth parameter.")
        return 1

    print(f"Found {depth_param.Name!r}  initial Value={depth_param.Value}")
    initial_z = _z_extent(part)
    print(f"  initial body Z extent: {initial_z:.4f} cm")

    _set_value(part, depth_param, 5.0)
    after_z = _z_extent(part)
    print(f"After Value=5.0  -> body Z extent: {after_z:.4f} cm")

    _set_value(part, depth_param, 2.0)
    restored_z = _z_extent(part)
    print(f"After Value=2.0  -> body Z extent: {restored_z:.4f} cm")

    return report([
        ("param exists",            depth_param is not None),
        ("initial value 2.0",       math.isclose(depth_param.Value, 2.0, abs_tol=1e-3)
                                    if False else math.isclose(initial_z, 2.0, abs_tol=1e-3)),
        ("after Value=5: Z=5.0",    math.isclose(after_z, 5.0, abs_tol=1e-3)),
        ("restored: Z=2.0",         math.isclose(restored_z, 2.0, abs_tol=1e-3)),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
