"""Port of AlibreScript ``Reference-Geometry.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/default-reference-geometry

Identical to ``Default-Reference-Geometry.py`` in the source repo
(both point at the same help URL). Running it directly re-runs the
other file.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name("Default-Reference-Geometry.py")
    runpy.run_path(str(target), run_name="__main__")
    sys.exit(0)
