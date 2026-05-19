"""Probe every feature in the active part's feature tree."""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_object


def main() -> None:
    root = connect()
    part = require_active_part(root)
    feats = part.Features

    print(f"Feature count: {part.FeatureCount}")
    print(f"Features collection Count: {feats.Count}")
    for i in range(feats.Count):
        try:
            f = feats.Item(i)
        except Exception as exc:  # noqa: BLE001
            print(f"[{i}] <Item failed: {exc}>")
            continue
        probe_object(f, f"Feature[{i}]")


if __name__ == "__main__":
    sys.exit(run_example(main))
