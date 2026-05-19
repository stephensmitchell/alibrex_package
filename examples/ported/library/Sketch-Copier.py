"""Port stub for AlibreScript ``Utilities/Sketch Copier.py``.

AlibreX has no ``Sketch.CopyFrom(other, ...)``. To replicate it you'd
walk the source sketch's ``Figures`` collection and emit equivalent
``AddLine`` / ``AddCircle`` / ``AddCircularArc*`` / ``AddEllipse*`` /
``AddBspline*`` calls on the destination sketch, transforming
coordinates as needed.

The script is short enough (~25 lines) that a custom port is the right
move when you know which figure types you'll encounter.

This file is intentionally a stub.
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "Sketch-Copier is a stub. AlibreX has no Sketch.CopyFrom; iterate "
        "Figures and re-emit each primitive manually on the destination sketch."
    )


if __name__ == "__main__":
    main()
