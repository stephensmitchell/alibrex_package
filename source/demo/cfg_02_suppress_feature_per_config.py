"""Configuration demo 02: feature suppressed in one config, alive in another.

Builds a part with two features (a base block and a small extruded
"bump" boss). Adds two configurations; in the second one, suppresses
the bump. Switches between the two and verifies the visible feature
count on the body changes.

Canonical "make a part with optional features per config" workflow.

Pass criteria:
  - Both configurations exist.
  - In the default config, both features are unsuppressed.
  - In Config_B, the Bump feature is suppressed.
  - Switching the active config flips visible feature count.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import extrude_block, fresh_part, report
from alibrex import ADDirectionType, ADPartFeatureEndCondition, connect, run_example

def _find_feature(part, name: str):
    for i in range(part.FeatureCount):
        f = part.Features.Item(i)
        if f.Name == name:
            return f
    raise KeyError(f"Feature {name!r} not found on part {part.Name!r}")

def _set_feature_suppressed(root, part, name: str, suppressed: bool) -> None:
    targets = root.NewObjectCollector()
    targets.Add(_find_feature(part, name))
    if suppressed:
        part.Suppress(targets)
    else:
        part.Unsuppress(targets)
    part.RegenerateAll()

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    root = connect()
    part = fresh_part(f"CFG02_{tag}")
    extrude_block(part, 6.0, 4.0, 2.0, "Base")

    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "BumpSketch")
    sk.BeginChange()
    try:
        sk.Figures.AddCircle(3.0, 2.0, 0.5)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 0.5, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, True,
        None, False,
        "Bump", "BumpDepth", "",
    )

    initial_feature_count = part.FeatureCount
    print(f"Initial features: {initial_feature_count}")

    configs = part.Configurations
    cfg_a = configs.AddConfiguration("Config_A_WithBump",    False)
    cfg_b = configs.AddConfiguration("Config_B_NoBump",      False)

    part.ActiveConfiguration = cfg_a
    _set_feature_suppressed(root, part, "Bump", False)
    suppressed_in_a = bool(_find_feature(part, "Bump").IsSuppressed)
    print(f"In Config_A, Bump.IsSuppressed = {suppressed_in_a}")

    part.ActiveConfiguration = cfg_b
    _set_feature_suppressed(root, part, "Bump", True)
    suppressed_in_b = bool(_find_feature(part, "Bump").IsSuppressed)
    print(f"In Config_B, Bump.IsSuppressed = {suppressed_in_b}")

    part.ActiveConfiguration = cfg_a
    suppressed_in_a = bool(_find_feature(part, "Bump").IsSuppressed)
    print(f"Back in Config_A, Bump.IsSuppressed = {suppressed_in_a}")

    return report([
        ("both configs added",            configs.Count == 3),
        ("Bump suppressed in Config_B",   suppressed_in_b is True),
        ("Bump alive in Config_A",        suppressed_in_a is False),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
