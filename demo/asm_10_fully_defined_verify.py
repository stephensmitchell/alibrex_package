"""Assembly demo 10: empirically verify a part is FULLY DEFINED.

AlibreX doesn't expose ``IsFullyDefined`` / ``DegreesOfFreedom``
properties on ``IADOccurrence``, so the only honest way to prove a part
is fully constrained is to **try to move it and watch the solver pull
it back**. A fully constrained part has zero remaining degrees of
freedom: any ``ApplyTransform`` drift gets rejected by the solver and
the WorldTransform stays put.

Pipeline:
  1. Open a fresh assembly with two muffler parts.
  2. Anchor A, leave B floating; record B's translation.
  3. Verify B is *not* fully defined by drifting it; assert B's
     position changed.
  4. Add three plane-align constraints between A and B (the standard
     fully-constrain pattern from asm_05).
  5. Verify B is now fully defined by drifting it again; the solver
     should restore B to the constrained position.

Pass criteria:
  - Pre-constraint drift: B's translation changed (under-constrained).
  - Post-constraint drift: B's translation matches the constrained
    position (within 1e-3 cm): the solver pulled it back.
  - All three constraints report ``HasError == False``.
"""
from __future__ import annotations

import math
import os
import sys
import uuid

from _demo_utils import MUFFLER_DIR, report
from alibrex import ADAssemblyConstraintType, connect, run_example


def _translation(occ) -> tuple[float, float, float]:
    flat = list(occ.WorldTransform.Array())
    return (flat[12], flat[13], flat[14])


def _approx_eq(a: tuple[float, ...], b: tuple[float, ...], tol: float = 1e-3) -> bool:
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b))


def main() -> int:
    part_a = os.path.join(MUFFLER_DIR, "cylinder.AD_PRT")
    part_b = os.path.join(MUFFLER_DIR, "choke tube.AD_PRT")
    tag = uuid.uuid4().hex[:6]

    root = connect()
    asm = root.CreateEmptyAssembly(f"FullyDefined_{tag}")
    geo = asm.GeometryFactory

    a_obj: object = part_a
    b_obj: object = part_b
    asm.RootOccurrence.Occurrences.Add(a_obj, geo.CreateTranslationTransformByXYZ(0.0, 0.0, 0.0))
    asm.RootOccurrence.Occurrences.Add(b_obj, geo.CreateTranslationTransformByXYZ(10.0, 5.0, 8.0))
    asm.RootOccurrence.Occurrences.Item(0).IsAnchored = True

    # ----- Phase 1: drift WITHOUT constraints (under-constrained) -----
    pre_drift = _translation(asm.RootOccurrence.Occurrences.Item(1))
    drift_xform = geo.CreateTranslationTransformByXYZ(7.0, 3.0, 4.0)
    asm.RootOccurrence.Occurrences.Item(1).ApplyTransform(drift_xform)
    post_drift_no_constraints = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"Phase 1 (no constraints):")
    print(f"  before drift: {pre_drift}")
    print(f"  after  drift: {post_drift_no_constraints}")

    # ----- Phase 2: fully constrain via 3 plane aligns -----
    for idx, label in [(0, "XY"), (1, "YZ"), (2, "ZX")]:
        occ_a = asm.RootOccurrence.Occurrences.Item(0)
        occ_b = asm.RootOccurrence.Occurrences.Item(1)
        t_a = asm.NewTargetProxy(occ_a, occ_a.DesignSession.DesignPlanes.Item(idx))
        t_b = asm.NewTargetProxy(occ_b, occ_b.DesignSession.DesignPlanes.Item(idx))
        asm.AssemblyConstraints.AddConstraint(
            t_a, t_b, ADAssemblyConstraintType.AD_ALIGN_TYPE,
            None, False, f"Align_{label}", "",
        )

    constrained_pos = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"\nPhase 2 (3 plane aligns applied):")
    print(f"  constrained position: {constrained_pos}")
    expected = (0.0, 0.0, 0.0)

    # ----- Phase 3: drift WITH constraints (fully-constrained) -----
    asm.RootOccurrence.Occurrences.Item(1).ApplyTransform(drift_xform)
    post_drift_constrained = _translation(asm.RootOccurrence.Occurrences.Item(1))
    print(f"\nPhase 3 (drift attempt while fully constrained):")
    print(f"  position after drift attempt: {post_drift_constrained}")

    errors = [bool(asm.AssemblyConstraints.Item(i).HasError) for i in range(3)]
    print(f"\nConstraint errors: {errors}")

    return report([
        ("under-constrained: drift changed B",
            not _approx_eq(pre_drift, post_drift_no_constraints)),
        ("constraints landed at origin",
            _approx_eq(constrained_pos, expected)),
        ("fully constrained: drift snapped back",
            _approx_eq(post_drift_constrained, expected)),
        ("no constraint errors",
            not any(errors)),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
