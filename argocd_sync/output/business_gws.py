#!/usr/bin/env python3
"""Write business pivot view to Google Sheets via the Sheets API.

Historical name kept for compatibility with BUSINESS_OUTPUT=gws and
sync.sh, but the implementation no longer shells out to the third-party
`gws` CLI — see sheets_client.py.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform import pivot, PRODUCT_COLUMNS
from versions import enrich_with_versions, TARGET_APPS
from sheets_client import (
    batch_update_values,
    clear_range,
    col_letter,
    ensure_tab,
)

SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
BUSINESS_TAB = "Business"
HEADERS = ["customer_name", "environment"] + PRODUCT_COLUMNS + ["nextcloud_storage_used"] + TARGET_APPS


def main(new_rows_path: str) -> None:
    with open(new_rows_path) as f:
        rows = json.load(f)

    result = enrich_with_versions(pivot(rows))

    ensure_tab(SPREADSHEET_ID, BUSINESS_TAB)
    clear_range(SPREADSHEET_ID, BUSINESS_TAB)

    values = [HEADERS]
    for row in result:
        values.append([str(row.get(h, "")) for h in HEADERS])

    num_rows = len(values)
    end_col = col_letter(len(HEADERS))
    sheet_range = f"{BUSINESS_TAB}!A1:{end_col}{num_rows}"

    batch_update_values(
        SPREADSHEET_ID,
        [{"range": sheet_range, "majorDimension": "ROWS", "values": values}],
    )
    print(f"[business/gws] Written {len(result)} rows to '{BUSINESS_TAB}' in {SPREADSHEET_ID}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: output/business_gws.py <new_rows.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
