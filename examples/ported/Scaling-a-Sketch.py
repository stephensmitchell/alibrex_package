"""Port of AlibreScript ``Scaling-a-Sketch.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/scaling-a-sketch

The original uses ``Sketch.CopyFrom(other, ox, oy, oz, rx, ry, rz, ra,
scalePercent)`` which AlibreX has no equivalent for. The closest stable
substitute is ``AddScaleFeature`` (scales the *part body* rather than
the sketch), which is what we expose here.

If you genuinely need to scale a sketch's 2D figures, iterate through
the source sketch's ``Figures`` collection and recreate each figure on
the target plane with coordinates multiplied by your scale factor.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example, require_active_part
SCALE_FACTOR = 4.125 / 8.25

def main() -> None:
    root = connect()
    part = require_active_part(root)
    feat = part.Features.AddScaleFeature(
        True,            # scale about centroid
        True,            # uniform
        SCALE_FACTOR,
        SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR,
        "Scale", "", "", "",
        "TestRoomScale",
    )
    print(f"Added uniform scale feature '{feat.Name}' "
          f"(factor={SCALE_FACTOR:.4f}).")


if __name__ == "__main__":
    sys.exit(run_example(main))
