"""Probe the IADRoot itself + its session list and material libraries.

Works regardless of which document type is active. Needs only a
running Alibre instance.
"""
from __future__ import annotations

import sys

from alibrex import connect, run_example, probe_collection, probe_object


def main() -> None:
    root = connect()

    probe_object(root, "IADRoot")
    probe_collection(root.Sessions, "Sessions", limit=10)
    try:
        probe_collection(root.MaterialLibraries, "MaterialLibraries", limit=3)
    except Exception as exc:  # noqa: BLE001
        print(f"MaterialLibraries probe failed: {exc}")


if __name__ == "__main__":
    sys.exit(run_example(main))
