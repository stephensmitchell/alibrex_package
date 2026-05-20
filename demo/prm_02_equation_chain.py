"""Parameter demo 02 - equation chain A -> B -> C.

Creates three free-standing parameters where each is driven by the
previous via an equation. Changing the head of the chain should
propagate through both equations.

  A: numeric value (set directly)
  B: equation = A * 2
  C: equation = B + 1

Pass criteria:
  - After A=3.0  -  B=6.0, C=7.0.
  - After A=10.0 -  B=20.0, C=21.0.
  - Equations on B and C are preserved across the value change.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADParameterType, run_example


def _find(part, name: str):
    params = part.Parameters
    for i in range(params.Count):
        p = params.Item(i)
        if p.Name == name:
            return p
    raise KeyError(f"Parameter {name!r} not found on part {part.Name!r}")


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM02_{tag}")
    params = part.Parameters

    a = params.NewParameter("A", ADParameterType.AD_DISTANCE)
    b = params.NewParameter("B", ADParameterType.AD_DISTANCE)
    c = params.NewParameter("C", ADParameterType.AD_DISTANCE)

    # Set A=3, B=A*2, C=B+1 inside one transaction.
    params.OpenParameterTransaction()
    try:
        a.Value = 3.0
        b.Equation = "A * 2"
        c.Equation = "B + 1"
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()

    a3 = _find(part, "A").Value
    b3 = _find(part, "B").Value
    c3 = _find(part, "C").Value
    eq_b = _find(part, "B").Equation
    eq_c = _find(part, "C").Equation
    print(f"A=3 step  -> A={a3}  B={b3}  (eq={eq_b!r})  C={c3}  (eq={eq_c!r})")

    # Bump A to 10.
    params.OpenParameterTransaction()
    try:
        _find(part, "A").Value = 10.0
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()

    a10 = _find(part, "A").Value
    b10 = _find(part, "B").Value
    c10 = _find(part, "C").Value
    print(f"A=10 step -> A={a10}  B={b10}  C={c10}")

    return report([
        ("B = A*2 at A=3",   math.isclose(b3, 6.0, abs_tol=1e-3)),
        ("C = B+1 at A=3",   math.isclose(c3, 7.0, abs_tol=1e-3)),
        ("B follows A=10",   math.isclose(b10, 20.0, abs_tol=1e-3)),
        ("C follows A=10",   math.isclose(c10, 21.0, abs_tol=1e-3)),
        ("eq on B preserved",  _find(part, "B").Equation == "A * 2"),
        ("eq on C preserved",  _find(part, "C").Equation == "B + 1"),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
