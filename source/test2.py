from alibrex import CurrentPart

part = CurrentPart()
body = part.Bodies.Item(0)

for i in range(body.Edges.Count):
    edge = body.Edges.Item(i)
    sv = edge.StartVertex.Point
    ev = edge.EndVertex.Point
    print(f"edge[{i}]: ({sv.X},{sv.Y},{sv.Z}) -> ({ev.X},{ev.Y},{ev.Z})")
