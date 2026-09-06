"""PDM 09: inspect the safe's recycle bin.

The recycle bin holds soft-deleted items. An IADPDMSafeRecycleBin exposes
only Count / Item(i); it has no FileItems. Each top-level Item is an
organizing folder (e.g. "By Type"), and the deleted files live inside
those folders. Wrap each item as an IADPDMFolder and walk it recursively.

The bin's Item(i) is typed as Object, so AlibreX hands back a raw COM
object that the bridge can't auto-wrap. The shared as_folder() helper
(see _pdm_util.py) casts it to a typed IADPDMFolder.
"""
from alibrex import connect

from _pdm_util import as_folder

PDM_URL      = "http://localhost:8099/"
PDM_DOMAIN   = ""
PDM_USER     = ""
PDM_PASSWORD = ""

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

def walk(folder, depth=0):
    pad = "  " * depth
    print(f"{pad}[{folder.Name}/]")
    files = folder.FileItems
    for i in range(files.Count):
        fi = files.Item(i)
        print(f"{pad}  - {fi.Name}.{fi.Extension}  "
              f"(v{fi.CurrentVersionID}, {fi.FileSize:,} bytes)")
    subs = folder.Folders
    for i in range(subs.Count):
        walk(subs.Item(i), depth + 1)

if bin.Count == 0:
    print("Recycle bin is empty.")
else:
    for i in range(bin.Count):
        walk(as_folder(bin.Item(i)))
