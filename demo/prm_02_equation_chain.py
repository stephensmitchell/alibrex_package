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


def _equation_matches(actual: str, expected: str) -> bool:
    return "".join(actual.split()) == "".join(expected.split())


def _set_chain(part, a_value: float, set_equations: bool = False) -> None:
    params = part.Parameters
    params.OpenParameterTransaction()
    try:
        _find(part, "A").Value = a_value
        if set_equations:
            _find(part, "B").Equation = "A * 2"
            _find(part, "C").Equation = "B + 1"
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM02_{tag}")
    params = part.Parameters

    params.NewParameter("A", ADParameterType.AD_DISTANCE)
    params.NewParameter("B", ADParameterType.AD_DISTANCE)
    params.NewParameter("C", ADParameterType.AD_DISTANCE)

    _set_chain(part, 3.0, set_equations=True)

    a3 = _find(part, "A").Value
    b3 = _find(part, "B").Value
    c3 = _find(part, "C").Value
    eq_b = _find(part, "B").Equation
    eq_c = _find(part, "C").Equation
    print(f"A=3 step  -> A={a3}  B={b3}  (eq={eq_b!r})  C={c3}  (eq={eq_c!r})")

    _set_chain(part, 10.0)

    a10 = _find(part, "A").Value
    b10 = _find(part, "B").Value
    c10 = _find(part, "C").Value
    print(f"A=10 step -> A={a10}  B={b10}  C={c10}")

    return report([
        ("B = A*2 at A=3",   math.isclose(b3, 6.0, abs_tol=1e-3)),
        ("C = B+1 at A=3",   math.isclose(c3, 7.0, abs_tol=1e-3)),
        ("B follows A=10",   math.isclose(b10, 20.0, abs_tol=1e-3)),
        ("C follows A=10",   math.isclose(c10, 21.0, abs_tol=1e-3)),
        ("eq on B preserved",  _equation_matches(_find(part, "B").Equation, "A * 2")),
        ("eq on C preserved",  _equation_matches(_find(part, "C").Equation, "B + 1")),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
