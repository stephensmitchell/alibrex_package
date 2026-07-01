"""Example 19: export the active part to STEP / IGES / STL / OBJ.

Files are written to a timestamped folder under the system temp dir.
Run with any part open. Exercises the IADPartSession.Export* family.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time

from alibrex import connect, run_example, require_active_part
def main() -> None:
    root = connect()
    part = require_active_part(root)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(tempfile.gettempdir(), f"alibrex_export_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    base = os.path.join(out_dir, part.Name or "part")

    # STEP (AP242, newer)
    step_path = base + ".step"
    part.ExportAP242(step_path)

    # IGES
    iges_path = base + ".igs"
    part.ExportIGES(iges_path)

    # STL: coarse mesh
    stl_path = base + ".stl"
    part.ExportSTL(stl_path, 0.5, 15.0, 0.05)

    # OBJ
    obj_path = base + ".obj"
    part.ExportOBJ(obj_path)

    print(f"Exported '{part.Name}' to {out_dir}:")
    for p in (step_path, iges_path, stl_path, obj_path):
        size = os.path.getsize(p) if os.path.exists(p) else 0
        print(f"  {os.path.basename(p):30s}  {size:>10,d} bytes")


if __name__ == "__main__":
    sys.exit(run_example(main))
