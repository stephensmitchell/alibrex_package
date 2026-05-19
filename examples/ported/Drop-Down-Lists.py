"""Port of AlibreScript ``Drop-Down-Lists.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/drop-down-lists

Demonstrates a ``StringList`` (combobox) input with an ``on_change``
callback that fires while the dialog is open and an ``on_select``
callback that fires when the action button is clicked. As in the
original, the value handed to the callbacks is the *index* into the
choices list — look it up against ``DIAMETER_NAMES``.
"""
from __future__ import annotations

from alibrex.dialogs import InputType, utility_dialog
DIAMETER_NAMES = ["M6", "M8", "M10", "M12"]
DEFAULT_DIAMETER = "M6"


def on_change(index: int, value) -> None:
    if index == 0:
        print(f"Selection changed to: {DIAMETER_NAMES[value]}")


def on_select(values) -> None:
    size = DIAMETER_NAMES[values[0]]
    print(f"Applied: {size}")


def main() -> None:
    options = [
        ["Size", InputType.StringList, DIAMETER_NAMES, DEFAULT_DIAMETER],
    ]
    utility_dialog("Test", "Apply", on_select, on_change, options, width=400)


if __name__ == "__main__":
    main()
