"""Port of AlibreScript ``Geodesic-Dome-Reference-Geometry.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/geodesic-dome-reference-geometry

Tessellates a sphere by recursively subdividing an icosahedron, then
adds a reference point at each unique vertex. Pure math + a flurry of
``DesignPoints.CreatePoint`` calls.
"""
from __future__ import annotations

import sys
from math import sqrt
from alibrex import connect, run_example
_A = 0.525731112119133606
_B = 0.850650808352039932

ICOSA_VERTS = [
    [ _A,  0.0, -_B], [-_A,  0.0, -_B], [ _A,  0.0,  _B], [-_A,  0.0,  _B],
    [0.0, -_B, -_A], [0.0, -_B,  _A], [0.0,  _B, -_A], [0.0,  _B,  _A],
    [-_B, -_A,  0.0], [ _B, -_A,  0.0], [-_B,  _A,  0.0], [ _B,  _A,  0.0],
]
ICOSA_INDICES = [
    [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1], [8,10,1], [8,3,10],
    [5,3,8], [5,2,3], [2,7,3], [7,10,3], [7,6,10], [7,11,6], [11,0,6],
    [0,1,6], [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11],
]

def normalize(a):
    d = sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]) or 1.0
    return [a[0]/d, a[1]/d, a[2]/d]

def recurse(a, b, c, div, r, verts):
    if div == 0:
        verts.add((a[0]*r, a[1]*r, a[2]*r))
        verts.add((b[0]*r, b[1]*r, b[2]*r))
        verts.add((c[0]*r, c[1]*r, c[2]*r))
        return
    ab = normalize([(a[i]+b[i])/2 for i in range(3)])
    ac = normalize([(a[i]+c[i])/2 for i in range(3)])
    bc = normalize([(b[i]+c[i])/2 for i in range(3)])
    recurse(a,  ab, ac, div-1, r, verts)
    recurse(b,  bc, ab, div-1, r, verts)
    recurse(c,  ac, bc, div-1, r, verts)
    recurse(ab, bc, ac, div-1, r, verts)

DETAIL = 1
RADIUS_CM = 1.0

def main() -> None:
    verts = set()
    for tri in ICOSA_INDICES:
        recurse(ICOSA_VERTS[tri[0]], ICOSA_VERTS[tri[1]], ICOSA_VERTS[tri[2]],
                DETAIL, RADIUS_CM, verts)

    root = connect()
    part = root.CreateEmptyPart("Geodesic Sphere", False)
    for i, (x, y, z) in enumerate(sorted(verts)):
        part.DesignPoints.CreatePoint(x, y, z, f"Geodesic {i}")
    print(f"Added {len(verts)} reference points.")

if __name__ == "__main__":
    sys.exit(run_example(main))
