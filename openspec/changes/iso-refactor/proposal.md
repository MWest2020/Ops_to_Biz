## Why

Zes triggers vallen samen die onafhankelijk al groot genoeg waren:

1. **Auditor-rolconflict (missie-trigger).** De huidige interne auditor combineert die rol met operationele verantwoordelijkheden (team lead). ISO 19011 §6.4.2 onderkent dit conflict; in een organisatie van Conduction's omvang is personele scheiding niet realistisch. De tool is de structurele mitigatie. Dat positioneert het tool fundamenteel anders dan een efficiency-tool: het meet of het managementsysteem werkt zoals het hoort, en signaleert wanneer de menselijke auditor blinde vlekken heeft of in een patroon van vooringenomen oordelen zit. Zie `docs/missie.md`.
2. **Repo-splitsing.** `audit/` is volledig self-contained binnen `Ops_to_Biz` (geverifieerd: geen imports vanuit `argocd_sync/`, geen reverse imports). De ISO 27001-context van het tool zelf vraagt om eigen CI, eigen versie-beheer en eigen audit-trail — niet gemengd met onverwante ops-scripts.
3. **Bron-pluggability.** De huidige architectuur is hard gekoppeld aan Google Drive (`drive_ingest.py`, `gws_client.py`, `planning_ingest.py`). Jira komt later als tweede source; daarna MCP en REST. Capability 1 uit de missie (onafhankelijke bronnen, geen curated input) werkt structureel niet met één hard-gecodeerde bron — één bron is per definitie curatie via wie die bron beheert. **De source-adapter-laag moet er vóór Jira staan, niet erna.**
4. **Handoff-pluggability.** Voor integer-modus (mens-in-de-lus op kritieke beslismomenten) is een communicatiekanaal tussen tool en auditor nodig. Slack werkt voor Conduction; voor gemeentelijke afnemers (M365/Outlook/Teams-standaard) of organisaties op andere stacks niet. Hard-coded Slack maakt de tool onverkoopbaar buiten Conduction zonder rewrite — dezelfde valkuil als bij sources, andere laag. **Notifier-protocol moet er vanaf dag 1 staan.**

Drie afgeleide opportunities raken hetzelfde codepad en gaan daarom mee in deze refactor:

5. **Miro-consolidatie.** Drie Miro-clients in vier locaties, elk met eigen `_headers()`, `_post()`, rate-limit handling. Eén gedeelde sub-package, drie consumers eromheen.
6. **Dubbele finding_classification.** `finding_classification.py` (414 regels) en `finding_classification_20260420.py` (750 regels). Tweede importeert uit de eerste (regel 645: `from audit.finding_classification import review_en_bevestig, sla_op_in_sheets`); refactor is moment om de twee bestanden te ontvlechten en te consolideren.
7. **Modes-architectuur.** Greenfield werk; `autonoom` (end-to-end zelfstandig) en `integer` (mens-in-de-lus op kritieke beslismomenten). Blokker voor de eerste integer-run, dus moet hier ontworpen.

## What Changes

- **Nieuwe repo `iso-audit`** (kebab-case repo, snake-case package `iso_audit`); fresh git-history; Python `>=3.12`.
- **Source-protocol** (`src/iso_audit/sources/base.py`) met `Source` Protocol + `Document` / `Finding` dataclasses; alle bron-adapters implementeren dit contract; configuratie immutable binnen een audit-run.
- **Drive-adapter** (`src/iso_audit/sources/drive.py`) — alleen het read-pad uit `drive_ingest.py`; Google-Workspace-client (`gws_client.py`) blijft als interne client-module (`src/iso_audit/clients/gws.py`) tot Sink in milestone C komt.
- **Planning-adapter** (`src/iso_audit/sources/planning.py`) — Google-Sheets-bron uit `planning_ingest.py` + `gsa_client.py`; aparte adapter naast Drive omdat het conceptueel een eigen bron is, niet Drive.
- **Jira-adapter** (`src/iso_audit/sources/jira.py`) — nieuw, voor de eerste integer-run.
- **Sink-protocol** (`src/iso_audit/sinks/base.py`) — spec-only in milestone A; eerste implementatie (`DriveSink` voor rapport-publicatie) in milestone C.
- **Modes-architectuur** (`src/iso_audit/modes/`) met `Mode` Protocol, `autonoom`, `integer` implementaties; pipeline emitteert `Decision`-events op zeven beslispunten; `decisions`-tabel als rapporteerbare data, niet als runtime-state.
- **Notifier-protocol** (`src/iso_audit/notifiers/base.py`) — kanaal-agnostische handoff-laag voor integer-modus; `Slack` en `Email` als eerste twee adapters; `DecisionResolver`-protocol scheidt response-parsing van kanaal-specifieke implementatie.
- **Miro sub-package** (`src/iso_audit/miro/`) met gedeelde `client.py` + `board_setup.py` / `ingest.py` / `interview.py` consumers.
- **Classificatie-traceability**: elke classificatie persisteert input-hash, prompt-versie, model-versie, raw LLM-output naast geparseerde classificatie. Vereiste voor toekomstige patroondetectie en spiegel-laag (capability 2 en 3 uit missie).
- **Maintainability-fundament**: `pyproject.toml` + `uv` + `ruff` + `mypy --strict` + `pytest` + GitHub Actions CI + pre-commit met gitleaks + issue-templates inclusief `source-adapter`, `notifier-adapter` (forceren protocol-conformance + tests + docs).
- **Contract-tests** voor Sources én Notifiers; nieuwe adapter pas mergeable als pasvorm-test groen is.
- **Verhuizing van vier OpenSpec-changes** mee naar `iso-audit`: `audit-rapport-management-taal`, `gsuite-iso-audit-automation`, `miro-kennissessie-generator`, `hww-2-0`.
- **Missie-document** `docs/missie.md` als ankerdocument: drie capabilities, PDCA-rol, scope buiten Conduction, beperkingen.
- **BREAKING**: `--source` flag is verplicht (geen default); CLI-error toont beschikbare adapters. Voorkomt stilzwijgende val-naar-Drive in geautomatiseerde runs. `ISO_AUDIT_DEFAULT_SOURCE` env-var beschikbaar voor cron-context — expliciet in unit-file, geen CLI-default.
- **BREAKING**: `--mode autonoom|integer` is verplicht (geen default); `--notifier` verplicht alleen wanneer `--mode integer`.
- **BREAKING**: CLI-naam `iso-audit` (entry-point in `pyproject.toml`); module-form `python -m iso_audit.pipeline` blijft werken.
- **BREAKING**: `Ops_to_Biz/audit/` wordt deprecated in milestone B en verwijderd in milestone C.

Expliciet uitgesloten:
- `argocd_sync/` raken — blijft in `Ops_to_Biz`.
- `~/projects/miro-incident-board` en `~/projects/miro-desired-state` migreren — eigen change-proposal als deze consumers actief raken.
- MCP- en REST-source-adapter-implementaties — eigen change-proposals.
- Teams- en Mattermost-Notifier-implementaties — eigen change-proposals zodra een afnemer het vraagt; Notifier-protocol staat klaar.
- `audit/archive/` (eenmalige remediation-scripts) meeverhuizen.
- **Spiegel-laag (capability 3 uit missie)** — eigen change-proposal `iso-audit-mirror-foundation` na minimaal vier integer-runs in `decisions`-tabel. Deze refactor zet alleen de hooks (decisions-tabel als data-object, classificatie-traceability), bouwt geen analyse-laag.

## Capabilities

### New Capabilities

- `sources`: pluggable Source-protocol + Drive-, Planning- en Jira-adapters; immutable runtime-configuratie; contract-tests; bron-registry.
- `modes`: autonoom + integer runmodes; `Decision`-events op zeven vooraf gedefinieerde beslispunten; `decisions`-tabel als rapporteerbare audit-trail data; SQLite-persistentie voor pauze-staat.
- `notifiers`: pluggable Notifier-protocol + Slack- en Email-adapters; `DecisionResolver` kanaal-agnostisch; `--notifier` CLI-flag; contract-tests; notifier-registry.
- `repo-structure`: standalone `iso-audit` repo (fresh git, Python `>=3.12`); maintainability-stack (uv, ruff, mypy, pytest, CI, pre-commit, gitleaks); Miro sub-package consolidatie; CLI entry-point + module-form.

### Modified Capabilities

Geen — de bestaande `Ops_to_Biz` specs (`content-transform`, `doc-ingest`, `handbook-output`, `removal-report`) horen bij het handbook-werk en raken het audit-pad niet.

## Impact

**Code (Ops_to_Biz):**
- `audit/` — feature-frozen vanaf milestone A; deprecated vanaf milestone B; verwijderd in milestone C.
- `Ops_to_Biz/CLAUDE.md` — sectie "ISO Audit pipeline" verwijderen, vervangen door verhuispointer (PR direct na merge B).
- `output/audit*.db`, `output/audit_reports/*` — blijven in `Ops_to_Biz` (instance-data); nieuwe runs schrijven naar `iso-audit`.

**Code (iso-audit, nieuw):**
- Volledige `src/iso_audit/` package per doel-architectuur; `tests/` met contract-tests voor sources én notifiers; `docs/`, `examples/fixture-audit-2026-q1/`.
- `docs/missie.md` als ankerdocument voor toekomstige Claude-sessies en externe code-review.

**APIs / interfaces:**
- Pipeline-CLI breaking: `--source` verplicht, `--mode autonoom|integer` verplicht, `--notifier` verplicht bij `--mode integer`, console-script `iso-audit`.
- Source-protocol contract: nieuwe adapters moeten `list_documents`, `fetch_content`, `list_findings`, `healthcheck` implementeren; configuratie immutable na pipeline-start.
- Mode-protocol contract: nieuwe modes implementeren `beslis(Decision) → besluit`; AutonoomMode persisteert alleen hoog-risico-besluiten in `decisions`-tabel.
- Notifier-protocol contract: nieuwe notifiers implementeren `vraag_besluit(Decision) → decision_id` + `healthcheck()`; response-parsing via aparte `DecisionResolver`-protocol.

**Dependencies:**
- `pyproject.toml`-managed via `uv`; nieuwe deps voor Slack-SDK, Email-handling (smtplib + Flask-mini-portal voor magic-link) en Jira-SDK.
- CI vereist GitHub Actions runners met Python 3.12 en `uv`.

**Memory / docs:**
- Twee `CLAUDE.md`-files (één per repo), één PR-paar bij merge B.
- Gedeelde Claude-memory: paden updaten van `audit/` naar `iso-audit/` na milestone B; ISO 27001-framing en boring-and-auditable-principe blijven onveranderd.
- `docs/missie.md` is ankerdocument; toekomstige Claude-sessies in `iso-audit` lezen dit voor context.

**Externe systemen:**
- Drive, Miro, Jira (nieuw), Anthropic API — credentials en scopes blijven gelijk.
- Slack-webhook nieuw voor SlackNotifier; SMTP-credentials nieuw voor EmailNotifier; magic-link-portaal draait lokaal op pipeline-host (geen externe service).
