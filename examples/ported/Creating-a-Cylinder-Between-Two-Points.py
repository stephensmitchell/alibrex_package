"""Port of AlibreScript ``Creating-a-Cylinder-Between-Two-Points.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/creating-a-cylinder-between-two-points

Builds a cylinder whose ends are centered on two arbitrary 3-space
points. Differences from the AlibreScript original:

- AlibreScript has ``P.AddPlane(name, normal_vector, point)`` that
  creates a plane from a normal + point. AlibreX has no equivalent —
  ``IADDesignPlanes.CreateBy3Points`` is the closest. We construct
  three points on a plane whose normal is ``p2 - p1``.
- ``S.GlobaltoPoint(x,y,z)`` (project world→sketch-plane coords) has no
  AlibreX equivalent. Since we built the plane *centered* on ``p1``, the
  in-plane circle is centered at sketch coordinates ``(0, 0)``.
- ``P.AddAxis(name, p1, p2)`` → ``part.DesignAxes.CreateBy2Points`` with
  two design points.
"""
from __future__ import annotations

import math
import sys
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
)
from alibrex import connect, run_example
# AlibreScript values were in mm; convert to cm for AlibreX.
P1 = (0.1, 0.5, 0.2)   # (1, 5, 2) mm
P2 = (1.0, 1.4, 0.8)   # (10, 14, 8) mm
DIAMETER_CM = 0.6      # 6 mm


def _ortho_basis(n: tuple[float, float, float]):
    """Return two unit vectors orthogonal to ``n`` (forming a plane basis)."""
    nx, ny, nz = n
    # Pick the world axis least aligned with n
    if abs(nx) <= abs(ny) and abs(nx) <= abs(nz):
        helper = (1.0, 0.0, 0.0)
    elif abs(ny) <= abs(nz):
        helper = (0.0, 1.0, 0.0)
    else:
        helper = (0.0, 0.0, 1.0)
    # u = n x helper, v = n x u
    ux, uy, uz = (ny * helper[2] - nz * helper[1],
                  nz * helper[0] - nx * helper[2],
                  nx * helper[1] - ny * helper[0])
    ulen = math.sqrt(ux*ux + uy*uy + uz*uz) or 1.0
    ux, uy, uz = ux / ulen, uy / ulen, uz / ulen
    vx, vy, vz = (ny * uz - nz * uy,
                  nz * ux - nx * uz,
                  nx * uy - ny * ux)
    vlen = math.sqrt(vx*vx + vy*vy + vz*vz) or 1.0
    return (ux, uy, uz), (vx / vlen, vy / vlen, vz / vlen)


def main() -> None:
    dx, dy, dz = (P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2])
    length = math.sqrt(dx*dx + dy*dy + dz*dz)

    root = connect()
    part = root.CreateEmptyPart("Cylinder", False)
    gf = part.GeometryFactory

    p1 = part.DesignPoints.CreatePoint(P1[0], P1[1], P1[2], "Start")
    p2 = part.DesignPoints.CreatePoint(P2[0], P2[1], P2[2], "End")
    part.DesignAxes.CreateBy2Points(None, p1, None, p2, "Cylinder Axis")

    # Build the start-cap plane via three coplanar points around P1
    u, v = _ortho_basis((dx, dy, dz))
    ring = DIAMETER_CM   # any non-zero offset works; using diameter for clarity
    pa = gf.CreatePoint(P1[0],                P1[1],                P1[2])
    pb = gf.CreatePoint(P1[0] + ring * u[0],  P1[1] + ring * u[1],  P1[2] + ring * u[2])
    pc = gf.CreatePoint(P1[0] + ring * v[0],  P1[1] + ring * v[1],  P1[2] + ring * v[2])
    try:
        cap_plane = part.DesignPlanes.CreateBy3Points(
            None, pa, None, pb, None, pc, "Cyl Start Plane",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Skipping cylinder build: CreateBy3Points failed "
              f"({type(exc).__name__}). This is the AlibreX 29 upstream "
              "bug S8 — `Cannot create plane with Collinear points` is "
              "raised for every triple. The axis between the points is "
              "still in place. See KNOWN_ISSUES.md S8.")
        return

    sketch = part.Sketches.AddSketch(None, cap_plane, "Cylinder End")
    sketch.Figures.AddCircle(0.0, 0.0, DIAMETER_CM / 2.0)

    part.Features.AddExtrudedBoss(
        sketch, length, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Cylinder", "Length", "",
    )
    print(f"Created cylinder of length {length:.4f} cm "
          f"between {P1} and {P2}.")


if __name__ == "__main__":
    sys.exit(run_example(main))
