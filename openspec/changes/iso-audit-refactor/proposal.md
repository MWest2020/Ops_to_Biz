## Why

Twee triggers vallen samen die onafhankelijk al groot genoeg waren:

1. **Repo-splitsing.** `audit/` is volledig self-contained binnen `Ops_to_Biz` (geverifieerd: geen imports vanuit `argocd_sync/`, geen reverse imports). De ISO 27001-context van het tool zelf vraagt om eigen CI, eigen versie-beheer en eigen audit-trail — niet gemengd met onverwante ops-scripts.
2. **Bron-pluggability.** De huidige architectuur is hard gekoppeld aan Google Drive (`drive_ingest.py`, `gws_client.py`, `planning_ingest.py`). Jira komt in juni als tweede source; daarna MCP en REST. Als we Jira als tweede uitzondering bouwen, bouwen we MCP als derde uitzondering, en is over zes maanden de consolidatie-winst weg. **De source-adapter laag moet er vóór Jira staan, niet erna.**

Drie afgeleide opportunities raken hetzelfde codepad en gaan daarom mee in deze refactor:

3. **Miro-consolidatie.** Drie Miro-clients in vier locaties, elk met eigen `_headers()`, `_post()`, rate-limit handling. Eén gedeelde sub-package, drie consumers eromheen.
4. **Dubbele finding_classification.** `finding_classification.py` (414 regels) en `finding_classification_20260420.py` (750 regels). Tweede is nieuwer; refactor is moment om te kiezen en te schrappen.
5. **Modes-architectuur.** Greenfield werk; `autonoom` (end-to-end zelfstandig) en `integer` (mens-in-de-lus op kritieke beslismomenten). Blokker voor juni-run, dus moet hier ontworpen.

## What Changes

- **Nieuwe repo `iso-audit`** (kebab-case repo, snake-case package `iso_audit`); fresh git-history; Python `>=3.12`.
- **Source-protocol** (`src/iso_audit/sources/base.py`) met `Source` Protocol + `Document` / `Finding` dataclasses; alle bron-adapters implementeren dit contract.
- **Drive-adapter** (`src/iso_audit/sources/drive.py`) gemerged uit `drive_ingest.py` + `gws_client.py` + `planning_ingest.py`.
- **Jira-adapter** (`src/iso_audit/sources/jira.py`) — nieuw, juni-run-blokker.
- **Miro sub-package** (`src/iso_audit/miro/`) met gedeelde `client.py` + `board_setup.py` / `ingest.py` / `interview.py` consumers.
- **Modes-architectuur** (`src/iso_audit/modes/`) met `Mode` Protocol, `autonoom`, `integer` implementaties; pipeline emitteert `Decision`-events op zes beslispunten.
- **Slack Block Kit handoff** voor drie hoog-risico beslispunten in integer-modus.
- **Maintainability-fundament**: `pyproject.toml` + `uv` + `ruff` + `mypy --strict` + `pytest` + GitHub Actions CI + pre-commit met gitleaks + issue-templates inclusief `source-adapter` (forceert protocol-conformance + tests + docs).
- **Contract-tests** (`tests/sources/test_protocol_contract.py`) — fixture-set draait tegen elke geregistreerde adapter; nieuwe adapter is pas mergeable als pasvorm-test groen is.
- **Verhuizing van vier OpenSpec-changes** mee naar `iso-audit`: `audit-rapport-management-taal`, `gsuite-iso-audit-automation`, `miro-kennissessie-generator`, `hww-2-0`.
- **BREAKING**: `--source` flag is verplicht (geen default); CLI-error toont beschikbare adapters. Voorkomt stilzwijgende val-naar-Drive in geautomatiseerde runs.
- **BREAKING**: CLI-naam `iso-audit` (entry-point in `pyproject.toml`); module-form `python -m iso_audit.pipeline` blijft werken.
- **BREAKING**: `Ops_to_Biz/audit/` wordt deprecated in milestone B en verwijderd in milestone C.

Expliciet uitgesloten:
- `argocd_sync/` raken — blijft in `Ops_to_Biz`.
- `~/projects/miro-incident-board` en `~/projects/miro-desired-state` migreren — eigen change-proposal als deze consumers actief raken.
- MCP- en REST-adapter-implementaties — eigen change-proposals ná juni-run.
- `audit/archive/` (eenmalige remediation-scripts) meeverhuizen.

## Capabilities

### New Capabilities

- `sources`: pluggable Source-protocol + Drive- en Jira-adapters; contract-tests; bron-registry voor de pipeline.
- `modes`: autonoom + integer runmodes; `Decision`-events op vooraf gedefinieerde beslispunten; Slack Block Kit handoff voor hoog-risico punten; SQLite-persistentie voor pauze-staat.
- `repo-structure`: standalone `iso-audit` repo (fresh git, Python `>=3.12`); maintainability-stack (uv, ruff, mypy, pytest, CI, pre-commit, gitleaks); Miro sub-package consolidatie; CLI entry-point + module-form.

### Modified Capabilities

Geen — de bestaande `Ops_to_Biz` specs (`content-transform`, `doc-ingest`, `handbook-output`, `removal-report`) horen bij het handbook-werk en raken het audit-pad niet.

## Impact

**Code (Ops_to_Biz):**
- `audit/` — feature-frozen vanaf milestone A; deprecated vanaf milestone B; verwijderd in milestone C.
- `Ops_to_Biz/CLAUDE.md` — sectie "ISO Audit pipeline" verwijderen, vervangen door verhuispointer (PR direct na merge B).
- `output/audit*.db`, `output/audit_reports/*` — blijven in `Ops_to_Biz` (instance-data); nieuwe runs schrijven naar `iso-audit`.

**Code (iso-audit, nieuw):**
- Volledige `src/iso_audit/` package per doel-architectuur; `tests/` met contract-tests; `docs/`, `examples/fixture-audit-2026-q1/`.

**APIs / interfaces:**
- Pipeline-CLI breaking: `--source` verplicht, `--mode autonoom|integer` nieuw, console-script `iso-audit`.
- Source-protocol contract: nieuwe adapters moeten `list_documents`, `fetch_content`, `list_findings`, `healthcheck` implementeren.
- Mode-protocol contract: nieuwe modes implementeren `beslis(Decision) → besluit`.

**Dependencies:**
- `pyproject.toml`-managed via `uv`; nieuwe deps voor Slack Block Kit (juni-run) en mogelijk Jira-SDK.
- CI vereist GitHub Actions runners met Python 3.12 en `uv`.

**Memory / docs:**
- Twee `CLAUDE.md`-files (één per repo), één PR-paar bij merge B.
- Gedeelde Claude-memory: paden updaten van `audit/` naar `iso-audit/` na milestone B; ISO 27001-framing en boring-and-auditable-principe blijven onveranderd.

**Externe systemen:**
- Drive, Miro, Jira (nieuw), Anthropic API — credentials en scopes blijven gelijk; Slack-webhook nieuw voor integer-modus handoff.
