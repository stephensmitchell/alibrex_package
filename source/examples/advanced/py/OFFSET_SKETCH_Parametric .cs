// Created with AlibreX Genie by Stephen S. Mitchell, https://github.com/stephensmitchell
internal static class Program
{
    private const double VertexTol = 0.0000001;
    private const double MiterFactor = 8.0;

    // =========================
    // User inputs - edit these
    // =========================
    private const string SketchName = "Sketch<1>";
    private const double OffsetValue = 1;

    [STAThread]
    private static int Main()
    {
        try
        {
            IAutomationHook hook = (IAutomationHook)GetActiveObject("AlibreX.AutomationHook", throwOnError: true);
            IADRoot root = (IADRoot)hook.Root;

            IADSession session = root.TopmostSession
                ?? throw new InvalidOperationException("No active Alibre Design session was found.");

            IADPartSession part = session as IADPartSession
                ?? throw new InvalidOperationException("The topmost Alibre Design session is not a part session.");

            Console.WriteLine($"Offsetting sketch '{SketchName}' by {OffsetValue}.");

            Dictionary<string, object> result = OffsetSketch(root, part, SketchName, OffsetValue);
            PrintResult(result);

            if (StringEquals(result, "Status", "Success") || StringEquals(result, "Status", "Warning"))
            {
                try
                {
                    part.RegenerateAll();
                    Console.WriteLine("Part regenerated.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine("RegenerateAll failed: " + ex.Message);
                }
            }

            return StringEquals(result, "Status", "Success") || StringEquals(result, "Status", "Warning") || StringEquals(result, "Status", "AlreadyApplied")
                ? 0
                : 2;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("ERROR: " + ex.Message);
            return 1;
        }
    }

    private static Dictionary<string, object> OffsetSketch(IADRoot root, IADPartSession part, string sketchName, double offsetValue)
    {
        Dictionary<string, object> result = new Dictionary<string, object>(StringComparer.Ordinal);
        List<string> warnings = new List<string>();

        try
        {
            Debug.WriteLine($"=== OFFSET SKETCH === Sketch: '{sketchName}', Offset: {offsetValue}");

            double d = Math.Abs(offsetValue);
            if (d <= VertexTol)
                return Error("Offset value must be non-zero.");

            IADSketch sketch = FindSketch(part, sketchName);
            if (sketch == null)
                return Error($"Sketch '{sketchName}' not found in the active part.");

            bool consumed = false;
            try { consumed = sketch.IsConsumed; } catch { }
            if (consumed)
            {
                string featureName = "a feature";
                try
                {
                    IADPartFeature consumingFeature = sketch.ConsumingFeature;
                    if (consumingFeature != null)
                        featureName = consumingFeature.Name;
                }
                catch { }

                return Error($"Sketch '{sketch.Name}' is consumed by '{featureName}' and cannot be edited. Roll back or delete the consuming feature first.");
            }

            bool suppressed = false;
            try { suppressed = sketch.IsSuppressed; } catch { }
            if (suppressed)
                return Error($"Sketch '{sketch.Name}' is suppressed and cannot be edited.");

            List<OffEdge> edges = new List<OffEdge>();
            List<string> skipped = new List<string>();

            for (int i = 0; i < sketch.Figures.Count; i++)
            {
                object rawFigure = sketch.Figures.Item(i);
                if (rawFigure is IADSketchPoint)
                    continue;

                IADSketchFigure fig = rawFigure as IADSketchFigure;
                if (fig == null)
                    continue;

                bool isReference = false;
                try { isReference = fig.IsReference; } catch { }
                if (isReference)
                    continue;

                if (fig is IADSketchLine ln)
                {
                    double dx0 = ln.End.X - ln.Start.X;
                    double dy0 = ln.End.Y - ln.Start.Y;
                    if (Math.Sqrt(dx0 * dx0 + dy0 * dy0) <= VertexTol)
                    {
                        skipped.Add("DegenerateLine");
                        continue;
                    }

                    edges.Add(new OffEdge
                    {
                        Kind = "Line",
                        OrigLine = ln,
                        X1 = ln.Start.X,
                        Y1 = ln.Start.Y,
                        X2 = ln.End.X,
                        Y2 = ln.End.Y
                    });
                }
                else if (fig is IADSketchCircularArc ar)
                {
                    edges.Add(new OffEdge
                    {
                        Kind = "Arc",
                        OrigArc = ar,
                        CX = ar.Center.X,
                        CY = ar.Center.Y,
                        R = ar.Radius,
                        X1 = ar.Start.X,
                        Y1 = ar.Start.Y,
                        X2 = ar.End.X,
                        Y2 = ar.End.Y
                    });
                }
                else if (fig is IADSketchCircle ci)
                {
                    edges.Add(new OffEdge
                    {
                        Kind = "Circle",
                        OrigCircle = ci,
                        CX = ci.Center.X,
                        CY = ci.Center.Y,
                        R = ci.Radius
                    });
                }
                else
                {
                    skipped.Add(fig.FigureType.ToString());
                }
            }

            if (edges.Count == 0)
            {
                result["Status"] = "Error";
                result["Message"] = "Sketch contains no offsettable line/circle/arc geometry.";
                result["SkippedTypes"] = skipped;
                return result;
            }

            for (int i = 0; i < edges.Count; i++)
                edges[i].Index = i;

            string markerName = OffsetMarker(sketch.Name);
            if (MarkerExists(sketch, markerName))
            {
                result["Status"] = "AlreadyApplied";
                result["Message"] = $"Sketch '{sketch.Name}' already carries an offset from this tool (dimension '{markerName}'). To change it, edit that driving dimension in Alibre, or delete the prior offset geometry before re-running.";
                result["SketchName"] = sketch.Name;
                return result;
            }

            List<EndRef> ends = new List<EndRef>();
            foreach (OffEdge e in edges)
            {
                if (e.Kind == "Line" || e.Kind == "Arc")
                {
                    ends.Add(new EndRef { Edge = e, WhichEnd = 1, X = e.X1, Y = e.Y1 });
                    ends.Add(new EndRef { Edge = e, WhichEnd = 2, X = e.X2, Y = e.Y2 });
                }
            }

            List<List<EndRef>> groups = BuildGroups(ends);
            for (int gi = 0; gi < groups.Count; gi++)
            {
                foreach (EndRef ep in groups[gi])
                {
                    ep.GroupId = gi;
                    if (ep.WhichEnd == 1)
                        ep.Edge.GroupStart = gi;
                    else
                        ep.Edge.GroupEnd = gi;
                }
            }

            AssignOutwardByWinding(edges, groups, warnings);

            double cx = 0.0;
            double cy = 0.0;
            int cn = 0;
            foreach (OffEdge e in edges)
            {
                switch (e.Kind)
                {
                    case "Line":
                    case "Arc":
                        cx += e.X1 + e.X2;
                        cy += e.Y1 + e.Y2;
                        cn += 2;
                        break;
                    case "Circle":
                        cx += e.CX;
                        cy += e.CY;
                        cn += 1;
                        break;
                }
            }

            if (cn > 0)
            {
                cx /= cn;
                cy /= cn;
            }

            int radiusErrors = 0;
            foreach (OffEdge e in edges)
            {
                switch (e.Kind)
                {
                    case "Line":
                        if (!e.HasNormal)
                            AssignCentroidNormal(e, cx, cy, warnings);
                        e.OX1 = e.X1 + d * e.NX;
                        e.OY1 = e.Y1 + d * e.NY;
                        e.OX2 = e.X2 + d * e.NX;
                        e.OY2 = e.Y2 + d * e.NY;
                        break;

                    case "Circle":
                        e.RNew = e.R + d;
                        break;

                    case "Arc":
                        if (!e.HasNormal)
                            AssignArcGrowByCentroid(e, cx, cy);

                        e.RNew = e.Grow ? e.R + d : e.R - d;
                        if (e.RNew <= VertexTol)
                        {
                            e.Skip = true;
                            radiusErrors++;
                            warnings.Add($"Arc skipped: inward offset {d:0.###} exceeds radius {e.R:0.###}.");
                            continue;
                        }

                        double scale = e.RNew / e.R;
                        e.OX1 = e.CX + (e.X1 - e.CX) * scale;
                        e.OY1 = e.CY + (e.Y1 - e.CY) * scale;
                        e.OX2 = e.CX + (e.X2 - e.CX) * scale;
                        e.OY2 = e.CY + (e.Y2 - e.CY) * scale;
                        break;
                }
            }

            List<string> unjoined = new List<string>();
            List<EndRef[]> joinPlan = new List<EndRef[]>();

            foreach (List<EndRef> group in groups)
            {
                List<EndRef> live = group.FindAll(ep => !ep.Edge.Skip);
                if (live.Count < 2)
                    continue;

                if (live.Count > 2)
                {
                    unjoined.Add($"({group[0].X:0.###},{group[0].Y:0.###}) x{live.Count} edges");
                    continue;
                }

                EndRef a = live[0];
                EndRef b = live[1];

                if (a.Edge.Kind == "Line" && b.Edge.Kind == "Line")
                {
                    if (MiterIntersect(a.Edge, b.Edge, out double ix, out double iy))
                    {
                        SetOff(a, ix, iy);
                        SetOff(b, ix, iy);
                        joinPlan.Add(new[] { a, b });
                        MarkJoined(a);
                        MarkJoined(b);
                    }
                    else
                    {
                        unjoined.Add($"({group[0].X:0.###},{group[0].Y:0.###}) near-parallel lines");
                    }
                }
                else
                {
                    double ax = OffX(a);
                    double ay = OffY(a);
                    double bx = OffX(b);
                    double by = OffY(b);
                    double sep = Math.Sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by));

                    if (sep <= Math.Max(VertexTol * 10.0, d * 0.0001))
                    {
                        joinPlan.Add(new[] { a, b });
                        MarkJoined(a);
                        MarkJoined(b);
                    }
                    else
                    {
                        unjoined.Add($"({group[0].X:0.###},{group[0].Y:0.###}) non-tangent {a.Edge.Kind}/{b.Edge.Kind}");
                    }
                }
            }

            try
            {
                sketch.BeginChange();
            }
            catch (Exception exBegin)
            {
                return Error($"Could not enter edit mode for sketch '{sketch.Name}'. It may be open in Alibre's sketch editor - exit sketch mode and run again. Detail: {exBegin.Message}");
            }

            List<IADSketchFigure> created = new List<IADSketchFigure>();
            IADDimension placedDim = null;
            ConstraintHelper ch = new ConstraintHelper(root, sketch);
            IADSketchLine master = null;
            int joins = 0;
            int refTotal = 0;
            bool dimensioned = false;
            string hardError = null;

            try
            {
                foreach (OffEdge e in edges)
                {
                    if (e.Skip)
                        continue;

                    switch (e.Kind)
                    {
                        case "Line":
                            e.OffLine = sketch.Figures.AddLine(e.OX1, e.OY1, e.OX2, e.OY2);
                            created.Add(e.OffLine);
                            e.OStartPt = e.OffLine.Start;
                            e.OEndPt = e.OffLine.End;

                            double mx = (e.X1 + e.X2) / 2.0;
                            double my = (e.Y1 + e.Y2) / 2.0;
                            e.MidRef = sketch.Figures.AddLine(mx, my, mx + d * e.NX, my + d * e.NY);
                            e.MidRef.IsReference = true;
                            created.Add(e.MidRef);

                            if (!e.JoinedStart)
                            {
                                e.TieStart = sketch.Figures.AddLine(e.X1, e.Y1, e.OX1, e.OY1);
                                e.TieStart.IsReference = true;
                                created.Add(e.TieStart);
                            }

                            if (!e.JoinedEnd)
                            {
                                e.TieEnd = sketch.Figures.AddLine(e.X2, e.Y2, e.OX2, e.OY2);
                                e.TieEnd.IsReference = true;
                                created.Add(e.TieEnd);
                            }
                            break;

                        case "Circle":
                            e.OffCircle = sketch.Figures.AddCircle(e.CX, e.CY, e.RNew);
                            created.Add(e.OffCircle);

                            e.RadRef = sketch.Figures.AddLine(e.CX + e.R, e.CY, e.CX + e.RNew, e.CY);
                            e.RadRef.IsReference = true;
                            created.Add(e.RadRef);
                            break;

                        case "Arc":
                            double signedAngle = ArcSignedAngle(e.OrigArc);
                            e.OffArc = sketch.Figures.AddCircularArcByCenterStartAngle(e.CX, e.CY, e.OX1, e.OY1, signedAngle);
                            created.Add(e.OffArc);
                            e.OStartPt = e.OffArc.Start;
                            e.OEndPt = e.OffArc.End;

                            e.RadRef = sketch.Figures.AddLine(e.X1, e.Y1, e.OX1, e.OY1);
                            e.RadRef.IsReference = true;
                            created.Add(e.RadRef);

                            e.RadRef2 = sketch.Figures.AddLine(e.X2, e.Y2, e.OX2, e.OY2);
                            e.RadRef2.IsReference = true;
                            created.Add(e.RadRef2);
                            break;
                    }
                }

                foreach (OffEdge e in edges)
                {
                    if (e.Skip)
                        continue;

                    if (e.MidRef != null)
                    {
                        master = e.MidRef;
                        break;
                    }

					if (e.RadRef != null)
					{
						master = e.RadRef;
						break;
					}
				}

				foreach (OffEdge e in edges)
				{
					if (e.Skip)
						continue;

					switch (e.Kind)
					{
						case "Line":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_PARALLEL, e.OffLine, e.OrigLine);
							break;
						case "Circle":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.OffCircle.Center, e.OrigCircle.Center);
							break;
						case "Arc":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.OffArc.Center, e.OrigArc.Center);
							break;
					}
				}

				foreach (OffEdge e in edges)
				{
					if (e.Skip)
						continue;

					switch (e.Kind)
					{
						case "Line":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_MIDPOINT, e.MidRef.Start, e.OrigLine);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR, e.MidRef, e.OrigLine);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.MidRef.End, e.OffLine);

							if (e.TieStart != null)
							{
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.TieStart.Start, e.OrigLine.Start);
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.TieStart.End, e.OffLine.Start);
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR, e.TieStart, e.OrigLine);
							}

							if (e.TieEnd != null)
							{
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.TieEnd.Start, e.OrigLine.End);
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.TieEnd.End, e.OffLine.End);
								ch.Add(ADSketchConstraintType.AD_CONSTRAINT_PERPENDICULAR, e.TieEnd, e.OrigLine);
							}
							break;

						case "Circle":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef.Start, e.OrigCircle);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef.End, e.OffCircle);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.OrigCircle.Center, e.RadRef);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_HORIZONTAL, e.RadRef);
							break;

						case "Arc":
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef.Start, e.OrigArc.Start);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef.End, e.OffArc.Start);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.OrigArc.Center, e.RadRef);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef2.Start, e.OrigArc.End);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.RadRef2.End, e.OffArc.End);
							ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, e.OrigArc.Center, e.RadRef2);
							break;
					}
				}

				foreach (EndRef[] pair in joinPlan)
				{
					IADSketchPoint p0 = OffPoint(pair[0]);
					IADSketchPoint p1 = OffPoint(pair[1]);
					if (p0 == null || p1 == null)
						continue;

					if (ch.Add(ADSketchConstraintType.AD_CONSTRAINT_COINCIDENT, p0, p1))
						joins++;
				}

				foreach (OffEdge e in edges)
				{
					if (e.Skip)
						continue;

					IADSketchLine driver = e.Kind == "Line" ? e.MidRef : e.RadRef;
					if (driver == null)
						continue;

					refTotal++;
					if (ReferenceEquals(driver, master))
						continue;

					ch.Add(ADSketchConstraintType.AD_CONSTRAINT_EQUAL, driver, master);
				}

				if (master != null)
				{
					try
					{
						placedDim = sketch.Dimensions.PlaceLinearDimension(master, null);
						dimensioned = placedDim != null;
						if (placedDim?.Parameter != null)
							placedDim.Parameter.Name = markerName;
					}
					catch (Exception exDim)
					{
						Debug.WriteLine("  dimension placement failed: " + exDim.Message);
					}
				}
			}
			catch (Exception ex)
			{
				hardError = ex.Message;
				Debug.WriteLine("  Edit error: " + ex.Message);
			}
			finally
			{
				try
				{
					sketch.EndChange();
				}
				catch (Exception exEnd)
				{
					hardError = (hardError == null ? "" : hardError + " | ") + "EndChange failed: " + exEnd.Message;
				}
			}

			if (hardError != null)
			{
				RollbackFigures(sketch, created, placedDim);
				result["Status"] = "Error";
				result["Message"] = $"Offset of '{sketch.Name}' failed and was rolled back: {hardError}";
				result["SketchName"] = sketch.Name;
				result["Detail"] = hardError;
				return result;
			}

			int liveCount = edges.FindAll(e => !e.Skip).Count;
			bool ok = ch.Failed == 0 && dimensioned && unjoined.Count == 0;

			result["Status"] = ok ? "Success" : "Warning";
			result["Message"] = ok
				? $"Offset '{sketch.Name}' by {d}: {liveCount} entities, {refTotal} driven reference lines, {ch.Added} constraints, {joins} corner joins."
				: $"Offset '{sketch.Name}' by {d} completed with notes: {ch.Failed} rejected constraint(s), {unjoined.Count} unjoined corner(s), dimensioned={dimensioned}.";
			result["SketchName"] = sketch.Name;
			result["OffsetDistance"] = d;
			result["EntitiesOffset"] = liveCount;
			result["DrivenReferenceLines"] = refTotal;
			result["ConstraintsAdded"] = ch.Added;
			result["ConstraintsFailed"] = ch.Failed;
			result["CornerJoins"] = joins;
			result["Dimensioned"] = dimensioned;
			result["SkippedFigures"] = skipped.Count;
			if (skipped.Count > 0)
				result["SkippedTypes"] = skipped;
			if (radiusErrors > 0)
				result["ArcsSkipped"] = radiusErrors;
			if (unjoined.Count > 0)
				result["UnjoinedCorners"] = unjoined;
			if (warnings.Count > 0)
				result["Warnings"] = warnings;
			result["IsClosed"] = sketch.IsClosed;
			result["TotalConstraints"] = sketch.SketchConstraints.Count;
			result["TotalDimensions"] = sketch.Dimensions.Count;
			return result;
		}
		catch (Exception ex)
		{
			result.Clear();
			result["Status"] = "Error";
			result["Message"] = ex.Message;
			result["Detail"] = ex.ToString();
			return result;
		}
	}

	private static Dictionary<string, object> Error(string message)
	{
		return new Dictionary<string, object>(StringComparer.Ordinal)
		{
			["Status"] = "Error",
			["Message"] = message
		};
	}

	private static IADSketch FindSketch(IADPartSession part, string name)
	{
		for (int i = 0; i < part.Sketches.Count; i++)
		{
			IADSketch s = part.Sketches.Item(i);
			if (string.Equals(s.Name, name, StringComparison.Ordinal))
				return s;
		}

		for (int i = 0; i < part.Sketches.Count; i++)
		{
			IADSketch s = part.Sketches.Item(i);
			if (string.Equals(s.Name, name, StringComparison.OrdinalIgnoreCase))
				return s;
		}

		return null;
	}

	private static string OffsetMarker(string sketchName)
	{
		System.Text.StringBuilder sb = new System.Text.StringBuilder("Offset_");
		foreach (char c in sketchName)
			sb.Append(char.IsLetterOrDigit(c) ? c : '_');

		return sb.ToString();
	}

	private static bool MarkerExists(IADSketch sketch, string markerName)
	{
		try
		{
			for (int i = 0; i < sketch.Dimensions.Count; i++)
			{
				IADParameter p = sketch.Dimensions.Item(i).Parameter;
				if (p != null && string.Equals(p.Name, markerName, StringComparison.Ordinal))
					return true;
			}
		}
		catch (Exception ex)
		{
			Debug.WriteLine("  MarkerExists check failed: " + ex.Message);
		}

		return false;
	}

	private static void RollbackFigures(IADSketch sketch, List<IADSketchFigure> created, IADDimension dimObj)
	{
		try
		{
			sketch.BeginChange();
			try
			{
				if (dimObj?.Parameter != null)
				{
					try { dimObj.Parameter.Remove(); }
					catch (Exception exP) { Debug.WriteLine("  Rollback dimension failed: " + exP.Message); }
				}

				for (int i = created.Count - 1; i >= 0; i--)
				{
					try { created[i]?.Delete(); }
					catch (Exception exF) { Debug.WriteLine("  Rollback figure delete failed: " + exF.Message); }
				}
			}
			finally
			{
				sketch.EndChange();
			}
		}
		catch (Exception ex)
		{
			Debug.WriteLine("  RollbackFigures failed: " + ex.Message);
		}
	}

	private static List<List<EndRef>> BuildGroups(List<EndRef> ends)
	{
		List<List<EndRef>> groups = new List<List<EndRef>>();
		bool[] used = new bool[ends.Count];

		for (int i = 0; i < ends.Count; i++)
		{
			if (used[i])
				continue;

			List<EndRef> group = new List<EndRef> { ends[i] };
			used[i] = true;

			for (int j = i + 1; j < ends.Count; j++)
			{
				if (used[j])
					continue;

				if (Math.Abs(ends[i].X - ends[j].X) <= VertexTol &&
					Math.Abs(ends[i].Y - ends[j].Y) <= VertexTol)
				{
					group.Add(ends[j]);
					used[j] = true;
				}
			}

			groups.Add(group);
		}

		return groups;
	}

	private static void MarkJoined(EndRef ep)
	{
		if (ep.WhichEnd == 1)
			ep.Edge.JoinedStart = true;
		else
			ep.Edge.JoinedEnd = true;
	}

	private static double OffX(EndRef ep) => ep.WhichEnd == 1 ? ep.Edge.OX1 : ep.Edge.OX2;
	private static double OffY(EndRef ep) => ep.WhichEnd == 1 ? ep.Edge.OY1 : ep.Edge.OY2;

	private static void SetOff(EndRef ep, double x, double y)
	{
		if (ep.WhichEnd == 1)
		{
			ep.Edge.OX1 = x;
			ep.Edge.OY1 = y;
		}
		else
		{
			ep.Edge.OX2 = x;
			ep.Edge.OY2 = y;
		}
	}

	private static IADSketchPoint OffPoint(EndRef ep) => ep.WhichEnd == 1 ? ep.Edge.OStartPt : ep.Edge.OEndPt;

	private static double ArcSignedAngle(IADSketchCircularArc arc)
	{
		double a = arc.IncludedAngle;
		try
		{
			if (!arc.IsRightHandRule)
				a = -a;
		}
		catch { }

		return a;
	}

	private static bool MiterIntersect(OffEdge a, OffEdge b, out double ix, out double iy)
	{
		ix = 0.0;
		iy = 0.0;

		double aux = a.X2 - a.X1;
		double auy = a.Y2 - a.Y1;
		double bux = b.X2 - b.X1;
		double buy = b.Y2 - b.Y1;
		double alen = Math.Sqrt(aux * aux + auy * auy);
		double blen = Math.Sqrt(bux * bux + buy * buy);

		if (alen <= VertexTol || blen <= VertexTol)
			return false;

		aux /= alen;
		auy /= alen;
		bux /= blen;
		buy /= blen;

		double denom = aux * buy - auy * bux;
		if (Math.Abs(denom) < 0.000001)
			return false;

		double a0x = a.OX1;
		double a0y = a.OY1;
		double b0x = b.OX1;
		double b0y = b.OY1;
		double wx = b0x - a0x;
		double wy = b0y - a0y;
		double t = (wx * buy - wy * bux) / denom;

		ix = a0x + t * aux;
		iy = a0y + t * auy;

		double miterLen = Math.Sqrt((ix - a0x) * (ix - a0x) + (iy - a0y) * (iy - a0y));
		return miterLen <= MiterFactor * Math.Max(alen, blen);
	}

	private static void AssignOutwardByWinding(List<OffEdge> edges, List<List<EndRef>> groups, List<string> warnings)
	{
		bool[] visited = new bool[edges.Count];
		bool openGeometry = false;

		for (int start = 0; start < edges.Count; start++)
		{
			if (visited[start])
				continue;

			if (edges[start].Kind == "Circle")
			{
				visited[start] = true;
				continue;
			}

			List<EndRef> path = new List<EndRef>();
			int cur = start;
			int enterEnd = 1;
			bool closed = false;
			bool broke = false;
			int guard = 0;

			while (true)
			{
				if (visited[cur])
				{
					closed = cur == start && path.Count > 0;
					break;
				}

				visited[cur] = true;
				OffEdge ce = edges[cur];
				path.Add(new EndRef { Edge = ce, WhichEnd = enterEnd });

				int exitGroup = enterEnd == 1 ? ce.GroupEnd : ce.GroupStart;
				if (exitGroup < 0)
				{
					broke = true;
					break;
				}

				EndRef nextEp = null;
				int degree = 0;
				foreach (EndRef ep in groups[exitGroup])
				{
					if (ep.Edge.Kind == "Circle")
						continue;

					degree++;
					if (!ReferenceEquals(ep.Edge, ce))
						nextEp = ep;
				}

				if (degree != 2 || nextEp == null)
				{
					broke = true;
					break;
				}

				enterEnd = nextEp.WhichEnd;
				cur = nextEp.Edge.Index;

				if (cur == start)
				{
					closed = true;
					break;
				}

				guard++;
				if (guard > edges.Count + 2)
				{
					broke = true;
					break;
				}
			}

			if (closed && !broke && path.Count >= 2)
			{
				double area = 0.0;
				for (int k = 0; k < path.Count; k++)
				{
					EndRef p = path[k];
					EndRef q = path[(k + 1) % path.Count];
					double px = p.WhichEnd == 1 ? p.Edge.X1 : p.Edge.X2;
					double py = p.WhichEnd == 1 ? p.Edge.Y1 : p.Edge.Y2;
					double qx = q.WhichEnd == 1 ? q.Edge.X1 : q.Edge.X2;
					double qy = q.WhichEnd == 1 ? q.Edge.Y1 : q.Edge.Y2;
					area += px * qy - qx * py;
				}

				bool ccw = area > 0.0;

				foreach (EndRef p in path)
				{
					OffEdge e = p.Edge;
					double sx = p.WhichEnd == 1 ? e.X1 : e.X2;
					double sy = p.WhichEnd == 1 ? e.Y1 : e.Y2;
					double ex = p.WhichEnd == 1 ? e.X2 : e.X1;
					double ey = p.WhichEnd == 1 ? e.Y2 : e.Y1;
					double ux = ex - sx;
					double uy = ey - sy;
					double len = Math.Sqrt(ux * ux + uy * uy);

					if (len <= VertexTol)
						continue;

					ux /= len;
					uy /= len;

					double nx;
					double ny;
					if (ccw)
					{
						nx = uy;
						ny = -ux;
					}
					else
					{
						nx = -uy;
						ny = ux;
					}

					if (e.Kind == "Line")
					{
						e.NX = nx;
						e.NY = ny;
						e.HasNormal = true;
					}
					else if (e.Kind == "Arc")
					{
						double signedAngle = ArcSignedAngle(e.OrigArc);
						double a0 = Math.Atan2(e.Y1 - e.CY, e.X1 - e.CX);
						double aMid = a0 + signedAngle / 2.0;
						double mrx = Math.Cos(aMid);
						double mry = Math.Sin(aMid);
						e.Grow = (mrx * nx + mry * ny) >= 0.0;
						e.HasNormal = true;
					}
				}
			}
			else
			{
				openGeometry = true;
			}
		}

		if (openGeometry)
			warnings.Add("Some geometry is not part of a clean closed loop; outward direction for those edges is a best-effort guess.");
	}

	private static void AssignCentroidNormal(OffEdge e, double cx, double cy, List<string> warnings)
	{
		double dx = e.X2 - e.X1;
		double dy = e.Y2 - e.Y1;
		double len = Math.Sqrt(dx * dx + dy * dy);

		if (len <= VertexTol)
		{
			e.NX = 0.0;
			e.NY = 0.0;
			e.HasNormal = true;
			return;
		}

		double ux = dx / len;
		double uy = dy / len;
		double n1x = uy;
		double n1y = -ux;
		double mx = (e.X1 + e.X2) / 2.0;
		double my = (e.Y1 + e.Y2) / 2.0;
		double dot = (mx - cx) * n1x + (my - cy) * n1y;

		if (Math.Abs(dot) > VertexTol)
		{
			if (dot >= 0.0)
			{
				e.NX = n1x;
				e.NY = n1y;
			}
			else
			{
				e.NX = -n1x;
				e.NY = -n1y;
			}
		}
		else
		{
			double eps = Math.Max(VertexTol, len * 0.001);
			double dA = Sq(mx + eps * n1x - cx) + Sq(my + eps * n1y - cy);
			double dB = Sq(mx - eps * n1x - cx) + Sq(my - eps * n1y - cy);

			if (dA >= dB)
			{
				e.NX = n1x;
				e.NY = n1y;
			}
			else
			{
				e.NX = -n1x;
				e.NY = -n1y;
			}

			warnings.Add("Ambiguous outward direction for an edge (centroid on edge line); offset side may be wrong.");
		}

		e.HasNormal = true;
	}

	private static void AssignArcGrowByCentroid(OffEdge e, double cx, double cy)
	{
		double signedAngle = ArcSignedAngle(e.OrigArc);
		double a0 = Math.Atan2(e.Y1 - e.CY, e.X1 - e.CX);
		double aMid = a0 + signedAngle / 2.0;
		double midx = e.CX + e.R * Math.Cos(aMid);
		double midy = e.CY + e.R * Math.Sin(aMid);
		double radOutX = midx - e.CX;
		double radOutY = midy - e.CY;
		double awayX = midx - cx;
		double awayY = midy - cy;

		e.Grow = (radOutX * awayX + radOutY * awayY) >= 0.0;
		e.HasNormal = true;
	}

	private static double Sq(double v) => v * v;

	private static void PrintResult(Dictionary<string, object> result)
	{
		foreach (KeyValuePair<string, object> item in result)
		{
			if (item.Value is System.Collections.IEnumerable enumerable && !(item.Value is string))
			{
				Console.WriteLine(item.Key + ":");
				foreach (object value in enumerable)
					Console.WriteLine("  - " + value);
			}
			else
			{
				Console.WriteLine(item.Key + ": " + item.Value);
			}
		}
	}

	private static bool StringEquals(Dictionary<string, object> dict, string key, string value)
	{
		return dict.TryGetValue(key, out object raw) &&
			   string.Equals(Convert.ToString(raw, CultureInfo.InvariantCulture), value, StringComparison.Ordinal);
	}

	private static object GetActiveObject(string progId, bool throwOnError = false)
	{
		if (progId == null)
			throw new ArgumentNullException(nameof(progId));

		int hr = CLSIDFromProgIDEx(progId, out Guid clsid);
		if (hr < 0)
		{
			if (throwOnError)
				Marshal.ThrowExceptionForHR(hr);

			return null;
		}

		hr = GetActiveObject(clsid, IntPtr.Zero, out object obj);
		if (hr < 0)
		{
			if (throwOnError)
				Marshal.ThrowExceptionForHR(hr);

			return null;
		}

		return obj;
	}

	[DllImport("ole32")]
	private static extern int CLSIDFromProgIDEx(
		[MarshalAs(UnmanagedType.LPWStr)] string lpszProgID,
		out Guid lpclsid);

	[DllImport("oleaut32")]
	private static extern int GetActiveObject(
		[MarshalAs(UnmanagedType.LPStruct)] Guid rclsid,
		IntPtr pvReserved,
		[MarshalAs(UnmanagedType.IUnknown)] out object ppunk);

	private sealed class OffEdge
	{
		public int Index;
		public string Kind;
		public IADSketchLine OrigLine;
		public IADSketchCircle OrigCircle;
		public IADSketchCircularArc OrigArc;

		public double X1;
		public double Y1;
		public double X2;
		public double Y2;

		public double OX1;
		public double OY1;
		public double OX2;
		public double OY2;

		public double NX;
		public double NY;
		public bool HasNormal;

		public double CX;
		public double CY;
		public double R;
		public double RNew;
		public bool Grow;
		public bool Skip;

		public int GroupStart = -1;
		public int GroupEnd = -1;
		public bool JoinedStart;
		public bool JoinedEnd;

		public IADSketchLine OffLine;
		public IADSketchCircle OffCircle;
		public IADSketchCircularArc OffArc;
		public IADSketchPoint OStartPt;
		public IADSketchPoint OEndPt;

		public IADSketchLine MidRef;
		public IADSketchLine RadRef;
		public IADSketchLine RadRef2;
		public IADSketchLine TieStart;
		public IADSketchLine TieEnd;
	}

	private sealed class EndRef
	{
		public OffEdge Edge;
		public int WhichEnd;
		public double X;
		public double Y;
		public int GroupId;
	}

	private sealed class ConstraintHelper
	{
		private readonly IADRoot root;
		private readonly IADSketch sketch;

		public int Added { get; private set; }
		public int Failed { get; private set; }

		public ConstraintHelper(IADRoot root, IADSketch sketch)
		{
			this.root = root ?? throw new ArgumentNullException(nameof(root));
			this.sketch = sketch ?? throw new ArgumentNullException(nameof(sketch));
		}

		public bool Add(ADSketchConstraintType constraintType, params object[] targets)
		{
			try
			{
				IObjectCollector collector = root.NewObjectCollector();
				foreach (object target in targets)
					collector.Add(target);

				if (sketch.SketchConstraints.AddConstraint(collector, constraintType))
				{
					Added++;
					return true;
				}

				Failed++;
				Debug.WriteLine($"  Constraint {constraintType} returned false");
				return false;
			}
			catch (Exception ex)
			{
				Failed++;
				Debug.WriteLine($"  Constraint {constraintType} threw: {ex.Message}");
				return false;
			}
		}
	}
}
