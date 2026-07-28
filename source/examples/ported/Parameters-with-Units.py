"""Port of AlibreScript ``Parameters-with-Units.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/parameters-with-units

AlibreScript has a notion of *script units* (``Units.Current``) and lets
you pass an explicit ``ParameterUnits`` per call; AlibreX has no script
unit state: parameter values always read in the parameter's own
``ADUnits``. This port creates the same four parameters and prints their
values with units annotated.
"""
from __future__ import annotations

import sys
from alibrex import ADParameterType, ADUnits, connect, run_example
def show(p) -> None:
    print(f"  {p.Name:10s}  type={p.ParameterType!s:20s}  "
          f"value={p.Value:10.4f}  units={p.Units}")

def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Foo", False)
    params = part.Parameters

    length   = params.NewParameter("Length",   ADParameterType.AD_DISTANCE)
    rotation = params.NewParameter("Rotation", ADParameterType.AD_ANGLE)
    width    = params.NewParameter("Width",    ADParameterType.AD_DISTANCE)
    width2   = params.NewParameter("Width2",   ADParameterType.AD_DISTANCE)
    count    = params.NewParameter("Count",    ADParameterType.AD_COUNT)

    params.OpenParameterTransaction()
    try:
        length.Value = 12.34
        rotation.Units = ADUnits.AD_DEGREES
        rotation.Value = 34.2
        width.Units = ADUnits.AD_CENTIMETERS
        width.Value = 7.32
        width2.Units = ADUnits.AD_INCHES
        width2.Value = 1.0
        count.Units = ADUnits.AD_UNITLESS
        count.Value = 45
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise

    print("Parameters:")
    for p in (length, rotation, width, width2, count):
        show(p)

if __name__ == "__main__":
    sys.exit(run_example(main))
