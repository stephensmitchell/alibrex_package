"""Port of "valid chamfer" AlibreScript example.

Creates a 40 x 20 x 10 mm block, then applies a 2 mm equal-distance
chamfer to the four top edges (AlibreScript original hard-coded
``Edge<6>`` — picked geometrically here instead).
"""
from __future__ import annotations

import sys

from alibrex import ADEdgeChamferType, connect, run_example
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
CHAMFER = mm(2.0)


def main() -> None:
    root = connect()
    part = new_part("BlockForChamfer")

    sketch = sketch_rectangle(part, xy_plane(part), "BlockSketch", 0.0, 0.0, W, H)
    extrude_boss(part, sketch, D, "BlockExtrusion")

    top_idxs = top_edges_indices(part, n=4)
    print(f"Top-edge indices: {top_idxs}")

    edges_col = root.NewObjectCollector()
    edges_fresh = part.Bodies.Item(0).Edges
    for i in top_idxs:
        edges_col.Add(edges_fresh.Item(i))

    part.Features.AddEdgeChamferFeature(
        edges_col,
        ADEdgeChamferType.AD_EQUAL_DISTANCE,
        CHAMFER, CHAMFER, 0.0,
        True,
        "", "", "",
        "MyChamfer",
    )
    print(f"Chamfer applied: {CHAMFER} cm on {edges_col.Count} edge(s).")


if __name__ == "__main__":
    sys.exit(run_example(main))
