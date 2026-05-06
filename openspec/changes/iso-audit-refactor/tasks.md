## 1. Milestone A — Repo-skeleton + Source Protocol (week 1-2)

- [ ] 1.1 Maak GitHub-repo `MWest2020/iso-audit` aan (private, branch protection, signed commits, audit-trail features actief)
- [ ] 1.2 Initialiseer met `uv init`; voeg `pyproject.toml` toe met `requires-python = ">=3.12"`, project-metadata, console-script entry-point `iso-audit = "iso_audit.cli:main"`
- [ ] 1.3 Voeg dev-dependencies toe via `uv add --dev`: `ruff`, `mypy`, `pytest`, `pytest-cov`, `gitleaks`, `pre-commit`
- [ ] 1.4 Configureer `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` in `pyproject.toml` (mypy --strict op `src/`, coverage 70% gate)
- [ ] 1.5 Schrijf `.github/workflows/ci.yml` met parallel jobs: `lint` (ruff check), `format` (ruff format --check), `typecheck` (mypy --strict src/), `test` (pytest --cov --cov-fail-under=70)
- [ ] 1.6 Schrijf `.pre-commit-config.yaml` met `ruff check`, `ruff format --check`, `mypy`, `gitleaks`; rationale-comment over `--check` (niet `--write`) toevoegen
- [ ] 1.7 Maak `.github/ISSUE_TEMPLATE/{bug,feature,source-adapter}.md`; source-adapter-template forceert protocol-conformance + tests + docs checklist
- [ ] 1.8 Schrijf `.github/pull_request_template.md` met checklist (tests, CHANGELOG, breaking changes)
- [ ] 1.9 Schrijf `src/iso_audit/__init__.py` (versie-export) en `src/iso_audit/sources/__init__.py` (SourceRegistry)
- [ ] 1.10 Schrijf `src/iso_audit/sources/base.py` met `Source` Protocol, `Document` en `Finding` frozen dataclasses, `SourceRegistry` met `@register` decorator, `available()`, `get(naam)` methodes
- [ ] 1.11 Schrijf `tests/conftest.py` met fixture-set (sample-Documents, sample-Findings) gebruikt door contract-tests
- [ ] 1.12 Schrijf `tests/sources/test_protocol_contract.py` met parametrized tests die Protocol-invarianten valideren; lege adapter-set, draait leeg-groen
- [ ] 1.13 Schrijf `ARCHITECTURE.md` met source-protocol uitwerking, modes-contract overzicht, link naar design.md (van deze change-proposal)
- [ ] 1.14 Schrijf `iso-audit/CLAUDE.md` per memory-migratieplan: scope, source-protocol, modes-uitleg, OpenSpec-workflow, boring-auditable-principe, uv-workflow
- [ ] 1.15 Schrijf `README.md` met quick-start (`uv sync`, `iso-audit --help`), links naar ARCHITECTURE.md en docs/
- [ ] 1.16 Schrijf `CHANGELOG.md` (Keep a Changelog format) met initial v0.1.0-alpha entry
- [ ] 1.17 Schrijf `docs/sources/drive.md`, `docs/sources/jira.md`, `docs/sources/mcp.md`, `docs/sources/rest.md` (laatste twee: placeholder met "TODO: implementatie via eigen change-proposal")
- [ ] 1.18 Schrijf `docs/modes.md` (placeholder met verwijzing naar milestone C voor implementatie)
- [ ] 1.19 Eerste commit met scaffolding; tag `v0.1.0-alpha`; push naar `main`
- [ ] 1.20 Verifieer milestone-A acceptatie: CI groen, lege contract-test groen, ARCHITECTURE.md goedgekeurd door Mark, audit-trail features verifieerbaar in repo-settings

## 2. Milestone B — Verhuizing + Drive-adapter + Miro-consolidatie (week 3-5)

- [ ] 2.1 Maak `examples/fixture-audit-2026-q1/` met geanonimiseerde sample-CSV (≤20 rijen) + sample-rapport + README
- [ ] 2.2 Schrijf snapshot-tests in `tests/classification/test_findings_snapshot.py` die fixture-CSV door classifier draaien en byte-identiek match vereisen (baseline gegenereerd vóór refactor)
- [ ] 2.3 Migreer `Ops_to_Biz/audit/store.py` → `src/iso_audit/store.py` (schema ongewijzigd voor milestone B; `decisions`-tabel komt in milestone C)
- [ ] 2.4 Migreer `audit/auth.py` en `audit/notification.py` → `src/iso_audit/` (path-imports updaten)
- [ ] 2.5 Migreer `audit/normteksten.py` → `src/iso_audit/normteksten.py` (één-bestand voor nu; splitsing besluit in design-review tijdens deze milestone)
- [ ] 2.6 Migreer `audit/clause_mapping.py` → `src/iso_audit/classification/clause_mapping.py`
- [ ] 2.7 Merge `audit/finding_classification.py` + `audit/finding_classification_20260420.py` → `src/iso_audit/classification/findings.py`; commit-message documenteert welke versies wat zijn samengevoegd
- [ ] 2.8 Migreer `audit/thema_classifier.py` → `src/iso_audit/classification/thema.py`
- [ ] 2.9 Merge `audit/drive_ingest.py` + `audit/gws_client.py` + `audit/planning_ingest.py` → `src/iso_audit/sources/drive.py`; class `DriveSource` implementeert `Source` Protocol met `naam = "drive"`
- [ ] 2.10 Registreer DriveSource via `@register` decorator in module-level
- [ ] 2.11 Schrijf `tests/sources/test_drive.py` met DriveSource-specifieke tests; verifieer dat `tests/sources/test_protocol_contract.py` nu groene parametrized-tests heeft voor `drive`
- [ ] 2.12 Maak `src/iso_audit/miro/` package met `__init__.py`
- [ ] 2.13 Schrijf `src/iso_audit/miro/client.py` met gedeelde HTTP-laag: `_headers()`, `_post()`, `_get()`, rate-limit handling, retry-logica
- [ ] 2.14 Migreer `audit/miro_board_setup.py` → `src/iso_audit/miro/board_setup.py`; gebruikt `client.py` (geen eigen `_headers`/`_post`)
- [ ] 2.15 Migreer `audit/miro_ingest.py` → `src/iso_audit/miro/ingest.py`; gebruikt `client.py`
- [ ] 2.16 Migreer `audit/interview_miro.py` → `src/iso_audit/miro/interview.py`; gebruikt `client.py`
- [ ] 2.17 Schrijf `tests/miro/test_client.py` met rate-limit + retry-edge-cases
- [ ] 2.18 Visuele snapshot-test op één Miro-test-bord: JSON-export voor refactor → na refactor identiek
- [ ] 2.19 Migreer `audit/local_report.py` + `tabular_report.py` + `report_generation.py` + `slide_summary.py` → `src/iso_audit/reporting/`
- [ ] 2.20 Migreer `audit/md_to_html.py` + `html_to_docx.py` + `html_to_pdf.py` → `src/iso_audit/reporting/`
- [ ] 2.21 Migreer `audit/v2_handmatig.py` → `src/iso_audit/reporting/handmatig.py` (rename voor consistentie)
- [ ] 2.22 Migreer `audit/template_setup.py` → `src/iso_audit/reporting/template_setup.py`
- [ ] 2.23 Migreer `audit/assets/` → `src/iso_audit/assets/` (logo-SVG's)
- [ ] 2.24 Migreer `audit/config/` → `src/iso_audit/config/` (clause-maps, normteksten-yaml)
- [ ] 2.25 Schrijf `src/iso_audit/cli.py` als console-script entry-point; ondersteunt `iso-audit pipeline`, `iso-audit doctor`, `iso-audit setup-template` subcommands
- [ ] 2.26 Pas `src/iso_audit/pipeline.py` aan: gebruik `SourceRegistry` voor `--source` flag-resolution; flag is verplicht (geen default), exit-code 2 bij ontbreken/onbekend met beschikbare adapters in stderr
- [ ] 2.27 Test `python -m iso_audit.pipeline` werkt identiek aan `iso-audit pipeline` (backwards-compat voor cron-gebruikers)
- [ ] 2.28 Reproduceer alle bestaande pipeline-runs in `iso-audit`: `--norm 9001`, `--norm 27001`, `--norm beide`, `--chapter N`, `--local-only`, `--setup-template`, `--rehash`, `--dry-run-cost`, `--scherpte 0.5`, `--thema-llm`
- [ ] 2.29 Update `Ops_to_Biz/CLAUDE.md`: verwijder ISO-audit-pipeline-sectie, voeg verhuispointer toe (naar `MWest2020/iso-audit`); markeer `audit/` als feature-frozen tot milestone C
- [ ] 2.30 Verhuis 4 audit-OpenSpec-changes naar `iso-audit/openspec/changes/`: één commit per change-rename voor leesbare diff
  - [ ] 2.30.1 `audit-rapport-management-taal`
  - [ ] 2.30.2 `gsuite-iso-audit-automation`
  - [ ] 2.30.3 `miro-kennissessie-generator`
  - [ ] 2.30.4 `hww-2-0`
- [ ] 2.31 Verwijder de 4 verhuisde changes uit `Ops_to_Biz/openspec/changes/` (één commit met cleanup-verwijzingen)
- [ ] 2.32 Schrijf `iso-audit/CONTRIBUTING.md` met P0-bug-cherry-pick procedure (eenrichting Ops_to_Biz → iso-audit; geen reverse cherry-pick; alleen tijdens milestone B)
- [ ] 2.33 Verifieer milestone-B acceptatie: alle pipeline-runs reproduceerbaar, contract-tests Drive-adapter groen, Miro-snapshot-test groen, finding-classifier-snapshot-test exact-match groen, OpenSpec-changes succesvol verhuisd, CLAUDE.md-deprecation in Ops_to_Biz live
- [ ] 2.34 Tag `v0.2.0-beta` + merge milestone-B PR in beide repos

## 3. Milestone C — Modes + Jira-adapter (week 6-8, juni-run)

- [ ] 3.1 Schrijf `src/iso_audit/modes/__init__.py` met ModeRegistry
- [ ] 3.2 Schrijf `src/iso_audit/modes/base.py` met `Mode` Protocol, `Decision` dataclass (`punt`, `context`, `voorstel`, `risico`)
- [ ] 3.3 Voeg `decisions`-tabel migration-script toe in `src/iso_audit/store.py` (CREATE TABLE per design-doc)
- [ ] 3.4 Schrijf `src/iso_audit/modes/autonoom.py` (`AutonoomMode`); `delete_data` blokkeert altijd
- [ ] 3.5 Schrijf `src/iso_audit/modes/integer.py` (`IntegerMode`); persisteert pending Decisions in `decisions`-tabel; thread blokkeert tot resolved
- [ ] 3.6 Schrijf `tests/modes/test_autonoom.py` (alle 6 beslispunten getest)
- [ ] 3.7 Schrijf `tests/modes/test_integer.py` (escalatie, pause-resume, low-confidence-escalatie)
- [ ] 3.8 Schrijf `tests/modes/test_integer_handoff.py` (Slack Block Kit message-shape, button-handlers)
- [ ] 3.9 Pas pipeline aan om Decision te emitteren op `classify_finding` (midden-risico)
- [ ] 3.10 Pas pipeline aan om Decision te emitteren op `merge_drive_miro` (laag-risico)
- [ ] 3.11 Pas pipeline aan om Decision te emitteren op `assign_clausule` (midden-risico, escalatie bij low-confidence)
- [ ] 3.12 Pas pipeline aan om Decision te emitteren op `generate_report_section` (hoog-risico)
- [ ] 3.13 Pas pipeline aan om Decision te emitteren op `send_report` (hoog-risico)
- [ ] 3.14 Pas pipeline aan om Decision te emitteren op `delete_data` (hoog-risico, autonoom blokkeert)
- [ ] 3.15 Implementeer Slack Block Kit handoff in `src/iso_audit/modes/integer.py`: header, context-codeblock, voorstel-codeblock, action-buttons (`Goedkeuren`, `Afwijzen`, `Aanpassen`)
- [ ] 3.16 Implementeer Slack response-handler (HTTP endpoint via webhook of polling van Slack-channel) die `decisions`-rij update naar `status="resolved"` met `besluit_json`
- [ ] 3.17 Voeg `--mode` flag toe aan CLI (verplicht, opties `autonoom`/`integer`); exit-code 2 bij ontbreken
- [ ] 3.18 Test pipeline-restart-na-crash: pending Decisions worden hervat, geen dubbele Slack-message
- [ ] 3.19 Schrijf `src/iso_audit/sources/jira.py` met `JiraSource` (`naam = "jira"`); Jira Cloud REST API v3 + token-auth via env-vars
- [ ] 3.20 Registreer JiraSource via `@register` decorator
- [ ] 3.21 Schrijf `tests/sources/test_jira.py` met JiraSource-specifieke tests; verifieer dat parametrized contract-tests groen zijn voor `jira`
- [ ] 3.22 Update `docs/sources/jira.md` met env-var-vereisten, JQL-voorbeelden, mapping naar Document/Finding
- [ ] 3.23 Update `docs/modes.md` met autonoom + integer uitleg, beslispunten-tabel, Slack-setup-instructies
- [ ] 3.24 Smoke-test: `iso-audit pipeline --norm 27001 --source jira --source drive --mode integer` end-to-end met Mark als auditor in echte Slack-channel
- [ ] 3.25 Verifieer dat alle drie hoog-risico beslispunten zichtbaar zijn in Slack-handoffs tijdens smoke-test
- [ ] 3.26 Verifieer dat auditor-besluiten correct in `decisions`-tabel persistent worden met `resolved_at` timestamp
- [ ] 3.27 Verwijder `Ops_to_Biz/audit/` volledig (inclusief `audit/archive/`)
- [ ] 3.28 Update `Ops_to_Biz/CLAUDE.md`: verwijder verhuispointer, alleen historische zin in CHANGELOG behouden
- [ ] 3.29 Update gedeelde Claude-memory entries: paden van `audit/` → `iso-audit/` (project_audit_pipeline.md, project_audit_volgende_stappen.md indien van toepassing)
- [ ] 3.30 Tag `v1.0.0` + merge milestone-C PR in beide repos
- [ ] 3.31 Verifieer milestone-C acceptatie: end-to-end juni-audit gedraaid in integer-mode met Jira primair en Drive secundair, alle Slack-handoffs werkend, decisions-tabel populated, Ops_to_Biz/audit/ volledig verwijderd

## 4. Post-milestone follow-ups (backlog)

- [ ] 4.1 Snapshot-tests procedure documenteren in `iso-audit/CONTRIBUTING.md` (genereer-baseline-flow, update-bij-bedoelde-wijziging-flow)
- [ ] 4.2 Externe-certificeerder bundel: markdown-overzicht met drie milestone-tags + commit-ranges + acceptatie per milestone (voor Q3 audit)
- [ ] 4.3 Open vragen uit design.md sluiten in eigen change-proposals (Sink-protocol, Teams-handoff, normteksten-splitsing)
