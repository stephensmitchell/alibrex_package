"""Example 05: add fillets and a through-hole to the active part.

Demonstrates:
- IObjectCollector to bundle edges
- AddConstantRadiusFilletFeature
- A sketched hole using AddSimpleHole
"""
from __future__ import annotations

import sys

from alibrex import (
    ADDirectionType,
    ADHoleDepthCondition,
    ADPartFeatureEndCondition,
    connect,
    run_example,
    require_active_part,
)

def _bootstrap_block(part) -> None:
    """If the active part has no body, sketch + extrude a small block so
    there's something to fillet / drill."""
    if part.Bodies.Count > 0:
        return
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "AutoBase")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 4.0, 0.0)
        sk.Figures.AddLine(4.0, 0.0, 4.0, 3.0)
        sk.Figures.AddLine(4.0, 3.0, 0.0, 3.0)
        sk.Figures.AddLine(0.0, 3.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 2.0, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "AutoBlock", "AutoDepth", "",
    )

def _active_or_new_part(root):
    try:
        return require_active_part(root)
    except RuntimeError:
        return root.CreateEmptyPart("Holes_Fillets_Demo", False)

def main() -> None:
    root = connect()
    part = _active_or_new_part(root)
    _bootstrap_block(part)
    body = part.Bodies.Item(0)

    edges = root.NewObjectCollector()
    for i in range(body.Edges.Count):
        edges.Add(body.Edges.Item(i))

    fillet = part.Features.AddConstantRadiusFilletFeature(
        edges,
        0.2,
        True,
        "",
        "Fillets",
    )

    print(f"Created {fillet.Name} on {edges.Count} edges.")

    xy = part.DesignPlanes.Item(0)
    hole_sketch = part.Sketches.AddSketch(None, xy, "HoleCenter")
    hole_sketch.BeginChange()
    try:
        hole_sketch.Figures.AddSketchPoint(1.0, 1.0)
    finally:
        hole_sketch.EndChange()

    hole = part.Features.AddSimpleHole(
        hole_sketch,
        0.0,
        0.5,
        True,
        None,
        ADHoleDepthCondition.AD_HOLE_THROUGH_ALL,
        None, None, 0.0,
        "Hole_1",
        "",
    )
    print(f"Created {hole.Name}")

if __name__ == "__main__":
    sys.exit(run_example(main))
