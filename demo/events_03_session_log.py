"""Events demo 03: log session lifecycle and changes to a CSV.

Use case: keep an audit log of every document the user opens, edits, and
closes during an Alibre session. Each event becomes one CSV row with a
timestamp, the event name, and the session/part name.

The CSV is appended to, so a long-running listener accumulates history.
"""
from __future__ import annotations

import csv
import os
import sys
import time
from datetime import datetime

import clr
clr.AddReference("System.Windows.Forms")  # type: ignore[attr-defined]
from System.Windows.Forms import Application  # type: ignore[import-not-found]

from alibrex import connect
from _demo_utils import run_demo

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "session_log.csv")
LISTEN_SECONDS = 60


def main() -> int:
    root = connect()
    em = root.EventManager

    is_new = not os.path.exists(LOG_PATH)
    log_file = open(LOG_PATH, "a", newline="", encoding="utf-8")
    writer = csv.writer(log_file)
    if is_new:
        writer.writerow(["ts", "event", "session", "extra"])
        log_file.flush()

    state = {"rows": 0}

    def row(event_name: str, session=None, extra: str = "") -> None:
        try:
            name = session.Name if session is not None else ""
        except Exception:
            name = "<error>"
        writer.writerow([datetime.now().isoformat(timespec="seconds"), event_name, name, extra])
        log_file.flush()
        state["rows"] += 1
        print(f"  [logged] {event_name}  {name}")

    def on_open(session): row("OnSessionOpen", session)
    def on_close(session): row("OnSessionClose", session)
    def on_change(session, modified_items, change_types):
        n = modified_items.Length if modified_items is not None else 0
        row("OnSessionChange", session, f"items={n}")
    def on_load(session): row("OnModelLoadComplete", session)

    em.OnSessionOpen += on_open
    em.OnSessionClose += on_close
    em.OnSessionChange += on_change
    em.OnModelLoadComplete += on_load

    print(f"Logging to {LOG_PATH}")
    print(f"Listening {LISTEN_SECONDS}s - open / edit / close documents in Alibre.")
    try:
        end = time.time() + LISTEN_SECONDS
        while time.time() < end:
            Application.DoEvents()
            time.sleep(0.05)
    finally:
        em.OnSessionOpen -= on_open
        em.OnSessionClose -= on_close
        em.OnSessionChange -= on_change
        em.OnModelLoadComplete -= on_load
        log_file.close()

    print(f"\nWrote {state['rows']} row(s) to {os.path.basename(LOG_PATH)}.")
    return 0


if __name__ == "__main__":
    sys.exit(run_demo(main))
