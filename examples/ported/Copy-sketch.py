"""Port of AlibreScript ``Copy-sketch.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/copy-sketch

AlibreScript ``Sketch.CopyFrom(other, ...)`` clones a sketch onto a new
plane with optional translation/rotation/scale arguments. AlibreX has
no clone-sketch primitive; the port re-emits the same primitives on the
new plane. Sketch primitives are 2D and live in the new plane's local
frame, so the same numeric coords suffice for a straight copy.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example
def _add_outline(sketch) -> None:
    # Original "AddLines([0,10,0,0,10,0,10,10], False)": 3 connected segments.
    sketch.Figures.AddLine(0.0, 10.0, 0.0,  0.0)
    sketch.Figures.AddLine(0.0,  0.0, 10.0, 0.0)
    sketch.Figures.AddLine(10.0, 0.0, 10.0, 10.0)
    # 180-degree arc on top
    sketch.Figures.AddCircularArcByCenterStartAngle(5.0, 10.0, 10.0, 10.0,
                                                    3.14159265358979)


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("MyPart", False)
    xy = part.DesignPlanes.Item(0)
    yz = part.DesignPlanes.Item(1)

    s1 = part.Sketches.AddSketch(None, xy, "Sketch1")
    _add_outline(s1)
    s2 = part.Sketches.AddSketch(None, yz, "Sketch2")
    _add_outline(s2)
    print("Re-emitted the same outline onto two planes.")


if __name__ == "__main__":
    sys.exit(run_example(main))
