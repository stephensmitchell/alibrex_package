"""Port of AlibreScript ``Lofting-with-a-Guide-Curve.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/lofting-with-a-guide-curve

Two square cross-sections on parallel planes plus a 3D B-spline guide
curve, lofted together. AlibreScript ``GuideCurveTypes.Global`` -
``ADLoftGuideType.AD_GLOBAL``.
"""
from __future__ import annotations

import sys
from alibrex import ADLoftGuideType, connect, run_example, float_array


MM = 0.1


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("foo", False)

    xy = part.DesignPlanes.Item(0)
    top_plane = part.DesignPlanes.CreateAtOffsetToPlane(
        None, xy, 30 * MM, "Top Plane",
    )

    bottom = part.Sketches.AddSketch(None, xy, "Bottom")
    bottom.Figures.AddRectangle(0.0, 0.0, 10*MM, 10*MM)

    top = part.Sketches.AddSketch(None, top_plane, "Top")
    top.Figures.AddRectangle(0.0, 0.0, 50*MM, 50*MM)

    guide = part.Sketches3D.Add3DSketch("Guide")
    guide.Figures.AddBsplineByInterpolation(float_array([
        10*MM, 10*MM, 0.0,
        20*MM, 20*MM, 5*MM,
        45*MM, 45*MM, 15*MM,
        50*MM, 50*MM, 30*MM,
    ]))

    sections = root.NewObjectCollector()
    sections.Add(bottom)
    sections.Add(top)
    guides = root.NewObjectCollector()
    guides.Add(guide)

    part.Features.AddLoftBoss(
        sections, None, None, None, guides,
        ADLoftGuideType.AD_GLOBAL, True, False, False, False,
        "Loft Test",
    )
    print("Lofted two squares with a guide curve.")


if __name__ == "__main__":
    sys.exit(run_example(main))
