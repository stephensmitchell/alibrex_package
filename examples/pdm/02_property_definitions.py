"""PDM 02: list custom property definitions on a safe.

Property definitions describe the metadata fields that file items can
carry. Each definition has a value type (string, int, date, …) and a
"built-in" flag distinguishing PDM defaults from user-added fields.

Walks the FIRST safe; tweak `safe = safes.Item(0)` to pick another.
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
    raise SystemExit("No safes available on this connection.")

safe = safes.Item(0)
print(f"Safe: {safe.Name!r}\n")

defs = safe.PropertyDefinitions
print(f"Property definitions: {defs.Count}\n")

for i in range(defs.Count):
    pd = defs.Item(i)
    flavor   = "built-in" if pd.IsBuiltInPropertyDefinition else "custom"
    consumed = "consumed" if pd.IsConsumed else "free"
    print(f"  [{i}] {pd.DisplayName!r}  (name={pd.Name})")
    print(f"      type={pd.PropertyValueType}  {flavor}  {consumed}")
