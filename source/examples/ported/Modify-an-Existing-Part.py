"""Port of AlibreScript ``Modify-an-Existing-Part.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/modify-an-existing-part

Opens an existing part and adds a 3D B-spline sketch to it.
AlibreScript's ``Part(folder, name)`` becomes
``root.OpenFile(full_path)``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from alibrex import IADPartSession, connect, run_example, float_array

ROUTE_POINTS = [
    0.0, 0.0, 0.0,
    0.5, 0.0, 0.0,
    1.0, 0.5, 0.5,
    1.5, 1.0, 0.5,
    1.5, 1.5, 1.5,
]

def main() -> None:
    from _sample_inputs import ensure_sample_part
    parser = argparse.ArgumentParser()
    parser.add_argument("part_path", type=Path, nargs="?",
                        help="Path to a .AD_PRT file (defaults to the bundled sample)")
    args = parser.parse_args()
    part_path = args.part_path or ensure_sample_part()

    root = connect()
    session = root.OpenFile(str(part_path))
    part = cast(IADPartSession, session)

    route = part.Sketches3D.Add3DSketch("Route")
    route.Figures.AddBsplineByInterpolation(float_array(ROUTE_POINTS))
    print(f"Added 3D B-spline 'Route' to '{part.Name}'.")

if __name__ == "__main__":
    sys.exit(run_example(main))
