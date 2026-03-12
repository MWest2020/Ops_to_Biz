#!/usr/bin/env python3
"""Upsert logic: merge new ArgoCD rows into existing sheet rows.

Owned columns are updated on match; all other columns on existing rows are
left untouched.  New rows are appended.  Key field: 'name|namespace'.
Removed apps (present in sheet, absent from new rows) are soft-deleted.
"""

import json
import sys
from datetime import datetime, timezone

OWNED_COLUMNS: list[str] = [
    "customer_name",
    "environment",
    "is_frontend",
    "name",
    "namespace",
    "cluster",
    "repo_url",
    "target_revision",
    "sync_status",
    "health_status",
    "last_synced",
    "images",
    "app_type",
    "team",
    "removed_at",
]

_REMOVED_STATUS = "[REMOVED]"


def _key(row: dict) -> str:
    return f'{row.get("name", "")}|{row.get("namespace", "")}'


def upsert(current_rows: list[dict], new_rows: list[dict]) -> list[dict]:
    index: dict[str, int] = {_key(row): i for i, row in enumerate(current_rows)}
    matched: set[str] = set()
    result = list(current_rows)

    for new_row in new_rows:
        key = _key(new_row)
        if key in index:
            existing = dict(result[index[key]])
            # Restore a previously removed app
            if existing.get("sync_status") == _REMOVED_STATUS:
                existing["removed_at"] = ""
            for col in OWNED_COLUMNS:
                if col in new_row:
                    existing[col] = new_row[col]
            result[index[key]] = existing
        else:
            result.append(new_row)
        matched.add(key)

    # Soft-delete: mark rows absent from the new fetch
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for i, row in enumerate(result):
        if _key(row) not in matched and row.get("sync_status") != _REMOVED_STATUS:
            result[i] = dict(row)
            result[i]["sync_status"] = _REMOVED_STATUS
            result[i]["removed_at"] = today

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: upsert.py <current.json> <new.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        current = json.load(f)
    with open(sys.argv[2]) as f:
        new = json.load(f)

    print(json.dumps(upsert(current, new), indent=2))
