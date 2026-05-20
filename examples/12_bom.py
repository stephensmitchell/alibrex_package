"""Example 12 - read a Bill of Materials from a BOM table session."""
from __future__ import annotations

import sys

from alibrex import IADBOMTableSession, connect, run_example
def main() -> None:
    root = connect()

    bom_session: IADBOMTableSession | None = None
    for i in range(root.Sessions.Count):
        s = root.Sessions.Item(i)
        if isinstance(s, IADBOMTableSession):  # type: ignore[arg-type]
            bom_session = s  # type: ignore[assignment]
            break
    if bom_session is None:
        raise RuntimeError("No BOM table session open in Alibre.")

    n_cols = bom_session.ColumnCount
    n_rows = bom_session.RowCount
    print(f"BOM '{bom_session.Name}': {n_rows} rows x {n_cols} columns\n")

    # Columns() and Rows() return collections - they're methods on IADBOMTableSession.
    cols = bom_session.Columns(True)   # onlyVisibleOnes
    rows = bom_session.Rows(True)

    headers = [cols.Item(c).Name for c in range(cols.Count)]
    print(" | ".join(headers))
    print("-" * 80)
    for r in range(rows.Count):
        row = rows.Item(r)
        cells = [str(row.Value(c)) for c in range(cols.Count)]
        print(" | ".join(cells))


if __name__ == "__main__":
    sys.exit(run_example(main))
