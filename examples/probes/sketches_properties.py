"""Probe every 2D sketch on the active part, plus a sample of each
sketch's first few figures (lines, circles, arcs, …)."""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_collection, probe_object


def main() -> None:
    root = connect()
    part = require_active_part(root)

    print(f"Total 2D sketches: {part.Sketches.Count}")
    for i in range(part.Sketches.Count):
        sk = part.Sketches.Item(i)
        probe_object(sk, f"Sketch[{i}]")
        probe_collection(sk.Figures, f"Sketch[{i}].Figures", limit=4)

    print(f"\nTotal 3D sketches: {part.Sketches3D.Count}")
    for i in range(part.Sketches3D.Count):
        sk = part.Sketches3D.Item(i)
        probe_object(sk, f"Sketch3D[{i}]")
        probe_collection(sk.Figures, f"Sketch3D[{i}].Figures", limit=4)


if __name__ == "__main__":
    sys.exit(run_example(main))
