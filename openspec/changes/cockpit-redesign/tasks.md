## 1. Pre-migration

- [ ] 1.1 Manually clear the `Deployments` tab in Google Sheets (one-time, before first run with new code)
- [ ] 1.2 Confirm the known environment suffix list with the ops team (`prod`, `accept`, `acc`, `staging`, `dev`, `test`, `uat`)

## 2. Dependencies

- [x] 2.1 Create `requirements.txt` with pinned versions: `requests`, `openpyxl`
- [x] 2.2 Update `Dockerfile` to install from `requirements.txt` instead of bare `pip install`

## 3. Namespace Parsing

- [x] 3.1 Add `parse_namespace(namespace)` function in `fetch.py` returning `(customer_name, environment)` using the known suffix list
- [x] 3.2 Add `is_frontend` derivation in `extract_row`: `True` when `app-type=frontend`, else `False`
- [x] 3.3 Add `customer_name`, `environment`, `is_frontend` fields to the dict returned by `extract_row`

## 4. Composite Key Upsert

- [x] 4.1 Update `OWNED_COLUMNS` in `upsert.py` to include `customer_name`, `environment`, `is_frontend`, `removed_at`
- [x] 4.2 Change upsert index key from `row["name"]` to `f'{row["name"]}|{row["namespace"]}'`
- [x] 4.3 Write unit tests for composite key: same name different namespace → two rows; same name same namespace → update in place

## 5. Soft Delete

- [x] 5.1 Add soft-delete pass in `upsert.py`: after processing new rows, iterate remaining existing rows; if not matched by any new row, set `sync_status = [REMOVED]` and `removed_at = today UTC` (skip if already `[REMOVED]`)
- [x] 5.2 Add restore logic: if a matched row has `sync_status = [REMOVED]`, clear `sync_status` and `removed_at` before applying owned columns
- [x] 5.3 Write unit tests for soft-delete and restore scenarios

## 6. GWS Stale Rows Fix

- [x] 6.1 In `output/gws.py write_sheet`, add a `spreadsheets.values.clear` call on the full tab range before the `batchUpdate` write
- [x] 6.2 Verify the clear uses the same `TAB` constant and the spreadsheet ID

## 7. Kubernetes Config Split

- [x] 7.1 Create `k8s/configmap.yaml` with `OUTPUT_MODE` and `LOCAL_OUTPUT_PATH`
- [x] 7.2 Update `k8s/cronjob.yaml`: reference `configMapKeyRef` for those two env vars; remove them from `secretKeyRef`
- [x] 7.3 Update the `kubectl create secret` command in `README.md` to remove those two keys

## 8. Column Order

- [x] 8.1 Update `OWNED_COLUMNS` order to: `customer_name`, `environment`, `is_frontend`, `name`, `namespace`, `cluster`, `repo_url`, `target_revision`, `sync_status`, `health_status`, `last_synced`, `images`, `app_type`, `team`, `removed_at`
- [x] 8.2 Verify `output/local.py` and `output/gws.py` both pick up the updated column list automatically (they read `OWNED_COLUMNS` from `upsert.py`)

## 9. Documentation

- [x] 9.1 Update `README.md` environment variables table to reflect ConfigMap split
- [x] 9.2 Add namespace convention section to `README.md` (describes `{org}` / `{org}-{env}` pattern and known suffix list)
- [x] 9.3 Update upsert behaviour section to describe composite key, soft-delete, and column list
