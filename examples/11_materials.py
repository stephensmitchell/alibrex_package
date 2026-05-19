"""Example 11 — assign a material to the active part.

Browses installed material libraries and applies the first material whose
name contains 'Steel'.
"""
from __future__ import annotations

import sys

from alibrex import ADMaterialPropertyKey, connect, run_example, require_active_part
def _active_or_new_part(root):
    try:
        return require_active_part(root)
    except RuntimeError:
        return root.CreateEmptyPart("Materials_Demo", False)


def main() -> None:
    root = connect()
    part = _active_or_new_part(root)
    libs = root.MaterialLibraries

    target = None
    for li in range(libs.Count):
        lib = libs.Item(li)
        for mi in range(lib.Materials.Count):
            mat = lib.Materials.Item(mi)
            if "steel" in mat.Name.lower():
                target = mat
                break
        if target:
            break

    if target is None:
        raise RuntimeError("No 'Steel' material found in any library.")

    print(f"Applying material: {target.Name}")
    print(f"  density   : {target.Density:.2f} g/cm^3")
    print(f"  modulus E : {target.getMaterialPropertyValue(ADMaterialPropertyKey.MODULUS_OF_ELASTICITY_PROPERTY):.2e}")
    # Material lives on DesignProperties as a string (the material name).
    part.DesignProperties.Material = target.Name


if __name__ == "__main__":
    sys.exit(run_example(main))
