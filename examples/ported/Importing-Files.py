"""Port of AlibreScript ``Importing-Files.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/importing-files

AlibreScript's ``Part(path, Part.FileTypes.STEP)`` becomes
``root.ImportSTEPFile(path)`` and likewise for IGES. The returned object
is an ``IADSession`` you can cast to ``IADPartSession``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from alibrex import connect, run_example
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=Path, help="STEP file to import")
    parser.add_argument("--iges", type=Path, help="IGES file to import")
    args = parser.parse_args()

    root = connect()

    if args.step:
        s = root.ImportSTEPFile(str(args.step))
        print(f"Imported STEP → session '{s.Name}'")
    if args.iges:
        s = root.ImportIGESFile(str(args.iges))
        print(f"Imported IGES → session '{s.Name}'")
    if not (args.step or args.iges):
        parser.print_help()


if __name__ == "__main__":
    sys.exit(run_example(main))
