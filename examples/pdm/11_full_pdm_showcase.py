"""PDM 11 - full showcase (Python port of the C# `Program.cs` example).

Comprehensive walk-through covering:
  1. Server connection details
  2. Available safes
  3. Property definitions on a safe
  4. Classes (with data items + default properties)
  5. Templates (with levels)
  6. Projects (one-level folder browse)
  7. Libraries (one-level folder browse)
  8. Recycle bin
  9. Open Alibre sessions

This script consolidates the 00–10 demos into a single end-to-end
report. Run it as your "is everything healthy?" verification.
"""
from alibrex import connect

# === EDIT IF NEEDED =========================================================
PDM_URL      = "http://localhost:8099/"
PDM_DOMAIN   = ""
PDM_USER     = ""
PDM_PASSWORD = ""
# ============================================================================

root = connect()
try:
    conn = root.GetActiveServerConnection()
except Exception:
    conn = None
if conn is None:
    conn = root.ConnectToPDM(PDM_URL, PDM_DOMAIN, PDM_USER, PDM_PASSWORD)


def _hdr(title: str) -> None:
    bar = "=" * 60
    line = "-" * 60
    print(f"\n{bar}\n {title}\n{line}")


_hdr("Alibre Design Info")
print(f"  Version   : {root.Version}")
print(f"  Product   : {root.AppTitle}")
print(f"  Language  : {root.LanguageForResources}")

_hdr("1. PDM Server Connection")
print(f"  Server    : {conn.URL}")
print(f"  Domain    : {conn.Domain}")
print(f"  User      : {conn.UserName}")
print(f"  Online    : {conn.IsOnline}")

_hdr("2. Available Safes")
safes = conn.Safes
print(f"  Count: {safes.Count}")
for i in range(safes.Count):
    safe = safes.Item(i)
    print(f"  [{i}] {safe.Name!r}  (ref: {safe.Reference})")

if safes.Count == 0:
    raise SystemExit("\nNo safes - nothing else to report.")

safe = safes.Item(0)
print(f"\n  Working with safe: {safe.Name!r}")

_hdr("3. Property Definitions")
defs = safe.PropertyDefinitions
print(f"  Count: {defs.Count}")
for i in range(defs.Count):
    pd = defs.Item(i)
    flavor = "built-in" if pd.IsBuiltInPropertyDefinition else "custom"
    print(f"  [{i}] {pd.DisplayName!r} ({pd.Name}) "
          f"- {flavor}, type={pd.PropertyValueType}, consumed={pd.IsConsumed}")

_hdr("4. Classes")
classes = safe.Classes
print(f"  Count: {classes.Count}")
for i in range(classes.Count):
    cls = classes.Item(i)
    flavor = "core" if cls.IsCoreClass else "custom"
    print(f"  [{i}] {cls.Name!r} - {flavor}, consumed={cls.IsConsumed}")
    for d in range(cls.DataItems.Count):
        print(f"       DataItem   : {cls.DataItems.Item(d).Name!r}")
    for p in range(cls.DefaultProperties.Count):
        prop = cls.DefaultProperties.Item(p)
        val  = prop.Value if prop.HasValue else "(no value)"
        print(f"       DefaultProp: {prop.DisplayName!r} = {val}")

_hdr("5. Templates")
templates = safe.Templates
print(f"  Count: {templates.Count}")
for i in range(templates.Count):
    tmpl = templates.Item(i)
    print(f"  [{i}] {tmpl.Name!r} - consumed={tmpl.IsConsumed}")
    for l in range(tmpl.Levels.Count):
        lvl = tmpl.Levels.Item(l)
        print(f"       Level: {lvl.Name!r} (class: {lvl.ClassItem.Name!r})")

_hdr("6. Projects")
projects = safe.Projects
print(f"  Count: {projects.Count}")
for i in range(projects.Count):
    proj = projects.Item(i)
    n_files = proj.FileItems.Count
    n_subs  = proj.Folders.Count
    print(f"  [{i}] {proj.Name!r}  (ref: {proj.Reference})  "
          f"files={n_files}  subfolders={n_subs}")

_hdr("7. Libraries")
libs = safe.Libraries
print(f"  Count: {libs.Count}")
for i in range(libs.Count):
    lib = libs.Item(i)
    n_files = lib.FileItems.Count
    n_subs  = lib.Folders.Count
    print(f"  [{i}] {lib.Name!r}  (ref: {lib.Reference})  "
          f"files={n_files}  subfolders={n_subs}")

_hdr("8. Recycle Bin")
bin = safe.RecycleBin
print(f"  Name  : {bin.Name}")
print(f"  Items : {bin.Count}")

_hdr("9. Open Sessions (Alibre UI)")
sessions = root.Sessions
print(f"  Count: {sessions.Count}")
for i in range(sessions.Count):
    s = sessions.Item(i)
    print(f"  [{i}] {s.FilePath}")

_hdr("Done")
