"""Probe every configuration on the active part."""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_object


def main() -> None:
    root = connect()
    part = require_active_part(root)
    configs = part.Configurations

    print(f"Active configuration: {part.ActiveConfiguration.Name}")
    print(f"Total configurations: {configs.Count}")
    for i in range(configs.Count):
        cfg = configs.Item(i)
        probe_object(cfg, f"Configuration[{i}]")


if __name__ == "__main__":
    sys.exit(run_example(main))
