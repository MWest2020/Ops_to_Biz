#!/usr/bin/env python3
"""Write business pivot view to Google Sheets via the gws CLI."""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform import pivot, PRODUCT_COLUMNS
from versions import enrich_with_versions, TARGET_APPS
from output.gws import _col_letter, _env, ensure_tab_exists

SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
BUSINESS_TAB = "Business"
HEADERS = ["customer_name", "environment"] + PRODUCT_COLUMNS + TARGET_APPS


def main(new_rows_path: str) -> None:
    with open(new_rows_path) as f:
        rows = json.load(f)

    result = enrich_with_versions(pivot(rows))

    ensure_tab_exists(SPREADSHEET_ID, BUSINESS_TAB, _env)
    # Clear before write to remove stale rows.
    subprocess.run(
        [
            "gws", "sheets", "spreadsheets", "values", "clear",
            "--params", json.dumps({
                "spreadsheetId": SPREADSHEET_ID,
                "range": BUSINESS_TAB,
            }),
        ],
        check=True,
        env=_env(),
    )

    values = [HEADERS]
    for row in result:
        values.append([str(row.get(h, "")) for h in HEADERS])

    num_rows = len(values)
    end_col = _col_letter(len(HEADERS))
    sheet_range = f"{BUSINESS_TAB}!A1:{end_col}{num_rows}"

    body = {
        "valueInputOption": "RAW",
        "data": [{"range": sheet_range, "majorDimension": "ROWS", "values": values}],
    }

    subprocess.run(
        [
            "gws", "sheets", "spreadsheets", "values", "batchUpdate",
            "--params", json.dumps({"spreadsheetId": SPREADSHEET_ID}),
            "--json", json.dumps(body),
        ],
        check=True,
        env=_env(),
    )
    print(f"[business/gws] Written {len(result)} rows to '{BUSINESS_TAB}' in {SPREADSHEET_ID}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: output/business_gws.py <new_rows.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
