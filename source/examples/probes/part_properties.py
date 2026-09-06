"""Probe every readable property on the active part session.

Covers the headline objects hanging off an ``IADPartSession``:
``DesignProperties``, ``Parameters``, ``Configurations``, ``Bodies``,
``Sketches``, ``Sketches3D``, ``DesignPlanes``, ``DesignAxes``,
``DesignPoints``, plus the part itself.
"""
from __future__ import annotations

import sys

from alibrex import connect, require_active_part, run_example, probe_collection, probe_object

def main() -> None:
    root = connect()
    part = require_active_part(root)

    probe_object(part, "active part")
    probe_object(part.DesignProperties, "DesignProperties", skip={"VersionComment"})
    probe_collection(part.Parameters,      "Parameters",      limit=5)
    probe_collection(part.Configurations,  "Configurations",  limit=5)
    probe_collection(part.Bodies,          "Bodies",          limit=3)
    probe_collection(part.Sketches,        "Sketches",        limit=3)
    probe_collection(part.Sketches3D,      "Sketches3D",      limit=3)
    probe_collection(part.DesignPlanes,    "DesignPlanes",    limit=3)
    probe_collection(part.DesignAxes,      "DesignAxes",      limit=3)
    probe_collection(part.DesignPoints,    "DesignPoints",    limit=3)

if __name__ == "__main__":
    sys.exit(run_example(main))
