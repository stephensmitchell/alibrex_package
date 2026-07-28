"""Port stub for AlibreScript ``Pocket-Hole-Creator.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/pocket-hole-creator

Same pattern as ``Joint-Creator.py``: relies on
``Sketch.StartFaceMapping`` / ``PointtoGlobal`` / ``GlobaltoPoint`` and
``WindowsInputTypes.Edge`` / ``Face`` for interactive picks, none of
which AlibreX exposes.

The geometric idea is portable:

1. From an edge + adjacent face, compute the in-plane basis: ``u`` =
   normalised edge direction, ``v`` = ``face_normal × u``.
2. Add reference points at the desired (u, v, offset) coordinates by
   transforming back to world space.
3. Build a perpendicular plane via ``DesignPlanes.CreateBy3Points``
   anchored on the entry point.
4. Sketch two concentric circles on that plane and cut once mid-plane,
   once through-all (``ADPartFeatureEndCondition.AD_MID_PLANE`` /
   ``AD_THROUGH_ALL``).

See the original for the pocket math (entry/exit centres from edge
distance + angle).
"""
from __future__ import annotations

def main() -> None:
    raise NotImplementedError(
        "Pocket-Hole-Creator is a stub. See docstring for the porting plan."
    )

if __name__ == "__main__":
    main()
