"""Port of AlibreScript ``Supressing-Unsupressing-and-Removing-Features.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/supressing-unsupressing-and-removing-features
(filename typo preserved at the source; corrected here)

Builds a cube + through-hole, then exercises feature suppression and
deletion. Mapping:

- ``P.SuppressFeature('Cube')``: ``part.Features.Item('Cube').IsSuppressed = True``
- ``P.UnsuppressFeature(feat)``: ``feat.IsSuppressed = False``
- ``P.RemoveFeature('Hole')``: ``part.Features.Item('Hole').Delete()``
- ``P.RemoveSketch(sketch)``: ``sketch.Delete()``
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
def _extrude(part, sketch, name: str, depth: float, is_cut: bool):
    fn = part.Features.AddExtrudedCutout if is_cut else part.Features.AddExtrudedBoss
    return fn(
        sketch, depth, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        name, "Depth", "",
    )

def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Example Part", False)
    xy = part.DesignPlanes.Item(0)

    cube_sk = part.Sketches.AddSketch(None, xy, "CubeProfile")
    cube_sk.Figures.AddRectangle(0.0, 0.0, 1.0, 1.0)
    cube = _extrude(part, cube_sk, "Cube", 1.0, is_cut=False)

    hole_sk = part.Sketches.AddSketch(None, xy, "HoleProfile")
    hole_sk.Figures.AddRectangle(0.2, 0.2, 0.8, 0.8)
    _extrude(part, hole_sk, "Hole", 1.0, is_cut=True)

    print(f"Before: features={part.FeatureCount}, "
          f"cube.IsSuppressed={cube.IsSuppressed}")

    part.Features.Item("Cube").IsSuppressed = True
    print(f"Suppressed 'Cube' by name; cube.IsSuppressed={cube.IsSuppressed}")
    cube.IsSuppressed = False
    print(f"Unsuppressed via reference; cube.IsSuppressed={cube.IsSuppressed}")

    part.Features.Item("Hole").Delete()
    hole_sk.Delete()
    print(f"After delete: features={part.FeatureCount}, "
          f"sketches={part.Sketches.Count}")

if __name__ == "__main__":
    sys.exit(run_example(main))
