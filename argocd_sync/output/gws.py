#!/usr/bin/env python3
"""Write merged ArgoCD rows to Google Sheets via the gws CLI."""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from upsert import OWNED_COLUMNS, upsert

SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
CREDS_FILE = os.environ.get("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE")
TAB = "Deployments"


def _env() -> dict:
    env = os.environ.copy()
    if CREDS_FILE:
        env["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] = CREDS_FILE
    return env


def read_sheet() -> tuple[list[str], list[dict]]:
    result = subprocess.run(
        [
            "gws", "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({
                "spreadsheetId": SPREADSHEET_ID,
                "range": TAB,
            }),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=_env(),
    )
    values = json.loads(result.stdout).get("values", [])
    if not values:
        return [], []

    headers = [str(h) for h in values[0]]
    rows = [dict(zip(headers, row)) for row in values[1:]]
    return headers, rows


def ensure_tab_exists(spreadsheet_id: str, tab_name: str, env_fn) -> None:
    """Create tab_name if it does not already exist in the spreadsheet."""
    result = subprocess.run(
        [
            "gws", "sheets", "spreadsheets", "get",
            "--params", json.dumps({
                "spreadsheetId": spreadsheet_id,
                "fields": "sheets.properties.title",
            }),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env_fn(),
    )
    titles = [
        s["properties"]["title"]
        for s in json.loads(result.stdout).get("sheets", [])
    ]
    if tab_name not in titles:
        body = {"requests": [{"addSheet": {"properties": {"title": tab_name}}}]}
        subprocess.run(
            [
                "gws", "sheets", "spreadsheets", "batchUpdate",
                "--params", json.dumps({"spreadsheetId": spreadsheet_id}),
                "--json", json.dumps(body),
            ],
            check=True,
            env=env_fn(),
        )
        print(f"[gws] Created tab '{tab_name}'")


def write_sheet(headers: list[str], rows: list[dict]) -> None:
    ensure_tab_exists(SPREADSHEET_ID, TAB, _env)
    # Clear the full tab first to prevent stale rows from persisting when
    # the row count decreases between runs.
    subprocess.run(
        [
            "gws", "sheets", "spreadsheets", "values", "clear",
            "--params", json.dumps({
                "spreadsheetId": SPREADSHEET_ID,
                "range": TAB,
            }),
        ],
        check=True,
        env=_env(),
    )

    values = [headers]
    for row in rows:
        values.append([("" if row.get(h) is None else str(row.get(h))) for h in headers])

    # Compute explicit range so Sheets knows how many rows to write.
    num_rows = len(values)
    num_cols = len(headers)
    end_col = _col_letter(num_cols)
    sheet_range = f"{TAB}!A1:{end_col}{num_rows}"

    body = {
        "valueInputOption": "RAW",
        "data": [
            {
                "range": sheet_range,
                "majorDimension": "ROWS",
                "values": values,
            }
        ],
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


def _col_letter(n: int) -> str:
    """Convert 1-based column number to A1 letter (e.g. 27 → AA)."""
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


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
