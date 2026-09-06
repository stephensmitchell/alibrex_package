"""Example 00: connect to a running Alibre Design instance.

Run with the venv:
    .venv\\Scripts\\python.exe python\\examples\\00_connect.py

Pre-req: Alibre Design must be running.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example
def _safe(label: str, fn) -> None:
    try:
        print(f"{label:20s}: {fn()}")

    except Exception as exc:  # noqa: BLE001
        print(f"{label:20s}: (unavailable - {type(exc).__name__})")

def main() -> None:
    root = connect()
    print(f"Connected to Alibre {root.Version}\n")
    _safe("Open sessions",   lambda: root.Sessions.Count)
    _safe("Topmost session", lambda: root.TopmostSession.Name if root.TopmostSession else "(none)")
    _safe("Material libs",   lambda: root.MaterialLibraries.Count)
    _safe("Repositories",    lambda: root.Repositories.Count)
    print("\nTip: open a part/assembly/drawing in Alibre, then re-run.")

if __name__ == "__main__":
    sys.exit(run_example(main))
