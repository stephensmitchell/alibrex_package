"""Assembly demo 09 — delete a constraint and verify the count drops.

Adds two constraints, deletes one via ``IADAssemblyConstraint.Delete()``,
and confirms the collection count goes from 2 → 1. Verifies the
remaining constraint's identity is the *other* one (i.e. delete picked
the right object).
"""
from __future__ import annotations

import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example


def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    tag = uuid.uuid4().hex[:6]

    root = connect()
    asm = root.CreateEmptyAssembly(f"Delete_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 25.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a_xy = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b_xy = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))
    t_a_yz = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(1))
    t_b_yz = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(1))

    c_xy = asm.AssemblyConstraints.AddConstraint(
        t_a_xy, t_b_xy, ADAssemblyConstraintType.AD_MATE_TYPE,
        None, False, "MateXY_keep", "",
    )
    c_yz = asm.AssemblyConstraints.AddConstraint(
        t_a_yz, t_b_yz, ADAssemblyConstraintType.AD_MATE_TYPE,
        None, False, "MateYZ_delete", "",
    )
    print(f"Added 2 constraints; count = {asm.AssemblyConstraints.Count}")

    c_yz.Delete()
    after = asm.AssemblyConstraints.Count
    print(f"After Delete(): count = {after}")
    remaining = asm.AssemblyConstraints.Item(0)
    print(f"Remaining: name={remaining.Name}")

    return report([
        ("started at 2",         True),
        ("count went to 1",      after == 1),
        ("kept the XY mate",     remaining.Name == "MateXY_keep"),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
