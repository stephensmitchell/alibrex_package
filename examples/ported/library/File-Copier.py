"""Port of AlibreScript ``Utilities/File Copier.py``.

Walks a source folder, opens each part or assembly, ``SaveAs``-es it
into the destination folder, and closes. Assemblies use ``SaveAll`` so
the inclusion list is rewritten to point at the copied parts.

Mapping:

- ``Part(folder, filename)``         - ``root.OpenFile(full_path)``
- ``P.SaveAs(folder, stem)``         - ``session.SaveAs(folder, stem)``
- ``Assembly(folder, filename)``     - ``root.OpenFile(full_path)``
- ``A.SaveAll(folder)``              - ``session.SaveAll(folder)``
"""
from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path
from alibrex import connect, run_example
from alibrex.dialogs import (
    InputType, error_dialog, info_dialog, options_dialog,
)


COPY_TYPES = ["Only parts", "Assemblies, sub-assemblies and parts in assemblies"]


def main() -> None:
    home = str(Path.home())
    values = options_dialog(
        "File Copier",
        [
            ["Source folder",      InputType.String,     home],
            ["Destination folder", InputType.String,     home],
            ["Copy",               InputType.StringList, COPY_TYPES, COPY_TYPES[0]],
        ],
        width=520,
    )
    if values is None:
        sys.exit("User cancelled")
    src, dst, copy_type = values
    if not (src and os.path.isdir(src)):
        error_dialog("Source folder does not exist", "File Copier")
        sys.exit()
    if not (dst and os.path.isdir(dst)):
        error_dialog("Destination folder does not exist", "File Copier")
        sys.exit()

    pattern = "*.AD_PRT" if copy_type == 0 else "*.AD_ASM"
    files: list[str] = []
    for root_dir, _dirs, filenames in os.walk(src):
        for fn in fnmatch.filter(filenames, pattern):
            files.append(os.path.join(root_dir, fn))
    if not files:
        error_dialog("No parts or assemblies found", "File Copier")
        sys.exit()

    root = connect()
    for path in files:
        print(f"Copying {path}...")
        session = root.OpenFile(path)
        stem, _ext = os.path.splitext(os.path.basename(path))
        if copy_type == 0:
            session.SaveAs(dst, stem)
        else:
            session.SaveAll(dst)
        session.Close(False)

    label = "part" if copy_type == 0 else "assembly"
    suffix = "" if len(files) == 1 else "s"
    info_dialog(f"Copied {len(files)} {label}{suffix}", "File Copier")


if __name__ == "__main__":
    sys.exit(run_example(main))
