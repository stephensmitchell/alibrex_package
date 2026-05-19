"""Example 14 — Python port of example.linq (VB.NET / LINQPad).

Original walked the active part's body, listed every face, every edge, and
printed each edge's start- and end-vertex (X,Y,Z) converted from Alibre's
internal cm to inches (÷ 2.54).

Porting notes vs. the VB original:
 - VB `GetObject(, "AlibreX.AutomationHook")` (COM ROT lookup) becomes
   `connect_to_running_alibre()` — bridges the COM proxy through CLR
   reflection so attribute access is typed and transparent.
 - VB `For Each e In edges` -> Python `for i in range(edges.Count): edges.Item(i)`
   (CLR collections expose `.Item(i)`; PythonNet doesn't auto-iterate them).
 - VB implicit interface narrowing (`Dim p As IADPartSession = session`) is
   handled automatically by the bridge — once you touch a derived member
   (`Bodies`), it widens the proxy to IADPartSession.
 - LINQPad `.Dump()` -> `print()`.
 - VB module-level singleton -> `functools.cache` on a connect helper.
"""
from __future__ import annotations

import functools
import sys

from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    IADPartSession,
    IADRoot,
    connect_to_running_alibre,
    require_active_part,
    run_example,
)
CONVERT_CM_TO_IN = 2.54


def _bootstrap_block(part: IADPartSession) -> None:
    """If the active part has no body, sketch and extrude a small block
    so there's geometry to enumerate."""
    if part.Bodies.Count > 0:
        return
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "AutoBase")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 2.0, 0.0)
        sk.Figures.AddLine(2.0, 0.0, 2.0, 1.0)
        sk.Figures.AddLine(2.0, 1.0, 0.0, 1.0)
        sk.Figures.AddLine(0.0, 1.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 0.5, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "AutoBlock", "AutoDepth", "",
    )


@functools.cache
def root() -> IADRoot:
    """Lazily-initialised singleton, like the VB AlibreSingleton."""
    return connect_to_running_alibre()


def print_point(x: float, y: float, z: float) -> str:
    return (
        f"{round(x / CONVERT_CM_TO_IN, 6)}:"
        f"{round(y / CONVERT_CM_TO_IN, 6)}:"
        f"{round(z / CONVERT_CM_TO_IN, 6)}"
    )


def _active_or_new_part(r) -> IADPartSession:
    try:
        return require_active_part(r)
    except RuntimeError:
        return r.CreateEmptyPart("PortVbnetLinq_Demo", False)


def send_curves_to_alibre() -> None:
    part: IADPartSession = _active_or_new_part(root())
    _bootstrap_block(part)
    body = part.Bodies.Item(0)
    print(f"DesignSurfaces.Count = {part.DesignSurfaces.Count}")

    faces = body.Faces
    for y in range(faces.Count):
        face = faces.Item(y)
        edges = face.Edges
        for z in range(edges.Count):
            edge = edges.Item(z)
            print(f"position : {y}")
            sv = edge.StartVertex.Point
            ev = edge.EndVertex.Point
            print(print_point(sv.X, sv.Y, sv.Z))
            print(print_point(ev.X, ev.Y, ev.Z))
            print(f"position : {y}")


def main() -> None:
    send_curves_to_alibre()


if __name__ == "__main__":
    sys.exit(run_example(main))
