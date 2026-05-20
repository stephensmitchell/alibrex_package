from alibrex import CurrentPart

part = CurrentPart()                   # implicit connect + narrow to IADPartSession

print(f"Part name: {part.Name}")