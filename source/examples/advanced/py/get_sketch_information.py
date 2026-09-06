"""Port of "Get Sketch Information" AlibreScript example.

Walks the active part's 3D sketches and prints each one's name, figure
count, and figure types. If no part is open, creates a demo part with
one populated 3D sketch so the script always has something to show.

Differences from the original:
  * AlibreScript's ``part.Get3DSketch("3D Sketch<N>")`` looked sketches
    up by their Alibre-assigned name; alibrex exposes them via
    ``part.Sketches3D.Item(i)`` indexed access, which is cleaner.
"""
from __future__ import annotations

import sys

from alibrex import run_example
from _porting_utils import mm, part_or_open

def _seed_demo_sketch(part) -> None:
    """Add a small 3D sketch so the script has something to inspect."""
    sk = part.Sketches3D.Add3DSketch("DemoSketch")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 0.0, mm(10), 0.0, mm(5))
        sk.Figures.AddPoint(mm(5), mm(5), 0.0)
    finally:
        sk.EndChange()

def main() -> int:
    part = part_or_open("SketchInfoDemo")
    if part.Sketches3D.Count == 0:
        _seed_demo_sketch(part)

    sketches3d = part.Sketches3D
    print(f"Part '{part.Name}': {sketches3d.Count} 3D sketch(es).")
    for i in range(sketches3d.Count):
        sk = sketches3d.Item(i)
        figs = sk.Figures
        fcount = figs.Count
        print("-" * 40)
        print(f"  [{i}] {sk.Name}  ({fcount} figure(s))")
        for j in range(fcount):
            fig = figs.Item(j)
            print(f"      Figure {j}: {type(fig).__name__}")
    return 0

if __name__ == "__main__":
    sys.exit(run_example(main))
