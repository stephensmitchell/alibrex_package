"""Example 09 - subscribe to Alibre's session lifecycle events.

EventManager exposes session-open/close/change events. PythonNet wires
event handlers via `+=` just like in C#.
"""
from __future__ import annotations

import sys
import time

from alibrex import EventManager, connect, run_example
def main() -> None:
    root = connect()
    em: EventManager = root.EventManager  # type: ignore[assignment]

    def on_open(session) -> None:
        print(f"  [event] session opened: {session.Name}")

    def on_close(session) -> None:
        print(f"  [event] session closed: {session.Name}")

    def on_change(session) -> None:
        print(f"  [event] session changed: {session.Name}")

    em.OnSessionOpen += on_open       # type: ignore[operator]
    em.OnSessionClose += on_close     # type: ignore[operator]
    em.OnSessionChange += on_change   # type: ignore[operator]

    print("Listening for 30 seconds - open/close/edit a document in Alibre…")
    try:
        for _ in range(30):
            time.sleep(1.0)
    finally:
        em.OnSessionOpen -= on_open       # type: ignore[operator]
        em.OnSessionClose -= on_close     # type: ignore[operator]
        em.OnSessionChange -= on_change   # type: ignore[operator]
        print("Unsubscribed.")


if __name__ == "__main__":
    sys.exit(run_example(main))
