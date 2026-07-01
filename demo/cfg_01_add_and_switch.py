"""Configuration demo 01: add configurations and switch the active one.

Adds two custom configurations (one locked, one unlocked) to a fresh
part, switches the active configuration to each, and verifies the
switch took effect by comparing IDs.

Pass criteria:
  - Initial configurations.Count is 1 (the default config Alibre creates).
  - After two AddConfiguration calls, Count is 3.
  - Switching ``ActiveConfiguration`` to ``Foo`` makes ActiveConfiguration.ID == Foo.ID.
  - Switching to ``Bar`` makes ActiveConfiguration.ID == Bar.ID.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import run_example


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"CFG01_{tag}")
    configs = part.Configurations

    initial = configs.Count
    print(f"Initial configurations: {initial}")
    foo = configs.AddConfiguration("Foo", False)  # unlocked
    bar = configs.AddConfiguration("Bar", True)   # locked
    after_add = part.Configurations.Count
    print(f"After Add: count={after_add} (added Foo, Bar)")

    part.ActiveConfiguration = foo
    active_foo_id = part.ActiveConfiguration.ID
    active_foo_name = part.ActiveConfiguration.Name
    print(f"Set ActiveConfiguration = Foo  -> active={active_foo_name!r} (id={active_foo_id})")

    part.ActiveConfiguration = bar
    active_bar_id = part.ActiveConfiguration.ID
    active_bar_name = part.ActiveConfiguration.Name
    print(f"Set ActiveConfiguration = Bar  -> active={active_bar_name!r} (id={active_bar_id})")

    return report([
        ("started with 1 config",      initial == 1),
        ("3 configs after add",        after_add == 3),
        ("switched to Foo",            active_foo_id == foo.ID),
        ("switched to Bar",            active_bar_id == bar.ID),
        ("two switches are distinct",  active_foo_id != active_bar_id),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
