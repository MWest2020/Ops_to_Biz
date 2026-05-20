#!/usr/bin/env python3
"""Write merged ArgoCD rows to Google Sheets via the Sheets API.

Historical name kept for compatibility with OUTPUT_MODE=gws and sync.sh,
but the implementation no longer shells out to the third-party `gws`
CLI — see sheets_client.py.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from upsert import OWNED_COLUMNS, upsert
from sheets_client import (
    batch_update_values,
    clear_range,
    col_letter,
    ensure_tab,
    get_values,
)

SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
TAB = "Deployments"


def read_sheet() -> tuple[list[str], list[dict]]:
    values = get_values(SPREADSHEET_ID, TAB)
    if not values:
        return [], []
    headers = [str(h) for h in values[0]]
    rows = [dict(zip(headers, row)) for row in values[1:]]
    return headers, rows


def write_sheet(headers: list[str], rows: list[dict]) -> None:
    ensure_tab(SPREADSHEET_ID, TAB)
    # Clear the full tab first so removed rows don't linger when the row
    # count decreases between runs.
    clear_range(SPREADSHEET_ID, TAB)

    values = [headers]
    for row in rows:
        values.append([("" if row.get(h) is None else str(row.get(h))) for h in headers])

    num_rows = len(values)
    num_cols = len(headers)
    end_col = col_letter(num_cols)
    sheet_range = f"{TAB}!A1:{end_col}{num_rows}"

    batch_update_values(
        SPREADSHEET_ID,
        [{"range": sheet_range, "majorDimension": "ROWS", "values": values}],
    )


def main(new_rows_path: str) -> None:
    with open(new_rows_path) as f:
        new_rows = json.load(f)

    existing_headers, current_rows = read_sheet()

    all_headers = list(OWNED_COLUMNS)
    for h in existing_headers:
        if h not in all_headers:
            all_headers.append(h)

    merged = upsert(current_rows, new_rows)
    write_sheet(all_headers, merged)
    print(f"[gws] Written {len(merged)} rows to '{TAB}' in spreadsheet {SPREADSHEET_ID}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: output/gws.py <new_rows.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
