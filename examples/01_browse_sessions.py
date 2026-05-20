"""Example 01 - enumerate all open sessions and classify them by type."""
from __future__ import annotations

import sys

from alibrex import (
    ADObjectSubType,
    IADAssemblySession,
    IADDrawingSession,
    IADPartSession,
    IADSession,
)
from alibrex import connect, run_example
def classify(session: IADSession) -> str:
    if isinstance(session, IADPartSession):  # type: ignore[arg-type]
        return "Part"
    if isinstance(session, IADAssemblySession):  # type: ignore[arg-type]
        return "Assembly"
    if isinstance(session, IADDrawingSession):  # type: ignore[arg-type]
        return "Drawing"
    return f"Other({session.SessionType})"


def main() -> None:
    root = connect()
    sessions = root.Sessions
    print(f"{sessions.Count} open session(s):\n")
    for i in range(sessions.Count):
        s = sessions.Item(i)
        kind = classify(s)
        # CLR enums don't expose Python's .name; str() dispatches to Enum.ToString().
        sub = str(ADObjectSubType(int(s.SessionType)))
        print(f"  [{i}] {kind:9s}  sub={sub:20s}  name={s.Name}")


if __name__ == "__main__":
    sys.exit(run_example(main))
