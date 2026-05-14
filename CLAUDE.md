# Ops_to_Biz — Project Instructions

## What this repo is

Eén actief Python subsysteem in deze repo:

| Subsystem | Path | Purpose |
|---|---|---|
| ArgoCD → Sheets sync | `argocd_sync/` | Daily sync of ArgoCD app data to Google Sheets or .xlsx |

All argocd-sync code lives under `argocd_sync/`.

### Verhuisd: ISO Audit pipeline

> **`audit/` is DEPRECATED** (per milestone B van `openspec/changes/iso-refactor/`,
> afgerond 2026-05-14). De actuele code leeft in
> [`MWest2020/iso-audit`](https://github.com/MWest2020/iso-audit) onder
> de `refactor/iso-audit-milestone-b`-branch. Gebruik die repo voor alle
> nieuwe werk; deze `audit/`-directory wordt niet meer bijgewerkt.

> **Niet geraakt door de refactor:** `output/business_gws.py` en
> `output/gws.py` blijven hier — die zijn onderdeel van het
> handbook/output-pad, niet van de audit-pipeline.

---

## Running things

### ArgoCD sync

```bash
export OUTPUT_MODE=local   # or gws
./argocd_sync/sync.sh
```

### ISO Audit pipeline

Verhuisd naar [`MWest2020/iso-audit`](https://github.com/MWest2020/iso-audit).
Gebruik dat project:

```bash
# In iso-audit repo:
uv sync
uv run iso-audit pipeline --source drive --norm 9001
uv run iso-audit setup-template  # first-time only
uv run iso-audit doctor          # environment check
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
