"""Port of AlibreScript ``Square-hollow-formed-profiles.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/square-hollow-formed-profiles

Square hollow hot/cold formed profiles per BS/EN-10210-2:1997 and
BS/EN-10219:1997. Tables abbreviated to the smaller sizes;
extend ``HOT_DATA`` / ``COLD_DATA`` from the original article as needed.

The original ``Sketch.CopyFrom(Profile,0,0,0,0,0,0,0,scaleFactor)``
(copy-and-scale onto the same sketch) is replaced with a second
explicit inner rectangle. The original ``AddFillet`` by named edges
becomes a fillet of all eight vertical-axis (Z) corner edges of the
extruded prism.
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

# Subset of the original tables: extend as needed.
HOT_DATA = {
    20: [(2.0, 0.3, 0.2), (2.5, 0.375, 0.25)],
    25: [(2.0, 0.3, 0.2), (2.5, 0.375, 0.25), (3.0, 0.45, 0.3)],
    40: [(2.5, 0.375, 0.25), (3.0, 0.45, 0.3), (4.0, 0.6, 0.4), (5.0, 0.75, 0.5)],
    50: [(2.5, 0.375, 0.25), (3.0, 0.45, 0.3), (5.0, 0.75, 0.5), (6.0, 0.9, 0.6)],
}
COLD_DATA = {
    20: [(2.0, 0.4, 0.2), (2.5, 0.5, 0.25)],
    25: [(2.0, 0.4, 0.2), (2.5, 0.5, 0.25), (3.0, 0.6, 0.3)],
    40: [(2.0, 0.4, 0.2), (3.0, 0.6, 0.3), (4.0, 0.8, 0.4)],
    50: [(2.0, 0.4, 0.2), (3.0, 0.6, 0.3), (4.0, 0.8, 0.4), (5.0, 1.0, 0.5)],
}


def main() -> None:
    values = options_dialog(
        "Square Hollow Profile",
        [
            ["Type",          InputType.StringList, ["Hot", "Cold"], "Hot"],
            ["Size (mm)",     InputType.StringList, ["20", "25", "40", "50"], "25"],
            ["Thickness idx", InputType.Integer,    0],
            ["Length (mm)",   InputType.Real,       100.0],
        ],
    )
    if values is None:
        sys.exit("User cancelled")
    type_idx, size_idx, thick_idx, length_mm = values
    table = HOT_DATA if type_idx == 0 else COLD_DATA
    sizes = sorted(table.keys())
    size_mm = sizes[size_idx]
    thicknesses = table[size_mm]
    thick_mm, ro_mm, ri_mm = thicknesses[thick_idx % len(thicknesses)]

    size, thick, length = size_mm * MM, thick_mm * MM, length_mm * MM

    root = connect()
    part = root.CreateEmptyPart(
        f"Hollow Section {size_mm}x{thick_mm}x{length_mm:.0f}", False,
    )
    xy = part.DesignPlanes.Item(0)
    profile = part.Sketches.AddSketch(None, xy, "Profile")
    h = size / 2.0
    # outer square
    profile.Figures.AddRectangle(-h, -h, h, h)
    # inner square
    inner = h - thick
    profile.Figures.AddRectangle(-inner, -inner, inner, inner)

    part.Features.AddExtrudedBoss(
        profile, length, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False, "Extrude", "Length", "",
    )

    # Apply outer and inner fillets to all Z-aligned edges (vertical corners)
    body = part.Bodies.Item(0)
    outer_edges = root.NewObjectCollector()
    inner_edges = root.NewObjectCollector()
    for i in range(body.Edges.Count):
        e = body.Edges.Item(i)
        a, b = e.StartVertex.Point, e.EndVertex.Point
        dz = abs(a.Z - b.Z)
        if dz < 1e-6:
            continue   # only Z-aligned (vertical) corner edges
        x_mid = 0.5 * (a.X + b.X)
        y_mid = 0.5 * (a.Y + b.Y)
        # outer if near +/-h, inner if near +/-inner
        if abs(abs(x_mid) - h) < 1e-4 and abs(abs(y_mid) - h) < 1e-4:
            outer_edges.Add(e)
        elif abs(abs(x_mid) - inner) < 1e-4 and abs(abs(y_mid) - inner) < 1e-4:
            inner_edges.Add(e)

    if outer_edges.Count:
        part.Features.AddConstantRadiusFilletFeature(
            outer_edges, ro_mm * MM, False, "OuterRad", "Outer Fillet",
        )
    if inner_edges.Count:
        part.Features.AddConstantRadiusFilletFeature(
            inner_edges, ri_mm * MM, False, "InnerRad", "Inner Fillet",
        )
    print(f"Built {size_mm}x{size_mm}x{thick_mm} mm hollow section, "
          f"{length_mm:.0f} mm long; filleted {outer_edges.Count} outer "
          f"and {inner_edges.Count} inner corners.")


if __name__ == "__main__":
    sys.exit(run_example(main))
