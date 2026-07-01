"""PDM 04: browse the project folder tree.

Projects are top-level folders inside a safe. Each project is an
IADPDMFolder, so it has both FileItems (files at that level) and
Folders (subfolders).

Prints one level of subfolders per project to keep output manageable.
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
projects = safe.Projects

print(f"Safe: {safe.Name!r}")
print(f"Projects: {projects.Count}\n")

for i in range(projects.Count):
    proj = projects.Item(i)
    print(f"  [{i}] {proj.Name!r}  (ref: {proj.Reference})")

    files = proj.FileItems
    if files.Count > 0:
        print(f"        files: {files.Count}")
        for j in range(min(files.Count, 3)):
            fi = files.Item(j)
            print(f"          - {fi.Name}.{fi.Extension}  ({fi.FileSize:,} bytes)")
        if files.Count > 3:
            print(f"          ... {files.Count - 3} more")

    subs = proj.Folders
    if subs.Count > 0:
        print(f"        subfolders: {subs.Count}")
        for j in range(min(subs.Count, 5)):
            sf = subs.Item(j)
            kind = " (template)" if sf.IsTemplateFolder else ""
            print(f"          - {sf.Name}/{kind}")
        if subs.Count > 5:
            print(f"          ... {subs.Count - 5} more")
    print()
