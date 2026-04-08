# Ops_to_Biz — Project Instructions

## What this repo is

Two independent Python subsystems in one repo:

| Subsystem | Path | Purpose |
|---|---|---|
| ArgoCD → Sheets sync | `argocd_sync/` | Daily sync of ArgoCD app data to Google Sheets or .xlsx |
| ISO Audit pipeline | `audit/` | Automated ISO 9001/27001 audit pipeline using GSuite + Miro |

All argocd-sync code lives under `argocd_sync/`.

---

## Running things

### ArgoCD sync

```bash
export OUTPUT_MODE=local   # or gws
./argocd_sync/sync.sh
```

### ISO Audit pipeline

```bash
pip install -r requirements.txt
python -m audit.pipeline --norm 9001     # or 27001 / beide
python -m audit.pipeline --setup-template  # first-time only
```

---

## Key conventions

### Namespace parsing (argocd_sync)

- Pattern `{org}` → customer=org, env=(empty)
- Pattern `{org}-{env}` → only if suffix is in: `prod, accept, acc, staging, dev, test, uat`
- Otherwise: full namespace = customer name, no env

### Upsert (argocd_sync)

- Composite key: `name + namespace`
- Owned columns are overwritten every run; extra/manual columns are preserved
- Soft-delete: removed apps get `sync_status=[REMOVED]` + `removed_at` date; never deleted

### Miro colour convention (audit)

| Colour | Meaning |
|---|---|
| Green | Positive / conform |
| Orange | NC (non-conformity) |
| Red | NC (non-conformity) |
| Other | No pre-classification |

---

## External integrations

- **Google Workspace** — service account with domain-wide delegation; scopes: Drive, Docs, Sheets, Slides, Gmail (optional), Calendar (optional)
- **Miro** — REST API token with `boards:read`
- **ArgoCD** — bearer token; read-only (`applications, get`)

Credentials are always in `.env` (never committed). See `.env.example`.

---

## Design workflow (OpenSpec)

Changes are tracked under `openspec/changes/`. Use the `/openspec-*` skills to explore, propose, apply, and archive changes. Specs live in `openspec/specs/`.

---

## Output artefacts

Outputs go under `output/` — this directory is gitignored. Do not commit `.xlsx`, `.db`, or report files.
