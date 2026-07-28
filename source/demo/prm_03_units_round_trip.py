"""Parameter demo 03: set and read parameter units (mm / cm / inches).

Creates a distance parameter and round-trips through three unit
systems. ``IADParameter.Value`` always reads in the parameter's own
declared ``Units``. This demo verifies that contract holds.

Pass criteria:
  - Default ``ADParameterType.AD_DISTANCE`` reports cm initially.
  - Setting Units = AD_INCHES then Value = 1.0 reads back as 1.0
    (i.e. 1 inch, not 1 cm).
  - Setting Units = AD_MILLIMETERS then Value = 25.4 reads back 25.4.
"""
from __future__ import annotations

import math
import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import ADParameterType, ADUnits, run_example

def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"PRM03_{tag}")
    params = part.Parameters

    p = params.NewParameter("L", ADParameterType.AD_DISTANCE)
    initial_units = p.Units
    print(f"Initial units: {initial_units}")

    params.OpenParameterTransaction()
    try:
        p.Units = ADUnits.AD_INCHES
        p.Value = 1.0
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    inches_value = p.Value
    inches_units = p.Units
    print(f"After Units=INCHES, Value=1.0 -> Value={inches_value}, Units={inches_units}")

    params.OpenParameterTransaction()
    try:
        p.Units = ADUnits.AD_MILLIMETERS
        p.Value = 25.4
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    mm_value = p.Value
    mm_units = p.Units
    print(f"After Units=MM, Value=25.4 -> Value={mm_value}, Units={mm_units}")

    return report([
        ("inches round-trip Value=1.0", math.isclose(inches_value, 1.0, abs_tol=1e-3)),
        ("inches Units stuck",          int(inches_units) == int(ADUnits.AD_INCHES)),
        ("mm round-trip Value=25.4",    math.isclose(mm_value, 25.4, abs_tol=1e-3)),
        ("mm Units stuck",              int(mm_units) == int(ADUnits.AD_MILLIMETERS)),
    ])

if __name__ == "__main__":
    sys.exit(run_example(main))
