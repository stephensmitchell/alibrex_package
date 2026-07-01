"""Port of AlibreScript ``Working-with-Configurations.py``.

Original: https://help.alibre.com/articles/#!alibre-help-v28/working-with-configurations

Adds, locks, and activates part configurations. The biggest API shape
difference: AlibreScript has ``Foo.Activate()`` / ``IsActive``, while
AlibreX activates by assigning to
``IADDesignSession.ActiveConfiguration`` and checks "is active" by
comparing IDs against the session's current active configuration.
"""
from __future__ import annotations

import sys

import clr
from System import Enum

from alibrex import ADConfigurationLockType, connect, run_example


def _lock_value(mask: int):
    """Construct an ADConfigurationLockType from an arbitrary int mask.

    Calling ``ADConfigurationLockType(mask)`` directly raises
    ``Invalid enumeration value`` if ``mask`` isn't a defined member.
    The pythonnet escape hatch is the second-arg-True overload, which
    skips the validation.
    """
    return ADConfigurationLockType(mask, True)
def is_active(session, cfg) -> bool:
    return session.ActiveConfiguration.ID == cfg.ID


def find(configs, name: str):
    for i in range(configs.Count):
        c = configs.Item(i)
        if c.Name == name:
            return c
    return None


def main() -> None:
    root = connect()
    part = root.CreateEmptyPart("Test", False)
    configs = part.Configurations

    foo = configs.AddConfiguration("Foo", False)
    # Unlock all = clear the bitmask
    foo.Locks = _lock_value(0)
    foo.Locks = ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES
    # Combine flags via a mask
    foo.Locks = _lock_value(
        int(ADConfigurationLockType.AD_SUPPRESS_NEW_FEATURES)
        | int(ADConfigurationLockType.AD_LOCK_COLOR_PROPERTIES)
    )
    part.ActiveConfiguration = foo

    bar = configs.AddConfiguration("Bar", False)
    part.ActiveConfiguration = bar

    # The default configuration's name varies by locale; find it
    # (the one we did not add). Then apply the "lock everything"
    # equivalent by OR-ing all known bits. CLR enums don't iterate the
    # same way Python enums do; use Enum.GetValues.
    all_bits = 0
    for v in Enum.GetValues(clr.GetClrType(ADConfigurationLockType)):  # type: ignore[attr-defined]
        all_bits |= int(v)
    default = None
    for i in range(configs.Count):
        c = configs.Item(i)
        if c.ID not in (foo.ID, bar.ID):
            default = c
            break
    if default is not None:
        default.Locks = _lock_value(all_bits)

    # Re-fetch the collection: it's a snapshot, additions don't show
    # up in the original handle. Also guard the Item(1) lookup in case
    # AlibreX collapsed configurations on this build.
    configs = part.Configurations
    active = part.ActiveConfiguration
    print(f"Current active configuration is: {active.Name}")
    print(f"Total number of configurations: {configs.Count}")
    if configs.Count >= 2:
        second = configs.Item(1)
        print(f"Second configuration is: {second.Name}")
        print(f"Is second configuration active? {'yes' if is_active(part, second) else 'no'}")
    else:
        print("(only one configuration in the collection - skipping Item(1) probe)")
    print(f"Is configuration 'Bar' active? {'yes' if is_active(part, bar) else 'no'}")


if __name__ == "__main__":
    sys.exit(run_example(main))
