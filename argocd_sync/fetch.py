#!/usr/bin/env python3
"""Fetch ArgoCD application data and emit a deduplicated JSON array to stdout."""

import json
import os
import sys
from collections import OrderedDict

import requests

ARGOCD_URL = os.environ["ARGOCD_URL"].rstrip("/")
ARGOCD_TOKEN = os.environ["ARGOCD_TOKEN"]
SELECTORS = [
    s.strip()
    for s in os.environ.get("ARGOCD_LABEL_SELECTORS", "").split(",")
    if s.strip()
]

_HEADERS = {"Authorization": f"Bearer {ARGOCD_TOKEN}"}

_ENV_SUFFIXES = {"prod", "accept", "acc", "staging", "dev", "test", "uat"}


def parse_namespace(namespace: str) -> tuple[str, str]:
    """Return (customer_name, environment) by parsing the namespace convention.

    Convention: ``{org}`` or ``{org}-{env}`` where env is a known suffix token.
    Examples:
        "acme"         → ("acme", "")
        "acme-prod"    → ("acme", "prod")
        "big-corp-dev" → ("big-corp", "dev")
        "acme-internal"→ ("acme-internal", "")  # 'internal' not a known suffix
    """
    parts = namespace.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in _ENV_SUFFIXES:
        return parts[0], parts[1]
    return namespace, ""


def fetch_apps(selector: str) -> list[dict]:
    params = {"selector": selector} if selector else {}
    resp = requests.get(
        f"{ARGOCD_URL}/api/v1/applications",
        headers=_HEADERS,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("items", [])


def extract_row(app: dict) -> dict:
    meta = app.get("metadata", {})
    spec = app.get("spec", {})
    status = app.get("status", {})
    source = spec.get("source", {})
    dest = spec.get("destination", {})
    sync = status.get("sync", {})
    health = status.get("health", {})
    op_state = status.get("operationState", {})
    labels = meta.get("labels", {})

    images = status.get("summary", {}).get("images", [])
    last_synced = op_state.get("finishedAt") or status.get("reconciledAt", "")
    namespace = dest.get("namespace", "")
    customer_name, environment = parse_namespace(namespace)
    is_frontend = labels.get("app-type", "") == "frontend"

    return {
        "customer_name": customer_name,
        "environment": environment,
        "is_frontend": is_frontend,
        "name": meta.get("name", ""),
        "namespace": namespace,
        "cluster": dest.get("server") or dest.get("name", ""),
        "repo_url": source.get("repoURL", ""),
        "target_revision": source.get("targetRevision", ""),
        "sync_status": sync.get("status", ""),
        "health_status": health.get("status", ""),
        "last_synced": last_synced,
        "images": ", ".join(images),
        "app_type": labels.get("app-type", ""),
        "team": labels.get("team", ""),
        "removed_at": "",
    }


def main() -> None:
    seen: OrderedDict[str, dict] = OrderedDict()

    targets = SELECTORS if SELECTORS else [""]
    for selector in targets:
        for app in fetch_apps(selector):
            row = extract_row(app)
            if row["name"] not in seen:
                seen[row["name"]] = row

    print(json.dumps(list(seen.values()), indent=2))


if __name__ == "__main__":
    main()
