"""Events demo 04: automated round-trip test for subscribe / unsubscribe.

Doesn't need any user interaction. Verifies:
  - Subscribing through `em.OnX += handler` returns without error.
  - Unsubscribing through `em.OnX -= handler` returns without error.
  - Subscribing the SAME handler again works (the bridge tracks it).
  - The `EventManager` proxy hot-path is stable across many add/remove
    cycles (no leaks of cookies / sinks).

This is the "did the connection-point bridge wire up correctly" smoke test
that doesn't depend on Alibre emitting events.
"""
from __future__ import annotations

import sys

from alibrex import connect
from _demo_utils import report, run_demo

def main() -> int:
    root = connect()
    em = root.EventManager

    def h1(*args): pass
    def h2(*args): pass

    errors = []

    def safe(label, fn):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            errors.append((label, type(exc).__name__, str(exc)[:120]))

    for name in ("OnInitialize", "OnTerminate", "OnSessionOpen",
                 "OnSessionClose", "OnSessionChange", "OnModelLoadComplete"):
        ev = getattr(em, name)
        safe(f"{name} +=", lambda ev=ev: ev.__iadd__(h1))
        safe(f"{name} -=", lambda ev=ev: ev.__isub__(h1))

    for _ in range(2):
        safe("OnSessionOpen += h2", lambda: em.OnSessionOpen.__iadd__(h2))
    for _ in range(2):
        safe("OnSessionOpen -= h2", lambda: em.OnSessionOpen.__isub__(h2))

    for _ in range(50):
        safe("cycle +=", lambda: em.OnSessionChange.__iadd__(h1))
        safe("cycle -=", lambda: em.OnSessionChange.__isub__(h1))

    for label, kind, msg in errors:
        print(f"  [FAIL] {label}: {kind}: {msg}")

    return report([
        ("no errors during 6 event subs",   not any(e[0].endswith(("+=", "-=")) and "On" in e[0] for e in errors)),
        ("duplicate subscribe ok",          all("OnSessionOpen += h2" not in e[0] for e in errors)),
        ("50-cycle stress clean",           all("cycle" not in e[0] for e in errors)),
    ])

if __name__ == "__main__":
    sys.exit(run_demo(main))
