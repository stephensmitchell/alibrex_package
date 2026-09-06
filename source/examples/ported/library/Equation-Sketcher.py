"""Port of AlibreScript ``Mathematical/Equation Sketcher.py``.

Samples a user-supplied expression ``y = f(x)`` at *N* points and lays
the result down as a B-spline on a chosen plane of the *active* part.

Differences:

- ``WindowsInputTypes.Plane`` (interactive plane pick) becomes an integer
  index into ``part.DesignPlanes``.
- The original ``Sk.AddBspline`` (variadic 2D points) becomes
  ``AddBsplineByInterpolation`` with a flat ``[x0,y0,x1,y1,...]`` array.
- Needs ``pip install sympy``.
"""
from __future__ import annotations

import sys
from alibrex import connect, run_example, require_active_part
from alibrex.dialogs import InputType, error_dialog, options_dialog
from alibrex import float_array

def main() -> None:
    values = options_dialog(
        "Equation Sketcher",
        [
            ["Start point X",      InputType.Real,    0.0],
            ["Start point Y",      InputType.Real,    0.0],
            ["Equation y =",       InputType.String,  "0.1*x**2"],
            ["Plane index",        InputType.Integer, 0],
            ["X range start",      InputType.Real,    0.0],
            ["X range end",        InputType.Real,    10.0],
            ["Number of points",   InputType.Integer, 10],
            ["Swap X and Y",       InputType.Boolean, False],
        ],
        width=360,
    )
    if values is None:
        sys.exit("User cancelled")
    node_x, node_y, equation, plane_idx, start_x, end_x, n_points, swap_xy = values

    if not equation:
        error_dialog("No equation entered", "Equation Sketcher")
        sys.exit()
    if start_x > end_x:
        error_dialog("Start X > end X", "Equation Sketcher")
        sys.exit()
    if n_points < 2:
        error_dialog("Need at least 2 points", "Equation Sketcher")
        sys.exit()

    root = connect()
    part = require_active_part(root)
    plane = part.DesignPlanes.Item(plane_idx)
    sketch = part.Sketches.AddSketch(None, plane, "Equation Sketch")

    print("Loading sympy...")
    from sympy import Symbol, sympify  # type: ignore[import-not-found]

    x = Symbol("x")
    expr = sympify(equation)
    step_x = (end_x - start_x) / n_points

    flat: list[float] = []
    val_x = start_x
    for _ in range(n_points):
        val_y = float(expr.subs(x, val_x))
        if swap_xy:
            px, py = val_y, val_x
        else:
            px, py = val_x, val_y
        flat.extend([px + node_x, py + node_y])
        val_x += step_x

    print("Generating sketch...")
    sketch.Figures.AddBsplineByInterpolation(float_array(flat))

if __name__ == "__main__":
    sys.exit(run_example(main))
