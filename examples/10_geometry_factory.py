"""Example 10: points, vectors, and transformations.

IADGeometryFactory is the canonical builder for math primitives. The
factory is reached through the active part session.
"""
from __future__ import annotations

import math
import sys

from alibrex import connect, run_example, require_active_part
def main() -> None:
    root = connect()
    part = require_active_part(root)
    gf = part.GeometryFactory

    # 3-D point and vector
    p = gf.CreatePoint(1.0, 2.0, 3.0)
    v = gf.CreateVector(0.0, 0.0, 1.0)
    print(f"Point: ({p.X}, {p.Y}, {p.Z})")
    print(f"Vector: <{v.X}, {v.Y}, {v.Z}>  |v|={v.Length}")

    # Identity, translation, rotation, scale
    ident = gf.CreateIdentityTransform()
    trans = gf.CreateTranslationTransformByXYZ(10.0, 0.0, 0.0)
    rot   = gf.CreateRotationTransform(v, p, math.radians(90.0))
    scale = gf.CreateUniformScalingTransform(2.0)

    for name, t in [("identity", ident), ("translate", trans),
                    ("rotate90Z", rot), ("scale2x", scale)]:
        # Transformation exposes a 4x4 matrix via decomposition helpers
        print(f"  {name}: {type(t).__name__}")


if __name__ == "__main__":
    sys.exit(run_example(main))
