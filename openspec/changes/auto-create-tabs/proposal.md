## Why

The sync fails with a 400 error if the target tab (`Deployments` or `Business`) does not exist. Operators must create tabs manually before the first run. This is error-prone and blocks k8s CronJob automation from being fully self-sufficient.

## What Changes

- Before clearing/writing any tab, check if it exists in the spreadsheet.
- If the tab is missing, create it via `gws sheets spreadsheets batchUpdate` with an `addSheet` request.
- Applies to both `output/gws.py` (Deployments tab) and `output/business_gws.py` (Business tab).

## Capabilities

### New Capabilities

- `tab-auto-create`: Ensure a named tab exists before writing, creating it if absent.

### Modified Capabilities

*(none)*

## Impact

- `output/gws.py`: add `ensure_tab_exists(tab_name)` call before clear+write.
- `output/business_gws.py`: same.
- No changes to fetch, upsert, transform, or k8s manifests.
