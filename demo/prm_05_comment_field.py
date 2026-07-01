"""Parameter demo 05: round-trip the ``comment`` field on a parameter.

AlibreX exposes a free-form ``comment`` string on every parameter
(used by AlibreScript-style "favorites" + downstream PDM integrations
that tag parameters with semantic metadata). The property name is
*lowercase* ``comment``, not ``Comment``.

Pass criteria:
  - New parameter's comment is empty by default.
  - After assigning, the comment reads back what we set.
  - Setting back to empty restores the original.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADParameterType, run_example


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM05_{tag}")
    params = part.Parameters
    p = params.NewParameter("Tagged", ADParameterType.AD_DISTANCE)

    initial = p.comment
    print(f"Initial comment: {initial!r}")

    params.OpenParameterTransaction()
    try:
        p.comment = "favorite|exposed-to-pdm|category=structural"
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    set_value = p.comment
    print(f"After set      : {set_value!r}")

    params.OpenParameterTransaction()
    try:
        p.comment = ""
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    cleared = p.comment
    print(f"After clear    : {cleared!r}")

    return report([
        ("initial empty",       initial == ""),
        ("set round-trip",      set_value == "favorite|exposed-to-pdm|category=structural"),
        ("clear round-trip",    cleared == ""),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
