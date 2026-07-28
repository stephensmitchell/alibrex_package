"""Assembly demo 06: suppress and unsuppress a constraint.

Builds a one-mate assembly, captures B's position with the constraint
active, then flips ``IsSuppressed`` on the constraint and verifies B
becomes free to drift back. Depending on the kernel's behavior B may
stay put; the *attribute* should at least round-trip. Then
unsuppresses again.

Pass criteria:
  - ``IsSuppressed`` reads False initially.
  - After setting True, reads True.
  - After setting False again, reads False.
  - ``HasError`` doesn't flip to True from the toggle.
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
    asm = root.CreateEmptyAssembly(f"Suppress_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 25.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    occ_a = asm.RootOccurrence.Occurrences.Item(0)
    occ_b = asm.RootOccurrence.Occurrences.Item(1)
    t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(0))
    t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(0))
    c = asm.AssemblyConstraints.AddConstraint(
        t_a, t_b, ADAssemblyConstraintType.AD_MATE_TYPE,
        None, False, f"MateXY_{tag}", "",
    )

    initial = bool(c.IsSuppressed)
    print(f"Initial IsSuppressed = {initial}, HasError = {c.HasError}")

    c.IsSuppressed = True
    c2 = asm.AssemblyConstraints.Item(0)
    after_suppress = bool(c2.IsSuppressed)
    print(f"After  IsSuppressed = True  -> reads {after_suppress}, HasError = {c2.HasError}")

    c2.IsSuppressed = False
    c3 = asm.AssemblyConstraints.Item(0)
    after_restore = bool(c3.IsSuppressed)
    print(f"After  IsSuppressed = False -> reads {after_restore}, HasError = {c3.HasError}")

    return report([
        ("initial unsuppressed",       initial is False),
        ("suppress to True landed",    after_suppress is True),
        ("restored to False",          after_restore is False),
        ("no kernel errors on toggle", not bool(c3.HasError)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
