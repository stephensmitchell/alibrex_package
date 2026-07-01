"""Port of "SimpleEE (Simple Equation Editor) 3" AlibreScript example.

A dialog that lets the user re-bind every parameter on the active part
to a new equation or numeric value, then regenerates the model. Each
text input shows either the parameter's current equation or its numeric
value, and changes are pushed live as the user edits.

Differences from the original:
  * AlibreScript's ``Windows().UtilityDialog(...)`` is replaced by
    ``alibrex.dialogs.utility_dialog`` (tkinter-backed).
  * AlibreScript's ``WindowsInputTypes.String`` becomes
    ``alibrex.dialogs.InputType.String``.
  * tk offers no equivalent of the original's "refresh other rows"
    trick for pushing driven values back into the dialog, so the
    dialog updates only after the user clicks the action button.
"""
from __future__ import annotations

import sys

from alibrex import CurrentPart, run_example
from alibrex.dialogs import InputType, error_dialog, utility_dialog


def _param_repr(param) -> str:
    eq = (param.Equation or "").strip()
    return eq if eq else f"{param.Value}"


def main() -> int:
    try:
        part = CurrentPart()
    except RuntimeError:
        print("No active part. Open a part with parameters first.")
        return 1

    params = [part.Parameters.Item(i) for i in range(part.Parameters.Count)]
    if not params:
        print(f"Part '{part.Name}' has no parameters.")
        return 0

    options = [
        [p.Name, InputType.String, _param_repr(p)]
        for p in params
    ]

    def apply_to_param(p, text: str) -> bool:
        text = text.strip()
        try:
            p.Equation = text
        except Exception:
            try:
                p.Equation = ""
                p.Value = float(text)
            except Exception:
                error_dialog(f"Invalid expression or number: {text!r}",
                             title="Parameter Update Error")
                return False
        return True

    def on_change(idx: int, new_value) -> None:
        if not apply_to_param(params[idx], str(new_value)):
            return
        try:
            part.RegenerateAll()
        except Exception as exc:
            print(f"Regenerate failed: {type(exc).__name__}: {exc}")

    def on_apply(values) -> None:
        for p, v in zip(params, values):
            apply_to_param(p, str(v))
        try:
            part.RegenerateAll()
            print(f"Regenerated '{part.Name}'.")
        except Exception as exc:
            print(f"Regenerate failed: {type(exc).__name__}: {exc}")

    print(f"Editing {len(params)} parameter(s) on '{part.Name}'.")
    utility_dialog(
        title="SimpleEE",
        button_label="Regenerate",
        on_select=on_apply,
        on_change=on_change,
        options=options,
        width=500,
    )
    return 0


if __name__ == "__main__":
    sys.exit(run_example(main))
