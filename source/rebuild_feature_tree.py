"""Recreate an Alibre Design part from a cad-feature-tree/v1 JSON file.

This is the round-trip partner of ``scan_feature_tree.py``: it reads the
generic JSON and replays the model history into a brand-new part, proving the
captured data is complete and self-consistent.

Usage
-----
    python rebuild_feature_tree.py model.feature_tree.json [NewPartName]

What rebuilds faithfully
------------------------
* model units, named parameters (values + equations)
* sketches that live on a base plane (XY / YZ / ZX), with their 2D entities
* self-contained features: extruded boss, extruded cutout, simple hole

What is reported as skipped (and why)
-------------------------------------
Features whose definition depends on geometry references that a *generic*
format cannot carry - a sweep path/edge, a mirror plane, fillet/chamfer
edges, a revolve axis, pattern seeds, sketches placed on a model face. These
are logged with the reason rather than guessed at.
"""
from __future__ import annotations

import json
import sys

import alibrex
from alibrex import (
    ADDirectionType,
    ADHoleDepthCondition,
    ADParameterType,
    ADPartFeatureEndCondition,
    ADUnits,
    connect,
)

def get_enum(enum_cls, stripped_name, prefix="AD_", default=None):
    """Resolve 'TO_DEPTH' -> ADPartFeatureEndCondition.AD_TO_DEPTH."""
    if stripped_name is None:
        return default
    name = stripped_name if stripped_name.startswith(prefix) else prefix + stripped_name
    return getattr(enum_cls, name, default)

def axis_of(normal):
    """Return 'x' | 'y' | 'z' for the dominant component of a normal vector."""
    if not normal:
        return None
    comps = {"x": abs(normal.get("x") or 0.0),
             "y": abs(normal.get("y") or 0.0),
             "z": abs(normal.get("z") or 0.0)}
    return max(comps, key=comps.get)

_AXIS_TO_PLANE_INDEX = {"z": 0, "x": 1, "y": 2}

def num(ref, default=0.0):
    """Pull a numeric value out of a param_ref dict (or a bare number)."""
    if isinstance(ref, dict):
        v = ref.get("value")
        return default if v is None else v
    return default if ref is None else ref

def build_sketch(part, sketch, log, model_tolerance=None):
    axis = axis_of(sketch.get("plane_normal"))
    idx = _AXIS_TO_PLANE_INDEX.get(axis)
    if idx is None:
        log.append((sketch["id"], "skip", "sketch not on a base plane (face/offset plane)"))
        return None

    plane = part.DesignPlanes.Item(idx)
    sk = part.Sketches.AddSketch(None, plane, sketch.get("name"))
    added = 0
    healed = ""
    sk.BeginChange()
    try:
        for e in sketch.get("entities", []):
            fig = add_entity(sk, e)
            if fig is None:
                continue
            added += 1
            if e.get("is_reference"):
                try:
                    fig.IsReference = True
                except Exception:  # noqa: BLE001
                    pass
        if sketch.get("is_closed"):
            try:
                tol = max(model_tolerance or 0.0, 1e-3)
                sk.Analyze(True, True, False, False, False, True, tol)
                healed = " (healed)"
            except Exception:  # noqa: BLE001
                healed = " (heal failed)"
    finally:
        sk.EndChange()

    log.append((sketch["id"], "ok", f"{added} entities on plane {plane.Name}{healed}"))
    return sk

def add_entity(sk, e):
    t = e.get("type")
    figs = sk.Figures
    if t == "line":
        s, en = e["start"], e["end"]
        return figs.AddLine(s["x"], s["y"], en["x"], en["y"])
    if t == "circle":
        c = e["center"]
        return figs.AddCircle(c["x"], c["y"], e["radius"])
    if t == "arc":
        c, s = e["center"], e["start"]
        ang = e.get("included_angle")
        if ang is not None:
            signed = ang if e.get("ccw", True) else -ang
            return figs.AddCircularArcByCenterStartAngle(c["x"], c["y"], s["x"], s["y"], signed)
        en = e["end"]
        return figs.AddCircularArcByCenterStartEnd(c["x"], c["y"], s["x"], s["y"], en["x"], en["y"])
    if t == "ellipse":
        c = e["center"]
        return figs.AddEllipse(c["x"], c["y"], e["major_axis"], e["minor_major_ratio"], e["major_axis_angle"])
    if t == "elliptic_arc":
        c, s, en = e["center"], e["start"], e["end"]
        return figs.AddEllipticArc(c["x"], c["y"], e["major_axis"], e["minor_major_ratio"],
                                   s["x"], s["y"], en["x"], en["y"], e["major_axis_angle"])
    if t == "point":
        return figs.AddSketchPoint(e["x"], e["y"])
    return None

def build_extrude(part, feat, sketches_by_id, cut, log):
    p = feat["parameters"]
    sk = sketches_by_id.get(p.get("profile_sketch"))
    if sk is None:
        return ("skip", "profile sketch unavailable (not on a base plane)")
    end = get_enum(ADPartFeatureEndCondition, p.get("end_condition"),
                   default=ADPartFeatureEndCondition.AD_TO_DEPTH)
    direction = get_enum(ADDirectionType, p.get("direction"),
                         default=ADDirectionType.AD_ALONG_NORMAL)
    depth = num(p.get("depth"), 1.0)
    reversed_ = bool(p.get("direction_reversed"))
    depth_name = (p.get("depth") or {}).get("name") if isinstance(p.get("depth"), dict) else None
    add = part.Features.AddExtrudedCutout if cut else part.Features.AddExtrudedBoss
    add(sk, depth, end, None, None, 0.0, direction, None, None, reversed_,
        0.0, False, feat.get("name"), depth_name, "")
    return ("ok", f"depth={depth} {'cut' if cut else 'boss'}")

def build_hole(part, feat, sketches_by_id, log):
    p = feat["parameters"]
    sk = sketches_by_id.get(p.get("profile_sketch"))
    if sk is None:
        return ("skip", "hole locator sketch unavailable")
    depth = p.get("depth") or 1.0
    diameter = p.get("diameter") or 0.5
    cond = get_enum(ADHoleDepthCondition, p.get("depth_condition"),
                    default=ADHoleDepthCondition.AD_HOLE_TO_DEPTH)
    part.Features.AddSimpleHole(sk, depth, diameter, False, None, cond,
                                None, None, 0.0, feat.get("name"), None)
    return ("ok", f"d={diameter} depth={depth}")

_NEEDS_REFERENCES = {
    "revolve": "needs revolve axis (not captured as portable geometry)",
    "cut_revolve": "needs revolve axis",
    "sweep": "needs path sketch + profile binding",
    "loft": "needs ordered cross-section / guide references",
    "mirror": "needs mirror plane + source features",
    "pattern": "needs seed features + pattern directions",
    "fillet": "needs edge/face selection set",
    "chamfer": "needs edge/face selection set",
    "shell": "needs faces-to-remove selection set",
    "draft": "needs neutral plane + face set",
}

def build_feature(part, feat, sketches_by_id, log):
    op = feat["operation"]
    name = feat.get("name")
    try:
        if op == "extrude":
            status, msg = build_extrude(part, feat, sketches_by_id, cut=False, log=log)
        elif op == "cut_extrude":
            status, msg = build_extrude(part, feat, sketches_by_id, cut=True, log=log)
        elif op == "hole":
            status, msg = build_hole(part, feat, sketches_by_id, log)
        elif op in _NEEDS_REFERENCES:
            status, msg = "skip", _NEEDS_REFERENCES[op]
        else:
            status, msg = "skip", f"no generic rebuilder for '{op}'"
    except Exception as exc:  # noqa: BLE001
        text = str(exc)
        if "open sketch" in text.lower():
            status, msg = "skip", "profile did not re-close (sketch constraints not captured)"
        else:
            status, msg = "error", f"{type(exc).__name__}: {text.splitlines()[0][:120]}"
    log.append((name, status, msg))
    return status

_PARAM_TYPES = {
    "DISTANCE": ADParameterType.AD_DISTANCE,
    "ANGLE": ADParameterType.AD_ANGLE,
    "COUNT": ADParameterType.AD_COUNT,
    "SCALE": ADParameterType.AD_SCALE,
}

def restore_parameters(part, params, log):
    existing = {}
    coll = part.Parameters
    for i in range(coll.Count):
        pr = coll.Item(i)
        try:
            existing[pr.Name] = pr
        except Exception:  # noqa: BLE001
            pass

    for spec in params:
        nm = spec.get("name")
        if nm and nm not in existing:
            ptype = _PARAM_TYPES.get(spec.get("param_type"), ADParameterType.AD_DISTANCE)
            try:
                coll.NewParameter(nm, ptype)
            except Exception as exc:  # noqa: BLE001
                log.append((nm, "skip", f"create failed: {type(exc).__name__}"))

    existing = {}
    for i in range(coll.Count):
        pr = coll.Item(i)
        try:
            existing[pr.Name] = pr
        except Exception:  # noqa: BLE001
            pass

    coll.OpenParameterTransaction()
    try:
        for spec in params:
            pr = existing.get(spec.get("name"))
            if pr is None:
                continue
            try:
                if spec.get("equation"):
                    pr.Equation = spec["equation"]
                elif spec.get("value") is not None:
                    pr.Value = spec["value"]
            except Exception:  # noqa: BLE001
                pass
        coll.CloseParameterTransaction()
    except Exception:  # noqa: BLE001
        coll.CancelParameterTransaction()
    part.RegenerateAll()

def rebuild(model, part_name):
    root = connect()
    units = get_enum(ADUnits, model["document"].get("model_units"),
                     default=ADUnits.AD_CENTIMETERS)
    part = root.CreateEmptyPart(part_name, False)
    try:
        part.DesignProperties.ModelUnits = units
    except Exception:  # noqa: BLE001
        pass

    sketch_log, feature_log, param_log = [], [], []

    model_tol = model["document"].get("model_tolerance")
    sketches_by_id = {}
    for sketch in model.get("sketches", []):
        sk = build_sketch(part, sketch, sketch_log, model_tol)
        if sk is not None:
            sketches_by_id[sketch["id"]] = sk

    for feat in model.get("features", []):
        build_feature(part, feat, sketches_by_id, feature_log)

    restore_parameters(part, model.get("parameters", []), param_log)

    return part, sketch_log, feature_log, param_log

def _print_log(title, rows):
    ok = sum(1 for _, s, _ in rows if s == "ok")
    print(f"\n{title}: {ok}/{len(rows)} rebuilt")
    for nameid, status, msg in rows:
        mark = {"ok": "[ ok ]", "skip": "[skip]", "error": "[ERR ]"}.get(status, "[ ?? ]")
        print(f"  {mark} {nameid}: {msg}")

def main(argv):
    if len(argv) < 2:
        print("usage: python rebuild_feature_tree.py model.feature_tree.json [NewPartName]",
              file=sys.stderr)
        return 2
    with open(argv[1], "r", encoding="utf-8") as fh:
        model = json.load(fh)
    if model.get("schema") != "cad-feature-tree/v1":
        print(f"[warn] unexpected schema: {model.get('schema')!r}", file=sys.stderr)

    base = model["document"].get("name") or "Rebuilt"
    part_name = argv[2] if len(argv) > 2 else f"{base}__rebuilt"

    part, sk_log, ft_log, pm_log = rebuild(model, part_name)

    print(f"[ok] Rebuilt part: {part.Name!r}")
    _print_log("Sketches", sk_log)
    _print_log("Features", ft_log)
    _print_log("Parameters", pm_log)

    ft_ok = sum(1 for _, s, _ in ft_log if s == "ok")
    ft_err = sum(1 for _, s, _ in ft_log if s == "error")
    print(f"\nSummary: {ft_ok} features rebuilt, "
          f"{sum(1 for _,s,_ in ft_log if s=='skip')} skipped (need geometry refs), "
          f"{ft_err} errored. Part left open in Alibre for inspection.")
    return 1 if ft_err else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
