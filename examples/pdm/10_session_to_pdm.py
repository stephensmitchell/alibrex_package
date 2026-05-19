"""PDM 10 — cross-reference an open Alibre session with PDM.

For each open document in the active Alibre instance, check whether
it's stored in a known PDM repository and report its file path and
PDM reference.
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

sessions = root.Sessions
print(f"Open Alibre sessions: {sessions.Count}\n")

for i in range(sessions.Count):
    s = sessions.Item(i)
    print(f"  [{i}] {s.Name!r}  type={s.SessionType}")
    print(f"        path: {s.FilePath}")

    try:
        from_repo = root.IsOpenedFromRepository(s.FilePath)
    except Exception:
        from_repo = False

    if from_repo:
        try:
            ref = root.GetRepositoryReference(s.FilePath)
            print(f"        PDM ref: {ref}")
        except Exception:
            print("        (in PDM but reference unavailable)")
    else:
        print("        (not from a PDM repository)")
    print()
