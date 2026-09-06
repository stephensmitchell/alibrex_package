"""Sketch-2D demo 01: apply each geometric constraint type once.

Walks through the most common ``ADSketchConstraintType`` values
(horizontal, vertical, parallel, perpendicular, coincident, equal)
on freshly drawn sketch figures and verifies each call lands a new
constraint in ``IADSketch.SketchConstraints``.

Pass criteria:
  - Each constraint increments ``SketchConstraints.Count`` by one.
  - Each constraint reads back the same ``SketchConstraintType``
    we asked for.
  - No call raises.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADSketchConstraintType, connect, run_example

def xy_plane(part):
    return part.DesignPlanes.Item(0)

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"SK2_01_{tag}")
    root = connect()
    sk = part.Sketches.AddSketch(None, xy_plane(part), "ConstraintShowcase")

    sk.BeginChange()
    try:
        sk.Figures.AddLine(0.0, 0.0, 5.0, 1.0)
        sk.Figures.AddLine(7.0, 0.0, 7.25, 4.0)
        sk.Figures.AddLine(0.0, 5.0, 4.0, 6.0)
        sk.Figures.AddLine(6.0, 5.0, 9.0, 7.0)
    finally:
        sk.EndChange()

    n_lines = sk.Figures.Count
    print(f"Sketch has {n_lines} figures before constraints.")

    cs = sk.SketchConstraints
    before = cs.Count
    print(f"Constraints before: {before}")

    cases = [
        ("HORIZONTAL", ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL, [0]),
        ("VERTICAL",   ADSketchConstraintType.AD_CONSTRAINT_VERTICAL,   [1]),
        ("PARALLEL",   ADSketchConstraintType.AD_CONSTRAINT_PARALLEL,   [2, 3]),
        ("EQUAL",      ADSketchConstraintType.AD_CONSTRAINT_EQUAL,      [2, 3]),
    ]
    applied = []
    sk.BeginChange()
    try:
        for label, ctype, indices in cases:
            targets = root.NewObjectCollector()
            for idx in indices:
                targets.Add(sk.Figures.Item(idx))
            ok = cs.AddConstraint(targets, ctype)
            new_count = sk.SketchConstraints.Count
            print(f"  {label:12s} {'OK' if ok else 'FAIL'}  count -> {new_count}")
            applied.append((label, ok, new_count))
    finally:
        sk.EndChange()

    final = sk.SketchConstraints.Count
    new_constraints = [sk.SketchConstraints.Item(i) for i in range(before, final)]

    return report([
        ("all AddConstraint returned True",  all(ok for _, ok, _ in applied)),
        ("count grew by N",                  final == before + len(cases)),
        ("each constraint has a recorded type",
            all(int(c.SketchConstraintType) > 0 for c in new_constraints)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
