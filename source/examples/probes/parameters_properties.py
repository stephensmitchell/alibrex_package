"""Probe every parameter on the active part.

Each ``IADParameter`` exposes ``Name``, ``Value``, ``Units``,
``ParameterType``, ``Equation``, ``ExternallyDriven``, ``comment``,
``SourceDocumentID``, ``SourceItemID``, ``IsMissingGlobal``, and
``IsConflictingGlobal``.
"""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_object

def main() -> None:
    root = connect()
    part = require_active_part(root)
    params = part.Parameters

    print(f"Total parameters: {params.Count}")
    for i in range(params.Count):
        try:
            p = params.Item(i)
        except Exception as exc:  # noqa: BLE001
            print(f"[{i}] <Item failed: {exc}>")
            continue
        probe_object(p, f"Parameter[{i}]")

if __name__ == "__main__":
    sys.exit(run_example(main))
