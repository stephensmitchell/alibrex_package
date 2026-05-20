"""PDM 08 - find every locked file across all projects in the safe.

Recursively walks every project's folder tree and reports any file
whose IsLocked flag is True. Useful for "who has X checked out?"
status reports.
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
print(f"Safe: {safe.Name!r}")
print("Scanning all projects for locked files...\n")

# Iterative DFS - no recursive function.
stack = []
for i in range(safe.Projects.Count):
    proj = safe.Projects.Item(i)
    stack.append((proj.Name, proj))

found = 0
checked = 0
while stack:
    path, folder = stack.pop()

    files = folder.FileItems
    for i in range(files.Count):
        fi = files.Item(i)
        checked += 1
        if fi.IsLocked:
            found += 1
            print(f"  LOCKED: {path}/{fi.Name}.{fi.Extension}")
            print(f"          by {fi.LockUser}, v{fi.CurrentVersionID}")

    subs = folder.Folders
    for i in range(subs.Count):
        sub = subs.Item(i)
        stack.append((f"{path}/{sub.Name}", sub))

print(f"\nScanned {checked} file(s); {found} locked.")
