"""Example 26: build an assembly from scratch.

Creates a new empty assembly, adds three empty-part occurrences at
different translations, walks the resulting tree, and runs an
interference check (which should report none for empty parts).

Covers: IADRoot.CreateEmptyAssembly, IADAssemblySession.RootOccurrence,
IADOccurrence.Occurrences, IADOccurrences.AddEmptyPart,
IADGeometryFactory.CreateTranslationTransformByXYZ,
IADAssemblySession.CheckInterference.
"""
from __future__ import annotations

import sys

from alibrex import IADAssemblySession, IADOccurrence, connect, run_example
def walk(occ: IADOccurrence, depth: int = 0) -> None:
    indent = "  " * depth
    t = occ.LocalTransform
    # IADTransformation exposes position/rotation; print the name
    print(f"{indent}- {occ.Name}  (children={occ.Occurrences.Count})")
    for i in range(occ.Occurrences.Count):
        walk(occ.Occurrences.Item(i), depth + 1)


def main() -> None:
    root = connect()
    asm: IADAssemblySession = root.CreateEmptyAssembly("AssemblyBuild_Demo")

    geo = asm.GeometryFactory   # GeometryFactory lives on IADSession
    root_occ = asm.RootOccurrence

    layout = [
        ("PartA",  0.0,  0.0, 0.0, False),
        ("PartB",  5.0,  0.0, 0.0, False),
        ("PartC",  2.5,  4.0, 0.0, True),   # sheet metal
    ]
    for name, x, y, z, is_sheet in layout:
        xform = geo.CreateTranslationTransformByXYZ(x, y, z)
        occ = root_occ.Occurrences.AddEmptyPart(name, is_sheet, xform)
        kind = "sheet metal" if is_sheet else "part"
        print(f"Added {kind} '{occ.Name}' at ({x},{y},{z}).")

    print(f"\nAssembly tree ('{asm.Name}'):")
    walk(root_occ)

    # CheckInterference has two optional ref params; pass None/None and unpack
    result = asm.CheckInterference(None, None)
    interferences = result[0] if isinstance(result, tuple) else result
    print(f"\nInterference check: {interferences.Count} interference(s).")


if __name__ == "__main__":
    sys.exit(run_example(main))
