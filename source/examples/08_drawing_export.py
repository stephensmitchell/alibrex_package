"""Example 08: export the active drawing to PDF, DWG, DXF, and BOM."""
from __future__ import annotations

import sys
from pathlib import Path
from alibrex import connect, run_example, require_active_drawing
def main() -> None:
    out_dir = Path.cwd() / "exports"
    out_dir.mkdir(exist_ok=True)

    root = connect()
    drawing = require_active_drawing(root)

    base = drawing.Name.replace(" ", "_")
    pdf  = str(out_dir / f"{base}.pdf")
    dwg  = str(out_dir / f"{base}.dwg")
    dxf  = str(out_dir / f"{base}.dxf")
    bom  = str(out_dir / f"{base}_BOM.csv")

    print(f"Exporting drawing '{drawing.Name}' to:")
    drawing.ExportPDF(pdf, False); print(f"  PDF: {pdf}")
    drawing.ExportDWG(dwg);        print(f"  DWG: {dwg}")
    drawing.ExportDXF(dxf);        print(f"  DXF: {dxf}")
    drawing.ExportBOM(bom);        print(f"  BOM: {bom}")
    print(f"\nSheets: {drawing.Sheets.Count}")

if __name__ == "__main__":
    sys.exit(run_example(main))
