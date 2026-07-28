"""Parameter demo 04: Remove() a parameter and verify it's gone.

Creates three free parameters, removes the middle one via
``IADParameter.Remove()``, and re-counts. The remaining two should
still be findable by name; the removed one should be absent.

Pass criteria:
  - Count starts at 3 after the three NewParameter calls.
  - Count drops to 2 after Remove().
  - The removed name no longer appears in the collection.
  - The two kept names are still present.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADParameterType, run_example

def _names(part) -> set[str]:
    params = part.Parameters
    return {params.Item(i).Name for i in range(params.Count)}

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM04_{tag}")
    params = part.Parameters

    params.NewParameter("KeepA", ADParameterType.AD_DISTANCE)
    middle = params.NewParameter("RemoveMe", ADParameterType.AD_DISTANCE)
    params.NewParameter("KeepB", ADParameterType.AD_DISTANCE)

    before_count = part.Parameters.Count
    before_names = _names(part)
    print(f"Before remove: count={before_count}, names={sorted(before_names)}")

    middle.Remove()

    after_count = part.Parameters.Count
    after_names = _names(part)
    print(f"After remove : count={after_count}, names={sorted(after_names)}")

    return report([
        ("3 params before",   before_count == 3),
        ("2 params after",    after_count == 2),
        ("RemoveMe gone",     "RemoveMe" not in after_names),
        ("KeepA still here",  "KeepA" in after_names),
        ("KeepB still here",  "KeepB" in after_names),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
