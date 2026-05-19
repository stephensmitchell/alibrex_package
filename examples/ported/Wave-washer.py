"""Port of AlibreScript ``Wave-washer.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/wave-washer

Generates a sinusoidal closed 3D B-spline path, builds a rectangular
profile on a perpendicular plane at its start, and sweeps the profile
along the path. Same options form as the original via tkinter.

The original's ``P.AddPlane(name, normal_vector, anchor_point)`` has no
direct AlibreX equivalent — we use ``DesignPlanes.CreateBy3Points`` with
three coplanar points whose plane has the desired normal.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from alibrex import ADPartFeatureEndCondition, connect, run_example
from alibrex.dialogs import InputType, options_dialog
from alibrex import float_array


MM = 0.1


def _ortho_basis(n):
    if abs(n[0]) <= abs(n[1]) and abs(n[0]) <= abs(n[2]):
        helper = (1.0, 0.0, 0.0)
    elif abs(n[1]) <= abs(n[2]):
        helper = (0.0, 1.0, 0.0)
    else:
        helper = (0.0, 0.0, 1.0)
    ux = n[1] * helper[2] - n[2] * helper[1]
    uy = n[2] * helper[0] - n[0] * helper[2]
    uz = n[0] * helper[1] - n[1] * helper[0]
    ul = math.sqrt(ux*ux + uy*uy + uz*uz) or 1.0
    u = (ux/ul, uy/ul, uz/ul)
    vx = n[1] * u[2] - n[2] * u[1]
    vy = n[2] * u[0] - n[0] * u[2]
    vz = n[0] * u[1] - n[1] * u[0]
    vl = math.sqrt(vx*vx + vy*vy + vz*vz) or 1.0
    return u, (vx/vl, vy/vl, vz/vl)


def main() -> None:
    values = options_dialog(
        "Wave Washer Generator",
        [
            ["Radius (mm)",        InputType.Real,    100.0],
            ["Amplitude (mm)",     InputType.Real,    10.0],
            ["Number of Waves",    InputType.Integer, 4],
            ["Width (mm)",         InputType.Real,    10.0],
            ["Thickness (mm)",     InputType.Real,    5.0],
        ],
    )
    if values is None:
        sys.exit("User cancelled")
    R, A, B, width, thickness = values
    R, A, width, thickness = R*MM, A*MM, width*MM, thickness*MM

    path_pts: list[float] = []
    t_step = 0.1
    t_max = 2 * math.pi
    t = 0.0
    p1: tuple[float, float, float] = (0.0, 0.0, 0.0)
    p2: tuple[float, float, float] = (0.0, 0.0, 0.0)
    n = 0
    while t < t_max:
        x = R * math.sin(t)
        y = R * math.cos(t)
        z = A * math.sin(B * t)
        path_pts.extend([x, y, z])
        if n == 0:
            p1 = (x, y, z)
        elif n == 1:
            p2 = (x, y, z)
        t += t_step
        n += 1
    # close
    path_pts.extend(path_pts[0:3])

    root = connect()
    part = root.CreateEmptyPart("Wave Washer", False)

    path = part.Sketches3D.Add3DSketch("Path")
    path.Figures.AddBsplineByInterpolation(float_array(path_pts))

    nrm = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
    u, v = _ortho_basis(nrm)
    gf = part.GeometryFactory
    pa = gf.CreatePoint(*p1)
    pb = gf.CreatePoint(p1[0]+u[0]*MM, p1[1]+u[1]*MM, p1[2]+u[2]*MM)
    pc = gf.CreatePoint(p1[0]+v[0]*MM, p1[1]+v[1]*MM, p1[2]+v[2]*MM)
    try:
        start_plane = part.DesignPlanes.CreateBy3Points(
            None, pa, None, pb, None, pc, "Start Plane",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Skipping washer sweep: CreateBy3Points failed "
              f"({type(exc).__name__}). AlibreX 29 upstream bug S8 — "
              "see KNOWN_ISSUES.md. The 3D helix path is built; only the "
              "swept profile is missing.")
        return

    profile = part.Sketches.AddSketch(None, start_plane, "Cross Section")
    profile.Figures.AddRectangle(-thickness/2, -width/2, thickness/2, width/2)

    paths = root.NewObjectCollector()
    paths.Add(path)
    part.Features.AddSweptBoss(
        profile, paths, False,
        ADPartFeatureEndCondition.AD_ENTIRE_PATH,
        None, None, 0.0,
        None, False, "Washer",
    )
    print(f"Built wave washer R={R:.4f} A={A:.4f} cm.")


if __name__ == "__main__":
    sys.exit(run_example(main))
