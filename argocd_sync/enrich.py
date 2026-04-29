#!/usr/bin/env python3
"""Enrich ArgoCD rows with Nextcloud PVC usage data.

Reads JSON rows from <input>, adds 'nextcloud_storage_used' on rows that
represent a Nextcloud application (matched by app name), and writes the
result to <output>. Non-Nextcloud rows get an empty string.

Aborts with non-zero exit if the cluster lookup fails entirely, so a
broken kubeconfig does not silently overwrite existing values in the sheet.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storage import nextcloud_used_per_namespace

_NC_APP_EXCLUDE = (
    "mariadb", "redis", "postgres", "postgresql", "pgbouncer",
    "imaginary", "collabora", "onlyoffice", "elasticsearch",
)


def _is_nextcloud_app(name: str) -> bool:
    """Match the Nextcloud-app classification used elsewhere in the pipeline.

    New convention: nc-{customer}-{env}.
    Legacy:         {customer}-{env}-nextcloud (and not a sidecar).
    """
    if not name:
        return False
    if name.startswith("nc-"):
        return True
    n = name.lower()
    if "nextcloud" not in n:
        return False
    return not any(x in n for x in _NC_APP_EXCLUDE)


def main(in_path: str, out_path: str) -> None:
    with open(in_path) as f:
        rows = json.load(f)

    usage = nextcloud_used_per_namespace()
    if usage is None:
        print("[enrich] FATAL: storage lookup failed; aborting before write",
              file=sys.stderr)
        sys.exit(1)

    enriched = 0
    matched_app_no_data = 0
    for row in rows:
        if _is_nextcloud_app(row.get("name", "")):
            ns = row.get("namespace", "")
            value = usage.get(ns, "")
            row["nextcloud_storage_used"] = value
            if value:
                enriched += 1
            else:
                matched_app_no_data += 1
        else:
            row["nextcloud_storage_used"] = ""

    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"[enrich] Set nextcloud_storage_used on {enriched} row(s); "
          f"{matched_app_no_data} Nextcloud app(s) had no PVC data",
          file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: enrich.py <in.json> <out.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
