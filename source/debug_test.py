"""Set a breakpoint on any line below to test debugging.

In VS Code: F5 with this file active, or pick "Python: Current File"
from the debug dropdown. The Variables panel should show:
  - 'root' as a ComProxy(IADRoot)
  - Expanding it shows Sessions, MaterialLibraries, etc. via __dir__
  - 'edge' lets you watch StartVertex.Point.X / .Y / .Z
"""
from alibrex import CurrentPart

part = CurrentPart()

body = part.Bodies.Item(0)
print(f"Edge count: {body.Edges.Count}")

for i in range(body.Edges.Count):
    edge = body.Edges.Item(i)
    sv = edge.StartVertex.Point
    print(f"edge[{i}] start = ({sv.X}, {sv.Y}, {sv.Z})")
