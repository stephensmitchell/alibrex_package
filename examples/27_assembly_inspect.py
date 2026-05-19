"""Example 27 — inspect the active assembly's structure and constraints.

Run this against an existing assembly (any complexity). It prints the
full occurrence tree with world transforms, lists every assembly
constraint with its type, and dumps any global parameters declared on
the session.

Covers: IADAssemblySession.RootOccurrence / AssemblyConstraints,
IADOccurrence.WorldTransform, IADAssemblyConstraint.ConstraintType /
Name, IADDesignSession.GlobalParameters (where supported).
"""
from __future__ import annotations

import sys

from alibrex import IADOccurrence, connect, run_example, require_active_assembly
def walk(occ: IADOccurrence, depth: int = 0) -> None:
    indent = "  " * depth
    print(f"{indent}- {occ.Name}  (children={occ.Occurrences.Count}, "
          f"suppressed={occ.IsSuppressed})")
    for i in range(occ.Occurrences.Count):
        walk(occ.Occurrences.Item(i), depth + 1)


def _active_or_new_assembly(root):
    try:
        return require_active_assembly(root)
    except RuntimeError:
        return root.CreateEmptyAssembly("AssemblyInspect_Demo")


def main() -> None:
    root = connect()
    asm = _active_or_new_assembly(root)

    print(f"Assembly: {asm.Name}\n")
    print("Occurrence tree:")
    walk(asm.RootOccurrence)

    # AlibreX returns None for these collections when empty rather than an
    # empty collection — guard each access.
    def safe_count(coll):
        return coll.Count if coll is not None else 0

    constraints = asm.AssemblyConstraints
    print(f"\nConstraints ({safe_count(constraints)}):")
    if constraints is not None:
        for i in range(constraints.Count):
            c = constraints.Item(i)
            try:
                ctype = c.ConstraintType
            except Exception:
                ctype = "?"
            print(f"  [{i}] {c.Name!r}  type={ctype}  suppressed={c.IsSuppressed}")

    # Inter-design relations and exploded views are also useful indicators.
    try:
        idr = asm.HasInterDesignRelations()
    except Exception as exc:  # noqa: BLE001
        idr = f"<unavailable: {type(exc).__name__}>"
    print(f"\nHasInterDesignRelations(): {idr}")
    print(f"Exploded views: {safe_count(asm.ExplodedViews)}")
    print(f"Assembly features: {safe_count(asm.Features)}")


if __name__ == "__main__":
    sys.exit(run_example(main))
