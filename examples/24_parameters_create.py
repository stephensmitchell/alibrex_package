"""Example 24 - create and drive new parameters.

Adds a fresh part, sketches a rectangle and extrudes it while *naming*
the depth and width parameters at creation, then:

- Creates a free-standing parameter (`ADParameterType.AD_DISTANCE`).
- Reads all parameters and prints (name, type, value, units, equation).
- Inside a parameter transaction, sets an equation that links the
  extrusion depth to the new parameter, and changes its value.
- Regenerates and prints the resulting feature size.

Covers: IADParameters.NewParameter, OpenParameterTransaction,
CloseParameterTransaction, IADParameter.Equation/Value/Units.
"""
from __future__ import annotations

import sys

from alibrex import (
    ADDirectionType,
    ADParameterType,
    ADPartFeatureEndCondition,
    IADPartSession,
)
from alibrex import connect, run_example
def main() -> None:
    root = connect()
    part: IADPartSession = root.CreateEmptyPart("Param_Demo", False)

    xy = part.DesignPlanes.Item(0)
    sketch = part.Sketches.AddSketch(None, xy, "Base")
    sketch.BeginChange()
    try:
        sketch.Figures.AddRectangle(0.0, 0.0, 4.0, 2.0)
    finally:
        sketch.EndChange()

    part.Features.AddExtrudedBoss(
        sketch, 1.5, ADPartFeatureEndCondition.AD_TO_DEPTH,
        None, None, 0.0,
        ADDirectionType.AD_ALONG_NORMAL, None, None, False,
        None, False,
        "Block",
        "Depth", "",   # name the depth parameter "Depth"
    )

    # Free-standing parameter. Note: part.Parameters returns a *snapshot*
    # collection - call part.Parameters again to see additions.
    user_param = part.Parameters.NewParameter("Stretch", ADParameterType.AD_DISTANCE)
    print(f"\nCreated {user_param.Name!r} (type={user_param.ParameterType}, "
          f"units={user_param.Units}).")

    params = part.Parameters  # fresh snapshot, now includes Stretch
    print(f"\nAll parameters ({params.Count}):")
    for i in range(params.Count):
        p = params.Item(i)
        eq = f" = {p.Equation}" if p.Equation else ""
        print(f"  {p.Name:24s}  type={p.ParameterType!s:20s}  "
              f"value={p.Value:8.3f}  units={p.Units}{eq}")

    # Link Depth -> Stretch via an equation, inside a transaction
    depth = None
    stretch = None
    for i in range(params.Count):
        p = params.Item(i)
        if p.Name == "Depth":
            depth = p
        elif p.Name == "Stretch":
            stretch = p
    if depth is None or stretch is None:
        raise RuntimeError("Expected 'Depth' and 'Stretch' parameters.")

    print("\nDriving Depth = Stretch * 2 inside a transaction...")
    params.OpenParameterTransaction()
    try:
        stretch.Value = 1.0
        depth.Equation = "Stretch * 2"
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise

    part.RegenerateAll()
    print(f"After regen: Depth = {depth.Value:.3f} cm (equation: {depth.Equation!r})")

    # Bump Stretch and watch Depth follow
    params.OpenParameterTransaction()
    try:
        stretch.Value = 2.5
        params.CloseParameterTransaction()
    except Exception:
        params.CancelParameterTransaction()
        raise
    part.RegenerateAll()
    print(f"Stretch={stretch.Value:.3f}  ->  Depth={depth.Value:.3f} cm")


if __name__ == "__main__":
    sys.exit(run_example(main))
