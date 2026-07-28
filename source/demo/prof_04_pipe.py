"""Profile demo 04: pipe annulus extrusion + revolved reducer + flange.

Three sub-builds in the same part:

  1. Pipe annulus extruded into a 200 mm straight pipe (sketch on XY,
     extrude along Z).
  2. Reducer half-profile revolved 360° about the X-axis to produce an
     axisymmetric reducer body.
  3. Flange half-profile revolved 360° about the X-axis (a slip-on
     flange without bolt holes).

Each is sketched on its own plane so the three results sit side by
side in 3D.

Pass criteria:
  - 3 features total.
  - Each revolve uses ``math.radians(360)`` (S9: Alibre takes radians).
  - STL exports >= 10 KB.
"""
from __future__ import annotations

import math
import os
import sys
import tempfile
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADDirectionType, ADPartFeatureEndCondition, run_example
from profiles import mm
from profiles import pipe as pipe_profiles

PIPE_LENGTH = mm(200.0)

def _sketch_on(part, plane, name: str, draw_fn, **params):
    sk = part.Sketches.AddSketch(None, plane, name)
    sk.BeginChange()
    try:
        draw_fn(sk, **params)
    finally:
        sk.EndChange()
    return sk

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PipeFittings_{tag}")
    xy = part.DesignPlanes.Item(0)
    x_axis = part.DesignAxes.Item(0)

    pipe_sk = _sketch_on(part, xy, "PipeProfile", pipe_profiles.pipe_annulus,
                         od=mm(50), wall=mm(4), cx=mm(0))
    part.Features.AddExtrudedBoss(
        pipe_sk, PIPE_LENGTH, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Pipe", "PipeLen", "",
    )

    reducer_sk = _sketch_on(part, xy, "ReducerProfile", pipe_profiles.reducer_half,
                            od_in=mm(60), od_out=mm(40),
                            length=mm(80), wall_in=mm(4),
                            cx=mm(150))
    part.Features.AddRevolvedBoss(
        reducer_sk, None, x_axis, math.radians(360.0), "Reducer",
    )

    flange_sk = _sketch_on(part, xy, "FlangeProfile", pipe_profiles.flange_face,
                           od=mm(120), id_bore=mm(50), hub_od=mm(80),
                           face_thk=mm(15), hub_len=mm(30),
                           cx=mm(280))
    part.Features.AddRevolvedBoss(
        flange_sk, None, x_axis, math.radians(360.0), "Flange",
    )

    feature_count = part.FeatureCount
    body_count = part.Bodies.Count

    out_path = os.path.join(tempfile.gettempdir(), f"pipe_fittings_{tag}.stl")
    if os.path.exists(out_path):
        os.remove(out_path)
    try:
        part.ExportSTL(out_path, 0.5, 15.0, 0.05)
        stl_size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    except Exception:
        stl_size = 0
    print(f"Features: {feature_count}, Bodies: {body_count}, STL: {stl_size:,} bytes ({out_path})")

    return report([
        ("3 features",        feature_count == 3),
        ("at least 1 body",   body_count >= 1),
        ("STL >= 10 KB",      stl_size >= 10_000),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
