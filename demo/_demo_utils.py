"""Tiny shared helpers for the CRUD demos.

Pattern: demos create their own document by default so they do not mutate
whatever the user currently has open in Alibre. Set
``ALIBREX_DEMOS_USE_ACTIVE=1`` to opt into the older active-document workflow.
"""
from __future__ import annotations

import os
import sys
import traceback
from collections import Counter
from collections.abc import Callable

import alibrex as _alibrex
from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    AlibreNotRunning,
    CurrentAssembly,
    CurrentPart,
    IADAssemblySession,
    connect,
    narrow,
)

def _session_key(session) -> tuple[str, str, str, str]:
    """Stable-enough identity for comparing Alibre sessions across snapshots."""
    def read(name: str) -> str:
        try:
            value = getattr(session, name)
        except Exception:  # noqa: BLE001
            return ""
        return "" if value is None else str(value)

    return (
        read("Identifier"),
        read("FilePath"),
        read("Name"),
        read("SessionType"),
    )


SessionKey = tuple[str, str, str, str]


def _session_snapshot(root) -> Counter[SessionKey]:
    sessions: Counter[SessionKey] = Counter()
    for i in range(root.Sessions.Count):
        sessions[_session_key(root.Sessions.Item(i))] += 1
    return sessions


def _close_sessions_opened_after(root, before: Counter[SessionKey]) -> None:
    """Close documents created/opened by a demo, preserving pre-existing sessions."""
    remaining = before.copy()
    to_close = []
    for i in range(root.Sessions.Count):
        session = root.Sessions.Item(i)
        key = _session_key(session)
        if remaining[key] > 0:
            remaining[key] -= 1
            continue
        try:
            name = session.Name
        except Exception:  # noqa: BLE001
            name = "<unknown>"
        to_close.append((name, session))

    for name, session in reversed(to_close):
        try:
            session.Close(False)
            print(f"[cleanup] Closed demo session: {name}")
        except Exception as exc:  # noqa: BLE001
            if "Browser is not found" in str(exc) or "Index out of bounds" in str(exc):
                continue
            print(f"[cleanup] Could not close {name!r}: {type(exc).__name__}: {exc}")


def run_demo(fn: Callable[[], object]) -> int:
    """Run a demo, return its real status, and close sessions it opened."""
    root = None
    before = None
    try:
        root = connect()
        before = _session_snapshot(root)
        result = fn()
        if result is None:
            return 0
        if isinstance(result, int):
            return result
        return 0
    except AlibreNotRunning as exc:
        print(f"[skip] {exc}", file=sys.stderr)
        return 0
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        if root is not None and before is not None:
            try:
                _close_sessions_opened_after(root, before)
            except Exception as exc:  # noqa: BLE001
                print(f"[cleanup] Cleanup failed: {type(exc).__name__}: {exc}")


# Existing demo files import ``run_example`` from alibrex after importing this
# module. Patch that name in the demo process so they get the cleanup wrapper.
_alibrex.run_example = run_demo


def _use_active_document() -> bool:
    value = os.environ.get("ALIBREX_DEMOS_USE_ACTIVE", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def part_or_open(default_name: str):
    """Return a fresh part, unless active-document demos are explicitly enabled."""
    if _use_active_document():
        try:
            part = CurrentPart()
            print(f"[info] Using active part: {part.Name!r}")
            return part
        except RuntimeError:
            pass
    root = connect()
    part = root.CreateEmptyPart(default_name, False)
    print(f"[info] Created demo part: {part.Name!r}.")
    return part


def fresh_part(name: str):
    """Always create a new in-memory part (predictable starting state)."""
    return connect().CreateEmptyPart(name, False)


def assembly_or_open(default_name: str):
    """Return a fresh assembly, unless active-document demos are explicitly enabled."""
    if _use_active_document():
        try:
            asm = CurrentAssembly()
            print(f"[info] Using active assembly: {asm.Name!r}")
            return asm
        except RuntimeError:
            pass
    root = connect()
    asm = root.CreateEmptyAssembly(default_name)
    print(f"[info] Created demo assembly: {asm.Name!r}.")
    return asm


def report(checks):
    """Print PASS/FAIL lines for each check; return overall exit code."""
    fails = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if fails:
        print(f"RESULT: FAIL ({len(fails)} of {len(checks)})")
        return 1
    print("RESULT: PASS")
    return 0


# ---------------------------------------------------------------------------
# Sketch / feature primitives - wrap the AlibreX 29 quirk that figure
# additions must happen between sketch.BeginChange() and sketch.EndChange().
# ---------------------------------------------------------------------------

def sketch_rectangle(part, plane, name: str, w: float, h: float,
                     x0: float = 0.0, y0: float = 0.0):
    """Add a sketch with a rectangle drawn as 4 closed lines. Returns the sketch."""
    sk = part.Sketches.AddSketch(None, plane, name)
    sk.BeginChange()
    try:
        sk.Figures.AddLine(x0,     y0,     x0 + w, y0)
        sk.Figures.AddLine(x0 + w, y0,     x0 + w, y0 + h)
        sk.Figures.AddLine(x0 + w, y0 + h, x0,     y0 + h)
        sk.Figures.AddLine(x0,     y0 + h, x0,     y0)
    finally:
        sk.EndChange()
    return sk


def sketch_circle(part, plane, name: str, cx: float, cy: float, r: float):
    """Add a sketch containing one circle. Returns the sketch."""
    sk = part.Sketches.AddSketch(None, plane, name)
    sk.BeginChange()
    try:
        sk.Figures.AddCircle(cx, cy, r)
    finally:
        sk.EndChange()
    return sk


def extrude_block(part, w: float, h: float, d: float, name: str = "Block"):
    """Sketch + extrude a rectangular block on the XY plane. Returns the feature."""
    xy = part.DesignPlanes.Item(0)
    sk = sketch_rectangle(part, xy, f"{name}_Sketch", w, h)
    return part.Features.AddExtrudedBoss(
        sk, d, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        name, f"{name}_Depth", "",
    )


def save_part_as(part, folder: str, name: str) -> str:
    """Save the part to ``folder/name.AD_PRT`` via IADSession.SaveAs.

    ``SaveAs`` takes a `ref object` destination (Windows folder path or
    repository folder dispatch) plus the item name; our proxy auto-
    surfaces by-ref params as a tuple. Returns the resulting file path.
    """
    import os
    folder_ref: object = folder
    part.SaveAs(folder_ref, name)
    return os.path.join(folder, name + ".AD_PRT")


# ---------------------------------------------------------------------------
# Bundled muffler assembly - a real, multi-level industrial part used by the
# crud_13.. demos. Stays read-only so the demos can run repeatedly without
# corrupting the file.
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
MUFFLER_DIR = os.path.join(_HERE, "muffler")
MUFFLER_ASSEMBLY = os.path.join(MUFFLER_DIR, "0_Muffler_Assembly.AD_ASM")


def open_muffler() -> IADAssemblySession:
    """Open the bundled muffler assembly and return its IADAssemblySession."""
    if not os.path.exists(MUFFLER_ASSEMBLY):
        raise SystemExit(
            f"Muffler assembly not found at {MUFFLER_ASSEMBLY}. "
            "Drop the muffler/ folder next to _demo_utils.py, or update "
            "MUFFLER_DIR to point at it."
        )
    return narrow(connect().OpenFile(MUFFLER_ASSEMBLY), IADAssemblySession)


def walk_occurrences(root_occ, fn) -> None:
    """Depth-first walk: call ``fn(occurrence, depth)`` for each occurrence
    *under* ``root_occ`` (the root itself isn't visited)."""
    def visit(occ, depth):
        for i in range(occ.Occurrences.Count):
            child = occ.Occurrences.Item(i)
            fn(child, depth)
            visit(child, depth + 1)
    visit(root_occ, 0)


def find_occurrence_by_name(root_occ, name: str):
    """Depth-first search; first occurrence whose Name equals or starts
    with ``name``. Returns None if no match."""
    found = [None]
    def collect(occ, _depth):
        if found[0] is not None:
            return
        if occ.Name == name or occ.Name.startswith(name):
            found[0] = occ
    walk_occurrences(root_occ, collect)
    return found[0]


def stl_size(part, base_path: str) -> int:
    """Export STL and return its size in bytes (0 on failure).

    A non-zero STL means the BREP tessellated cleanly - a strong validity
    check on top of feature-count assertions.
    """
    path = base_path + ".stl"
    if os.path.exists(path):
        os.remove(path)
    try:
        part.ExportSTL(path, 0.5, 15.0, 0.05)
        return os.path.getsize(path) if os.path.exists(path) else 0
    except Exception:  # noqa: BLE001
        return 0
