"""Port stub for AlibreScript ``Utilities/Pattern Along.py``.

The original uses three methods on the 3D-sketch B-spline figure that
AlibreX does **not** expose:

- ``Bspline3D.SubdivideGetNormals(n)``: sample the curve at *n* evenly
  spaced parameter values and return the point + curve normal at each.
- ``Bspline3D.GetPointAt(t)`` / ``GetNormalAt(t)``: evaluate the curve
  at parameter ``t ∈ [0, 1]``.

``IAD3DSketchBspline`` only exposes ``StartPoint``, ``EndPoint``,
``GetDefinition``, and ``GetData`` (control points + knots + weights).
To implement this script:

1. Read the B-spline control points + knot vector via ``GetData``.
2. Evaluate the curve at *n* parameter values using the standard
   de Boor / Cox-de Boor algorithm.
3. Compute the tangent (and a perpendicular normal) at each sample by
   finite difference along the curve.
4. For each (point, normal) pair, build a plane via
   ``DesignPlanes.CreateBy3Points`` and emit a copy of the pattern
   sketch's primitives onto it.

That last step also needs a substitute for ``Sketch.CopyFrom``; see
``Sketch-Copier.py``'s stub.

This file is intentionally a stub.
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "Pattern-Along is a stub. See docstring for the porting plan."
    )


if __name__ == "__main__":
    main()
