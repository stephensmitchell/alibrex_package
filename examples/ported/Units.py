"""Port of AlibreScript ``Units.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/units

AlibreScript has a global ``Units.Current`` that rescales every
subsequent literal: convenient, but stateful. AlibreX has no such
notion: every length is centimetres internally and you convert at the
call site. This port keeps the original *intent* (three circles of
known sizes) and shows the explicit conversions instead.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example
MM_TO_CM = 0.1
IN_TO_CM = 2.54


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("My Part", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Sketch")

    sketch.Figures.AddCircle(0.0, 0.0, 50 * MM_TO_CM)   # 50 mm
    sketch.Figures.AddCircle(0.0, 0.0, 1.34 * IN_TO_CM) # 1.34 in
    sketch.Figures.AddCircle(0.0, 0.0, 4.2)             # 4.2 cm

    print(f"Sketched 3 circles: 50 mm, 1.34 in, 4.2 cm.")


if __name__ == "__main__":
    sys.exit(run_example(main))
