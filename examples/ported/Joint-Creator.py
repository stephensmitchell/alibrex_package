"""Port stub for AlibreScript ``Joint-Creator.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/joint-creator

The original is a 300+ line utility that depends on AlibreScript-only
features that have no direct AlibreX equivalent:

- ``WindowsInputTypes.Part``      - pick a part-occurrence in the
  assembly tree via the dialog. AlibreX has selection filters but no
  interactive picker; a port would prompt by name/path instead.
- ``Prt.AssemblyPointtoPartPoint(pt)`` - converts an assembly-world
  coordinate into the part's local frame. In AlibreX you would invert
  ``IADOccurrence.WorldTransform`` and apply it manually.
- ``Sketch.StartFaceMapping(v1, v2)`` / ``Sketch.AddPoint(x,y,False)`` -
  defines a 2D coordinate system on a 3D face anchored on an edge.
  AlibreX has no analogue; you'd compute the in-plane basis from the
  face normal and the edge direction and convert coordinates yourself.

The pin/slot generation math (``GeneratePinOffsets`` /
``GenerateSlotOffsets``) is pure Python and ports verbatim - see the
original.

If you need this script, the practical path is:

1. Replace the dialog with ``argparse`` taking the two part files.
2. Use ``Bodies.Item(0).Edges`` / ``Faces`` plus their endpoint
   vertices to find the shared edge and bracketing faces.
3. Implement a small helper that maps (u, v) face-local coordinates
   into world space by composing ``edge_direction`` and the
   face-normal-cross-edge direction.
4. Cut rectangles with ``AddExtrudedCutout`` using
   ``ADPartFeatureEndCondition.AD_THROUGH_ALL``.

This file is intentionally a stub.
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "Joint-Creator is a stub. See docstring for the porting plan."
    )


if __name__ == "__main__":
    main()
