## Why

Management and product owners need a single cockpit view to verify that customer subscriptions reconcile with live ArgoCD deployments. The current sync produces raw ops data with a broken deduplication key, stale rows after a write, and no business context — making the sheet unreliable and unreadable for non-technical stakeholders.

## What Changes

- **BREAKING** — Upsert key changes from `name` to `name|namespace`; existing rows without this composite key will be re-keyed on first run.
- Namespace is parsed to derive `customer_name` and `environment` (`acme-prod` → customer=`acme`, env=`prod`; `acme` → customer=`acme`, env=`-`).
- `is_frontend` boolean column derived from the `app-type` label.
- Apps removed from ArgoCD are soft-deleted: `sync_status` is set to `[REMOVED]` and a `removed_at` timestamp is written; the row is never deleted.
- `gws.py` write is preceded by a range clear to eliminate stale rows from previous runs.
- Non-secret config (`OUTPUT_MODE`, `LOCAL_OUTPUT_PATH`) moved from Secret to a ConfigMap.
- `requirements.txt` added with pinned dependency versions.

## Capabilities

### New Capabilities

- `namespace-parsing`: Derive `customer_name` and `environment` from namespace using the `{org}` / `{org}-{env}` convention.
- `soft-delete`: Track apps removed from ArgoCD with a `[REMOVED]` status and `removed_at` date rather than dropping the row.
- `composite-key-upsert`: Upsert logic keyed on `name|namespace` to correctly handle same-named apps in different namespaces or clusters.

### Modified Capabilities

*(none — no existing specs)*

## Impact

- `fetch.py`: No changes to fetch logic; row extraction adds derived fields.
- `upsert.py`: Key logic changes; owned columns list updated; soft-delete handling added.
- `output/gws.py`: Clear range before batchUpdate write.
- `output/local.py`: Column list updated to include new business columns.
- `k8s/cronjob.yaml` + new `k8s/configmap.yaml`: Non-secret env vars moved to ConfigMap.
- New `requirements.txt`: pins `requests`, `openpyxl`.
