"""PDM 06 - list files and their properties in a chosen folder.

Walks the first project's tree to find a folder with at least one file,
then prints each file's name, version, size, lock status, and PDM
properties.

Most projects organize files into subfolders rather than at the project
root, so the DFS finds something real even if the root is empty.
"""
from alibrex import connect

# === EDIT IF NEEDED (only used if no active PDM connection in the UI) =======
PDM_URL      = "http://localhost:8099/"
PDM_DOMAIN   = ""
PDM_USER     = ""            # your PDM username
PDM_PASSWORD = ""            # your PDM password
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
if projects.Count == 0:
    raise SystemExit("No projects in safe.")

proj = projects.Item(0)

# Walk subfolders to find a folder containing files.
stack = [(proj.Name, proj)]
target_folder = None
target_path = ""
while stack and target_folder is None:
    path, folder = stack.pop()
    if folder.FileItems.Count > 0:
        target_folder = folder
        target_path = path
    else:
        for i in range(folder.Folders.Count):
            sub = folder.Folders.Item(i)
            stack.append((f"{path}/{sub.Name}", sub))

if target_folder is None:
    raise SystemExit(f"Project {proj.Name!r} has no files at any depth.")

print(f"Folder: {target_path}\n")

files = target_folder.FileItems
print(f"Files: {files.Count}\n")

for i in range(files.Count):
    fi = files.Item(i)
    lock = f" [LOCKED by {fi.LockUser}]" if fi.IsLocked else ""
    mod  = " *modified*" if fi.LocallyModified else ""
    print(f"  {fi.Name}.{fi.Extension}  v{fi.CurrentVersionID}  ({fi.FileSize:,} bytes){lock}{mod}")

    props = fi.Properties
    for p in range(props.Count):
        prop = props.Item(p)
        val  = prop.Value if prop.HasValue else "(empty)"
        print(f"      {prop.DisplayName!r}: {val}")
    print()
