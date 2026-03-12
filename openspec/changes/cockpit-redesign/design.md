## Context

`argocd-sheets-sync` pushes ArgoCD application state into a spreadsheet read daily by management and product owners. The sheet is their cockpit for reconciling customer subscriptions against live deployments. Two critical bugs make the current output unreliable: (1) the upsert key is `name` alone, so apps with the same name in different namespaces silently collide; (2) `gws.py` writes from A1 without clearing first, leaving stale rows from previous runs indefinitely.

Beyond the bugs, the sheet has no business context. Namespace follows a predictable convention (`{org}` or `{org}-{environment}`) that can be parsed deterministically to derive `customer_name` and `environment` — the two fields management actually needs. Apps that disappear from ArgoCD must be flagged as `[REMOVED]` rather than silently persisting with stale status.

## Goals / Non-Goals

**Goals:**
- Correct the composite key bug so each app is identified by `name|namespace`.
- Derive `customer_name`, `environment`, and `is_frontend` from existing ArgoCD metadata — no new labels required.
- Soft-delete removed apps with a `[REMOVED]` status and `removed_at` timestamp.
- Fix the GWS stale-rows bug by clearing the sheet range before writing.
- Separate non-secret config into a ConfigMap.
- Pin Python dependencies in `requirements.txt`.

**Non-Goals:**
- Subscription data integration (out of scope — manager adds manually to preserved columns).
- Multi-sheet or multi-tab support.
- Real-time / webhook-driven sync.
- Changing the sync schedule.

## Decisions

### D1 — Derive business fields from namespace, not new labels

**Decision:** Parse `customer_name` and `environment` from namespace at row-extraction time in `fetch.py`. Convention: `{org}` → customer=org, env=`-`; `{org}-{suffix}` where suffix is a known environment token (`prod`, `accept`, `acc`, `staging`, `dev`, `test`) → customer=org, env=suffix; otherwise treat the full namespace as customer with no env.

**Why:** Zero label-rollout cost. The convention is already in use and stable. Adding new required labels would require touching every ArgoCD application definition.

**Alternative considered:** Require an explicit `customer` label on every app. Rejected — operationally expensive, relies on human discipline, breaks existing apps until labels are added.

---

### D2 — Composite key `name|namespace`

**Decision:** The upsert identity key is the string `name|namespace`. This is stored as a virtual key (not a column) used only for index lookup.

**Why:** ArgoCD uniquely identifies an application by name within a namespace. Using just name causes silent collision when the same app name exists in `acme-prod` and `acme-accept`.

**Alternative considered:** `name|namespace|cluster` triple key. Rejected for now — the current deployment has one cluster; adding cluster complicates the key without benefit yet. Can be revisited.

---

### D3 — Soft-delete: overwrite `sync_status`, add `removed_at` column

**Decision:** When an app is present in the sheet but absent from the current ArgoCD fetch, set `sync_status = [REMOVED]` and write the current UTC date to `removed_at`. The row is never deleted.

**Why:** Managers need a visible audit trail. Silent deletion would break reconciliation — a subscription might still be active for a removed deployment.

**Alternative considered:** Delete the row outright. Rejected — loses history and breaks the reconciliation use-case.

---

### D4 — GWS write: clear then batchUpdate

**Decision:** Before writing, call `spreadsheets.values.clear` on the full tab range, then proceed with `batchUpdate`.

**Why:** `batchUpdate` only overwrites cells it addresses. Rows beyond the new data count are left untouched, accumulating stale records indefinitely.

**Alternative considered:** Compute the old row count and overwrite the exact old range. Fragile — requires tracking prior dimensions. Clear-then-write is simpler and idempotent.

---

### D5 — ConfigMap for non-secret config

**Decision:** `OUTPUT_MODE` and `LOCAL_OUTPUT_PATH` move to a new `k8s/configmap.yaml`. Only `ARGOCD_TOKEN`, `ARGOCD_URL`, `GOOGLE_SPREADSHEET_ID`, and `gws-credentials.json` remain in the Secret.

**Why:** Mixing config with secrets violates least-privilege and makes auditing harder. A ConfigMap is visible to operators without secret access.

## Risks / Trade-offs

- **[Risk] Re-keying existing sheet on first run** → Rows previously keyed on `name` alone will not match the new `name|namespace` composite key. All existing rows will appear as new and be appended, leaving the old rows in place. **Mitigation:** Document a one-time pre-migration step: clear the `Deployments` tab manually before the first run with the new code.

- **[Risk] Namespace parsing false positives** → An org named `acme-prod` (prod is the org name, not the env) would be misclassified. **Mitigation:** The known-environment-suffix list is explicit and short; edge cases can be added. Document the convention requirement.

- **[Risk] GWS clear + write is not atomic** → A crash between clear and write leaves an empty sheet. **Mitigation:** `backoffLimit: 1` in the CronJob provides one retry. Acceptable for a daily cockpit.

## Migration Plan

1. Manually clear the `Deployments` tab in Google Sheets before the first run.
2. Deploy the new ConfigMap (`k8s/configmap.yaml`).
3. Update the Secret to remove `OUTPUT_MODE` and `LOCAL_OUTPUT_PATH` keys.
4. Build and push the new image (pinned digest).
5. Apply updated `k8s/cronjob.yaml`.
6. Trigger a manual job run and verify row count and derived columns.

## Open Questions

- Which exact environment suffixes should be recognised? Proposed set: `prod`, `accept`, `acc`, `staging`, `dev`, `test`, `uat`. Confirm with ops team.
- Should `removed_at` be cleared if an app reappears after a removal? (Proposed: yes — clear `removed_at` and restore normal `sync_status`.)
