"""Port of AlibreScript ``Calculating-Length-of-Curves.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/calculating-length-of-curves

Pure-math example - no AlibreX interaction. The original imported
``sympy``; this port does the same. Run with::

    pip install sympy
    python Calculating-Length-of-Curves.py
"""
from __future__ import annotations

from sympy import Symbol, diff, integrate, sqrt  # type: ignore[import-not-found]


def main() -> None:
    x = Symbol("x")
    formula = 2 * x ** 2
    x_min = 5.0
    x_max = 10.0
    d = diff(formula, x)
    integral = integrate(sqrt(1 + d ** 2), (x, x_min, x_max))
    length = integral.evalf()
    print(f"Length of curve over x={x_min:.3f} to x={x_max:.3f} is {length:.3f} mm")


if __name__ == "__main__":
    main()
