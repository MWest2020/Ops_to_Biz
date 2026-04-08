#!/usr/bin/env python3
"""Fetch installed app versions from Nextcloud pods via kubectl exec."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_APPS = ["opencatalogi", "openregister", "openconnector"]
_EMPTY = {app: "" for app in TARGET_APPS}


def _resolve_target(row: dict) -> tuple[str, str]:
    """Return (namespace, deployment) for a Business pivot row.

    Uses the actual ArgoCD destination namespace stored in the row.
    Two conventions:
    - Namespace is {org}-{env}  → deployment = "nextcloud"
    - Namespace is {org} only   → deployment = ArgoCD app name (e.g. beek-accept-nextcloud)
    """
    namespace = row.get("nextcloud_namespace", "")
    app_name = row.get("nextcloud_app_name", "")
    customer = row.get("customer_name", "")

    if not namespace:
        return customer, app_name or f"{customer}-nextcloud"

    # If namespace ends with a known env suffix → single deployment named "nextcloud"
    parts = namespace.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in {"prod", "accept", "acc", "staging", "dev", "test", "uat", "preprod"}:
        return namespace, "nextcloud"

    # Namespace is org-only → deployment is the full ArgoCD app name
    return namespace, app_name


def fetch_versions(row: dict) -> dict:
    """Return {app: version} for TARGET_APPS by execing into the Nextcloud pod.

    Returns empty strings for all apps on any failure.
    """
    namespace, deployment = _resolve_target(row)
    try:
        result = subprocess.run(
            [
                "kubectl", "exec",
                f"deploy/{deployment}",
                "-n", namespace,
                "-c", "nextcloud",
                "--",
                "su", "-s", "/bin/bash", "www-data",
                "-c", "php occ app:list --output json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"[versions] exec failed for {namespace}/{deployment}: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return dict(_EMPTY)

        data = json.loads(result.stdout)
        enabled = data.get("enabled", {})
        disabled = data.get("disabled", {})
        all_apps = {**enabled, **disabled}

        return {app: all_apps.get(app, "") for app in TARGET_APPS}

    except Exception as exc:
        print(f"[versions] error for {namespace}/{deployment}: {exc}", file=sys.stderr)
        return dict(_EMPTY)


def enrich_with_versions(rows: list[dict]) -> list[dict]:
    """Add version columns to Business pivot rows where nextcloud=True.

    Runs concurrently to minimise total sync time.
    """
    nextcloud_rows = [r for r in rows if r.get("nextcloud")]

    if not nextcloud_rows:
        for row in rows:
            row.update(_EMPTY)
        return rows

    results: dict[int, dict] = {}
    indices = {id(r): i for i, r in enumerate(rows)}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_versions, row): row for row in nextcloud_rows}
        for future in as_completed(futures):
            row = futures[future]
            idx = indices[id(row)]
            results[idx] = future.result()

    for i, row in enumerate(rows):
        row.update(results.get(i, dict(_EMPTY)))

    return rows
