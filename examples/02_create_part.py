"""Example 02 — create new part / assembly / drawing documents.

Demonstrates IADRoot.CreateEmptyPart / CreateEmptyAssembly / CreateEmptyDrawing.
The new sessions appear in Alibre as untitled in-memory documents.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example
def main() -> None:
    root = connect()

    part = root.CreateEmptyPart("AutoPart_Demo", False)
    print(f"Created part:     {part.Name}")

    sm_part = root.CreateEmptyPart("AutoSheetMetal_Demo", True)
    print(f"Created sheet:    {sm_part.Name}")

    assembly = root.CreateEmptyAssembly("AutoAssembly_Demo")
    print(f"Created assembly: {assembly.Name}")

    drawing = root.CreateEmptyDrawing("AutoDrawing_Demo")
    print(f"Created drawing:  {drawing.Name}")


if __name__ == "__main__":
    sys.exit(run_example(main))
