"""Port of AlibreScript ``Import-points-from-a-CSV-file-rotate-them-and-connect-into-a-polyline.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/import-points-from-a-csv-file-rotate-them-and-connect-into-a-polyline

Reads a 2-column XY CSV, rotates each point about ``ROTATION_POINT``,
and emits consecutive line segments on the XY plane. AlibreX is
unit-fixed, so the original mm values become cm (×0.1).

Pass the CSV path as a positional arg::

    python Import-points-from-a-CSV-file-...py path\\to\\sample.csv
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from alibrex import connect, run_example
ANGLE_DEG = 45.0
ROTATION_POINT = (1.5, 0.0)   # 15 mm in the original
MM = 0.1


def rotate2d(degrees: float, point, origin):
    rad = math.radians(degrees)
    x = point[0] - origin[0]
    y = point[1] - origin[1]
    rx = x * math.cos(rad) - y * math.sin(rad) + origin[0]
    ry = x * math.sin(rad) + y * math.cos(rad) + origin[1]
    return rx, ry


_DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent / "_sample_files" / "sample.csv"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path, nargs="?", default=_DEFAULT_CSV,
                        help=f"CSV of XY points in mm (default: {_DEFAULT_CSV.name})")
    args = parser.parse_args()
    if not args.csv_path.exists():
        sys.exit(f"CSV not found: {args.csv_path}")

    pts: list[tuple[float, float]] = []
    with args.csv_path.open() as f:
        for row in csv.reader(f):
            x_mm, y_mm = float(row[0]), float(row[1])
            pts.append(rotate2d(ANGLE_DEG, (x_mm * MM, y_mm * MM), ROTATION_POINT))
    print(f"Found {len(pts)} points.")

    root = connect()
    part = root.CreateEmptyPart("My Part", False)
    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Point Sketch")
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        sketch.Figures.AddLine(x1, y1, x2, y2)


if __name__ == "__main__":
    sys.exit(run_example(main))
