"""CRUD demo 01 - extrude a box in a demo part, export, verify.

Creates a fresh part by default so the demo does not alter a user document.

Pass criteria:
  - Feature count increases by exactly 1 after AddExtrudedBoss.
  - Bodies.Count increases by at least 1.
  - At least one export file is written and >= 1 KB on disk.
"""
from __future__ import annotations

import os
import sys

from _demo_utils import part_or_open, report
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    run_example,
)

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, D = 4.0, 3.0, 1.5  # cm


def main() -> int:
    part = part_or_open("CRUD01_BoxRoundtrip")

    fc_before = part.FeatureCount
    bc_before = part.Bodies.Count

    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "CRUD01_Base")
    sk.BeginChange()
    try:
        figs = sk.Figures
        figs.AddLine(0.0, 0.0, W,   0.0)
        figs.AddLine(W,   0.0, W,   H  )
        figs.AddLine(W,   H,   0.0, H  )
        figs.AddLine(0.0, H,   0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, D, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "CRUD01_Box", "CRUD01_Depth", "",
    )

    fc_after = part.FeatureCount
    bc_after = part.Bodies.Count

    # NOTE: ExportAP242 (STEP) has AccessViolation-crashed Alibre 29 on
    # simple solids - a native crash the CLR cannot catch, which would
    # terminate this whole demo before the verification step. So we only
    # exercise STL and IGES here. Restore AP242 once Alibre fixes it.
    base = os.path.join(HERE, f"crud_01_{part.Name}")
    exports = (
        ("stl", lambda p: part.ExportSTL(p, 0.5, 15.0, 0.05)),
        ("igs", lambda p: part.ExportIGES(p)),
    )
    written = []
    for ext, fn in exports:
        path = f"{base}.{ext}"
        if os.path.exists(path):
            os.remove(path)
        try:
            fn(path)
            size = os.path.getsize(path) if os.path.exists(path) else 0
            written.append((ext, path, size))
            print(f"Exported {ext.upper():4s}: {size:,} bytes  ({path})")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] Export {ext.upper()} failed: {type(exc).__name__}")

    print(f"Feature count: {fc_before} -> {fc_after}")
    print(f"Bodies count : {bc_before} -> {bc_after}")

    return report([
        ("feature added",         fc_after == fc_before + 1),
        ("body added",            bc_after >= bc_before + 1),
        ("at least 1 export ok",  len(written) >= 1),
        ("export >= 1 KB",        any(s >= 1024 for _, _, s in written)),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
