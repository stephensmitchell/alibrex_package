"""Filename alias for the typo'd source script.

See ``Suppressing-Unsuppressing-and-Removing-Features.py`` for the port;
this file runs that one when executed directly.
"""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name(
        "Suppressing-Unsuppressing-and-Removing-Features.py"
    )
    runpy.run_path(str(target), run_name="__main__")
    sys.exit(0)
