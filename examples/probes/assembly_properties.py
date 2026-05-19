"""Probe the active assembly's occurrence tree + constraint list."""
from __future__ import annotations

import sys

from alibrex import connect, require_active_assembly, run_example, probe_collection, probe_object


def walk_occurrences(occ, depth: int = 0) -> None:
    probe_object(occ, f"{'  ' * depth}Occurrence: {occ.Name}")
    for i in range(occ.Occurrences.Count):
        walk_occurrences(occ.Occurrences.Item(i), depth + 1)


def main() -> None:
    root = connect()
    asm = require_active_assembly(root)

    probe_object(asm, "active assembly")
    probe_object(asm.RootOccurrence, "RootOccurrence")
    print(f"\nTotal top-level occurrences: {asm.RootOccurrence.Occurrences.Count}")

    walk_occurrences(asm.RootOccurrence)

    probe_collection(asm.AssemblyConstraints, "AssemblyConstraints", limit=10)
    probe_collection(asm.ExplodedViews,       "ExplodedViews",       limit=5)
    probe_collection(asm.Features,            "AssemblyFeatures",    limit=5)


if __name__ == "__main__":
    sys.exit(run_example(main))
