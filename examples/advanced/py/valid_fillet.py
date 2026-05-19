"""Port of "valid fillet" AlibreScript example.

Creates a 40 x 20 x 10 mm block, then applies a 2 mm constant-radius
fillet to the four top edges (the AlibreScript original picked a single
hardcoded ``Edge<6>`` — alibrex doesn't expose names, so we pick edges
by geometry instead).
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example
from _porting_utils import (
    extrude_boss,
    mm,
    new_part,
    sketch_rectangle,
    top_edges_indices,
    xy_plane,
)

W = mm(40.0)
H = mm(20.0)
D = mm(10.0)
RADIUS = mm(2.0)


def main() -> None:
    root = connect()
    part = new_part("BlockForFillet")

    sketch = sketch_rectangle(part, xy_plane(part), "SketchBlock", 0.0, 0.0, W, H)
    extrude_boss(part, sketch, D, "BlockExtrusion")

    # Pick the 4 top edges by geometry (AlibreScript used Edge<6>).
    top_idxs = top_edges_indices(part, n=4)
    print(f"Top-edge indices: {top_idxs}")

    edges_col = root.NewObjectCollector()
    edges_fresh = part.Bodies.Item(0).Edges
    for i in top_idxs:
        edges_col.Add(edges_fresh.Item(i))

    part.Features.AddConstantRadiusFilletFeature(
        edges_col, RADIUS, True, "", "MyFillet",
    )
    print(f"Fillet applied: radius {RADIUS} cm on {edges_col.Count} edge(s).")


if __name__ == "__main__":
    sys.exit(run_example(main))
