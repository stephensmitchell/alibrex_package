from alibrex import CurrentAssembly

ass = CurrentAssembly()                   # implicit connect + narrow to IADAssemblySession

print(f"Assembly name: {ass.Name}")
