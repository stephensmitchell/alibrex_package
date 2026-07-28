"""Parametric sketch offset tool ported from Stephen S. Mitchell's C# gist.

Source:
  https://gist.github.com/stephensmitchell/c621a57c304109c0251a35fed85e577a

Offsets line, circle, and circular-arc figures in an editable 2D sketch,
adds reference driver geometry, ties offsets back to the source geometry
with constraints, and places one driving dimension named from the sketch.

Usage:
  python offset_sketch_parametric.py
  python offset_sketch_parametric.py "Sketch<1>" 1.0
"""
from __future__ import annotations

import math
import sys
import traceback
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from alibrex import (
    ADGeometryType,
    ADSketchConstraintType,
    IADPartSession,
    IADSketchCircle,
    IADSketchCircularArc,
    IADSketchLine,
    connect,
    narrow,
    require_active_part,
)

VERTEX_TOL = 0.0000001
MITER_FACTOR = 8.0

DEFAULT_SKETCH_NAME = "Sketch<1>"
DEFAULT_OFFSET_VALUE = 1.0

@dataclass
class OffEdge:
    index: int = -1
    kind: str = ""

    orig_line: Any = None
    orig_circle: Any = None
    orig_arc: Any = None

    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0

    ox1: float = 0.0
    oy1: float = 0.0
    ox2: float = 0.0
    oy2: float = 0.0

    nx: float = 0.0
    ny: float = 0.0
    has_normal: bool = False

    cx: float = 0.0
    cy: float = 0.0
    r: float = 0.0
    r_new: float = 0.0
    grow: bool = False
    skip: bool = False

    group_start: int = -1
    group_end: int = -1
    joined_start: bool = False
    joined_end: bool = False

    off_line: Any = None
    off_circle: Any = None
    off_arc: Any = None
    o_start_pt: Any = None
    o_end_pt: Any = None

    mid_ref: Any = None
    rad_ref: Any = None
    rad_ref2: Any = None
    tie_start: Any = None
    tie_end: Any = None

@dataclass
class EndRef:
    edge: OffEdge
    which_end: int
    x: float
    y: float
    group_id: int = -1

class ConstraintHelper:
    def __init__(self, root, sketch) -> None:
        self.root = root
        self.sketch = sketch
        self.added = 0
        self.failed = 0

    def add(self, constraint_type: ADSketchConstraintType, *targets: object) -> bool:
        try:
            collector = self.root.NewObjectCollector()
            for target in targets:
                collector.Add(target)
            if self.sketch.SketchConstraints.AddConstraint(collector, constraint_type):
                self.added += 1
                return True
            self.failed += 1
            print(f"  Constraint {constraint_type} returned false")
            return False
        except Exception as exc:  # noqa: BLE001
            self.failed += 1
            print(f"  Constraint {constraint_type} threw: {exc}")
            return False

def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    try:
        sketch_name = args[0] if args else DEFAULT_SKETCH_NAME
        offset_value = float(args[1]) if len(args) > 1 else DEFAULT_OFFSET_VALUE
        root = connect()
        part = require_active_part(root)

        print(f"Offsetting sketch {sketch_name!r} by {offset_value}.")
        result = offset_sketch(root, part, sketch_name, offset_value)
        print_result(result)

        if string_equals(result, "Status", "Success") or string_equals(result, "Status", "Warning"):
            try:
                part.RegenerateAll()
                print("Part regenerated.")
            except Exception as exc:  # noqa: BLE001
                print(f"RegenerateAll failed: {exc}")

        if (
            string_equals(result, "Status", "Success")
            or string_equals(result, "Status", "Warning")
            or string_equals(result, "Status", "AlreadyApplied")
        ):
            return 0
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

def offset_sketch(root, part: IADPartSession, sketch_name: str, offset_value: float) -> dict[str, object]:
    result: dict[str, object] = {}
    warnings: list[str] = []

    try:
        d = abs(offset_value)
        if d <= VERTEX_TOL:
            return error("Offset value must be non-zero.")

        sketch = find_sketch(part, sketch_name)
        if sketch is None:
            return error(f"Sketch {sketch_name!r} not found in the active part.")

        if safe_bool(sketch, "IsConsumed"):
            feature_name = "a feature"
            try:
                consuming_feature = sketch.ConsumingFeature
                if consuming_feature is not None:
                    feature_name = consuming_feature.Name
            except Exception:  # noqa: BLE001
                pass
            return error(
                f"Sketch {sketch.Name!r} is consumed by {feature_name!r} and cannot be edited. "
                "Roll back or delete the consuming feature first."
            )

        if safe_bool(sketch, "IsSuppressed"):
            return error(f"Sketch {sketch.Name!r} is suppressed and cannot be edited.")

        edges: list[OffEdge] = []
        skipped: list[str] = []

        for i in range(sketch.Figures.Count):
            raw_figure = sketch.Figures.Item(i)
            fig_type = figure_type(raw_figure)
            if fig_type == int(ADGeometryType.AD_POINT):
                continue

            if safe_bool(raw_figure, "IsReference"):
                continue

            if fig_type == int(ADGeometryType.AD_LINE):
                line = narrow(raw_figure, IADSketchLine)
                dx0 = line.End.X - line.Start.X
                dy0 = line.End.Y - line.Start.Y
                if math.hypot(dx0, dy0) <= VERTEX_TOL:
                    skipped.append("DegenerateLine")
                    continue
                edges.append(
                    OffEdge(
                        kind="Line",
                        orig_line=line,
                        x1=line.Start.X,
                        y1=line.Start.Y,
                        x2=line.End.X,
                        y2=line.End.Y,
                    )
                )
            elif fig_type == int(ADGeometryType.AD_CIRCULAR_ARC):
                arc = narrow(raw_figure, IADSketchCircularArc)
                edges.append(
                    OffEdge(
                        kind="Arc",
                        orig_arc=arc,
                        cx=arc.Center.X,
                        cy=arc.Center.Y,
                        r=arc.Radius,
                        x1=arc.Start.X,
                        y1=arc.Start.Y,
                        x2=arc.End.X,
                        y2=arc.End.Y,
                    )
                )
            elif fig_type == int(ADGeometryType.AD_CIRCLE):
                circle = narrow(raw_figure, IADSketchCircle)
                edges.append(
                    OffEdge(
                        kind="Circle",
                        orig_circle=circle,
                        cx=circle.Center.X,
                        cy=circle.Center.Y,
                        r=circle.Radius,
                    )
                )
            else:
                skipped.append(str(getattr(raw_figure, "FigureType", "<unknown>")))

        if not edges:
            return {
                "Status": "Error",
                "Message": "Sketch contains no offsettable line/circle/arc geometry.",
                "SkippedTypes": skipped,
            }

        for i, edge in enumerate(edges):
            edge.index = i

        marker_name = offset_marker(sketch.Name)
        if marker_exists(sketch, marker_name):
            return {
                "Status": "AlreadyApplied",
                "Message": (
                    f"Sketch {sketch.Name!r} already carries an offset from this tool "
                    f"(dimension {marker_name!r}). To change it, edit that driving dimension "
                    "in Alibre, or delete the prior offset geometry before re-running."
                ),
                "SketchName": sketch.Name,
            }

        ends = [
            endpoint
            for edge in edges
            if edge.kind in {"Line", "Arc"}
            for endpoint in (
                EndRef(edge=edge, which_end=1, x=edge.x1, y=edge.y1),
                EndRef(edge=edge, which_end=2, x=edge.x2, y=edge.y2),
            )
        ]

        groups = build_groups(ends)
        for group_id, group in enumerate(groups):
            for endpoint in group:
                endpoint.group_id = group_id
                if endpoint.which_end == 1:
                    endpoint.edge.group_start = group_id
                else:
                    endpoint.edge.group_end = group_id

        assign_outward_by_winding(edges, groups, warnings)

        cx, cy, cn = 0.0, 0.0, 0
        for edge in edges:
            if edge.kind in {"Line", "Arc"}:
                cx += edge.x1 + edge.x2
                cy += edge.y1 + edge.y2
                cn += 2
            elif edge.kind == "Circle":
                cx += edge.cx
                cy += edge.cy
                cn += 1
        if cn:
            cx /= cn
            cy /= cn

        radius_errors = 0
        for edge in edges:
            if edge.kind == "Line":
                if not edge.has_normal:
                    assign_centroid_normal(edge, cx, cy, warnings)
                edge.ox1 = edge.x1 + d * edge.nx
                edge.oy1 = edge.y1 + d * edge.ny
                edge.ox2 = edge.x2 + d * edge.nx
                edge.oy2 = edge.y2 + d * edge.ny
            elif edge.kind == "Circle":
                edge.r_new = edge.r + d
            elif edge.kind == "Arc":
                if not edge.has_normal:
                    assign_arc_grow_by_centroid(edge, cx, cy)
                edge.r_new = edge.r + d if edge.grow else edge.r - d
                if edge.r_new <= VERTEX_TOL:
                    edge.skip = True
                    radius_errors += 1
                    warnings.append(
                        f"Arc skipped: inward offset {d:.3f} exceeds radius {edge.r:.3f}."
                    )
                    continue
                scale = edge.r_new / edge.r
                edge.ox1 = edge.cx + (edge.x1 - edge.cx) * scale
                edge.oy1 = edge.cy + (edge.y1 - edge.cy) * scale
                edge.ox2 = edge.cx + (edge.x2 - edge.cx) * scale
                edge.oy2 = edge.cy + (edge.y2 - edge.cy) * scale

        unjoined: list[str] = []
        join_plan: list[tuple[EndRef, EndRef]] = []

        for group in groups:
            live = [endpoint for endpoint in group if not endpoint.edge.skip]
            if len(live) < 2:
                continue
            if len(live) > 2:
                unjoined.append(f"({group[0].x:.3f},{group[0].y:.3f}) x{len(live)} edges")
                continue

            a, b = live
            if a.edge.kind == "Line" and b.edge.kind == "Line":
                hit = miter_intersect(a.edge, b.edge)
                if hit is None:
                    unjoined.append(f"({group[0].x:.3f},{group[0].y:.3f}) near-parallel lines")
                    continue
                ix, iy = hit
                set_off(a, ix, iy)
                set_off(b, ix, iy)
                join_plan.append((a, b))
                mark_joined(a)
                mark_joined(b)
            else:
                ax, ay = off_x(a), off_y(a)
                bx, by = off_x(b), off_y(b)
                sep = math.hypot(ax - bx, ay - by)
                if sep <= max(VERTEX_TOL * 10.0, d * 0.0001):
                    join_plan.append((a, b))
                    mark_joined(a)
                    mark_joined(b)
                else:
                    unjoined.append(
                        f"({group[0].x:.3f},{group[0].y:.3f}) "
                        f"non-tangent {a.edge.kind}/{b.edge.kind}"
                    )

        try:
            sketch.BeginChange()
        except Exception as exc_begin:  # noqa: BLE001
            return error(
                f"Could not enter edit mode for sketch {sketch.Name!r}. It may be open "
                f"in Alibre's sketch editor - exit sketch mode and run again. Detail: {exc_begin}"
            )

        created: list[Any] = []
        placed_dim = None
        constraint_helper = ConstraintHelper(root, sketch)
        master = None
        joins = 0
        ref_total = 0
        dimensioned = False
        hard_error = None

        try:
            for edge in edges:
                if edge.skip:
                    continue

                if edge.kind == "Line":
                    edge.off_line = sketch.Figures.AddLine(edge.ox1, edge.oy1, edge.ox2, edge.oy2)
                    created.append(edge.off_line)
                    edge.o_start_pt = edge.off_line.Start
                    edge.o_end_pt = edge.off_line.End

                    mx = (edge.x1 + edge.x2) / 2.0
                    my = (edge.y1 + edge.y2) / 2.0
                    edge.mid_ref = sketch.Figures.AddLine(
                        mx, my, mx + d * edge.nx, my + d * edge.ny
                    )
                    edge.mid_ref.IsReference = True
                    created.append(edge.mid_ref)

                    if not edge.joined_start:
                        edge.tie_start = sketch.Figures.AddLine(edge.x1, edge.y1, edge.ox1, edge.oy1)
                        edge.tie_start.IsReference = True
                        created.append(edge.tie_start)

                    if not edge.joined_end:
                        edge.tie_end = sketch.Figures.AddLine(edge.x2, edge.y2, edge.ox2, edge.oy2)
                        edge.tie_end.IsReference = True
                        created.append(edge.tie_end)

                elif edge.kind == "Circle":
                    edge.off_circle = sketch.Figures.AddCircle(edge.cx, edge.cy, edge.r_new)
                    created.append(edge.off_circle)
                    edge.rad_ref = sketch.Figures.AddLine(edge.cx + edge.r, edge.cy, edge.cx + edge.r_new, edge.cy)
                    edge.rad_ref.IsReference = True
                    created.append(edge.rad_ref)

                elif edge.kind == "Arc":
                    signed_angle = arc_signed_angle(edge.orig_arc)
                    edge.off_arc = sketch.Figures.AddCircularArcByCenterStartAngle(
                        edge.cx, edge.cy, edge.ox1, edge.oy1, signed_angle
                    )
                    created.append(edge.off_arc)
                    edge.o_start_pt = edge.off_arc.Start
                    edge.o_end_pt = edge.off_arc.End

                    edge.rad_ref = sketch.Figures.AddLine(edge.x1, edge.y1, edge.ox1, edge.oy1)
                    edge.rad_ref.IsReference = True
                    created.append(edge.rad_ref)

                    edge.rad_ref2 = sketch.Figures.AddLine(edge.x2, edge.y2, edge.ox2, edge.oy2)
                    edge.rad_ref2.IsReference = True
                    created.append(edge.rad_ref2)

            for edge in edges:
                if edge.skip:
                    continue
                if edge.mid_ref is not None:
                    master = edge.mid_ref
                    break
                if edge.rad_ref is not None:
                    master = edge.rad_ref
                    break

            for edge in edges:
                if edge.skip:
                    continue
                if edge.kind == "Line":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_PARALLEL,
                        edge.off_line,
                        edge.orig_line,
                    )
                elif edge.kind == "Circle":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.off_circle.Center,
                        edge.orig_circle.Center,
                    )
                elif edge.kind == "Arc":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.off_arc.Center,
                        edge.orig_arc.Center,
                    )

            for edge in edges:
                if edge.skip:
                    continue
                if edge.kind == "Line":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_MIDPOINT,
                        edge.mid_ref.Start,
                        edge.orig_line,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR,
                        edge.mid_ref,
                        edge.orig_line,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.mid_ref.End,
                        edge.off_line,
                    )
                    if edge.tie_start is not None:
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                            edge.tie_start.Start,
                            edge.orig_line.Start,
                        )
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                            edge.tie_start.End,
                            edge.off_line.Start,
                        )
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR,
                            edge.tie_start,
                            edge.orig_line,
                        )
                    if edge.tie_end is not None:
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                            edge.tie_end.Start,
                            edge.orig_line.End,
                        )
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                            edge.tie_end.End,
                            edge.off_line.End,
                        )
                        constraint_helper.add(
                            ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR,
                            edge.tie_end,
                            edge.orig_line,
                        )
                elif edge.kind == "Circle":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref.Start,
                        edge.orig_circle,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref.End,
                        edge.off_circle,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.orig_circle.Center,
                        edge.rad_ref,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL,
                        edge.rad_ref,
                    )
                elif edge.kind == "Arc":
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref.Start,
                        edge.orig_arc.Start,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref.End,
                        edge.off_arc.Start,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.orig_arc.Center,
                        edge.rad_ref,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref2.Start,
                        edge.orig_arc.End,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.rad_ref2.End,
                        edge.off_arc.End,
                    )
                    constraint_helper.add(
                        ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT,
                        edge.orig_arc.Center,
                        edge.rad_ref2,
                    )

            for pair in join_plan:
                p0 = off_point(pair[0])
                p1 = off_point(pair[1])
                if p0 is None or p1 is None:
                    continue
                if constraint_helper.add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, p0, p1):
                    joins += 1

            for edge in edges:
                if edge.skip:
                    continue
                driver = edge.mid_ref if edge.kind == "Line" else edge.rad_ref
                if driver is None:
                    continue
                ref_total += 1
                if driver is master:
                    continue
                constraint_helper.add(ADSketchConstraintType.AD_CONSTRAINT_EQUAL, driver, master)

            if master is not None:
                try:
                    placed_dim = sketch.Dimensions.PlaceLinearDimension(master, d)
                    dimensioned = placed_dim is not None
                    if placed_dim is not None:
                        parameter = placed_dim.Parameter
                        if parameter is None:
                            raise RuntimeError("created dimension has no parameter to name")
                        rename_parameter(part, parameter, marker_name)
                except Exception as exc_dim:  # noqa: BLE001
                    hard_error = f"dimension placement failed: {exc_dim}"
                    print(f"  {hard_error}")

        except Exception as exc:  # noqa: BLE001
            hard_error = str(exc)
            print(f"  Edit error: {exc}")
            traceback.print_exc()
        finally:
            try:
                sketch.EndChange()
            except Exception as exc_end:  # noqa: BLE001
                hard_error = (
                    f"{hard_error} | EndChange failed: {exc_end}"
                    if hard_error
                    else f"EndChange failed: {exc_end}"
                )

        if hard_error is not None:
            rollback_figures(sketch, created, placed_dim)
            return {
                "Status": "Error",
                "Message": f"Offset of {sketch.Name!r} failed and was rolled back: {hard_error}",
                "SketchName": sketch.Name,
                "Detail": hard_error,
            }

        live_count = len([edge for edge in edges if not edge.skip])
        ok = constraint_helper.failed == 0 and dimensioned and not unjoined

        result["Status"] = "Success" if ok else "Warning"
        result["Message"] = (
            f"Offset {sketch.Name!r} by {d}: {live_count} entities, {ref_total} driven "
            f"reference lines, {constraint_helper.added} constraints, {joins} corner joins."
            if ok
            else (
                f"Offset {sketch.Name!r} by {d} completed with notes: "
                f"{constraint_helper.failed} rejected constraint(s), {len(unjoined)} "
                f"unjoined corner(s), dimensioned={dimensioned}."
            )
        )
        result["SketchName"] = sketch.Name
        result["OffsetDistance"] = d
        result["EntitiesOffset"] = live_count
        result["DrivenReferenceLines"] = ref_total
        result["ConstraintsAdded"] = constraint_helper.added
        result["ConstraintsFailed"] = constraint_helper.failed
        result["CornerJoins"] = joins
        result["Dimensioned"] = dimensioned
        result["SkippedFigures"] = len(skipped)
        if skipped:
            result["SkippedTypes"] = skipped
        if radius_errors:
            result["ArcsSkipped"] = radius_errors
        if unjoined:
            result["UnjoinedCorners"] = unjoined
        if warnings:
            result["Warnings"] = warnings
        result["IsClosed"] = sketch.IsClosed
        result["TotalConstraints"] = sketch.SketchConstraints.Count
        result["TotalDimensions"] = sketch.Dimensions.Count
        return result

    except Exception as exc:  # noqa: BLE001
        return {
            "Status": "Error",
            "Message": str(exc),
            "Detail": traceback.format_exc(),
        }

def error(message: str) -> dict[str, object]:
    return {"Status": "Error", "Message": message}

def figure_type(fig) -> int | None:
    try:
        return int(fig.FigureType)
    except Exception:  # noqa: BLE001
        return None

def safe_bool(obj, name: str) -> bool:
    try:
        return bool(getattr(obj, name))
    except Exception:  # noqa: BLE001
        return False

def find_sketch(part: IADPartSession, name: str):
    for i in range(part.Sketches.Count):
        sketch = part.Sketches.Item(i)
        if sketch.Name == name:
            return sketch

    folded = name.casefold()
    for i in range(part.Sketches.Count):
        sketch = part.Sketches.Item(i)
        if sketch.Name.casefold() == folded:
            return sketch
    return None

def offset_marker(sketch_name: str) -> str:
    return "Offset_" + "".join(c if c.isalnum() else "_" for c in sketch_name)

def marker_exists(sketch, marker_name: str) -> bool:
    try:
        for i in range(sketch.Dimensions.Count):
            param = sketch.Dimensions.Item(i).Parameter
            if param is not None and param.Name == marker_name:
                return True
    except Exception as exc:  # noqa: BLE001
        print(f"  MarkerExists check failed: {exc}")
    return False

def rename_parameter(part: IADPartSession, parameter, name: str) -> None:
    params = part.Parameters
    params.OpenParameterTransaction()
    try:
        parameter.Name = name
        params.CloseParameterTransaction()
    except Exception:
        try:
            params.CancelParameterTransaction()
        except Exception as cancel_exc:  # noqa: BLE001
            print(f"  CancelParameterTransaction failed: {cancel_exc}")
        raise

def rollback_figures(sketch, created: list[Any], dim_obj) -> None:
    try:
        sketch.BeginChange()
        try:
            if dim_obj is not None and dim_obj.Parameter is not None:
                try:
                    dim_obj.Parameter.Remove()
                except Exception as exc:  # noqa: BLE001
                    print(f"  Rollback dimension failed: {exc}")

            for fig in reversed(created):
                try:
                    if fig is not None:
                        fig.Delete()
                except Exception as exc:  # noqa: BLE001
                    print(f"  Rollback figure delete failed: {exc}")
        finally:
            sketch.EndChange()
    except Exception as exc:  # noqa: BLE001
        print(f"  RollbackFigures failed: {exc}")

def build_groups(ends: list[EndRef]) -> list[list[EndRef]]:
    groups: list[list[EndRef]] = []
    used = [False] * len(ends)

    for i, endpoint in enumerate(ends):
        if used[i]:
            continue
        group = [endpoint]
        used[i] = True
        for j in range(i + 1, len(ends)):
            if used[j]:
                continue
            if abs(endpoint.x - ends[j].x) <= VERTEX_TOL and abs(endpoint.y - ends[j].y) <= VERTEX_TOL:
                group.append(ends[j])
                used[j] = True
        groups.append(group)
    return groups

def mark_joined(endpoint: EndRef) -> None:
    if endpoint.which_end == 1:
        endpoint.edge.joined_start = True
    else:
        endpoint.edge.joined_end = True

def off_x(endpoint: EndRef) -> float:
    return endpoint.edge.ox1 if endpoint.which_end == 1 else endpoint.edge.ox2

def off_y(endpoint: EndRef) -> float:
    return endpoint.edge.oy1 if endpoint.which_end == 1 else endpoint.edge.oy2

def set_off(endpoint: EndRef, x: float, y: float) -> None:
    if endpoint.which_end == 1:
        endpoint.edge.ox1 = x
        endpoint.edge.oy1 = y
    else:
        endpoint.edge.ox2 = x
        endpoint.edge.oy2 = y

def off_point(endpoint: EndRef):
    return endpoint.edge.o_start_pt if endpoint.which_end == 1 else endpoint.edge.o_end_pt

def arc_signed_angle(arc) -> float:
    angle = arc.IncludedAngle
    try:
        if not arc.IsRightHandRule:
            angle = -angle
    except Exception:  # noqa: BLE001
        pass
    return angle

def miter_intersect(a: OffEdge, b: OffEdge) -> tuple[float, float] | None:
    aux = a.x2 - a.x1
    auy = a.y2 - a.y1
    bux = b.x2 - b.x1
    buy = b.y2 - b.y1
    alen = math.hypot(aux, auy)
    blen = math.hypot(bux, buy)
    if alen <= VERTEX_TOL or blen <= VERTEX_TOL:
        return None

    aux /= alen
    auy /= alen
    bux /= blen
    buy /= blen

    denom = aux * buy - auy * bux
    if abs(denom) < 0.000001:
        return None

    wx = b.ox1 - a.ox1
    wy = b.oy1 - a.oy1
    t = (wx * buy - wy * bux) / denom

    ix = a.ox1 + t * aux
    iy = a.oy1 + t * auy

    miter_len = math.hypot(ix - a.ox1, iy - a.oy1)
    if miter_len <= MITER_FACTOR * max(alen, blen):
        return ix, iy
    return None

def assign_outward_by_winding(edges: list[OffEdge], groups: list[list[EndRef]], warnings: list[str]) -> None:
    visited = [False] * len(edges)
    open_geometry = False

    for start in range(len(edges)):
        if visited[start]:
            continue
        if edges[start].kind == "Circle":
            visited[start] = True
            continue

        path: list[EndRef] = []
        cur = start
        enter_end = 1
        closed = False
        broke = False
        guard = 0

        while True:
            if visited[cur]:
                closed = cur == start and bool(path)
                break

            visited[cur] = True
            current_edge = edges[cur]
            path.append(EndRef(edge=current_edge, which_end=enter_end, x=0.0, y=0.0))

            exit_group = current_edge.group_end if enter_end == 1 else current_edge.group_start
            if exit_group < 0:
                broke = True
                break

            next_endpoint = None
            degree = 0
            for endpoint in groups[exit_group]:
                if endpoint.edge.kind == "Circle":
                    continue
                degree += 1
                if endpoint.edge is not current_edge:
                    next_endpoint = endpoint

            if degree != 2 or next_endpoint is None:
                broke = True
                break

            enter_end = next_endpoint.which_end
            cur = next_endpoint.edge.index

            if cur == start:
                closed = True
                break

            guard += 1
            if guard > len(edges) + 2:
                broke = True
                break

        if closed and not broke and len(path) >= 2:
            area = 0.0
            for k, endpoint in enumerate(path):
                next_endpoint = path[(k + 1) % len(path)]
                px = endpoint.edge.x1 if endpoint.which_end == 1 else endpoint.edge.x2
                py = endpoint.edge.y1 if endpoint.which_end == 1 else endpoint.edge.y2
                qx = next_endpoint.edge.x1 if next_endpoint.which_end == 1 else next_endpoint.edge.x2
                qy = next_endpoint.edge.y1 if next_endpoint.which_end == 1 else next_endpoint.edge.y2
                area += px * qy - qx * py

            ccw = area > 0.0
            for endpoint in path:
                edge = endpoint.edge
                sx = edge.x1 if endpoint.which_end == 1 else edge.x2
                sy = edge.y1 if endpoint.which_end == 1 else edge.y2
                ex = edge.x2 if endpoint.which_end == 1 else edge.x1
                ey = edge.y2 if endpoint.which_end == 1 else edge.y1
                ux = ex - sx
                uy = ey - sy
                length = math.hypot(ux, uy)
                if length <= VERTEX_TOL:
                    continue
                ux /= length
                uy /= length

                nx, ny = (uy, -ux) if ccw else (-uy, ux)
                if edge.kind == "Line":
                    edge.nx = nx
                    edge.ny = ny
                    edge.has_normal = True
                elif edge.kind == "Arc":
                    signed_angle = arc_signed_angle(edge.orig_arc)
                    a0 = math.atan2(edge.y1 - edge.cy, edge.x1 - edge.cx)
                    a_mid = a0 + signed_angle / 2.0
                    mrx = math.cos(a_mid)
                    mry = math.sin(a_mid)
                    edge.grow = (mrx * nx + mry * ny) >= 0.0
                    edge.has_normal = True
        else:
            open_geometry = True

    if open_geometry:
        warnings.append(
            "Some geometry is not part of a clean closed loop; outward direction "
            "for those edges is a best-effort guess."
        )

def assign_centroid_normal(edge: OffEdge, cx: float, cy: float, warnings: list[str]) -> None:
    dx = edge.x2 - edge.x1
    dy = edge.y2 - edge.y1
    length = math.hypot(dx, dy)
    if length <= VERTEX_TOL:
        edge.nx = 0.0
        edge.ny = 0.0
        edge.has_normal = True
        return

    ux = dx / length
    uy = dy / length
    n1x = uy
    n1y = -ux
    mx = (edge.x1 + edge.x2) / 2.0
    my = (edge.y1 + edge.y2) / 2.0
    dot = (mx - cx) * n1x + (my - cy) * n1y

    if abs(dot) > VERTEX_TOL:
        edge.nx, edge.ny = (n1x, n1y) if dot >= 0.0 else (-n1x, -n1y)
    else:
        eps = max(VERTEX_TOL, length * 0.001)
        da = sq(mx + eps * n1x - cx) + sq(my + eps * n1y - cy)
        db = sq(mx - eps * n1x - cx) + sq(my - eps * n1y - cy)
        edge.nx, edge.ny = (n1x, n1y) if da >= db else (-n1x, -n1y)
        warnings.append(
            "Ambiguous outward direction for an edge (centroid on edge line); "
            "offset side may be wrong."
        )

    edge.has_normal = True

def assign_arc_grow_by_centroid(edge: OffEdge, cx: float, cy: float) -> None:
    signed_angle = arc_signed_angle(edge.orig_arc)
    a0 = math.atan2(edge.y1 - edge.cy, edge.x1 - edge.cx)
    a_mid = a0 + signed_angle / 2.0
    midx = edge.cx + edge.r * math.cos(a_mid)
    midy = edge.cy + edge.r * math.sin(a_mid)
    rad_out_x = midx - edge.cx
    rad_out_y = midy - edge.cy
    away_x = midx - cx
    away_y = midy - cy

    edge.grow = (rad_out_x * away_x + rad_out_y * away_y) >= 0.0
    edge.has_normal = True

def sq(value: float) -> float:
    return value * value

def print_result(result: dict[str, object]) -> None:
    for key, value in result.items():
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")

def string_equals(data: dict[str, object], key: str, value: str) -> bool:
    return str(data.get(key, "")) == value

if __name__ == "__main__":
    sys.exit(main())
