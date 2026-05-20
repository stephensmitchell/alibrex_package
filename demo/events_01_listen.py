"""Events demo 01 - subscribe to all Alibre lifecycle events and listen.

Pattern:
  - Subscribe via `em.OnX += handler` for each event.
  - Pump the windows message loop in a small idle loop so the COM
    apartment can dispatch incoming event callbacks.
  - Unsubscribe with `em.OnX -= handler` on exit.

How events fire in Alibre:
  - GUI-driven changes (the user opens/closes a document, modifies the
    model in the viewport, saves) fire events immediately.
  - Pure-API changes from the same Python script usually do NOT fire
    events - Alibre suppresses them on its automation path to avoid
    event storms while scripts are running.

Run this script, then in Alibre: open a part / make a change / close it.
You'll see the handler messages print here in real time.
"""
from __future__ import annotations

import sys
import time

import clr
clr.AddReference("System.Windows.Forms")  # type: ignore[attr-defined]
from System.Windows.Forms import Application  # type: ignore[import-not-found]

from alibrex import connect, run_example

LISTEN_SECONDS = 30


def main() -> int:
    root = connect()
    em = root.EventManager
    print(f"Subscribed to EventManager - listening {LISTEN_SECONDS}s.")
    print("Open a part / edit / close in Alibre to fire events.")

    counters = {"open": 0, "close": 0, "change": 0, "load": 0, "init": 0, "term": 0}

    def on_init():
        counters["init"] += 1
        print("  [event] OnInitialize")

    def on_term():
        counters["term"] += 1
        print("  [event] OnTerminate")

    def on_open(session):
        counters["open"] += 1
        try:
            name = session.Name
        except Exception:
            name = "<unknown>"
        print(f"  [event] OnSessionOpen   -> {name}")

    def on_close(session):
        counters["close"] += 1
        try:
            name = session.Name
        except Exception:
            name = "<unknown>"
        print(f"  [event] OnSessionClose  -> {name}")

    def on_change(session, modified_items, change_types):
        counters["change"] += 1
        try:
            name = session.Name
        except Exception:
            name = "<unknown>"
        n = modified_items.Length if modified_items is not None else 0
        print(f"  [event] OnSessionChange -> {name}  ({n} item(s) changed)")

    def on_load(session):
        counters["load"] += 1
        try:
            name = session.Name
        except Exception:
            name = "<unknown>"
        print(f"  [event] OnModelLoadComplete -> {name}")

    em.OnInitialize += on_init
    em.OnTerminate += on_term
    em.OnSessionOpen += on_open
    em.OnSessionClose += on_close
    em.OnSessionChange += on_change
    em.OnModelLoadComplete += on_load

    try:
        end = time.time() + LISTEN_SECONDS
        while time.time() < end:
            Application.DoEvents()
            time.sleep(0.05)
    finally:
        em.OnInitialize -= on_init
        em.OnTerminate -= on_term
        em.OnSessionOpen -= on_open
        em.OnSessionClose -= on_close
        em.OnSessionChange -= on_change
        em.OnModelLoadComplete -= on_load
        print("Unsubscribed.")

    print(f"\nCaptured: {counters}")
    return 0


if __name__ == "__main__":
    sys.exit(run_example(main))
