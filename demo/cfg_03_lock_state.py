"""Configuration demo 03: set / read lock-state flags on a configuration.

``IADConfiguration.Locks`` is a flag enum (``ADConfigurationLockType``)
controlling what kinds of edits Alibre allows in a given configuration.
Building an arbitrary mask requires the pythonnet unchecked-enum
constructor (``ADConfigurationLockType(mask, True)``). Bare
``ADConfigurationLockType(mask)`` raises if ``mask`` isn't a defined
member.

Pass criteria:
  - Empty mask (0) round-trips as no locks.
  - A single-bit assignment reads back identically.
  - An OR'd multi-bit mask reads back with the same bits.
"""
from __future__ import annotations

import sys
import uuid

import clr
from System import Enum

from _demo_utils import fresh_part, report
from alibrex import ADConfigurationLockType, run_example


def _lock_value(mask: int):
    return ADConfigurationLockType(mask, True)


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"CFG03_{tag}")
    cfg = part.Configurations.AddConfiguration(f"Locked_{tag}", False)

    # Clear all locks.
    cfg.Locks = _lock_value(0)
    cleared = int(cfg.Locks)
    print(f"After clear:   Locks = 0x{cleared:08x}")

    # Set a single flag.
    cfg.Locks = ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES
    one_bit = int(cfg.Locks)
    print(f"After 1 flag : Locks = 0x{one_bit:08x}")

    # OR two flags via the unchecked constructor.
    combined_mask = (
        int(ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES)
        | int(ADConfigurationLockType.AD_LOCK_COLOR_PROPERTIES)
    )
    cfg.Locks = _lock_value(combined_mask)
    two_bits = int(cfg.Locks)
    print(f"After 2 flags: Locks = 0x{two_bits:08x}  (expected 0x{combined_mask:08x})")

    # Enumerate the full mask members for diagnostic value.
    all_members = list(Enum.GetValues(clr.GetClrType(ADConfigurationLockType)))  # type: ignore[attr-defined]
    print(f"Total flag members: {len(all_members)}")

    return report([
        ("cleared mask is 0",         cleared == 0),
        ("single bit round-trip",     one_bit == int(ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES)),
        ("OR mask round-trip",        two_bits == combined_mask),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
