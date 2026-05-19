"""Port of AlibreScript ``Useful-Dialogs.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/useful-dialogs

Demonstrates the three message-box dialogs. AlibreScript exposes them as
methods on a ``Windows()`` instance; we use the equivalent helpers from
``_dialogs.py`` (which wraps tkinter).
"""
from __future__ import annotations

from alibrex.dialogs import error_dialog, info_dialog, question_dialog
def main() -> None:
    info_dialog("I am about to create a part", "My Script")
    error_dialog("Oops. That didn't go as planned", "My Script")
    answer = question_dialog("Shall I stop?", "My Script")
    print(answer)


if __name__ == "__main__":
    main()
