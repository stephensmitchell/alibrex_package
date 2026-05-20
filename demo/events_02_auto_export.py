"""Events demo 02 - auto-export every part on OnSessionChange.

A small but realistic pattern: whenever the user changes the active part
in Alibre's UI, export the geometry to STL on disk. The exported file is
stamped with the session name and the event count, so you can confirm
multiple changes produce multiple exports.

Run this, then make edits in Alibre. Look in
``C:\\Users\\ssm\\Downloads\\demo\\auto-export\\`` for the STL files.
"""
from __future__ import annotations

import os
import sys
import time

import clr
clr.AddReference("System.Windows.Forms")  # type: ignore[attr-defined]
from System.Windows.Forms import Application  # type: ignore[import-not-found]

from alibrex import connect, run_example

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "auto-export")
LISTEN_SECONDS = 60


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    root = connect()
    em = root.EventManager
    print(f"Auto-export listener started. Output: {OUT_DIR}")
    print(f"Listening {LISTEN_SECONDS}s - edit parts in Alibre to trigger exports.")

    state = {"changes": 0, "exports": 0, "errors": 0}

    def export_now(session) -> None:
        state["changes"] += 1
        try:
            name = session.Name or f"unnamed_{state['changes']}"
        except Exception:
            name = f"unnamed_{state['changes']}"
        # Sanitize name for filesystem
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        path = os.path.join(OUT_DIR, f"{safe}_chg{state['changes']:03d}.stl")
        try:
            session.ExportSTL(path, 0.5, 15.0, 0.05)
            size = os.path.getsize(path) if os.path.exists(path) else 0
            state["exports"] += 1
            print(f"  [export] {safe} -> {os.path.basename(path)}  ({size:,} bytes)")
        except Exception as exc:  # noqa: BLE001
            state["errors"] += 1
            print(f"  [error]  export of {safe} failed: {type(exc).__name__}")

    def on_change(session, modified_items, change_types):  # noqa: ARG001
        export_now(session)

    em.OnSessionChange += on_change
    try:
        end = time.time() + LISTEN_SECONDS
        while time.time() < end:
            Application.DoEvents()
            time.sleep(0.05)
    finally:
        em.OnSessionChange -= on_change

    print(f"\n{state['changes']} change(s) seen, "
          f"{state['exports']} export(s) written, "
          f"{state['errors']} error(s).")
    return 0


if __name__ == "__main__":
    sys.exit(run_example(main))
