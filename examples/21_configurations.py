"""Example 21 — list and add part configurations (design variants).

Exercises `IADPartSession.Configurations` and `AddConfiguration`. Each
configuration captures a parameter snapshot; the example reads the
existing set and appends a new one named with a timestamp.
"""
from __future__ import annotations

import sys
import time

from alibrex import connect, run_example, require_active_part
def main() -> None:
    root = connect()
    part = require_active_part(root)
    configs = part.Configurations

    print(f"Part '{part.Name}' has {configs.Count} configuration(s):")
    for i in range(configs.Count):
        c = configs.Item(i)
        print(f"  [{i}] {c.Name}")

    new_name = "auto_" + time.strftime("%Y%m%d_%H%M%S")
    print(f"\nAdding configuration {new_name!r} (locked=False)...")
    cfg = configs.AddConfiguration(new_name, False)
    print(f"Created '{cfg.Name}'. Configurations count is now {configs.Count}.")


if __name__ == "__main__":
    sys.exit(run_example(main))
