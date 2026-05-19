"""PDM 00 — connect and print server info.

Bare-bones starting point. Tier 0 of the 0-to-100 PDM curriculum.
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

print(f"Server   : {conn.URL}")
print(f"Domain   : {conn.Domain}")
print(f"User     : {conn.UserName}")
print(f"Online   : {conn.IsOnline}")
