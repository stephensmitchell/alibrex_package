"""Tiny helper that materialises sample .AD_PRT / .AD_ASM files on demand.

The file-loading examples in this folder accept a path argument; running
them without one used to fail with an argparse usage error. Each script
now falls back to ``ensure_sample_part()`` / ``ensure_sample_assembly()``
which lazily creates a small reference part / assembly in
``examples/_sample_files/`` the first time it's needed.

Subsequent runs reuse the cached files. Delete the folder to regenerate.
"""
from __future__ import annotations

import math
from pathlib import Path

from alibrex import (
    ADDirectionType,
    ADPartFeatureEndCondition,
    connect,
)

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "_sample_files"
SAMPLE_PART_NAME = "SamplePart"
SAMPLE_ASSEMBLY_NAME = "SampleAssembly"
SAMPLE_PART_PATH = SAMPLES_DIR / f"{SAMPLE_PART_NAME}.AD_PRT"
SAMPLE_ASSEMBLY_PATH = SAMPLES_DIR / f"{SAMPLE_ASSEMBLY_NAME}.AD_ASM"


def _save_session(session, folder: Path, name: str) -> Path:
    """``IADSession.SaveAs(ref folder, name)`` — folder is by-ref so our
    proxy returns a tuple. The file ends up at ``folder/name.AD_xxx``."""
    folder_str: object = str(folder)
    result = session.SaveAs(folder_str, name)
    # If proxy returns (out_folder,) tuple, the call still worked — both
    # forms acceptable.
    _ = result
    # Pick the produced file extension based on the session class.
    cls = type(session).__name__
    suffix = ".AD_ASM" if "Assembly" in str(session._clr.Name) else ".AD_PRT"
    return folder / f"{name}{suffix}"


def _build_sample_part(part) -> None:
    """Add a 40×20×10 mm extruded block so the file isn't empty."""
    xy = part.DesignPlanes.Item(0)
    sk = part.Sketches.AddSketch(None, xy, "Base")
    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 4.0, 0.0)
        sk.Figures.AddLine(4.0, 0.0, 4.0, 2.0)
        sk.Figures.AddLine(4.0, 2.0, 0.0, 2.0)
        sk.Figures.AddLine(0.0, 2.0, 0.0, 0.0)
    finally:
        sk.EndChange()
    part.Features.AddExtrudedBoss(
        sk, 1.0, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Block", "Depth", "",
    )


def ensure_sample_part(path: Path = SAMPLE_PART_PATH) -> Path:
    """Return a path to a small sample .AD_PRT, creating it if absent."""
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    root = connect()
    part = root.CreateEmptyPart(SAMPLE_PART_NAME, False)
    _build_sample_part(part)
    folder_ref: object = str(path.parent)
    part.SaveAs(folder_ref, SAMPLE_PART_NAME)
    return path


def ensure_sample_assembly(path: Path = SAMPLE_ASSEMBLY_PATH) -> Path:
    """Return a path to a small sample .AD_ASM (with a single occurrence)."""
    if path.exists():
        return path
    part_path = ensure_sample_part()
    path.parent.mkdir(parents=True, exist_ok=True)
    root = connect()
    asm = root.CreateEmptyAssembly(SAMPLE_ASSEMBLY_NAME)
    geo = asm.GeometryFactory
    xform = geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0)
    # ``IADOccurrences.Add`` takes a ``ref object designObject`` that can be
    # a file path string or an IADDesignSession.
    design_obj: object = str(part_path)
    asm.RootOccurrence.Occurrences.Add(design_obj, xform)
    folder_ref: object = str(path.parent)
    asm.SaveAs(folder_ref, SAMPLE_ASSEMBLY_NAME)
    return path
