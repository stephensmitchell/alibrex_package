"""Port of "Alibre Design Import/Export Utilities" AlibreScript example.

Wraps the common import/export calls on the current part (or a fresh
demo part) into a small utility class. Exercises:

  - ``ExportSAT``, ``ExportSTEP`` / ``ExportAP203`` / ``ExportAP214``,
    ``ExportIGES``, ``ExportSTL`` (on IADPartSession via IADDesignSession).
  - ``ImportSTEPFile``, ``ImportIGESFile``, ``ImportSATFile`` (on IADRoot).

Run produces a temp folder of exports + (if a sample STEP is provided)
re-imports it to confirm the round-trip works.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time

from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    connect,
    run_example,
)
from _porting_utils import (
    extrude_boss,
    mm,
    part_or_open,
    sketch_rectangle,
    xy_plane,
)

def _ensure_body(part) -> None:
    if part.Bodies.Count > 0:
        return
    sk = sketch_rectangle(part, xy_plane(part), "AutoBase", 0.0, 0.0, mm(40), mm(20))
    extrude_boss(part, sk, mm(10), "AutoBlock")

def export_part(part, folder: str) -> list[tuple[str, int]]:
    """Export the active part to every solid format alibrex supports.
    Returns a list of (path, size_bytes) tuples for successful exports."""
    base = os.path.join(folder, part.Name or "part")
    results = []
    plans = (
        ("sat",   lambda p: part.ExportSAT(p, 7)),
        ("igs",   lambda p: part.ExportIGES(p)),
        ("stl",   lambda p: part.ExportSTL(p, 0.5, 15.0, 0.05)),
        ("stp",   lambda p: part.ExportAP214(p)),
        ("obj",   lambda p: part.ExportOBJ(p)),
    )
    for ext, fn in plans:
        path = f"{base}.{ext}"
        try:
            fn(path)
            size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"  exported {ext.upper():4s}  {size:>10,d} bytes  {path}")
            results.append((path, size))
        except Exception as exc:  # noqa: BLE001
            print(f"  export  {ext.upper():4s}  FAILED ({type(exc).__name__})")
    return results

def reimport_step(root, step_path: str) -> None:
    """Read a STEP file back into Alibre to confirm the export is well-formed."""
    if not os.path.exists(step_path):
        print(f"  reimport STEP: skipped (no file at {step_path})")
        return
    try:
        root.ImportSTEPFile(step_path)
        print(f"  re-imported STEP: {step_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"  re-import STEP FAILED: {type(exc).__name__}: {exc}")

def main() -> int:
    root = connect()
    part = part_or_open("ImportExportDemo")
    _ensure_body(part)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(tempfile.gettempdir(), f"alibrex_io_{stamp}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Output folder: {out_dir}")

    results = export_part(part, out_dir)
    step_path = next((p for p, s in results if p.endswith(".stp") and s >= 1024), None)
    if step_path is not None:
        reimport_step(root, step_path)

    return 0

if __name__ == "__main__":
    sys.exit(run_example(main))
