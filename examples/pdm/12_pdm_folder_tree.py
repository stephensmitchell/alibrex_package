"""PDM 12 - recursive folder tree with files, properties, and history.

Mirrors the `PrintFolder` helper in the C# `Program.cs` reference:
walks each project (and library) to a given depth, printing indented
file entries with their lock state, properties, and recent version
history.

Tweak MAX_DEPTH and MAX_HISTORY_LINES to control verbosity.
"""
from alibrex import connect

# === EDIT IF NEEDED =========================================================
PDM_URL      = "http://localhost:8099/"
PDM_DOMAIN   = ""
PDM_USER     = ""
PDM_PASSWORD = ""
# ============================================================================

MAX_DEPTH = 2
MAX_HISTORY_LINES = 3


def _print_folder(folder, indent: str, depth: int) -> None:
    files = folder.FileItems
    for i in range(files.Count):
        fi = files.Item(i)
        lock = f" [LOCKED by {fi.LockUser}]" if fi.IsLocked else ""
        mod  = " *modified*" if fi.LocallyModified else ""
        print(f"{indent}|- {fi.Name}.{fi.Extension}  "
              f"(v{fi.CurrentVersionID}, {fi.FileSize:,} bytes){lock}{mod}")

        props = fi.Properties
        for p in range(props.Count):
            prop = props.Item(p)
            val  = prop.Value if prop.HasValue else "(empty)"
            print(f"{indent}|    prop: {prop.DisplayName!r} = {val}")

        history = fi.History
        shown = min(history.Count, MAX_HISTORY_LINES)
        for h in range(shown):
            ver = history.Item(h)
            rev = f" REV:{ver.Revision}" if ver.Revision else ""
            print(f"{indent}|    v{ver.Version}  {ver.CheckedInBy}"
                  f"  {ver.CheckedInAt}{rev}  {ver.VersionComment!r}")
        if history.Count > shown:
            print(f"{indent}|    ... {history.Count - shown} more versions")

    if depth < MAX_DEPTH:
        subs = folder.Folders
        for i in range(subs.Count):
            sub = subs.Item(i)
            tag = " (template)" if sub.IsTemplateFolder else ""
            print(f"{indent}|- [{sub.Name}/]{tag}")
            _print_folder(sub, indent + "|  ", depth + 1)


root = connect()
try:
    conn = root.GetActiveServerConnection()
except Exception:
    conn = None
if conn is None:
    conn = root.ConnectToPDM(PDM_URL, PDM_DOMAIN, PDM_USER, PDM_PASSWORD)

safes = conn.Safes
if safes.Count == 0:
    raise SystemExit("No safes available.")

safe = safes.Item(0)
print(f"Safe: {safe.Name!r}")

projects = safe.Projects
print(f"\n=== Projects ({projects.Count}) ===")
for i in range(projects.Count):
    proj = projects.Item(i)
    print(f"\nProject: {proj.Name!r}  (ref: {proj.Reference})")
    _print_folder(proj, "  ", 0)

libs = safe.Libraries
print(f"\n=== Libraries ({libs.Count}) ===")
for i in range(libs.Count):
    lib = libs.Item(i)
    print(f"\nLibrary: {lib.Name!r}  (ref: {lib.Reference})")
    _print_folder(lib, "  ", 0)
