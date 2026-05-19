from alibrex import connect_to_running_alibre

root = connect_to_running_alibre()
print(f"Alibre {root.Version}")
print(f"Open sessions: {root.Sessions.Count}")

session = root.TopmostSession
print(f"Active document: {session.Name}")