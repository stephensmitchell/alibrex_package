"""Scan an Alibre Design part and write its COMPLETE feature history to a file.

Walks the active part exhaustively - document/material/physical/configuration
properties, every parameter, all reference geometry, every sketch (2D + 3D)
with its figures, dimensions and constraints, every feature with its full
per-type parameter set and reference fingerprints, plus a topology summary -
and serializes everything to one CAD-agnostic JSON file
(``cad-feature-tree/v2``). The goal is that nothing in the feature tree is
left out: any programmatic CAD system can read the model history.

Usage
-----
    python scan_feature_tree.py [output.json]

If no output path is given the file is written next to the part
(``<PartName>.feature_tree.json``), falling back to the current directory.

Honest limits (AlibreX, not this scanner)
-----------------------------------------
* ``IADMirrorFeature`` / ``IADPatternFeature`` are empty interfaces - their
  definition cannot be read at all. Such features are still recorded, flagged
  ``"unreadable": true``.
* A few feature objects throw ``COMException`` when their concrete properties
  are read; every read is guarded so the scan never aborts and the datum is
  emitted as ``null``.
* Sketch constraints expose only their *type* (no target figures); dimensions
  expose only their type + driving parameter. Both are captured at that
  fidelity.
"""
from __future__ import annotations

import json
import os
import sys

import alibrex
from alibrex import (
    CurrentAssembly,
    CurrentPart,
    narrow,
    IADChamferFeature,
    IADDraftFeature,
    IADExternalThreadFeature,
    IADExtrusionFeature,
    IADFilletFeature,
    IADHelicalFeature,
    IADHoleFeature,
    IADLoftFeature,
    IADOffsetFaceFeature,
    IADProjectFeature,
    IADRevolutionFeature,
    IADScaleFeature,
    IADShellFeature,
    IADSweepFeature,
    IADVertexChamferFeature,
    IADWrapFeature,
    IADSketchBspline,
    IADSketchCircle,
    IADSketchCircularArc,
    IADSketchEllipse,
    IADSketchEllipticArc,
    IADSketchLine,
    IADSketchPoint,
    IADSketchText,
    IAD3DSketchLine,
    IAD3DSketchPoint,
    IAD3DSketchCircle,
    IAD3DSketchCircularArc,
    IAD3DSketchEllipse,
    IAD3DSketchEllipticArc,
    IAD3DSketchBspline,
)

try:
    from alibrex import ADAccuracySetting
except Exception:  # noqa: BLE001
    ADAccuracySetting = None

SCHEMA = "cad-feature-tree/v2"

def safe(fn, default=None):
    try:
        return fn()
    except Exception:  # noqa: BLE001
        return default

def enum_name(enum_cls, value, prefix=""):
    """Resolve an AlibreX enum integer back to its member name (prefix stripped)."""
    if value is None:
        return None
    try:
        ivalue = int(value)
    except Exception:  # noqa: BLE001
        return str(value)
    for member in dir(enum_cls):
        if member.startswith("_"):
            continue
        try:
            if int(getattr(enum_cls, member)) == ivalue:
                return member[len(prefix):] if prefix and member.startswith(prefix) else member
        except Exception:  # noqa: BLE001
            continue
    return str(ivalue)

def call_outparams(obj, method_name, n):
    """Call a CLR method with N out-params, tolerating the proxy bridge quirk."""
    fn = getattr(obj, method_name, None)
    if fn is None:
        return None
    for args in ((), (None,) * n):
        try:
            return fn(*args)
        except Exception:  # noqa: BLE001
            continue
    return None

_LEN_TO_MM = {"MILLIMETERS": 1.0, "CENTIMETERS": 10.0, "METERS": 1000.0,
              "INCHES": 25.4, "FEET": 304.8, "FEET_INCHES": 304.8}
_ANG_TO_DEG = {"DEGREES": 1.0, "DEGREES_MINUTES": 1.0,
               "DEGREES_MINUTES_SECONDS": 1.0, "RADIANS": 57.29577951308232}

def pt2(p):
    if p is None:
        return None
    return {"x": safe(lambda: p.X), "y": safe(lambda: p.Y)}

def pt3(p):
    if p is None:
        return None
    return {"x": safe(lambda: p.X), "y": safe(lambda: p.Y), "z": safe(lambda: p.Z)}

def vec3(v):
    if v is None:
        return None
    return {"x": safe(lambda: v.X), "y": safe(lambda: v.Y), "z": safe(lambda: v.Z)}

def units_name(u):
    return enum_name(alibrex.ADUnits, u, "AD_")

def parameter_dict(p):
    units = units_name(safe(lambda: p.Units))
    value = safe(lambda: p.Value)
    canonical = canonical_units = None
    if value is not None and units:
        if units in _LEN_TO_MM:
            canonical, canonical_units = value * _LEN_TO_MM[units], "mm"
        elif units in _ANG_TO_DEG:
            canonical, canonical_units = value * _ANG_TO_DEG[units], "deg"
    return {
        "name": safe(lambda: p.Name),
        "param_type": enum_name(alibrex.ADParameterType, safe(lambda: p.ParameterType), "AD_"),
        "value": value,
        "units": units,
        "canonical_value": canonical,
        "canonical_units": canonical_units,
        "equation": safe(lambda: p.Equation) or "",
        "externally_driven": safe(lambda: bool(p.ExternallyDriven)),
        "comment": safe(lambda: p.comment) or "",
        "source_document_id": safe(lambda: p.SourceDocumentID) or "",
        "source_item_id": safe(lambda: p.SourceItemID) or "",
        "is_missing_global": safe(lambda: bool(p.IsMissingGlobal)),
        "is_conflicting_global": safe(lambda: bool(p.IsConflictingGlobal)),
    }

def param_ref(p):
    """Compact reference to a feature/dimension-driving parameter."""
    if p is None:
        return None
    return {
        "name": safe(lambda: p.Name),
        "value": safe(lambda: p.Value),
        "equation": safe(lambda: p.Equation) or "",
        "units": units_name(safe(lambda: p.Units)),
    }

def scan_parameters(part):
    out = []
    params = safe(lambda: part.Parameters)
    for i in range(safe(lambda: params.Count, 0)):
        p = safe(lambda i=i: params.Item(i))
        if p is not None:
            out.append(parameter_dict(p))
    return out

def scan_document(part):
    dp = safe(lambda: part.DesignProperties)
    props = {}
    if dp is not None:
        props = {
            "density": safe(lambda: dp.Density),
            "material": safe(lambda: dp.Material) or "",
            "number": safe(lambda: dp.Number) or "",
            "description": safe(lambda: dp.Description) or "",
            "treat_as_part_in_bom": safe(lambda: bool(dp.TreatAsPartInBOM)),
            "version_comment": safe(lambda: dp.VersionComment) or "",
        }
    return {
        "name": safe(lambda: part.Name),
        "type": "part",
        "file_path": safe(lambda: part.FilePath) or "",
        "has_errors": safe(lambda: bool(part.HasErrors)),
        "feature_count": safe(lambda: part.FeatureCount),
        "body_count": safe(lambda: part.Bodies.Count),
        "units": {
            "model": units_name(safe(lambda: dp.ModelUnits)) if dp else None,
            "mass": units_name(safe(lambda: dp.MassUnits)) if dp else None,
            "length_display": units_name(safe(lambda: dp.LengthDisplayUnits)) if dp else None,
            "angle_display": units_name(safe(lambda: dp.AngleDisplayUnits)) if dp else None,
        },
        "model_tolerance": safe(lambda: part.ModelTolerance),
        "properties": props,
    }

def scan_physical(part):
    if ADAccuracySetting is None:
        return None
    pp = safe(lambda: part.PhysicalProperties(ADAccuracySetting.AD_MEDIUM))
    if pp is None:
        return None
    cog = call_outparams(pp, "GetCenterOfGravity", 3)
    extents = call_outparams(pp, "GetExtents", 2)
    bbox = None
    if extents and isinstance(extents, (tuple, list)) and len(extents) == 2:
        bbox = {"min": pt3(extents[0]), "max": pt3(extents[1])}
    return {
        "volume": safe(lambda: pp.Volume),
        "mass": safe(lambda: pp.Mass),
        "surface_area": safe(lambda: pp.SurfaceArea),
        "material": safe(lambda: pp.Material) or "",
        "faces_count": safe(lambda: pp.FacesCount),
        "edges_count": safe(lambda: pp.EdgesCount),
        "vertices_count": safe(lambda: pp.VerticesCount),
        "lumps_count": safe(lambda: pp.LumpsCount),
        "center_of_gravity": list(cog) if isinstance(cog, (tuple, list)) else None,
        "bbox": bbox,
    }

def scan_configurations(part):
    out = []
    cfgs = safe(lambda: part.Configurations)
    active = safe(lambda: part.ActiveConfiguration.Name)
    for i in range(safe(lambda: cfgs.Count, 0)):
        c = safe(lambda i=i: cfgs.Item(i))
        if c is None:
            continue
        name = safe(lambda: c.Name)
        out.append({
            "index": i,
            "name": name,
            "id": safe(lambda: c.ID),
            "locks": safe(lambda: int(c.Locks)),
            "is_active": name is not None and name == active,
        })
    return out

def scan_reference_geometry(part):
    planes, axes, points = [], [], []

    pl = safe(lambda: part.DesignPlanes)
    for i in range(safe(lambda: pl.Count, 0)):
        d = safe(lambda i=i: pl.Item(i))
        if d is None:
            continue
        planes.append({
            "index": i, "name": safe(lambda: d.Name),
            "plane_type": enum_name(alibrex.ADDesignGeometryType, safe(lambda: d.PlaneType), "AD_"),
            "normal": vec3(safe(lambda: d.Normal)),
            "is_base": i < 3,
        })

    ax = safe(lambda: part.DesignAxes)
    for i in range(safe(lambda: ax.Count, 0)):
        a = safe(lambda i=i: ax.Item(i))
        if a is None:
            continue
        axes.append({"index": i, "name": safe(lambda: a.Name),
                     "type": enum_name(alibrex.ADObjectType, safe(lambda: a.Type), "AD_")})

    dp = safe(lambda: part.DesignPoints)
    for i in range(safe(lambda: dp.Count, 0)):
        pnt = safe(lambda i=i: dp.Item(i))
        if pnt is None:
            continue
        points.append({
            "index": i, "name": safe(lambda: pnt.Name),
            "point_type": enum_name(alibrex.ADDesignGeometryType, safe(lambda: pnt.PointType), "AD_"),
            "location": pt3(safe(lambda: pnt.Geometry)),
        })

    return {"planes": planes, "axes": axes, "points": points}

def figure_dict(fig):
    gtype = enum_name(alibrex.ADGeometryType, safe(lambda: fig.FigureType), "AD_")
    base = {
        "geometry": gtype,
        "is_reference": safe(lambda: bool(fig.IsReference)),
        "is_anchored": safe(lambda: bool(fig.IsAnchored)),
        "is_owned": safe(lambda: bool(fig.IsOwned)),
        "id": safe(lambda: fig.ID),
    }
    if gtype == "LINE":
        f = narrow(fig, IADSketchLine)
        base.update(type="line", start=pt2(safe(lambda: f.Start)),
                    end=pt2(safe(lambda: f.End)), length=safe(lambda: f.Length))
    elif gtype == "CIRCLE":
        f = narrow(fig, IADSketchCircle)
        base.update(type="circle", center=pt2(safe(lambda: f.Center)),
                    radius=safe(lambda: f.Radius))
    elif gtype == "CIRCULAR_ARC":
        f = narrow(fig, IADSketchCircularArc)
        base.update(type="arc", center=pt2(safe(lambda: f.Center)),
                    radius=safe(lambda: f.Radius), start=pt2(safe(lambda: f.Start)),
                    end=pt2(safe(lambda: f.End)),
                    included_angle=safe(lambda: f.IncludedAngle),
                    ccw=safe(lambda: bool(f.IsRightHandRule)))
    elif gtype == "ELLIPSE":
        f = narrow(fig, IADSketchEllipse)
        base.update(type="ellipse", center=pt2(safe(lambda: f.Center)),
                    major_axis=safe(lambda: f.MajorAxis),
                    minor_major_ratio=safe(lambda: f.MinorMajorRatio),
                    major_axis_angle=safe(lambda: f.MajorAxisAngle))
    elif gtype == "ELLIPTICAL_ARC":
        f = narrow(fig, IADSketchEllipticArc)
        base.update(type="elliptic_arc", center=pt2(safe(lambda: f.Center)),
                    major_axis=safe(lambda: f.MajorAxis),
                    minor_major_ratio=safe(lambda: f.MinorMajorRatio),
                    start=pt2(safe(lambda: f.Start)), end=pt2(safe(lambda: f.End)),
                    major_axis_angle=safe(lambda: f.MajorAxisAngle),
                    ccw=safe(lambda: bool(f.IsRightHandRule)))
    elif gtype == "POINT":
        f = narrow(fig, IADSketchPoint)
        base.update(type="point", x=safe(lambda: f.X), y=safe(lambda: f.Y),
                    is_node=safe(lambda: bool(f.IsSketchNode)))
    elif gtype == "BSPLINE":
        f = narrow(fig, IADSketchBspline)
        base.update(type="bspline", start=pt2(safe(lambda: f.StartPoint)),
                    end=pt2(safe(lambda: f.EndPoint)))
        defn = call_outparams(f, "GetDefinition", 0)
        if isinstance(defn, (tuple, list)):
            base["definition"] = [x for x in defn]
        data = safe(lambda: f.GetBsplineData())
        if isinstance(data, (tuple, list)):
            base["bspline_data"] = _arrays_to_lists(data)
    elif gtype == "SKETCHTEXT":
        f = narrow(fig, IADSketchText)
        base.update(type="text", text=safe(lambda: f.TextString))
    else:
        base["type"] = (gtype or "unknown").lower()
    return base

def _arrays_to_lists(data):
    out = []
    for arr in data:
        try:
            out.append([x for x in arr])
        except Exception:  # noqa: BLE001
            out.append(str(arr))
    return out

def scan_sketch_dimensions(sk):
    out = []
    dims = safe(lambda: sk.Dimensions)
    for i in range(safe(lambda: dims.Count, 0)):
        d = safe(lambda i=i: dims.Item(i))
        if d is None:
            continue
        out.append({
            "dimension_type": enum_name(alibrex.ADDimensionType, safe(lambda: d.DimensionType), "AD_"),
            "parameter": param_ref(safe(lambda: d.Parameter)),
        })
    return out

def scan_sketch_constraints(sk):
    cons = safe(lambda: sk.SketchConstraints)
    count = safe(lambda: cons.Count, 0)
    by_type, flat = {}, []
    for i in range(count):
        c = safe(lambda i=i: cons.Item(i))
        if c is None:
            continue
        t = enum_name(alibrex.ADSketchConstraintType, safe(lambda: c.SketchConstraintType), "AD_CONSTRAINT_")
        flat.append(t)
        by_type[t] = by_type.get(t, 0) + 1
    return {"count": count, "by_type": by_type, "types": flat}

def scan_sketches(part):
    out = []
    sks = safe(lambda: part.Sketches)
    for i in range(safe(lambda: sks.Count, 0)):
        sk = safe(lambda i=i: sks.Item(i))
        if sk is None:
            continue
        figures = []
        figs = safe(lambda: sk.Figures)
        for j in range(safe(lambda: figs.Count, 0)):
            fig = safe(lambda j=j: figs.Item(j))
            if fig is not None:
                figures.append(safe(lambda fig=fig: figure_dict(fig), {"type": "unreadable"}))
        consuming = safe(lambda: sk.ConsumingFeature)
        plane_proxy = safe(lambda: sk.SketchPlane)
        out.append({
            "id": f"sketch_{i}", "index": i, "kind": "2d",
            "name": safe(lambda: sk.Name),
            "is_closed": safe(lambda: bool(sk.IsClosed)),
            "is_consumed": safe(lambda: bool(sk.IsConsumed)),
            "is_suppressed": safe(lambda: bool(sk.IsSuppressed)),
            "is_active": safe(lambda: bool(sk.IsActive)),
            "consumed_by": safe(lambda: consuming.Name) if consuming else None,
            "plane": {
                "name": safe(lambda: plane_proxy.DisplayName) if plane_proxy else None,
                "normal": vec3(safe(lambda: sk.SketchPlaneNormal)),
            },
            "origin": pt2(safe(lambda: sk.OriginPoint)),
            "entities": figures,
            "dimensions": scan_sketch_dimensions(sk),
            "constraints": scan_sketch_constraints(sk),
        })
    return out

def scan_sketches_3d(part):
    out = []
    sks = safe(lambda: part.Sketches3D)
    for i in range(safe(lambda: sks.Count, 0)):
        sk = safe(lambda i=i: sks.Item(i))
        if sk is None:
            continue
        figures = []
        figs = safe(lambda: sk.Figures)
        for j in range(safe(lambda: figs.Count, 0)):
            fig = safe(lambda j=j: figs.Item(j))
            if fig is not None:
                figures.append(safe(lambda fig=fig: figure3d_dict(fig), {"type": "unreadable"}))
        consuming = safe(lambda: sk.ConsumingFeature)
        out.append({
            "id": f"sketch3d_{i}", "index": i, "kind": "3d",
            "name": safe(lambda: sk.Name),
            "is_consumed": safe(lambda: bool(sk.IsConsumed)),
            "is_suppressed": safe(lambda: bool(sk.IsSuppressed)),
            "is_active": safe(lambda: bool(sk.IsActive)),
            "consumed_by": safe(lambda: consuming.Name) if consuming else None,
            "entities": figures,
        })
    return out

def figure3d_dict(fig):
    gtype = enum_name(alibrex.ADGeometryType, safe(lambda: fig.FigureType), "AD_")
    base = {"geometry": gtype, "is_reference": safe(lambda: bool(fig.IsReference)),
            "id": safe(lambda: fig.ID)}
    if gtype == "LINE":
        f = narrow(fig, IAD3DSketchLine)
        base.update(type="line", start=pt3(safe(lambda: f.Start)),
                    end=pt3(safe(lambda: f.End)), length=safe(lambda: f.Length))
    elif gtype == "POINT":
        f = narrow(fig, IAD3DSketchPoint)
        base.update(type="point", x=safe(lambda: f.X), y=safe(lambda: f.Y), z=safe(lambda: f.Z),
                    is_node=safe(lambda: bool(f.IsSketchNode)))
    elif gtype == "CIRCLE":
        f = narrow(fig, IAD3DSketchCircle)
        base.update(type="circle", center=pt3(safe(lambda: f.Center)),
                    normal=vec3(safe(lambda: f.Normal)), radius=safe(lambda: f.Radius))
    elif gtype == "CIRCULAR_ARC":
        f = narrow(fig, IAD3DSketchCircularArc)
        base.update(type="arc", center=pt3(safe(lambda: f.Center)), radius=safe(lambda: f.Radius),
                    start=pt3(safe(lambda: f.Start)), end=pt3(safe(lambda: f.End)),
                    included_angle=safe(lambda: f.IncludedAngle),
                    ccw=safe(lambda: bool(f.IsRightHandRule)))
    elif gtype == "ELLIPSE":
        f = narrow(fig, IAD3DSketchEllipse)
        base.update(type="ellipse", center=pt3(safe(lambda: f.Center)),
                    major_radius_point=pt3(safe(lambda: f.MajorRadiusPoint)),
                    minor_radius_point=pt3(safe(lambda: f.MinorRadiusPoint)))
    elif gtype == "ELLIPTICAL_ARC":
        f = narrow(fig, IAD3DSketchEllipticArc)
        base.update(type="elliptic_arc", center=pt3(safe(lambda: f.Center)),
                    major_radius_point=pt3(safe(lambda: f.MajorRadiusPoint)),
                    minor_radius_point=pt3(safe(lambda: f.MinorRadiusPoint)),
                    start=pt3(safe(lambda: f.Start)), end=pt3(safe(lambda: f.End)),
                    ccw=safe(lambda: bool(f.IsRightHandRule)))
    elif gtype == "BSPLINE":
        f = narrow(fig, IAD3DSketchBspline)
        base.update(type="bspline", start=pt3(safe(lambda: f.StartPoint)),
                    end=pt3(safe(lambda: f.EndPoint)))
    else:
        base["type"] = (gtype or "unknown").lower()
    return base

def _bbox(obj):
    ext = safe(lambda: obj.GetExtents())
    if isinstance(ext, (tuple, list)) and len(ext) == 2:
        return {"min": pt3(ext[0]), "max": pt3(ext[1])}
    return None

def edge_fingerprint(edge):
    return {
        "kind": "edge",
        "key": safe(lambda: str(edge.Key)),
        "curve": enum_name(alibrex.ADObjectType, safe(lambda: edge.Geometry.Type), "AD_"),
        "start": pt3(safe(lambda: edge.StartVertex.Point)),
        "end": pt3(safe(lambda: edge.EndVertex.Point)),
        "bbox": _bbox(edge),
        "timestamp": safe(lambda: edge.TimeStamp),
    }

def face_fingerprint(face):
    return {
        "kind": "face",
        "key": safe(lambda: str(face.Key)),
        "surface": enum_name(alibrex.ADObjectType, safe(lambda: face.Geometry.Type), "AD_"),
        "bbox": _bbox(face),
        "timestamp": safe(lambda: face.TimeStamp),
    }

def serialize_collection(coll):
    """Serialize an IObjectCollector of edges/faces into generic fingerprints.

    Members that are opaque ``__ComObject`` proxies (e.g. a sweep Path, which
    pythonnet cannot navigate) are marked ``opaque`` rather than guessed at.
    """
    out = []
    if coll is None:
        return out
    for i in range(safe(lambda: coll.Count, 0)):
        item = safe(lambda i=i: coll.Item(i))
        if item is None:
            continue
        if safe(lambda: item.StartVertex) is not None:
            out.append(edge_fingerprint(item))
        elif safe(lambda: item.Loops) is not None:
            out.append(face_fingerprint(item))
        else:
            out.append({"kind": "opaque",
                        "object_type": enum_name(alibrex.ADObjectType, safe(lambda: coll.ObjectType), "AD_")})
    return out

def scan_topology(part):
    bodies = []
    bc = safe(lambda: part.Bodies.Count, 0)
    for i in range(bc):
        ts = safe(lambda i=i: part.Bodies.Item(i).TopologySummary)
        body = safe(lambda i=i: part.Bodies.Item(i))
        bodies.append({
            "index": i,
            "faces": safe(lambda: ts.FacesCount),
            "edges": safe(lambda: ts.EdgesCount),
            "vertices": safe(lambda: ts.VerticesCount),
            "lumps": safe(lambda: ts.LumpsCount),
            "shells": safe(lambda: ts.ShellsCount),
            "loops": safe(lambda: ts.LoopsCount),
            "timestamp": safe(lambda: body.TimeStamp),
            "bbox": _bbox(body) if body else None,
        })
    return {"bodies": bodies}

_DUCK_PROBES = (
    (IADHoleFeature, "HoleType", "AD_HOLE_FEATURE"),
    (IADFilletFeature, "IsConstantRadius", "AD_FILLET_FEATURE"),
    (IADChamferFeature, "Distance1", "AD_CHAMFER_FEATURE"),
    (IADRevolutionFeature, "AngleParameter", "AD_REVOLUTION_FEATURE"),
    (IADSweepFeature, "IsRigid", "AD_SWEEP_FEATURE"),
    (IADExtrusionFeature, "DepthParameter", "AD_EXTRUSION_FEATURE"),
)
_NAME_PREFIXES = {
    "Extrusion": "AD_EXTRUSION_FEATURE", "Revolution": "AD_REVOLUTION_FEATURE",
    "Sweep": "AD_SWEEP_FEATURE", "Loft": "AD_LOFT_FEATURE",
    "Fillet": "AD_FILLET_FEATURE", "Chamfer": "AD_CHAMFER_FEATURE",
    "Hole": "AD_HOLE_FEATURE", "Shell": "AD_SHELL_FEATURE",
    "Mirror": "AD_MIRROR_FEATURE", "Pattern": "AD_PATTERN_FEATURE",
    "Draft": "AD_DRAFT_FEATURE", "Scale": "AD_SCALE_FEATURE",
    "Helix": "AD_HELICAL_FEATURE", "Thread": "AD_EXTERNAL_THREAD_FEATURE",
}

def infer_native_type(feat):
    raw = safe(lambda: feat.FeatureType)
    if raw is not None:
        return enum_name(alibrex.ADPartFeatureType, raw, "")
    for iface, prop, native in _DUCK_PROBES:
        probe = safe(lambda iface=iface: narrow(feat, iface))
        if probe is not None and safe(lambda probe=probe, prop=prop: getattr(probe, prop)) is not None:
            return native
    name = safe(lambda: feat.Name) or ""
    for prefix, native in _NAME_PREFIXES.items():
        if name.startswith(prefix):
            return native
    return "AD_UNKNOWN_FEATURE"

def _sketch_id_by_name(sketches, name):
    for s in sketches:
        if s["name"] == name:
            return s["id"]
    return None

def _proxy_ref(tp):
    if tp is None:
        return None
    return {"display_name": safe(lambda: tp.DisplayName)}

_OP_MAP = {
    "AD_EXTRUSION_FEATURE": "extrude", "AD_REVOLUTION_FEATURE": "revolve",
    "AD_HOLE_FEATURE": "hole", "AD_FILLET_FEATURE": "fillet",
    "AD_CHAMFER_FEATURE": "chamfer", "AD_VERTEX_CHAMFER_FEATURE": "vertex_chamfer",
    "AD_SHELL_FEATURE": "shell", "AD_SWEEP_FEATURE": "sweep",
    "AD_LOFT_FEATURE": "loft", "AD_PATTERN_FEATURE": "pattern",
    "AD_MIRROR_FEATURE": "mirror", "AD_DRAFT_FEATURE": "draft",
    "AD_SCALE_FEATURE": "scale", "AD_OFFSET_FACE_FEATURE": "offset_face",
    "AD_HELICAL_FEATURE": "helix", "AD_EXTERNAL_THREAD_FEATURE": "external_thread",
}

_UNREADABLE = {
    "AD_MIRROR_FEATURE", "AD_PATTERN_FEATURE", "AD_MESH_BOOLEAN_FEATURE",
    "AD_MOVE_FACE_FEATURE", "AD_REMOVE_FACE_FEATURE", "AD_DELETE_LUMPS_FEATURE",
    "AD_THIN_WALL_EXTRUSION_FEATURE", "AD_THIN_WALL_REVOLUTION_FEATURE",
    "AD_THIN_WALL_SWEEP_FEATURE", "AD_THICKEN_SURFACE_FEATURE",
    "AD_TRIM_MODEL_FEATURE", "AD_DESIGNBOOLEAN_FEATURE", "AD_IMPORT_FILE_FEATURE",
    "AD_SM_CLOSEDCORNER_FEATURE", "AD_SM_CORNERCHAMFER_FEATURE",
    "AD_SM_CORNERROUND_FEATURE", "AD_SM_DIMPLE_FEATURE", "AD_SM_FLANGE_FEATURE",
    "AD_SM_PUNCH_FEATURE", "AD_SM_REBEND_FEATURE", "AD_SM_TAB_FEATURE",
    "AD_SM_UNBEND_FEATURE",
}

def serialize_param_collection(coll):
    """Serialize an IObjectCollector of IADParameter into param refs."""
    out = []
    if coll is None:
        return out
    for i in range(safe(lambda: coll.Count, 0)):
        item = safe(lambda i=i: coll.Item(i))
        if item is not None:
            out.append(param_ref(item))
    return out

def feature_params(feat, native, sketches):
    p = {}
    if native == "AD_EXTRUSION_FEATURE":
        f = narrow(feat, IADExtrusionFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_extrude" if cut else "extrude", is_cutout=cut,
                 depth=param_ref(safe(lambda: f.DepthParameter)),
                 draft=param_ref(safe(lambda: f.DraftParameter)),
                 is_outward_draft=safe(lambda: bool(f.IsOutwardDraft)),
                 end_condition=enum_name(alibrex.ADPartFeatureEndCondition, safe(lambda: f.EndConditionType), "AD_"),
                 direction=enum_name(alibrex.ADDirectionType, safe(lambda: f.DirectionType), "AD_"),
                 direction_reversed=safe(lambda: bool(f.IsDirectionReversed)),
                 direction_vector=vec3(safe(lambda: f.DirectionVector)),
                 to_geometry_offset=safe(lambda: f.ToGeometryOffset),
                 end_condition_ref=_proxy_ref(safe(lambda: f.EndCondition)),
                 direction_ref=_proxy_ref(safe(lambda: f.Direction)),
                 profile_sketch=_profile_id(f, sketches))
    elif native == "AD_REVOLUTION_FEATURE":
        f = narrow(feat, IADRevolutionFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_revolve" if cut else "revolve", is_cutout=cut,
                 angle=param_ref(safe(lambda: f.AngleParameter)),
                 axis=_proxy_ref(safe(lambda: f.Axis)),
                 profile_sketch=_profile_id(f, sketches))
    elif native == "AD_SWEEP_FEATURE":
        f = narrow(feat, IADSweepFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_sweep" if cut else "sweep", is_cutout=cut,
                 is_rigid=safe(lambda: bool(f.IsRigid)),
                 draft=param_ref(safe(lambda: f.DraftParameter)),
                 is_outward_draft=safe(lambda: bool(f.IsOutwardDraft)),
                 end_condition=enum_name(alibrex.ADPartFeatureEndCondition, safe(lambda: f.EndConditionType), "AD_"),
                 to_geometry_offset=safe(lambda: f.ToGeometryOffset),
                 profile_sketch=_profile_id(f, sketches),
                 path=serialize_collection(safe(lambda: f.Path)))
    elif native == "AD_LOFT_FEATURE":
        f = narrow(feat, IADLoftFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_loft" if cut else "loft", is_cutout=cut,
                 uses_guide_curves=safe(lambda: bool(f.IsUsingGuideCurves)),
                 guide_curve_type=enum_name(alibrex.ADLoftGuideType, safe(lambda: f.GuideCurveType), "AD_"),
                 minimize_twist=safe(lambda: bool(f.IsMinimizeTwist)),
                 minimize_curvature=safe(lambda: bool(f.IsMinimizeCurvature)),
                 simplify_surface=safe(lambda: bool(f.IsSimplifySurface)),
                 connect_ends=safe(lambda: bool(f.IsConnectEnds)),
                 cross_sections=serialize_collection(safe(lambda: f.CrossSections)),
                 guide_curves=serialize_collection(safe(lambda: f.GuideCurves)))
    elif native == "AD_HOLE_FEATURE":
        f = narrow(feat, IADHoleFeature)
        p["operation"] = "hole"
        p["hole_type"] = enum_name(alibrex.ADHoleType, safe(lambda: f.HoleType), "AD_")
        p["depth_condition"] = enum_name(alibrex.ADHoleDepthCondition, safe(lambda: f.DepthConditionType), "AD_")
        for key in ("Diameter", "Depth", "NumberOfHoles", "MajorDiameter", "MinorDiameter",
                    "DrillAngle", "CounterBoreDiameter", "CounterBoreDepth", "CounterDrillDiameter",
                    "CounterDrillDepth", "CounterDrillAngle", "CounterSinkDiameter", "CounterSinkAngle",
                    "OffsetFromLimitingGeometry"):
            p[key.lower()] = safe(lambda key=key: getattr(f, key))
        p["has_thread"] = safe(lambda: bool(f.HasThread))
        p["thread"] = _thread_info(safe(lambda: f.TappedThread)) if safe(lambda: bool(f.HasThread)) else None
        p["start_plane"] = _proxy_ref(safe(lambda: f.StartPlane)) if not isinstance(safe(lambda: f.StartPlane), (int, float, type(None))) else safe(lambda: f.StartPlane)
        p["limiting_geometry"] = face_fingerprint(safe(lambda: f.LimitingGeometry)) if safe(lambda: f.LimitingGeometry) else None
        p["start_points"] = safe(lambda: f.NumberOfHoles)
        p["profile_sketch"] = _profile_id(f, sketches)
    elif native == "AD_FILLET_FEATURE":
        f = narrow(feat, IADFilletFeature)
        p.update(operation="fillet",
                 is_constant_radius=safe(lambda: bool(f.IsConstantRadius)),
                 radius=param_ref(safe(lambda: f.ConstantRadius)),
                 start_radius_params=serialize_param_collection(safe(lambda: f.StartRadiusParams)),
                 end_radius_params=serialize_param_collection(safe(lambda: f.EndRadiusParams)),
                 tangent_propagate=safe(lambda: bool(f.TangentPropagate)),
                 edges=serialize_collection(safe(lambda: f.EdgesOrFaces)))
    elif native == "AD_CHAMFER_FEATURE":
        f = narrow(feat, IADChamferFeature)
        p.update(operation="chamfer",
                 distance1=param_ref(safe(lambda: f.Distance1)),
                 distance2=param_ref(safe(lambda: f.Distance2)),
                 angle=param_ref(safe(lambda: f.Angle)),
                 tangent_propagate=safe(lambda: bool(f.TangentPropagate)),
                 edges=serialize_collection(safe(lambda: f.EdgesAndFaces)))
    elif native == "AD_VERTEX_CHAMFER_FEATURE":
        f = narrow(feat, IADVertexChamferFeature)
        p.update(operation="vertex_chamfer",
                 distance1=param_ref(safe(lambda: f.Distance1)),
                 distance2=param_ref(safe(lambda: f.Distance2)),
                 distance3=param_ref(safe(lambda: f.Distance3)),
                 vertices=serialize_collection(safe(lambda: f.Vertices)))
    elif native == "AD_SHELL_FEATURE":
        f = narrow(feat, IADShellFeature)
        mt = safe(lambda: f.MultiThicknesses)
        p.update(operation="shell",
                 thickness=param_ref(safe(lambda: f.StandardThickness)),
                 is_shell_outward=safe(lambda: bool(f.IsShellOutward)),
                 removed_faces=serialize_collection(safe(lambda: f.RemovedFaces)),
                 multi_thickness_faces=serialize_collection(safe(lambda: f.MultiThicknessFaces)),
                 multi_thicknesses=_arrays_to_lists([mt])[0] if mt is not None else None)
    elif native == "AD_DRAFT_FEATURE":
        f = narrow(feat, IADDraftFeature)
        p.update(operation="draft",
                 angle=param_ref(safe(lambda: f.DraftAngleParameter)),
                 is_outward_draft=safe(lambda: bool(f.IsOutwardDraft)),
                 neutral_plane=_proxy_ref(safe(lambda: f.DraftNeutralPlane)),
                 faces=serialize_collection(safe(lambda: f.DraftFaces)))
    elif native == "AD_SCALE_FEATURE":
        f = narrow(feat, IADScaleFeature)
        p.update(operation="scale",
                 about_centroid=safe(lambda: bool(f.ScaleAboutCenteroid)),
                 uniform=safe(lambda: bool(f.IsUniformScaling)),
                 factor=param_ref(safe(lambda: f.UniformScaleFactor)),
                 factor_x=param_ref(safe(lambda: f.UniformScaleFactorX)),
                 factor_y=param_ref(safe(lambda: f.UniformScaleFactorY)),
                 factor_z=param_ref(safe(lambda: f.UniformScaleFactorZ)))
    elif native == "AD_OFFSET_FACE_FEATURE":
        f = narrow(feat, IADOffsetFaceFeature)
        p.update(operation="offset_face",
                 offset=param_ref(safe(lambda: f.OffsetParameter)),
                 faces=serialize_collection(safe(lambda: f.OffsetFaces)))
    elif native == "AD_PROJECT_FEATURE":
        f = narrow(feat, IADProjectFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_project" if cut else "project", is_cutout=cut,
                 depth=param_ref(safe(lambda: f.DepthParameter)),
                 into_sketch_plane=safe(lambda: bool(f.IsIntoSketchPlane)),
                 profile_sketch=_profile_id(f, sketches))
    elif native == "AD_WRAP_FEATURE":
        f = narrow(feat, IADWrapFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_wrap" if cut else "wrap", is_cutout=cut,
                 depth=param_ref(safe(lambda: f.DepthParameter)),
                 focus_type=enum_name(alibrex.ADWrapFocusType, safe(lambda: f.FocusType), "AD_"),
                 target_face=_proxy_ref(safe(lambda: f.TargetFace)),
                 profile_sketch=_profile_id(f, sketches))
    elif native == "AD_HELICAL_FEATURE":
        f = narrow(feat, IADHelicalFeature)
        cut = safe(lambda: bool(f.IsCutout))
        p.update(operation="cut_helix" if cut else "helix", is_cutout=cut,
                 helix_type=enum_name(alibrex.ADHelixType, safe(lambda: f.HelixType), "AD_"),
                 pitch_type=enum_name(alibrex.ADPitchType, safe(lambda: f.PitchType), "AD_"),
                 clockwise=safe(lambda: bool(f.IsClockwise)),
                 reverse=safe(lambda: bool(f.IsReverse)),
                 height=param_ref(safe(lambda: f.Height)),
                 pitch=param_ref(safe(lambda: f.Pitch)),
                 revolutions=param_ref(safe(lambda: f.Revolutions)),
                 taper=param_ref(safe(lambda: f.Taper)),
                 axis=_proxy_ref(safe(lambda: f.Axis)),
                 profile_sketch=_profile_id(f, sketches))
    elif native == "AD_EXTERNAL_THREAD_FEATURE":
        f = narrow(feat, IADExternalThreadFeature)
        p.update(operation="external_thread",
                 major_diameter=safe(lambda: f.MajorDiameter),
                 minor_diameter=param_ref(safe(lambda: f.MinorDiameter)),
                 thread_length=param_ref(safe(lambda: f.ThreadLength)),
                 has_edge_chamfer=safe(lambda: bool(f.HasEdgeChamfer)),
                 callout=safe(lambda: f.Callout))
    else:
        p["operation"] = _OP_MAP.get(native, native.lower().replace("ad_", "").replace("_feature", ""))
    return p

def _profile_id(f, sketches):
    sk = safe(lambda: f.Sketch)
    return _sketch_id_by_name(sketches, safe(lambda: sk.Name)) if sk else None

def _thread_info(ti):
    if ti is None:
        return None
    return {
        "thread_type": enum_name(alibrex.ADTappedThreadType, safe(lambda: ti.ThreadType), "AD_"),
        "name": safe(lambda: ti.Name), "thread_class": safe(lambda: ti.ThreadClass),
        "pitch": safe(lambda: ti.Pitch), "tap_drill_diameter": safe(lambda: ti.TapDrillDiameter),
        "major_diameter": safe(lambda: ti.MajorDiameter), "minor_diameter": safe(lambda: ti.MinorDiameter),
        "pitch_diameter": safe(lambda: ti.PitchDiameter), "thread_length": safe(lambda: ti.ThreadLength),
        "is_valid": safe(lambda: bool(ti.IsValidThread)),
    }

def feature_appearance(feat):
    return {
        "face_color": safe(lambda: feat.FaceColor),
        "edge_color": safe(lambda: feat.EdgeColor),
        "opacity": safe(lambda: feat.Opacity),
        "reflectivity": safe(lambda: feat.Reflectivity),
        "use_part_color": safe(lambda: bool(feat.UsePartColor)),
    }

def scan_features(part, sketches):
    out = []
    feats = safe(lambda: part.Features)
    n = safe(lambda: feats.Count, 0)
    for i in range(n):
        feat = safe(lambda i=i: feats.Item(i))
        if feat is None:
            continue
        native = infer_native_type(feat)
        record = {
            "index": i,
            "name": safe(lambda: feat.Name),
            "native_type": native,
            "operation": _OP_MAP.get(native, native.lower().replace("ad_", "").replace("_feature", "")),
            "suppressed": safe(lambda: bool(feat.IsSuppressed)),
            "has_error": safe(lambda: bool(feat.HasError)),
            "is_active": safe(lambda: bool(feat.IsActive)),
            "is_sheet_metal": safe(lambda: bool(feat.IsSheetMetalFeature)),
            "unreadable": native in _UNREADABLE,
            "appearance": feature_appearance(feat),
        }
        if native in _UNREADABLE:
            record["parameters"] = {"operation": record["operation"],
                                    "note": "AlibreX exposes no readable definition for this feature type"}
        else:
            record["parameters"] = safe(lambda: feature_params(feat, native, sketches), {})
            if isinstance(record["parameters"], dict) and record["parameters"].get("operation"):
                record["operation"] = record["parameters"].pop("operation")

        consumed = [s["id"] for s in sketches if s.get("consumed_by") == record["name"]]
        record["consumed_sketches"] = consumed
        params = record["parameters"]
        if isinstance(params, dict) and record["operation"] in ("sweep", "cut_sweep"):
            profile = params.get("profile_sketch")
            params["path_sketches"] = [sid for sid in consumed if sid != profile]
        out.append(record)
    return out

def scan_part(part):
    sketches = scan_sketches(part)
    sketches3d = scan_sketches_3d(part)
    return {
        "schema": SCHEMA,
        "generator": "alibrex scan_feature_tree.py",
        "source_cad": "Alibre Design",
        "document": scan_document(part),
        "physical_properties": scan_physical(part),
        "configurations": scan_configurations(part),
        "parameters": scan_parameters(part),
        "reference_geometry": scan_reference_geometry(part),
        "sketches": sketches,
        "sketches_3d": sketches3d,
        "features": scan_features(part, sketches + sketches3d),
        "topology": scan_topology(part),
    }

def resolve_active_part():
    try:
        return CurrentPart()
    except Exception:  # noqa: BLE001
        return None

def default_output(part):
    path = safe(lambda: part.FilePath) or ""
    name = safe(lambda: part.Name) or "part"
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in name).strip()
    if path and os.path.isdir(os.path.dirname(path)):
        return os.path.join(os.path.dirname(path), f"{safe_name}.feature_tree.json")
    return os.path.join(os.getcwd(), f"{safe_name}.feature_tree.json")

def main(argv):
    part = resolve_active_part()
    if part is None:
        asm = safe(lambda: CurrentAssembly())
        if asm is not None:
            print("[error] Active document is an assembly. Open a PART and re-run.", file=sys.stderr)
        else:
            print("[error] No active part found. Open a part in Alibre Design.", file=sys.stderr)
        return 1

    print(f"[info] Scanning part: {safe(lambda: part.Name)!r}")
    model = scan_part(part)

    out_path = argv[1] if len(argv) > 1 else default_output(part)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(model, fh, indent=2, default=str)

    d = model["document"]
    print(f"[ok] Wrote {out_path}")
    print(f"     units={d['units']['model']}  features={len(model['features'])}  "
          f"sketches={len(model['sketches'])}(+{len(model['sketches_3d'])} 3D)  "
          f"params={len(model['parameters'])}  configs={len(model['configurations'])}")
    for f in model["features"]:
        flags = "".join([" S" if f["suppressed"] else "", " ERR" if f["has_error"] else "",
                         " UNREADABLE" if f["unreadable"] else ""])
        print(f"     {f['index']:>2}. {f['operation']:<15} {f['name']}{flags}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
