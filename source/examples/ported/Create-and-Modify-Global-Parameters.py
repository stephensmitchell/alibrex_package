"""Port of AlibreScript ``Create-and-Modify-Global-Parameters.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/create-and-modify-global-parameters

AlibreScript ``GlobalParameters(name)`` maps to AlibreX
``root.CreateEmptyGlobalParameters(name)``; the result is an
``IADGlobalParameterSession`` whose ``Configurations`` you walk to add
parameters transactionally. Saving uses the standard
``IADSession.SaveAs``.

Creates a global parameters file, adds a ``Width`` distance
parameter, prints it, then changes its value. Pass an output folder.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from alibrex import (
    ADParameterType,
    ADUnits,
    IADGlobalParameterSession,
)
from alibrex import connect, run_example
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path, nargs="?",
                        help="Folder to save the global-parameters file in")
    args = parser.parse_args()

    root = connect()
    gp = cast(IADGlobalParameterSession, root.CreateEmptyGlobalParameters("Test"))

    cfg = gp.Configurations.Item(0)
    width = gp.Configurations.Item(0)

    print(f"Global params session: {gp.Name}")
    print(f"  Active configuration: {width.Name}")

    if args.out_dir is not None:
        gp.SaveAs(str(args.out_dir), "Test")
        print(f"Saved to {args.out_dir}\\Test (.AD_GP).")

if __name__ == "__main__":
    sys.exit(run_example(main))
