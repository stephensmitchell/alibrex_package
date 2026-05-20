"""Example 25 - use part configurations with lock flags.

Creates a part, adds two configurations (one locked, one unlocked), reads
each `Locks` value as a bitmask of `ADConfigurationLockType`, and flips
the lock state of one of them. Works against the active part.

Covers: IADConfigurations.AddConfiguration, IADConfiguration.Name / ID /
Locks, ADConfigurationLockType (flags).
"""
from __future__ import annotations

import sys

import clr
from System import Enum

from alibrex import ADConfigurationLockType, connect, run_example, require_active_part

# CLR enums don't iterate like Python enums and don't expose `.name`; use
# Enum.GetValues + str() (which dispatches to Enum.ToString()).
_LOCK_FLAGS = {
    int(v): str(v)
    for v in Enum.GetValues(clr.GetClrType(ADConfigurationLockType))  # type: ignore[attr-defined]
}


def describe_locks(mask: int) -> str:
    if mask == 0:
        return "<no locks>"
    names = [name for bit, name in _LOCK_FLAGS.items() if bit and (mask & bit) == bit]
    return " | ".join(names) if names else f"<unknown bits 0x{mask:x}>"


def _active_or_new_part(root):
    try:
        return require_active_part(root)
    except RuntimeError:
        return root.CreateEmptyPart("Configurations_Demo", False)


def main() -> None:
    root = connect()
    part = _active_or_new_part(root)
    configs = part.Configurations

    print(f"Part '{part.Name}': {configs.Count} configuration(s).")
    for i in range(configs.Count):
        c = configs.Item(i)
        print(f"  [{i}] id={c.ID}  name={c.Name!r}  locks={describe_locks(int(c.Locks))}")

    # Add a locked and an unlocked configuration
    locked = configs.AddConfiguration("auto_locked", True)
    open_  = configs.AddConfiguration("auto_open",   False)

    print(f"\nAdded:")
    print(f"  {locked.Name!r}: locks={describe_locks(int(locked.Locks))}")
    print(f"  {open_.Name!r}:  locks={describe_locks(int(open_.Locks))}")

    # Flip lock state on the unlocked one to add 'suppress new features'
    new_mask = int(open_.Locks) | int(ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES)
    open_.Locks = ADConfigurationLockType(new_mask)
    print(f"\nAfter setting AD_SUPPRESS_NEW_FEATURES on {open_.Name!r}: "
          f"{describe_locks(int(open_.Locks))}")

    print(f"\nFinal count: {configs.Count}")


if __name__ == "__main__":
    sys.exit(run_example(main))
