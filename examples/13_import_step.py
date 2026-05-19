"""Example 13 — import a STEP file and inspect what was loaded."""
from __future__ import annotations

import sys
from pathlib import Path

from alibrex import connect, run_example
def main() -> None:
    if len(sys.argv) < 2:
        print("usage: 13_import_step.py <path-to-step-file>")
        return
    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        raise FileNotFoundError(path)

    root = connect()
    print(f"Importing: {path}")
    session = root.ImportSTEPFileEx(str(path), True, True)
    print(f"  -> session: {session.Name}  (type={session.SessionType})")


if __name__ == "__main__":
    sys.exit(run_example(main))
