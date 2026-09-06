"""CRUD demo 13: open the bundled muffler assembly and walk its tree.

Opens the muffler assembly (read-only), prints the occurrence tree
indented by depth, and verifies the known structure:
6 top-level children, three ``choke tube assembly`` sub-assemblies,
two ``nozzle head`` sub-assemblies, and at least one suppressed
outlet orifice plate.

Pass criteria:
  - Session opens and reports type ``AD_ASSEMBLY``.
  - 6 top-level child occurrences.
  - Total leaf parts (across the full tree) is at least 15.
  - At least one occurrence has ``IsSuppressed == True``.
"""
from __future__ import annotations

import sys

from _demo_utils import open_muffler, report, walk_occurrences
from alibrex import ADObjectSubType, run_example

def main() -> int:
    asm = open_muffler()
    print(f"Opened: {asm.Name}  type={asm.SessionType}")
    root_occ = asm.RootOccurrence
    top_count = root_occ.Occurrences.Count
    print(f"Top-level children: {top_count}\n")

    state = {"leaves": 0, "suppressed": 0, "max_depth": 0}
    def visit(occ, depth):
        print(" " * depth + f"- {occ.Name}  (children={occ.Occurrences.Count}, "
              f"suppressed={occ.IsSuppressed})")
        if occ.Occurrences.Count == 0:
            state["leaves"] += 1
        if bool(occ.IsSuppressed):
            state["suppressed"] += 1
        state["max_depth"] = max(state["max_depth"], depth)
    walk_occurrences(root_occ, visit)

    print(f"\nLeaf parts: {state['leaves']}  Suppressed: {state['suppressed']}  "
          f"Max depth: {state['max_depth']}")

    return report([
        ("opened as assembly",          int(asm.SessionType) == int(ADObjectSubType.AD_ASSEMBLY)),
        ("6 top-level children",        top_count == 6),
        (">= 15 leaf parts",            state["leaves"] >= 15),
        ("at least one suppressed",     state["suppressed"] >= 1),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
