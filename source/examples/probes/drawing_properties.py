"""Probe the active drawing session + its sheets and views."""
from __future__ import annotations

import sys

from alibrex import connect, require_active_drawing, run_example, probe_collection, probe_object

def main() -> None:
    root = connect()
    drw = require_active_drawing(root)

    probe_object(drw, "active drawing")
    probe_object(drw.Properties, "Drawing.Properties")
    probe_collection(drw.Sheets, "Sheets", limit=5)
    if drw.Sheets.Count > 0:
        sheet0 = drw.Sheets.Item(0)
        try:
            probe_collection(sheet0.Views, "Sheets[0].Views", limit=5)
        except AttributeError:
            print("Sheets[0] has no Views property - skipping.")

if __name__ == "__main__":
    sys.exit(run_example(main))
