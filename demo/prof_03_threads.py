"""Profile demo 03: sketch four thread-tooth cross-sections.

Drops four thread teeth (UN/metric, ACME, square, buttress) into a
single sketch, side by side along X. No extrusion. The tooth-profile
shapes let you confirm the geometry by eye in Alibre. Use as a
reference when authoring sweep paths for actual threading.

Pass criteria:
  - Sketch contains the expected number of figures (3 + 4 + 6 + 4 = 17
    line segments across the four teeth).
  - The sketch is on the active part.
"""
from __future__ import annotations

import sys
import uuid

from _demo_utils import fresh_part, report
from alibrex import run_example
from profiles import mm
from profiles import threads


def main() -> int:
    tag = uuid.uuid4().hex[:6]
    part = fresh_part(f"ThreadProfiles_{tag}")
    sk = part.Sketches.AddSketch(None, part.DesignPlanes.Item(0), "ThreadTeeth")

    P = mm(3.0)            # 3 mm pitch
    GAP = mm(2.0)           # 2 mm visual gap between teeth

    sk.BeginChange()
    try:
        # Lay the four teeth out along X, separated by GAP.
        x = 0.0
        threads.un_metric(sk,      P=P, cx=x);   x += P + GAP
        threads.acme(sk,           P=P, cx=x);   x += P + GAP
        threads.square_thread(sk,  P=P, cx=x);   x += P + GAP
        threads.buttress(sk,       P=P, cx=x)
    finally:
        sk.EndChange()

    n_figs = sk.Figures.Count
    # un_metric: 3 lines, acme: 4 lines, square: 6 lines, buttress: 4 lines
    expected = 3 + 4 + 6 + 4
    print(f"Figures in sketch: {n_figs}  (expected {expected})")

    return report([
        ("expected figure count",  n_figs == expected),
        ("sketch attached to part", part.Sketches.Count >= 1),
    ])


if __name__ == "__main__":
    sys.exit(run_example(main))
