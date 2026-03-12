## Why

The full ArgoCD sync produces 190 rows with 15 columns of operational detail. Management and product owners only need to know: which customers have which products deployed, and in which environment. Everything else is noise for the cockpit view.

## What Changes

- A new `transform.py` module produces a pivoted business view from the raw fetched rows.
- Only three product types are tracked: `nextcloud`, `react` (covers `reactfront`), `tilburg-ui` (covers `tilburg-woo-ui`).
- Rows for infra/platform namespaces (no known product type in the app name) are excluded entirely.
- The output shape is one row per `customer + environment`, with boolean columns per product type.
- Environment is derived from the app name when the namespace does not carry an env suffix (e.g. namespace `acato`, app `acato-accept-nextcloud` → env `accept`).
- A new output mode `business` is added to `sync.sh`; the existing `local` and `gws` modes are unchanged.
- The business sheet tab is named `Business` (separate from the ops `Deployments` tab).

## Capabilities

### New Capabilities

- `app-name-parsing`: Extract customer, environment, and product type from the ArgoCD app name using the pattern `{customer}-{env}-{product}`.
- `business-pivot`: Aggregate filtered rows into one row per customer+environment with boolean product columns.

### Modified Capabilities

*(none)*

## Impact

- New file: `transform.py` — filter, classify, and pivot raw rows into the business view.
- `sync.sh`: add `business` case dispatching to `output/business.py`.
- New file: `output/business.py` — write the pivoted rows to xlsx or Google Sheets.
- No changes to `fetch.py`, `upsert.py`, `output/local.py`, `output/gws.py`.
