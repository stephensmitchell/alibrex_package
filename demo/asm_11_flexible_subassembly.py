"""Assembly demo 11: toggle a sub-assembly's IsFlexible flag.

By default, a sub-assembly occurrence in a parent assembly behaves as
a rigid block: its internal constraints are pre-solved and the parent's
constraints can only move the whole sub-assembly. Setting
``IADOccurrence.IsFlexible = True`` lets the parent's solver also reach
into the sub-assembly's joints, useful for kinematic linkages.

Opens the muffler and toggles the IsFlexible flag on a sub-assembly
occurrence (``baffle plate choke tube assembly<1>``), verifying it
round-trips. The muffler is closed without saving.

Pass criteria:
  - Initial IsFlexible reads False.
  - After setting True, reads True.
  - After setting False, reads False.
"""
from __future__ import annotations

import sys

from _demo_utils import find_occurrence_by_name, open_muffler, report
from alibrex import run_example


def main() -> int:
    asm = open_muffler()
    target = find_occurrence_by_name(asm.RootOccurrence, "baffle plate choke tube assembly")
    if target is None:
        print("Couldn't find 'baffle plate choke tube assembly' in the muffler.")
        return 1

    initial = bool(target.IsFlexible)
    print(f"Found {target.Name!r}, initial IsFlexible={initial}")

    target.IsFlexible = True
    after_set = bool(target.IsFlexible)
    print(f"After IsFlexible=True  -> reads {after_set}")

    target.IsFlexible = False
    after_restore = bool(target.IsFlexible)
    print(f"After IsFlexible=False -> reads {after_restore}")

    return report([
        ("initial rigid",       initial is False),
        ("set to flexible",     after_set is True),
        ("restored to rigid",   after_restore is False),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
