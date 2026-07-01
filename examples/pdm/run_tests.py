"""Run every PDM example and write a transcript + summary to test-output.txt.

PDM allows only one external API client at a time. The examples each call
ConnectToPDM, so if their connections stay open the single-client lock
stays held ("Another client instance is already accessing the Server").
This runner executes every example inside a SINGLE process and calls
Logout() on each example's connection afterward (the examples name it
``conn``) so the next example starts on a free lock.

Run it with the interpreter that has alibrex installed, e.g.:
    py -3.13-64 run_tests.py
"""
from __future__ import annotations

import contextlib
import gc
import io
import sys
import time
import traceback
from pathlib import Path

from alibrex import connect

HERE = Path(__file__).resolve().parent
OUT = HERE / "test-output.txt"
PDM_URL = "http://localhost:8099/"

MAX_ATTEMPTS = 5      # per-example retries when the PDM lock is contended
LOCK_WAIT = 12        # seconds between those retries
SETTLE = 4            # seconds after Logout: PDM frees the session async,
                      # so reconnecting too soon races into a stuck lock
LOCK_MARKER = "accessing the Server"

# Make sibling helper modules (e.g. _pdm_util) importable by the examples.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def logout(conn) -> None:
    """Release a PDM connection and give the server time to free it.

    Logout() returns before the server releases the single-client
    session, so we collect the COM object and pause to let that complete.
    """
    if conn is not None:
        with contextlib.suppress(Exception):
            conn.Logout()
    gc.collect()
    time.sleep(SETTLE)


def wait_for_clear(attempts: int = 15, wait: int = 10) -> bool:
    """Block until PDM accepts (and releases) a client, so the next example
    starts on a free single-client lock. Returns False if it never clears."""
    root = connect()
    for _ in range(attempts):
        try:
            conn = root.ConnectToPDM(PDM_URL, "", "", "")
            _ = conn.IsOnline
            logout(conn)            # logout() also settles
            return True
        except Exception:
            time.sleep(wait)
    return False


def preflight() -> str:
    """Confirm PDM is reachable (and wait out a stale lock) before example 00."""
    return ("PDM reachable; starting." if wait_for_clear()
            else "WARNING: PDM still locked after preflight.")


def run_example(path: Path) -> tuple[str, str]:
    """Run one example in-process, then Logout its connection.

    PASS: ran clean; INFO: clean SystemExit (e.g. "no files");
    LOCK: transient PDM lock (caller may retry); FAIL: real crash.
    """
    ns: dict = {"__name__": "__main__", "__file__": str(path)}
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            exec(code, ns)
            status = "PASS"
        except SystemExit as e:
            if e.code in (0, None):
                status = "PASS"
            else:
                buf.write(f"\n[SystemExit: {e.code}]\n")
                status = "INFO"
        except Exception:
            traceback.print_exc(file=buf)
            status = "FAIL"
        finally:
            logout(ns.get("conn"))
            ns.clear()
            gc.collect()
    out = buf.getvalue()
    if status == "FAIL" and LOCK_MARKER in out:
        status = "LOCK"
    return status, out


def main() -> int:
    scripts = sorted(p for p in HERE.glob("*.py") if p.name[0].isdigit())

    transcript: list[str] = [
        "PDM example test run",
        f"Interpreter : {sys.version.split()[0]} ({sys.executable})",
        f"Scripts     : {len(scripts)}",
    ]
    note = preflight()
    transcript += [note, "=" * 70]
    print(note)

    results: list[tuple[str, str]] = []
    for s in scripts:
        attempts_log: list[str] = []
        for attempt in range(1, MAX_ATTEMPTS + 1):
            # Gate: only start the example once the lock is verifiably free.
            if not wait_for_clear():
                attempts_log.append("[gave up waiting for a free PDM lock]")
            status, out = run_example(s)
            if status != "LOCK" or attempt == MAX_ATTEMPTS:
                break
            attempts_log.append(
                f"[PDM lock contended; retry {attempt}/{MAX_ATTEMPTS - 1} after {LOCK_WAIT}s]"
            )
            time.sleep(LOCK_WAIT)
        if status == "LOCK":
            status = "FAIL"  # exhausted retries
        results.append((s.name, status))
        transcript.append(f"\n========== {s.name} ==========")
        if attempts_log:
            transcript.append("\n".join(attempts_log))
        transcript.append(out)
        print(f"  {status:5} {s.name}")

    counts = {k: sum(1 for _, st in results if st == k) for k in ("PASS", "INFO", "FAIL")}
    summary = [
        "=" * 70,
        "SUMMARY",
        "=" * 70,
        *[f"  {st:5} {name}" for name, st in results],
        "-" * 70,
        f"  {counts['PASS']} PASS, {counts['INFO']} INFO (clean early-exit), "
        f"{counts['FAIL']} FAIL  of {len(results)}",
        "  INFO = ran fine but raised SystemExit (e.g. the chosen project has no files)",
    ]

    OUT.write_text("\n".join(summary) + "\n\n" + "\n".join(transcript) + "\n",
                   encoding="utf-8")
    print("\n".join(summary))
    print(f"\nWrote {OUT}")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
