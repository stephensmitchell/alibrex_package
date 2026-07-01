r"""Close Alibre sessions left open by the demo/example scripts.

Closes only documents whose names match known demo prefixes or bundled
muffler sample names, discarding changes with ``Close(False)``.

Run:
    .venvv\Scripts\python.exe close_demo_sessions.py

Preview only:
    .venvv\Scripts\python.exe close_demo_sessions.py --dry-run
"""
from __future__ import annotations

import argparse
import sys

from alibrex import AlibreNotRunning, connect

DEMO_PREFIXES = (
    "CRUD",
    "SK2_",
    "PRM",
    "CFG_",
    "ASM_",
    "PROF_",
    "Profile_",
    "Mate_",
    "Align_",
    "Distance_",
    "Sub_",
    "Parent_",
    "FullyConstrain_",
)

MUFFLER_NAMES = {
    "0_Muffler_Assembly",
    "cylinder",
    "baffle plate choke tube assembly",
    "dished baffle plate",
    "choke tube assembly",
    "choke tube",
    "choke tube support block",
    "nozzle head assembly1",
    "nozzle head assembly2",
    "elliptical head",
    "nozzle1 reinf pad",
    "vessel nozzle 1",
    "inlet orifice plate",
    "outlet orifice plate",
    "outlet orifice plate 2a",
}


def is_demo_session(name: str, include_muffler: bool) -> bool:
    return name.startswith(DEMO_PREFIXES) or (
        include_muffler and name in MUFFLER_NAMES
    )


def session_name(session) -> str:
    try:
        return str(session.Name)
    except Exception:  # noqa: BLE001
        return "<unknown>"


def session_type(session) -> str:
    try:
        return str(session.SessionType)
    except Exception:  # noqa: BLE001
        return "<unknown>"


def is_gui_visible(session) -> bool:
    try:
        return bool(session.IsGUIVisible)
    except Exception:  # noqa: BLE001
        return True


def collect_targets(root, *, include_muffler: bool, include_hidden: bool):
    targets = []
    for i in range(root.Sessions.Count):
        session = root.Sessions.Item(i)
        name = session_name(session)
        if not is_demo_session(name, include_muffler):
            continue
        if not include_hidden and not is_gui_visible(session):
            continue
        targets.append(session)
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching sessions without closing them.",
    )
    parser.add_argument(
        "--no-muffler",
        action="store_true",
        help="Do not close bundled muffler sample sessions.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Also try to close non-visible constituent sessions.",
    )
    args = parser.parse_args(argv)

    try:
        root = connect()
    except AlibreNotRunning as exc:
        print(f"[skip] {exc}", file=sys.stderr)
        return 0

    targets = collect_targets(
        root,
        include_muffler=not args.no_muffler,
        include_hidden=args.include_hidden,
    )

    if not targets:
        print("No matching demo sessions are open.")
        return 0

    print(f"Matching demo sessions: {len(targets)}")
    for session in targets:
        print(f"  - {session_name(session)} ({session_type(session)})")

    if args.dry_run:
        return 0

    closed = 0
    failed = 0
    for session in list(targets):
        name = session_name(session)
        try:
            session.Close(False)
            closed += 1
            print(f"[closed] {name}")
        except Exception as exc:  # noqa: BLE001
            if "Browser is not found" in str(exc) or "Index out of bounds" in str(exc):
                continue
            failed += 1
            print(f"[failed] {name}: {type(exc).__name__}: {exc}")

    print(f"\nClosed {closed}; failed {failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
