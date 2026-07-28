"""Example 15: sweep a circular profile along a path.

Demonstrates `IADPartFeatures.AddSweptBoss`. The profile sketch lives on a
plane that is perpendicular to the start of the path; here the path is a
line on the XY design plane running in +X, and the profile is a circle on
the YZ design plane centered on the path start.
"""
from __future__ import annotations

import sys

from alibrex import ADPartFeatureEndCondition, IADPartSession, connect, run_example
PATH_LEN_CM = 4.0
PROFILE_RADIUS_CM = 0.4

def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("Sweep_Demo", False)

    xy = part.DesignPlanes.Item(0)
    yz = part.DesignPlanes.Item(1)

    path = part.Sketches.AddSketch(None, xy, "SweepPath")
    path.BeginChange()
    try:
        path.Figures.AddLine(0.0, 0.0, PATH_LEN_CM, 0.0)
    finally:
        path.EndChange()

    profile = part.Sketches.AddSketch(None, yz, "SweepProfile")
    profile.BeginChange()
    try:
        profile.Figures.AddCircle(0.0, 0.0, PROFILE_RADIUS_CM)
    finally:
        profile.EndChange()

    paths = root.NewObjectCollector()
    paths.Add(path)

    feat = part.Features.AddSweptBoss(
        profile,
        paths,
        True,
        ADPartFeatureEndCondition.AD_ENTIRE_PATH,
        None, None, 0.0,
        None, False,
        "Sweep",
    )
    print(f"Created sweep '{feat.Name}' along {PATH_LEN_CM} cm path "
          f"with r={PROFILE_RADIUS_CM} cm profile.")
    print(f"Feature count: {part.FeatureCount}")

if __name__ == "__main__":
    sys.exit(run_example(main))
