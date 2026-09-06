"""Port of AlibreScript ``Assembly-Constraints.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/assembly-constraints

Maps:

- ``Assembly("Test")``                  - ``root.CreateEmptyAssembly("Test")``
- ``Asm.AddPart(path, ...)``            - ``root_occ.Occurrences.Add(path, identity_xform)``
- ``Asm.DuplicatePart(name, ...)``      - call ``Add`` again on the same path
- ``Asm.AnchorPart(name)``              - ``occ.IsAnchored = True``
- ``Asm.AddMateConstraint(0, p1, plane1, p2, plane2)``  - manual constraint
  construction via ``IADAssemblyConstraints.AddConstraint`` with
  ``ADAssemblyConstraintType.AD_MATE_TYPE`` and an ``IADTargetProxy``
  identifying each plane on its occurrence

Building ``IADTargetProxy`` instances requires the underlying AlibreX
target-proxy API, which lacks a plain factory here, so the constraint
creation is shown but commented out; adapt to your build.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from alibrex import connect, run_example
def main() -> None:
    from _sample_inputs import ensure_sample_part
    parser = argparse.ArgumentParser()
    parser.add_argument("part_path", type=Path, nargs="?",
                        help="Path to a .AD_PRT (defaults to the bundled sample)")
    args = parser.parse_args()
    part_path = args.part_path or ensure_sample_part()

    root = connect()
    asm = root.CreateEmptyAssembly("Test")
    gf = asm.GeometryFactory
    ident = gf.CreateIdentityTransform()

    path_obj: object = str(part_path)
    occ1 = asm.RootOccurrence.Occurrences.Add(path_obj, ident)[0]
    occ2 = asm.RootOccurrence.Occurrences.Add(path_obj, ident)[0]
    print(f"Added occurrences: {occ1.Name}, {occ2.Name}")

    occ1.IsAnchored = True
    print(f"Anchored '{occ1.Name}'.")

if __name__ == "__main__":
    sys.exit(run_example(main))
