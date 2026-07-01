"""Port of AlibreScript ``Import and Export/STL Exporter.py``.

Notes / departures from the original:

- AlibreScript persists settings via ``CurrentPart().SetUserData(...)``
  and reads them back; AlibreX has no equivalent and the persistence is
  dropped.
- ``ExportRotatedSTL(filename, bottom_face, force_mm, custom, ...)`` is
  not exposed on ``IADPartSession``. Use the plain ``ExportSTL``
  instead; orient the part manually if you need the bottom-face
  semantics.
- ``Win.GetInputValue`` / ``Win.EnableInput`` (dialog state queries) are
  not implemented by ``_dialogs.py``; "Use custom settings" toggles
  which arguments are passed to ``ExportSTL`` rather than graying out
  fields.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example, require_active_part
from alibrex.dialogs import (
    InputType, error_dialog, info_dialog, options_dialog,
)


def main() -> None:
    values = options_dialog(
        "STL Exporter",
        [
            ["Output STL path",         InputType.String,  ""],
            ["Use custom mesh settings", InputType.Boolean, False],
            ["Max cell size (cm)",       InputType.Real,    0.5],
            ["Normal deviation (deg)",   InputType.Real,    10.0],
            ["Surface deviation (cm)",   InputType.Real,    0.05],
        ],
        width=380,
    )
    if values is None:
        sys.exit("User cancelled")
    out_path, use_custom, cell, normal, surface = values
    if not out_path:
        error_dialog("No filename entered", "STL Exporter")
        sys.exit()

    root = connect()
    part = require_active_part(root)

    if use_custom:
        part.ExportSTL(out_path, cell, normal, surface)
    else:
        part.ExportSTL2(out_path)
    info_dialog("Export completed", "STL Exporter")


if __name__ == "__main__":
    sys.exit(run_example(main))
