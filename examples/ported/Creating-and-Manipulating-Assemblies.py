"""Port of AlibreScript ``Creating-and-Manipulating-Assemblies.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/creating-and-manipulating-assemblies

Maps:

- ``Asm.AddPart(path, x, y, z, rx, ry, rz, ...)``  -
  build a ``IADTransformation`` (translation × rotation) via
  ``IADGeometryFactory``, then ``Occurrences.Add(path, xform)``
- ``Asm.AnchorPart(occ)`` - ``occ.IsAnchored = True``

There is no built-in "translate then rotate" vs "rotate then translate"
flag - compose transforms by multiplying matrices yourself if you need
exact parity with the AlibreScript ``Reverse`` argument.
"""
from __future__ import annotations

import argparse
import math
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

    path_obj: object = str(part_path)
    ident = gf.CreateIdentityTransform()
    # Occurrences.Add takes a `ref object`; pythonnet returns
    # (occurrence, modified_arg) - unpack the first.
    occ1 = asm.RootOccurrence.Occurrences.Add(path_obj, ident)[0]

    # Duplicate at (5,10,15) - AlibreX uses centimetres
    trans = gf.CreateTranslationTransformByXYZ(0.5, 1.0, 1.5)
    occ2 = asm.RootOccurrence.Occurrences.Add(path_obj, trans)[0]

    # Apply a rotation about Z (use a rotation transform). To combine
    # rotation + translation, call ApplyTransform on the occurrence.
    z_axis = gf.CreateVector(0.0, 0.0, 1.0)
    origin = gf.CreatePoint(0.0, 0.0, 0.0)
    rot = gf.CreateRotationTransform(z_axis, origin, math.radians(50))
    occ2.ApplyTransform(rot)

    occ1.IsAnchored = True
    print(f"Anchored '{occ1.Name}', placed and rotated '{occ2.Name}'.")
    print(f"'{occ1.Name}' faces (via owning session):")
    # In AlibreX you reach faces through the part body of the inclusion's
    # design session; not on the occurrence itself.
    sess = occ1.DesignSession
    try:
        part_sess = sess  # IADPartSession when occurrence is a part
        body = part_sess.Bodies.Item(0)  # type: ignore[attr-defined]
        print(f"  Faces: {body.Faces.Count}")
    except Exception as exc:  # noqa: BLE001
        print(f"  (couldn't enumerate faces: {exc})")


if __name__ == "__main__":
    sys.exit(run_example(main))
