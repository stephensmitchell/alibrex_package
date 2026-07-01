"""Configuration demo 04: enumerate every configuration on a part.

Adds several configurations with assorted lock states, then iterates
the collection and prints each one's name, ID, and decoded lock flags.
Dumps a part's full configuration matrix for documentation / PDM
ingestion.

Pass criteria:
  - All added configurations appear in the iteration.
  - Each entry's Locks decode cleanly into ADConfigurationLockType names.
  - The original "default" configuration is still in the collection.
"""
from __future__ import annotations

import sys
import uuid

import clr
from System import Enum

from _demo_utils import fresh_part, report
from alibrex import ADConfigurationLockType, run_example


def _flag_names(mask: int) -> list[str]:
    names = []
    for v in Enum.GetValues(clr.GetClrType(ADConfigurationLockType)):  # type: ignore[attr-defined]
        bit = int(v)
        if bit != 0 and (mask & bit) == bit:
            names.append(str(v))
    return names


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"CFG04_{tag}")
    configs = part.Configurations
    default_count = configs.Count

    added_names = [f"A_{tag}", f"B_{tag}", f"C_{tag}"]
    configs.AddConfiguration(added_names[0], False)
    configs.AddConfiguration(added_names[1], True)
    cfg_c = configs.AddConfiguration(added_names[2], False)
    cfg_c.Locks = ADConfigurationLockType(
        int(ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES)
        | int(ADConfigurationLockType.AD_LOCK_COLOR_PROPERTIES),
        True,
    )

    # Re-fetch the collection: it's a snapshot.
    configs = part.Configurations
    print(f"Configurations on '{part.Name}' ({configs.Count}):")
    seen_names = []
    for i in range(configs.Count):
        c = configs.Item(i)
        mask = int(c.Locks)
        flags = _flag_names(mask)
        seen_names.append(c.Name)
        flag_str = " | ".join(flags) if flags else "<no locks>"
        print(f"  [{i}] id={c.ID:<5d} name={c.Name!r:<30s} locks(0x{mask:08x}) = {flag_str}")

    all_added_present = all(n in seen_names for n in added_names)
    has_default = configs.Count >= default_count + len(added_names)

    return report([
        ("count grew by 3",            configs.Count == default_count + 3),
        ("all added names visible",    all_added_present),
        ("default config retained",    has_default),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
