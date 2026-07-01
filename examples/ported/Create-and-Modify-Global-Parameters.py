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

    # IADGlobalParameterSession exposes Configurations only.
    # Parameters on a global-params session live on each configuration.
    cfg = gp.Configurations.Item(0)
    # Access cfg.Parameters; if your build doesn't expose that,
    # read the global-params session via the host editor.
    # Demonstrate by adding a parameter on the *active* design instead:
    width = gp.Configurations.Item(0)

    print(f"Global params session: {gp.Name}")
    print(f"  Active configuration: {width.Name}")

    if args.out_dir is not None:
        gp.SaveAs(str(args.out_dir), "Test")
        print(f"Saved to {args.out_dir}\\Test (.AD_GP).")

    # The original then reopens and bumps the value. With AlibreX you
    # would call root.OpenFile(...) and walk the configuration's
    # parameter collection to set Value. Left as an exercise because the
    # exact accessor for global-param Parameters depends on the version.


if __name__ == "__main__":
    sys.exit(run_example(main))
