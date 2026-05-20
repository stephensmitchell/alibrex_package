"""PDM 01 - enumerate the safes available to this connection.

A "safe" is the top-level vault in Alibre PDM. Each safe contains its
own classes, property definitions, templates, projects, and libraries.
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
print(f"Found {safes.Count} safe(s):")
for i in range(safes.Count):
    safe = safes.Item(i)
    print(f"  [{i}] {safe.Name!r}  (ref: {safe.Reference})")
