#!/usr/bin/env python3
"""Transform raw ArgoCD rows into a pivoted business view.

Business view: one row per (customer, environment) with boolean columns
for each known product type (nextcloud, react, tilburg-ui).
"""

_ENV_TOKENS = {"prod", "accept", "acc", "staging", "dev", "test", "uat", "preprod"}

# Substring → canonical product type. Checked in order; first match wins.
_PRODUCT_MAP = [
    ("nextcloud", "nextcloud"),
    ("react", "react"),       # matches react, reactfront
    ("tilburg", "tilburg-ui"), # matches tilburg-ui, tilburg-woo-ui
]

PRODUCT_COLUMNS = ["nextcloud", "react", "tilburg-ui"]


def classify(app_name: str) -> str | None:
    """Return canonical product type for app_name, or None if not a business app.

    New convention: nc-{customer}-{env} → nextcloud (checked first).
    Legacy convention: {customer}-{env}-{product} → matched by substring.
    """
    if app_name.startswith("nc-"):
        return "nextcloud"
    for substring, canonical in _PRODUCT_MAP:
        if substring in app_name:
            return canonical
    return None


def parse_app_name(app_name: str, fallback_customer: str = "") -> tuple[str, str]:
    """Return (customer, environment) by scanning app name segments for env token.

    Supports two naming conventions:
    - Legacy:  {customer}-{env}-{product}   e.g. acato-accept-nextcloud → (acato, accept)
    - New:     nc-{customer}-{env}          e.g. nc-epe-accept → (epe, accept)

    The nc- prefix is stripped before scanning so it is never mistaken for the customer.
    First env token found wins.
    Falls back to (fallback_customer, "") if no env token found.
    """
    name = app_name[3:] if app_name.startswith("nc-") else app_name
    segments = name.split("-")
    for i, segment in enumerate(segments):
        if segment in _ENV_TOKENS:
            customer = "-".join(segments[:i]) or fallback_customer
            return customer, segment
    return fallback_customer, ""


def pivot(rows: list[dict]) -> list[dict]:
    """Filter, classify and pivot raw rows into one row per (customer, environment).

    - Excludes [REMOVED] apps.
    - Excludes apps not matching a known product type.
    - Returns rows sorted by customer_name asc, environment asc.
    """
    grouped: dict[tuple[str, str], dict[str, bool]] = {}

    # Track the nextcloud app name per (customer, environment) for exec resolution.
    nextcloud_app_names: dict[tuple[str, str], str] = {}

    for row in rows:
        if row.get("sync_status") == "[REMOVED]":
            continue

        product = classify(row.get("name", ""))
        if product is None:
            continue

        customer, environment = parse_app_name(
            row.get("name", ""),
            fallback_customer=row.get("customer_name", ""),
        )
        if not customer:
            continue

        if not environment:
            continue

        key = (customer, environment)
        if key not in grouped:
            grouped[key] = {col: False for col in PRODUCT_COLUMNS}
        grouped[key][product] = True

        if product == "nextcloud":
            nextcloud_app_names[key] = (row.get("name", ""), row.get("namespace", ""))

    result = [
        {
            "customer_name": customer,
            "environment": environment,
            "nextcloud_app_name": nextcloud_app_names.get((customer, environment), ("", ""))[0],
            "nextcloud_namespace": nextcloud_app_names.get((customer, environment), ("", ""))[1],
            **products,
        }
        for (customer, environment), products in grouped.items()
    ]

    return sorted(result, key=lambda r: (r["customer_name"], r["environment"]))
