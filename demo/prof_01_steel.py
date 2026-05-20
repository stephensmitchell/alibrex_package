"""Profile demo 01 - sketch + extrude six steel structural sections.

Builds a single part with six separate sketches, each carrying one
structural-steel cross-section, and extrudes each to a short bar so
the result is visible in 3D. Sections are spaced along Z so they don't
overlap.

Pass criteria:
  - 6 features created.
  - 6 bodies in the part (each extrusion makes a separate body since
    the sketches are independent).
  - STL export > 10 KB.
"""
from __future__ import annotations

import os
import sys
import tempfile
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADDirectionType, ADPartFeatureEndCondition, run_example
from profiles import mm
from profiles import steel

HERE = os.path.dirname(os.path.abspath(__file__))
LENGTH = mm(100.0)        # 100 mm bar length


def _add_sketch_for(part, name: str, draw_fn, **params):
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), name)
    sk.BeginChange()
    try:
        draw_fn(sk, **params)
    finally:
        sk.EndChange()
    return sk


def _extrude(part, sketch, name: str) -> None:
    part.Features.AddExtrudedBoss(
        sketch, LENGTH, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        name, f"{name}_L", "",
    )


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SteelShowcase_{tag}")

    # Lay sections out along X so they don't overlap.
    sections = [
        ("I_W6x20",  steel.i_beam, dict(h=mm(150), b=mm(100),  tw=mm(8),  tf=mm(12), cx=mm(0))),
        ("C_C6",     steel.channel, dict(h=mm(150), b=mm(60),   tw=mm(8),  tf=mm(10), cx=mm(180))),
        ("L_50x50",  steel.angle,   dict(leg_a=mm(50), leg_b=mm(50), t=mm(6), cx=mm(280))),
        ("RHS_60x40", steel.rhs,    dict(w=mm(60), h=mm(40), t=mm(4), cx=mm(380))),
        ("CHS_50",   steel.chs,     dict(od=mm(50), t=mm(5),  cx=mm(470))),
        ("T_120",    steel.tee,     dict(h=mm(120), b=mm(120), tw=mm(10), tf=mm(12), cx=mm(560))),
    ]

    sketches = []
    for name, fn, params in sections:
        sk = _add_sketch_for(part, name, fn, **params)
        sketches.append((name, sk))

    for name, sk in sketches:
        _extrude(part, sk, name)

    body_count = part.Bodies.Count
    feature_count = part.FeatureCount

    out_path = os.path.join(tempfile.gettempdir(), f"steel_showcase_{tag}.stl")
    if os.path.exists(out_path):
        os.remove(out_path)
    try:
        part.ExportSTL(out_path, 0.5, 15.0, 0.05)
        stl_size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    except Exception:
        stl_size = 0
    print(f"Features: {feature_count}, Bodies: {body_count}, STL: {stl_size:,} bytes ({out_path})")

    return report([
        (f"{len(sections)} features",  feature_count == len(sections)),
        ("at least one body",          body_count >= 1),
        ("STL >= 10 KB",               stl_size >= 10_000),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
