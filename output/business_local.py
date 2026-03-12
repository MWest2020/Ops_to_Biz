#!/usr/bin/env python3
"""Write business pivot view to a local .xlsx file."""

import json
import os
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform import pivot, PRODUCT_COLUMNS
from versions import enrich_with_versions, TARGET_APPS

OUTPUT_PATH = os.environ.get("BUSINESS_OUTPUT_PATH", "argocd_business.xlsx")
HEADERS = ["customer_name", "environment"] + PRODUCT_COLUMNS + TARGET_APPS


def main(new_rows_path: str) -> None:
    with open(new_rows_path) as f:
        rows = json.load(f)

    result = enrich_with_versions(pivot(rows))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADERS)
    for row in result:
        ws.append([row.get(h, "") for h in HEADERS])
    wb.save(OUTPUT_PATH)
    print(f"[business/local] Written {len(result)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: output/business_local.py <new_rows.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
