"""Port of AlibreScript ``Import and Export/Part Exporter.py``.

Walks a source folder for ``*.AD_PRT`` files, opens each, exports to the
chosen format, and closes. Inputs come from a tkinter form. Export
formats map straight onto AlibreX:

- STEP203  - ``ExportAP203``
- STEP214  - ``ExportAP214``
- STL      - ``ExportSTL`` (defaults from AlibreScript)
- IGES     - ``ExportIGES``
- SAT      - ``ExportSAT(path, version=18, saveColor=True)`` - uses ``ExportSAT2``
- BMP      - ``SaveCurrentViewSnapshot``
"""
from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path
from typing import cast

from alibrex import IADPartSession, connect, run_example
from alibrex.dialogs import (
    InputType, error_dialog, info_dialog, options_dialog,
)


EXPORT_TYPES = ["STEP203", "STEP214", "STL", "IGES", "SAT", "BMP"]


def main() -> None:
    home = str(Path.home())
    values = options_dialog(
        "Part Exporter",
        [
            ["Folder containing parts", InputType.String, home],
            ["Output folder",           InputType.String, home],
            ["Export type",             InputType.StringList, EXPORT_TYPES, EXPORT_TYPES[0]],
        ],
        width=480,
    )
    if values is None:
        sys.exit("User cancelled")

    parts_folder, output_folder, export_idx = values
    if not (parts_folder and os.path.isdir(parts_folder)):
        error_dialog("Folder containing parts does not exist", "Part Exporter")
        sys.exit()
    if not (output_folder and os.path.isdir(output_folder)):
        error_dialog("Output folder does not exist", "Part Exporter")
        sys.exit()
    export_type = EXPORT_TYPES[export_idx]

    parts: list[str] = []
    for root_dir, _dirs, filenames in os.walk(parts_folder):
        for fn in fnmatch.filter(filenames, "*.AD_PRT"):
            parts.append(os.path.join(root_dir, fn))
    if not parts:
        error_dialog("No parts found", "Part Exporter")
        sys.exit()

    root = connect()
    for part_path in parts:
        print(f"Exporting {part_path}...")
        session = root.OpenFile(part_path)
        part = cast(IADPartSession, session)
        stem, _ext = os.path.splitext(os.path.basename(part_path))
        out_base = os.path.join(output_folder, stem)
        if export_type == "STEP203":
            part.ExportAP203(out_base + ".stp")
        elif export_type == "STEP214":
            part.ExportAP214(out_base + ".stp")
        elif export_type == "STL":
            part.ExportSTL2(out_base + ".stl")
        elif export_type == "IGES":
            part.ExportIGES(out_base + ".igs")
        elif export_type == "SAT":
            part.ExportSAT2(out_base + ".sat", 18, True)
        elif export_type == "BMP":
            part.SaveCurrentViewSnapshot(out_base + ".bmp", 800, 600, True, False)
        part.Close(False)

    info_dialog(f"Exported {len(parts)} parts", "Part Exporter")


if __name__ == "__main__":
    sys.exit(run_example(main))
