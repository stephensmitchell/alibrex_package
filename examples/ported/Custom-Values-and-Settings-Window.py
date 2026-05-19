"""Port of AlibreScript ``Custom-Values-and-Settings-Window.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/custom-values-and-settings-window

Shows a form with the four primitive ``WindowsInputTypes`` (String,
Real, Boolean, Integer). The AlibreScript version returns ``None`` if
the user cancels; ``options_dialog`` mirrors that behaviour.
"""
from __future__ import annotations

from alibrex.dialogs import InputType, options_dialog
def main() -> None:
    options = [
        ["Name of the item", InputType.String,  "Baz"],
        ["Scale",            InputType.Real,    1.234],
        ["Enabled",          InputType.Boolean, True],
        ["Count",            InputType.Integer, 123456],
    ]
    values = options_dialog("Test", options)
    print(values)


if __name__ == "__main__":
    main()
