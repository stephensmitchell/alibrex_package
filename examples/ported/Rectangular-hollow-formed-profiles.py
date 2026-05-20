"""Port of AlibreScript ``Rectangular-hollow-formed-profiles.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/rectangular-hollow-formed-profiles

Rectangular hollow hot/cold formed profile per BS/EN-10210-2:1997 and
BS/EN-10219:1997. Tables abbreviated for brevity - extend
``HOT_DATA`` / ``COLD_DATA`` from the source article as needed.

Same simplifications as ``Square-hollow-formed-profiles.py``: explicit
inner rectangle instead of ``CopyFrom``, fillets applied to every
Z-aligned corner edge by midpoint position.
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
from alibrex.dialogs import InputType, options_dialog
MM = 0.1

# (size_mm, width_mm) -> list of (thick_mm, ro_mm, ri_mm)
HOT_DATA = {
    (50.0, 25.0): [(2.5, 3.75, 2.5), (3.0, 4.5, 3.0)],
    (50.0, 30.0): [(2.5, 3.75, 2.5), (3.0, 4.5, 3.0), (4.0, 6.0, 4.0)],
    (60.0, 40.0): [(2.5, 3.75, 2.5), (3.0, 4.5, 3.0), (4.0, 6.0, 4.0)],
    (80.0, 40.0): [(3.0, 4.5, 3.0), (4.0, 6.0, 4.0), (5.0, 7.5, 5.0)],
    (100.0, 50.0): [(3.0, 4.5, 3.0), (4.0, 6.0, 4.0), (5.0, 7.5, 5.0)],
    (100.0, 60.0): [(3.0, 4.5, 3.0), (4.0, 6.0, 4.0), (5.0, 7.5, 5.0)],
}
COLD_DATA = {
    (50.0, 25.0): [(2.0, 4.0, 2.0), (2.5, 5.0, 2.5)],
    (60.0, 40.0): [(2.0, 4.0, 2.0), (3.0, 6.0, 3.0), (4.0, 8.0, 4.0)],
    (80.0, 40.0): [(2.5, 5.0, 2.5), (3.0, 6.0, 3.0), (5.0, 10.0, 5.0)],
    (100.0, 50.0): [(3.0, 6.0, 3.0), (4.0, 8.0, 4.0), (5.0, 10.0, 5.0)],
}


def main() -> None:
    hot_keys = list(HOT_DATA.keys())
    cold_keys = list(COLD_DATA.keys())
    values = options_dialog(
        "Rectangular Hollow Profile",
        [
            ["Type",          InputType.StringList, ["Hot", "Cold"], "Hot"],
            ["Section",       InputType.StringList,
             [f"{h:.0f}x{w:.0f}" for h, w in hot_keys], f"{hot_keys[0][0]:.0f}x{hot_keys[0][1]:.0f}"],
            ["Thickness idx", InputType.Integer,    0],
            ["Length (mm)",   InputType.Real,       200.0],
        ],
    )
    if values is None:
        sys.exit("User cancelled")
    type_idx, section_idx, thick_idx, length_mm = values
    table = HOT_DATA if type_idx == 0 else COLD_DATA
    section_keys = list(table.keys())
    height_mm, width_mm = section_keys[section_idx % len(section_keys)]
    thicknesses = table[(height_mm, width_mm)]
    thick_mm, ro_mm, ri_mm = thicknesses[thick_idx % len(thicknesses)]

    width = width_mm * MM
    height = height_mm * MM
    thick = thick_mm * MM
    length = length_mm * MM

    root = connect()
    part = root.CreateEmptyPart(
        f"Hollow Section {height_mm:.0f}x{width_mm:.0f}x{thick_mm}x{length_mm:.0f}", False,
    )
    xy = part.DesignPlanes.Item(0)
    profile = part.Sketches.AddSketch(None, xy, "Profile")
    # outer rectangle (X = width, Y = height)
    profile.Figures.AddRectangle(-width/2, -height/2,  width/2,  height/2)
    profile.Figures.AddRectangle(
        -(width/2) + thick, -(height/2) + thick,
         (width/2) - thick,  (height/2) - thick,
    )

    part.Features.AddExtrudedBoss(
        profile, length, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Extrude", "Length", "",
    )

    # Fillet the eight Z-aligned corner edges (4 outer, 4 inner) by
    # midpoint. Don't cache `body` - KNOWN_ISSUES.md S2.
    edges = part.Bodies.Item(0).Edges
    outer = root.NewObjectCollector()
    inner = root.NewObjectCollector()
    for i in range(edges.Count):
        e = edges.Item(i)
        a, b = e.StartVertex.Point, e.EndVertex.Point
        if abs(a.Z - b.Z) < 1e-6:
            continue
        mx = 0.5 * (a.X + b.X)
        my = 0.5 * (a.Y + b.Y)
        if abs(abs(mx) - width/2) < 1e-4 and abs(abs(my) - height/2) < 1e-4:
            outer.Add(e)
        elif (abs(abs(mx) - (width/2 - thick)) < 1e-4
              and abs(abs(my) - (height/2 - thick)) < 1e-4):
            inner.Add(e)
    if outer.Count:
        part.Features.AddConstantRadiusFilletFeature(
            outer, ro_mm * MM, False, "OuterRad", "Outer Fillet",
        )
    if inner.Count:
        part.Features.AddConstantRadiusFilletFeature(
            inner, ri_mm * MM, False, "InnerRad", "Inner Fillet",
        )
    print(f"Built RHS {height_mm:.0f}x{width_mm:.0f}x{thick_mm} mm, "
          f"{length_mm:.0f} mm long.")


if __name__ == "__main__":
    sys.exit(run_example(main))
