"""PDM 03 — list classes and templates on the first safe.

Classes carry **data items** (typed fields) and **default property values**.
Templates assemble classes into multi-level workflows (each level has an
attached class).
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

safes = conn.Safes
if safes.Count == 0:
    raise SystemExit("No safes available.")

safe = safes.Item(0)
print(f"Safe: {safe.Name!r}\n")

# ---- Classes ---------------------------------------------------------------
classes = safe.Classes
print(f"=== Classes ({classes.Count}) ===")
for i in range(classes.Count):
    cls = classes.Item(i)
    flavor = "core" if cls.IsCoreClass else "custom"
    print(f"\n  [{i}] {cls.Name!r}  ({flavor}, consumed={cls.IsConsumed})")

    data_items = cls.DataItems
    for d in range(data_items.Count):
        print(f"       DataItem: {data_items.Item(d).Name!r}")

    defaults = cls.DefaultProperties
    for p in range(defaults.Count):
        prop = defaults.Item(p)
        val  = prop.Value if prop.HasValue else "(no value)"
        print(f"       Default : {prop.DisplayName!r} = {val}")

# ---- Templates -------------------------------------------------------------
templates = safe.Templates
print(f"\n=== Templates ({templates.Count}) ===")
for i in range(templates.Count):
    tmpl = templates.Item(i)
    print(f"\n  [{i}] {tmpl.Name!r}  (consumed={tmpl.IsConsumed})")
    levels = tmpl.Levels
    for l in range(levels.Count):
        lvl = levels.Item(l)
        print(f"       Level: {lvl.Name!r}  (class: {lvl.ClassItem.Name!r})")
