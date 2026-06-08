"""Diagnose your alibrex / Alibre Design setup.

Walks through every check the package performs at import time. Useful
for verifying a fresh install or troubleshooting when something fails.

Safe to run with or without Alibre Design open. Section 3 inspects the
AlibreX.dll discovery without needing a live connection; section 4
only succeeds if Alibre is running.

Run:
    python diagnose_setup.py

Exit codes:
    0  all checks passed (including a live Alibre connection)
    1  could not locate AlibreX.dll or required packages
    2  AlibreX.dll found, but Alibre Design is not running
"""
from __future__ import annotations

import os
import platform
import sys


print("=" * 60)
print("alibrex setup diagnostic")
print("=" * 60)

# --- 1. Environment ---------------------------------------------------------
print("\n[1] Environment")
print(f"  Python:     {sys.version.split()[0]}")
print(f"  Platform:   {platform.platform()}")
print(f"  Arch:       {platform.machine()}")

# --- 2. Package versions ----------------------------------------------------
print("\n[2] Package versions")
try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    print("  importlib.metadata unavailable on this Python")
    sys.exit(1)

missing = False
for pkg in ("alibrex", "pythonnet"):
    try:
        print(f"  {pkg:12s} {version(pkg)}")
    except PackageNotFoundError:
        print(f"  {pkg:12s} NOT INSTALLED")
        missing = True
if missing:
    print("\n  -> Install with: pip install alibrex")
    sys.exit(1)

# --- 3. AlibreX.dll discovery ----------------------------------------------
print("\n[3] AlibreX.dll discovery")

# Bypass the import-time running check so we can inspect the DLL path
# even when Alibre isn't open.
os.environ["ALIBREX_SKIP_RUNNING_CHECK"] = "1"

try:
    import alibrex
    from alibrex._discover import discover_sources, find_alibrex_dll
except Exception as exc:
    print(f"  ERROR importing alibrex: {type(exc).__name__}: {exc}")
    sys.exit(1)

sources = discover_sources()
labels = {
    "env_var":         "Source 1 ($ALIBREX_DLL):      ",
    "com_registry":    "Source 2 (Registry COM):      ",
    "alibre_registry": "Source 3 (Alibre install reg):",
    "program_files":   "Source 4 (%ProgramFiles%):    ",
}
for key, label in labels.items():
    print(f"  {label}  {sources[key] or '(no hit)'}")

resolved = str(find_alibrex_dll())
print(f"\n  Resolved DLL: {resolved}")

# List EVERY source whose hit matches the resolved DLL.
matches = [
    labels[key].strip().rstrip(":").strip()
    for key, hit in sources.items()
    if hit and os.path.normcase(str(hit)) == os.path.normcase(resolved)
]
if matches:
    print(f"\n  -> Sources that match the resolved DLL ({len(matches)}):")
    for m in matches:
        print(f"       - {m}")
else:
    print("\n  -> No source matches the resolved DLL (unexpected)")

# --- 4. Live Alibre connection ---------------------------------------------
print("\n[4] Live Alibre connection")
os.environ.pop("ALIBREX_SKIP_RUNNING_CHECK", None)

try:
    from alibrex import connect_to_running_alibre

    root = connect_to_running_alibre()
    print(f"  Alibre version: {root.Version}")
    print(f"  Open sessions:  {root.Sessions.Count}")

    topmost = root.TopmostSession
    if topmost is not None:
        print(f"  Active doc:     {topmost.Name}  type={topmost.SessionType}")
    else:
        print("  Active doc:     (none open)")

    print("\n  All checks passed.")
    sys.exit(0)
except Exception as exc:
    print(f"  Could not connect: {type(exc).__name__}: {exc}")
    print("\n  -> Alibre Design is not running, or the COM hook is unavailable.")
    print("    Start Alibre Design and re-run this diagnostic.")
    sys.exit(2)
