"""Port of AlibreScript ``Getting-User-Input.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/getting-user-input

The original prompts for ``Width``, ``Height``, and ``Depth`` one at a
time via ``Read()`` (console input). A single form dialog is friendlier.
It keeps the original's millimetre semantics by collecting
mm and dividing by 10 before handing values to AlibreX.
"""
from __future__ import annotations

import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
from alibrex.dialogs import InputType, error_dialog, options_dialog
def main() -> None:
    values = options_dialog(
        "Box dimensions (mm)",
        [
            ["Width (mm)",  InputType.Real, 50.0],
            ["Height (mm)", InputType.Real, 30.0],
            ["Depth (mm)",  InputType.Real, 10.0],
        ],
    )
    if values is None:
        sys.exit("User cancelled")

    width_mm, height_mm, depth_mm = values
    for label, v in zip(("Width", "Height", "Depth"), values):
        if v < 0.1:
            error_dialog(f"{label} must be at least 0.1 mm", "Box dimensions")
            sys.exit(f"{label} must be at least 0.1 mm")

    print(f"Creating a box {width_mm} x {height_mm} x {depth_mm} mm...")

    # AlibreX uses centimetres
    w, h, d = width_mm / 10.0, height_mm / 10.0, depth_mm / 10.0

    root = connect()
    part = root.CreateEmptyPart("My Part", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Profile")
    sketch.Figures.AddRectangle(0.0, 0.0, w, h)

    part.Features.AddExtrudedBoss(
        sketch, d, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Box", "Depth", "",
    )


if __name__ == "__main__":
    sys.exit(run_example(main))
