# Ops_to_Biz — Project Instructions

## What this repo is

Eén actief Python subsysteem:

| Subsystem | Path | Purpose |
|---|---|---|
| ArgoCD → Sheets sync | `argocd_sync/` | Daily sync van ArgoCD app-data naar Google Sheets of `.xlsx` |

Inclusief de pivot-tabbladen "Deployments" (ops view) en "Business"
(klant × product × env cockpit voor management).

### Historie: ISO Audit pipeline verhuisd

De ISO 9001/27001 audit-pipeline (voorheen `audit/`) is per
milestone B van het `iso-refactor` change-proposal verhuisd naar
[`MWest2020/iso-audit`](https://github.com/MWest2020/iso-audit).
De code is uit dit repo verwijderd op 2026-05-19; de OpenSpec-design
ligt in `openspec/changes/archive/iso-refactor/`. Voor alle audit-
gerelateerd werk: gebruik de `iso-audit` repo.

---

## Running

```bash
# Lokaal — schrijft .xlsx naar LOCAL_OUTPUT_PATH
export OUTPUT_MODE=local
./argocd_sync/sync.sh

# Productie — schrijft naar Google Sheets via gws CLI
export OUTPUT_MODE=gws
./argocd_sync/sync.sh

# Optionele business-view (extra tab/file naast de hoofd-output)
export BUSINESS_OUTPUT=gws   # of local
```

De pipeline draait dagelijks via `argocd_sync/k8s/cronjob.yaml`
(production, in-cluster) of via een systemd-timer op de laptop
zolang k8s-auth (zie `openspec/changes/k8s-cronjob-auth/`) niet
is gemigreerd.

---

## Key conventions

### Namespace parsing

- Pattern `{org}` → customer = org, env = (empty)
- Pattern `{org}-{env}` → alleen als suffix in
  `prod, accept, acc, staging, dev, test, uat`
- Anders: hele namespace = customer name, geen env

### Upsert

- Composite key: `name + namespace`
- Owned-columns worden elke run overschreven; manuele kolommen blijven
- Soft-delete: verwijderde apps krijgen `sync_status=[REMOVED]` +
  `removed_at` datum; rij wordt nooit gewist

### Business view

Tweede sheet/file met klant × product × env pivot. Product-detectie
op app-name pattern (`nextcloud`, `react`, `tilburg`). `[REMOVED]`
apps worden uitgesloten. Zie `argocd_sync/output/business_*.py`.

---

## External integrations

- **ArgoCD** — bearer token; read-only (`applications, get`)
- **Google Sheets** — via `gws` CLI (`OUTPUT_MODE=gws`); service-
  account JSON via `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`
- **Kubernetes** (optioneel) — `kubectl exec` voor Nextcloud
  storage-enrichment; `KUBECONFIG` of in-cluster service-account

Credentials staan in `.env` (nooit gecommit). Zie `.env.example`.

---

## Design workflow (OpenSpec)

Changes onder `openspec/changes/`. Capability-specs onder
`openspec/specs/`. Gebruik de `/openspec-*` skills om changes te
verkennen, voorstellen, toepassen en archiveren.

Open changes (2026-05-19):

- `auto-create-tabs` — Sheets-tabs auto-aanmaken bij sync
- `business-view-filter` — gefilterde cockpit-tab voor management
- `cockpit-redesign` — subscription ↔ deployment reconciliatie
- `k8s-cronjob-auth` — gws-creds in k8s Secret zodat CronJob in-cluster draait
- `nextcloud-app-versions` — app-versies per klant in cockpit
- `systemd-laptop-timer` — interim laptop-timer tot k8s-auth gefixed is

Gearchiveerd: `iso-refactor` (audit-verhuizing naar standalone repo).

---

## Output artefacten

Output gaat onder `output/` — die directory is gitignored. Commit
geen `.xlsx`, `.db`, of rapport-bestanden.
