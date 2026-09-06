"""CRUD demo 15: toggle an occurrence's suppression state, verify, restore.

Finds the ``outlet orifice plate 2a<1>`` leaf occurrence on the muffler
assembly, toggles ``IsSuppressed`` on / off, and reads the value back
each time to confirm the assignment landed. Leaves the assembly in its
original state.

Pass criteria:
  - Initial IsSuppressed reads False.
  - After setting True, reads True.
  - After setting False again, reads False.
"""
from __future__ import annotations

import sys

from _demo_utils import find_occurrence_by_name, open_muffler, report
from alibrex import run_example

def main() -> int:
    asm = open_muffler()
    target = find_occurrence_by_name(asm.RootOccurrence, "outlet orifice plate 2a")
    if target is None:
        print("Couldn't find 'outlet orifice plate 2a' in the muffler.")
        return 1

    initial = bool(target.IsSuppressed)
    print(f"Found {target.Name!r}, initial IsSuppressed={initial}")

    target.IsSuppressed = True
    after_set = bool(target.IsSuppressed)
    print(f"After setting True : IsSuppressed={after_set}")

    target.IsSuppressed = False
    after_restore = bool(target.IsSuppressed)
    print(f"After setting False: IsSuppressed={after_restore}")

    return report([
        ("initial unsuppressed",   initial is False),
        ("set to True landed",     after_set is True),
        ("restored to False",      after_restore is False),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
