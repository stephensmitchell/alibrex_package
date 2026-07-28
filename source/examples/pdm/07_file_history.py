"""PDM 07: version history of files in the first project.

Walks the first project's tree to find the first folder that contains
files, then prints each file's check-in history (version number, checker
name, timestamp, revision label, comment).

Walks subfolders because most projects store files below the project
root.
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
projects = safe.Projects
if projects.Count == 0:
    raise SystemExit("No projects in safe.")

proj = projects.Item(0)

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
for i in range(files.Count):
    fi = files.Item(i)
    print(f"  {fi.Name}.{fi.Extension}  (currently v{fi.CurrentVersionID})")

    history = fi.History
    if history.Count == 0:
        print("    (no history)")
        continue

    for h in range(history.Count):
        ver = history.Item(h)
        rev = f" rev:{ver.Revision}" if ver.Revision else ""
        print(f"    v{ver.Version}  {ver.CheckedInBy}  {ver.CheckedInAt}{rev}")
        if ver.VersionComment:
            print(f"        comment: {ver.VersionComment!r}")
    print()
