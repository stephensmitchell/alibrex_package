"""Port of AlibreScript ``Profile-and-Sweep-Path.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/profile-and-sweep-path

The AlibreScript original only sketches the profile and the path; it
does not call ``AddSweptBoss``. This port matches that
behaviour and prints the resulting sketch counts so the geometry can be
inspected. (See `python/examples/15_sweep.py` for the full sweep.)
"""
from __future__ import annotations

import sys
from pathlib import Path
from alibrex import connect, run_example, float_array

PATH_POINTS = [
    0.0, 0.0, 0.0,
    0.5, 0.0, 0.0,
    1.0, 0.5, 0.5,
    1.5, 1.0, 0.5,
    1.5, 1.5, 1.5,
]
PROFILE_RADIUS_CM = 0.5

def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Test", False)
    yz = part.DesignPlanes.Item(1)

    path = part.Sketches3D.Add3DSketch("Pipe Route")
    path.Figures.AddBsplineByInterpolation(float_array(PATH_POINTS))

    profile = part.Sketches.AddSketch(None, yz, "Start Profile")
    profile.Figures.AddCircle(0.0, 0.0, PROFILE_RADIUS_CM)

    print(f"Built {part.Sketches3D.Count} 3D sketch(es) and "
          f"{part.Sketches.Count} 2D sketch(es) on '{part.Name}'.")

if __name__ == "__main__":
    sys.exit(run_example(main))
