"""Example 16 - loft between two cross-section sketches.

Creates an offset reference plane parallel to XY, sketches a square on XY
and a smaller square on the offset plane, then lofts them. Exercises:
- IADDesignPlanes.CreateAtOffsetToPlane
- IADPartFeatures.AddLoftBoss
- IObjectCollector with multiple sketches
"""
from __future__ import annotations

import sys

from alibrex import ADLoftGuideType, IADPartSession, connect, run_example
BASE_SIZE_CM = 4.0
TOP_SIZE_CM = 1.5
HEIGHT_CM = 3.0


def square(sketch, size: float) -> None:
    h = size / 2.0
    sketch.BeginChange()
    try:
        f = sketch.Figures
        f.AddLine(-h, -h,  h, -h)
        f.AddLine( h, -h,  h,  h)
        f.AddLine( h,  h, -h,  h)
        f.AddLine(-h,  h, -h, -h)
    finally:
        sketch.EndChange()


def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("Loft_Demo", False)

    xy = part.DesignPlanes.Item(0)
    top_plane = part.DesignPlanes.CreateAtOffsetToPlane(
        None, xy, HEIGHT_CM, "TopPlane"
    )

    base = part.Sketches.AddSketch(None, xy, "Base")
    square(base, BASE_SIZE_CM)

    top = part.Sketches.AddSketch(None, top_plane, "Top")
    square(top, TOP_SIZE_CM)

    sections = root.NewObjectCollector()
    sections.Add(base)
    sections.Add(top)

    feat = part.Features.AddLoftBoss(
        sections,
        None, None, None,                # tangents / magnitudes / angles
        None,                            # guide curves
        ADLoftGuideType.AD_NONE,         # guide-curve type (no guides here)
        False, False, False, False,      # twist/curvature/simplify/connect-ends
        "Loft",
    )
    print(f"Created loft '{feat.Name}': "
          f"{BASE_SIZE_CM}cm sq -> {TOP_SIZE_CM}cm sq over {HEIGHT_CM} cm.")


if __name__ == "__main__":
    sys.exit(run_example(main))
