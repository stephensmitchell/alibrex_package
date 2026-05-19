"""PDM 09 — inspect the safe's recycle bin.

The recycle bin holds soft-deleted file items. Its IADPDMSafeRecycleBin
acts like an IADPDMFolder so you can iterate FileItems directly.
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
bin = safe.RecycleBin

print(f"Safe: {safe.Name!r}")
print(f"Recycle bin: {bin.Name!r}")
print(f"Items: {bin.Count}\n")

files = bin.FileItems
for i in range(files.Count):
    fi = files.Item(i)
    print(f"  {fi.Name}.{fi.Extension}  (v{fi.CurrentVersionID}, {fi.FileSize:,} bytes)")
