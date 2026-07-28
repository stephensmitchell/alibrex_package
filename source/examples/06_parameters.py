"""Example 06: read and write parametric values.

Parameters are how Alibre stores driving dimensions. Writing to a parameter
in a transaction triggers a regeneration that propagates downstream.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example, require_active_part
def main() -> None:
    root = connect()
    part = require_active_part(root)
    params = part.Parameters

    print(f"Part '{part.Name}' has {params.Count} parameter(s):\n")
    for i in range(params.Count):
        p = params.Item(i)
        eq = f"  =  {p.Equation}" if p.Equation else ""
        print(f"  {p.Name:24s} = {p.Value:10.4f} [{p.Units}]{eq}")

    target = None
    for i in range(params.Count):
        if params.Item(i).Name == "Depth":
            target = params.Item(i)
            break
    if target is None:
        print("\n(no 'Depth' parameter to drive - example finished)")
        return

    print(f"\nDoubling '{target.Name}' from {target.Value} to {target.Value * 2}")
    params.OpenParameterTransaction()
    try:
        target.Value = target.Value * 2.0
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()
    print("Regenerated.")

if __name__ == "__main__":
    sys.exit(run_example(main))
