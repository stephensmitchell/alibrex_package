"""Port of AlibreScript ``List-All-Parts-in-an-Assembly-and-Sub-Assemblies.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/list-all-parts-in-an-assembly-and-sub-assemblies

Recursively walks an assembly's occurrence tree, printing every
part. AlibreScript exposes ``.Parts`` and ``.SubAssemblies`` collections
directly; in AlibreX everything is a uniform tree of ``IADOccurrence``
objects whose own ``SessionType``/``Occurrences.Count`` reveal what they
contain.

Usage::

    python List-All-Parts-in-an-Assembly-and-Sub-Assemblies.py path\\to\\Main.AD_ASM
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from alibrex import ADObjectSubType, IADAssemblySession, IADOccurrence, connect, run_example
def _is_assembly_occ(occ: IADOccurrence) -> bool:
    return occ.Occurrences.Count > 0

def list_parts(occ: IADOccurrence, parent_name: str) -> None:
    if _is_assembly_occ(occ):
        for i in range(occ.Occurrences.Count):
            child = occ.Occurrences.Item(i)
            if _is_assembly_occ(child):
                list_parts(child, child.Name)
            else:
                print(f"{child.Name} in {parent_name}")
    else:
        print(f"{occ.Name} in {parent_name}")

def main() -> None:
    from _sample_inputs import ensure_sample_assembly
    parser = argparse.ArgumentParser()
    parser.add_argument("assembly_path", type=Path, nargs="?",
                        help="Path to a .AD_ASM file (defaults to the bundled sample)")
    args = parser.parse_args()
    asm_path = args.assembly_path or ensure_sample_assembly()

    root = connect()
    session = root.OpenFile(str(asm_path))
    if int(session.SessionType) != int(ADObjectSubType.AD_ASSEMBLY):
        raise RuntimeError(f"{asm_path} is not an assembly "
                           f"(got {session.SessionType}).")

    asm = cast(IADAssemblySession, session)
    list_parts(asm.RootOccurrence, asm.Name)
    asm.Close(False)

if __name__ == "__main__":
    sys.exit(run_example(main))
