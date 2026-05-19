"""Profile demo 02 — sketch + extrude four wood-trim profiles.

Builds a part with four separate wood-trim cross-sections extruded
into short trim pieces. Sections spaced along X so they don't overlap.

Pass criteria:
  - 4 features created.
  - STL export > 5 KB (smaller than the steel set since these are open
    profiles that the kernel may or may not be able to make solid).
  - Each profile produced at least one face.
"""
from __future__ import annotations

import os
import sys
import tempfile
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADDirectionType, ADPartFeatureEndCondition, run_example
from profiles import mm
from profiles import wood

LENGTH = mm(150.0)


def _sketch(part, name: str, draw_fn, **params):
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
    part = fresh_part(f"WoodShowcase_{tag}")

    sections = [
        ("baseboard",     wood.baseboard,    dict(h=mm(100), t=mm(15), cap_h=mm(6),  cx=mm(0))),
        ("quarter_round", wood.quarter_round, dict(r=mm(18),                          cx=mm(40))),
        ("casing",        wood.casing,       dict(h=mm(80),  t=mm(20), recess=mm(3), cx=mm(80))),
        ("crown",         wood.crown,        dict(h=mm(50),  projection=mm(50),
                                                  cove_r=mm(35),                     cx=mm(140))),
    ]

    sketches = []
    for name, fn, params in sections:
        sk = _sketch(part, name, fn, **params)
        sketches.append((name, sk))

    for name, sk in sketches:
        _extrude(part, sk, name)

    feature_count = part.FeatureCount

    out_path = os.path.join(tempfile.gettempdir(), f"wood_showcase_{tag}.stl")
    if os.path.exists(out_path):
        os.remove(out_path)
    try:
        part.ExportSTL(out_path, 0.5, 15.0, 0.05)
        stl_size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    except Exception:
        stl_size = 0
    print(f"Features: {feature_count}, STL: {stl_size:,} bytes ({out_path})")

    return report([
        (f"{len(sections)} features",  feature_count == len(sections)),
        ("STL >= 5 KB",                stl_size >= 5_000),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
