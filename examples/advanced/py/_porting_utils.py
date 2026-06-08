"""Shared helpers for porting AlibreScript examples to alibrex.

These wrap the repetitive AlibreScript -> alibrex translations that show
up in nearly every port:

  * Unit conversion (AlibreScript ships mm; alibrex is internally cm).
  * Block extrusion (AlibreScript: one call; alibrex: sketch + 14-arg AddExtrudedBoss).
  * Face / edge lookups by geometric criteria (AlibreScript: by name like
    ``"Face<5>"``; alibrex: iterate the collection).

These helpers are deliberately local to the advanced/ folder rather than
pushed into the alibrex package - porting glue, not core API.
"""
from __future__ import annotations

from typing import Callable, Iterable, Sequence

from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    CurrentAssembly,
    CurrentPart,
    connect,
    float_array,
)


# AlibreScript distances are millimetres; alibrex's internal unit is cm.
def mm(value: float) -> float:
    """Convert millimetres to centimetres (alibrex internal unit)."""
    return value / 10.0


def new_part(name: str):
    """Create a fresh empty part and return it. Mirrors AlibreScript ``Part(name)``."""
    return connect().CreateEmptyPart(name, False)


def part_or_open(default_name: str):
    """Return the active part. If none is open, create one called *default_name*."""
    try:
        return CurrentPart()
    except RuntimeError:
        return connect().CreateEmptyPart(default_name, False)


def assembly_or_open(default_name: str):
    """Return the active assembly. If none is open, create one called *default_name*."""
    try:
        return CurrentAssembly()
    except RuntimeError:
        return connect().CreateEmptyAssembly(default_name)


def xy_plane(part):
    return part.DesignPlanes.Item(0)


def yz_plane(part):
    return part.DesignPlanes.Item(1)


def zx_plane(part):
    return part.DesignPlanes.Item(2)


def sketch_rectangle(part, plane, name: str, x1: float, y1: float, x2: float, y2: float):
    """Sketch a closed rectangle from (x1,y1) to (x2,y2) on the given plane.

    Uses four AddLine calls - AlibreX 29's ``AddRectangle`` has been
    occasionally unreliable inside auto-bracketed transactions. The
    proxy auto-brackets BeginChange/EndChange.
    """
    sk = part.Sketches.AddSketch(None, plane, name)
    f = sk.Figures
    f.AddLine(x1, y1, x2, y1)
    f.AddLine(x2, y1, x2, y2)
    f.AddLine(x2, y2, x1, y2)
    f.AddLine(x1, y2, x1, y1)
    return sk


def sketch_circle(part, plane, name: str, cx: float, cy: float, radius: float):
    """Sketch a single circle on the plane. AlibreScript uses *diameter*;
    alibrex's ``AddCircle(cx, cy, r)`` uses *radius* - convert at the call site."""
    sk = part.Sketches.AddSketch(None, plane, name)
    sk.Figures.AddCircle(cx, cy, radius)
    return sk


def extrude_boss(part, sketch, depth_cm: float, name: str, reversed_: bool = False):
    """Vanilla extruded boss - 'to depth' along the sketch normal."""
    return part.Features.AddExtrudedBoss(
        sketch, depth_cm, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, reversed_,
        None, False,
        name, f"{name}_Depth", "",
    )


def extrude_cut_through(part, sketch, name: str, reversed_: bool = False):
    """Extruded cut, through-all."""
    return part.Features.AddExtrudedCutout(
        sketch, 0.0, ADPartFeatureEndCondition.AD_THROUGH_ALL,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, reversed_,
        None, False,
        name, f"{name}_CutDepth", "",
    )


# ---------------------------------------------------------------------------
# Face / edge picking helpers - AlibreScript users wrote `GetFace("Face<5>")`;
# alibrex doesn't expose names so we iterate the collection by geometric
# property. These return *indices* so callers can re-fetch fresh proxies on
# the line they're used (AlibreX 29 body proxies go stale across other calls).
# ---------------------------------------------------------------------------

def top_face_index(part) -> int:
    """Index of the face with the highest average Z in body 0. -1 if none."""
    faces = part.Bodies.Item(0).Faces
    best_idx, best_z = -1, float("-inf")
    for i in range(faces.Count):
        try:
            lo, hi = faces.Item(i).GetExtents(None, None)
        except Exception:
            continue
        z = 0.5 * (lo.Z + hi.Z)
        if z > best_z:
            best_idx, best_z = i, z
    return best_idx


def top_edges_indices(part, n: int = 4) -> list[int]:
    """Indices of the *n* edges with the highest mid-Z. Useful for picking
    the top rim of an upward-extruded block."""
    edges = part.Bodies.Item(0).Edges
    scored = []
    for i in range(edges.Count):
        e = edges.Item(i)
        try:
            z = 0.5 * (e.StartVertex.Point.Z + e.EndVertex.Point.Z)
        except Exception:
            continue
        scored.append((z, i))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [i for _, i in scored[:n]]


def edges_by_indices(part, indices: Sequence[int]):
    """Return the IADEdge objects at the given indices (fresh fetch)."""
    edges = part.Bodies.Item(0).Edges
    return [edges.Item(i) for i in indices]
