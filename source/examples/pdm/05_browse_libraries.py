"""PDM 05: browse the library folder tree.

Libraries sit beside projects on a safe, typically holding standard
parts, fasteners, materials, etc. They share the IADPDMFolder shape of
projects, so the browsing pattern is identical.
"""
from alibrex import connect

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
libs = safe.Libraries

print(f"Safe: {safe.Name!r}")
print(f"Libraries: {libs.Count}\n")

for i in range(libs.Count):
    lib = libs.Item(i)
    print(f"  [{i}] {lib.Name!r}  (ref: {lib.Reference})")

    files = lib.FileItems
    if files.Count > 0:
        print(f"        files: {files.Count}")
        for j in range(min(files.Count, 3)):
            fi = files.Item(j)
            print(f"          - {fi.Name}.{fi.Extension}")
        if files.Count > 3:
            print(f"          ... {files.Count - 3} more")

    subs = lib.Folders
    if subs.Count > 0:
        print(f"        subfolders: {subs.Count}")
        for j in range(min(subs.Count, 5)):
            print(f"          - {subs.Item(j).Name}/")
    print()
