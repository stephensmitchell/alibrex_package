"""CRUD demo 16: run a CheckInterference on the muffler assembly.

Calls ``IADAssemblySession.CheckInterference(None, None)`` which returns
an interference collection (and a second item depending on the build).
Prints any interference pairs found and asserts the call itself
succeeded.

Pass criteria:
  - CheckInterference call returns without exception.
  - The returned collection has a sane ``Count`` (>= 0).
"""
from __future__ import annotations

import sys

from _demo_utils import open_muffler, report
from alibrex import run_example

def main() -> int:
    asm = open_muffler()
    print(f"Running interference check on '{asm.Name}'...")
    result = asm.CheckInterference(None, None)
    interferences = result[0] if isinstance(result, tuple) else result

    n = interferences.Count
    print(f"Found {n} interference(s).")
    for i in range(n):
        item = interferences.Item(i)
        try:
            print(f"  [{i}] {item.Part1.Name}  <->  {item.Part2.Name}   vol={item.InterferenceVolume:.4f}")
        except Exception:
            print(f"  [{i}] {item!r}")

    return report([
        ("interference call returned a result",  interferences is not None),
        ("count is non-negative",                n >= 0),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
