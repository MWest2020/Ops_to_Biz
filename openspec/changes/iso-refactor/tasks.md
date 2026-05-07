## 1. Milestone A — Repo-skeleton + drie protocollen + missie (week 1-2)

### 1.1 Repo-setup en infrastructuur

- [ ] 1.1.1 Maak GitHub-repo `MWest2020/iso-audit` aan (private)
- [ ] 1.1.2 Configureer branch protection op `main`: required PR reviews (≥1), required status checks (alle CI-jobs), no force-push, no direct pushes
- [ ] 1.1.3 Configureer required signed commits (GPG of SSH-signing)
- [ ] 1.1.4 Indien Enterprise-tier beschikbaar: enable Audit Log; anders maak `compensating-control.md` met beschrijving van alternatieve audit-trail-borging
- [ ] 1.1.5 Initialiseer met `uv init`; voeg `pyproject.toml` toe met `requires-python = ">=3.12"`, project-metadata, console-script entry-point `iso-audit = "iso_audit.cli:main"`
- [ ] 1.1.6 Voeg dev-dependencies toe via `uv add --dev`: `ruff`, `mypy`, `pytest`, `pytest-cov`, `gitleaks`, `bandit`, `pre-commit`
- [ ] 1.1.7 Configureer `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.bandit]` in `pyproject.toml` (mypy --strict op `src/`, coverage tijdelijk 60% gate tot baseline-meting in milestone B)
- [ ] 1.1.8 Schrijf `.github/workflows/ci.yml` met parallel jobs: `lint` (ruff check), `format` (ruff format --check), `typecheck` (mypy --strict src/), `security` (bandit -r src/), `test` (pytest --cov --cov-fail-under=60)
- [ ] 1.1.9 Schrijf `.pre-commit-config.yaml` met `ruff check`, `ruff format --check`, `mypy`, `gitleaks`, `bandit`; rationale-comment over `--check` (niet `--write`) toevoegen
- [ ] 1.1.10 Maak `.github/ISSUE_TEMPLATE/{bug,feature,source-adapter,notifier-adapter}.md`; source- en notifier-adapter-templates forceren protocol-conformance + tests + docs checklists
- [ ] 1.1.11 Schrijf `.github/pull_request_template.md` met checklist (tests, CHANGELOG, breaking changes, missie-impact)

### 1.2 Source Protocol (in milestone A definiëren, geen implementaties)

- [ ] 1.2.1 Schrijf `src/iso_audit/__init__.py` (versie-export)
- [ ] 1.2.2 Schrijf `src/iso_audit/sources/__init__.py` met `SourceRegistry` (`@register` decorator, `available()`, `get(naam)`, ValueError op dubbele registratie)
- [ ] 1.2.3 Schrijf `src/iso_audit/sources/base.py` met `Source` Protocol (4 methodes), `Document` en `Finding` frozen dataclasses
- [ ] 1.2.4 Schrijf `tests/conftest.py` met fixture-set (sample-Documents, sample-Findings) gebruikt door alle contract-tests
- [ ] 1.2.5 Schrijf `tests/sources/test_protocol_contract.py` met parametrized tests die Protocol-invarianten valideren incl. immutability-check; lege adapter-set, draait leeg-groen

### 1.3 Sink Protocol (alleen spec, geen implementaties)

- [ ] 1.3.1 Schrijf `src/iso_audit/sinks/__init__.py`
- [ ] 1.3.2 Schrijf `src/iso_audit/sinks/base.py` met `Sink` Protocol (`send`, `healthcheck`), `SinkPayload`-hierarchy: `ReportPayload`, `NotificationPayload`, `MirrorPayload` (placeholder), `SinkResult` dataclass
- [ ] 1.3.3 Schrijf `tests/sinks/test_protocol_shape.py` met statische check dat Protocol-en-Payload-classes correct gedefinieerd zijn (geen runtime-tests want geen implementatie)

### 1.4 Notifier Protocol

- [ ] 1.4.1 Schrijf `src/iso_audit/notifiers/__init__.py` met `NotifierRegistry` (identiek patroon als SourceRegistry)
- [ ] 1.4.2 Schrijf `src/iso_audit/notifiers/base.py` met `Notifier` Protocol (`vraag_besluit`, `healthcheck`), `DecisionResolver` Protocol (`resolve`)
- [ ] 1.4.3 Schrijf `tests/notifiers/test_protocol_contract.py` met parametrized tests; lege adapter-set, draait leeg-groen

### 1.5 Documentatie en missie

- [ ] 1.5.1 Schrijf `docs/missie.md` (verbatim of licht-geredigeerd uit `Tool-ontwerp_audit-tool_2026-05-05.md`); versionering en datum-stempel
- [ ] 1.5.2 Schrijf `ARCHITECTURE.md` met source/sink/notifier-protocollen + modes-contract overzicht; expliciete link naar `docs/missie.md` en deze design-doc
- [ ] 1.5.3 Schrijf `iso-audit/CLAUDE.md` per memory-migratieplan: scope, missie-pointer, source/sink/notifier/modes-uitleg, OpenSpec-workflow, boring-auditable-principe, uv-workflow
- [ ] 1.5.4 Schrijf `README.md` met quick-start (`uv sync`, `iso-audit --help`), links naar ARCHITECTURE.md, docs/missie.md en docs/
- [ ] 1.5.5 Schrijf `CHANGELOG.md` (Keep a Changelog format) met initial v0.1.0-alpha entry
- [ ] 1.5.6 Schrijf `docs/sources/{drive,planning,jira,mcp,rest}.md` (laatste twee placeholder met "TODO: implementatie via eigen change-proposal")
- [ ] 1.5.7 Schrijf `docs/notifiers/{slack,email,teams,mattermost}.md` (laatste twee placeholder)
- [ ] 1.5.8 Schrijf `docs/modes.md` met sectie "Modi en de missie" (autonoom-runs leveren geen capability-3-data)
- [ ] 1.5.9 Schrijf `docs/sinks/README.md` als index met "implementaties vanaf milestone C"

### 1.6 Acceptatie milestone A

- [ ] 1.6.1 Eerste commit met scaffolding; tag `v0.1.0-alpha`; push naar `main`
- [ ] 1.6.2 Verifieer: CI groen op alle 5 jobs (lint, format, typecheck, security, test)
- [ ] 1.6.3 Verifieer: drie contract-tests draaien leeg-groen (sources, notifiers, en sinks-shape)
- [ ] 1.6.4 Verifieer: branch-protection en signed-commit-vereisten actief in repo-settings (screenshot of API-output bewaren)
- [ ] 1.6.5 Verifieer: `docs/missie.md` aanwezig en versie-gestempeld
- [ ] 1.6.6 Acceptatie door Mark: ARCHITECTURE.md gelezen en goedgekeurd

## 2. Milestone B — Verhuizing + Source-adapters + Miro + classificatie-traceability (week 3-5)

### 2.1 Voorbereiding en baseline

- [ ] 2.1.1 Maak `examples/fixture-audit-2026-q1/` met geanonimiseerde sample-CSV (≤20 rijen) + sample-rapport + README
- [ ] 2.1.2 Schrijf snapshot-tests in `tests/classification/test_findings_snapshot.py` die fixture-CSV door classifier draaien en byte-identiek match vereisen op `parsed_klasse` en `parsed_clausule` (baseline gegenereerd vóór refactor)
- [ ] 2.1.3 Meet test-coverage baseline op huidig `Ops_to_Biz/audit/`-codebase (kopie naar tijdelijke iso-audit-branch); bepaal definitieve gate `max(baseline + 5%, 70%)`, plafond 85%
- [ ] 2.1.4 Update CI-config: `--cov-fail-under=<gate>` met definitieve waarde

### 2.2 Module-migratie (kern, niet-source-specifiek)

- [ ] 2.2.1 Migreer `Ops_to_Biz/audit/store.py` → `src/iso_audit/store.py` (schema ongewijzigd voor milestone B; `decisions`- en `classifications`-tabellen komen later in deze milestone resp. milestone C)
- [ ] 2.2.2 Migreer `audit/auth.py` en `audit/notification.py` → `src/iso_audit/` (path-imports updaten)
- [ ] 2.2.3 Migreer `audit/normteksten.py` → splits naar `src/iso_audit/data/normteksten/iso9001.py` + `iso27001.py` + `__init__.py` met re-export (open-question-resolutie: korte termijn doen, YAML-migratie blijft eigen change na milestone C)
- [ ] 2.2.4 Migreer `audit/clause_mapping.py` → `src/iso_audit/classification/clause_mapping.py`
- [ ] 2.2.5 Ontvlecht `audit/finding_classification.py` en `audit/finding_classification_20260420.py`: documenteer in commit-message dat `_20260420.py` regel 645 importeert uit het oude bestand; consolideer naar `src/iso_audit/classification/findings.py` met behoud van beide functionaliteiten
- [ ] 2.2.6 Migreer `audit/thema_classifier.py` → `src/iso_audit/classification/thema.py`
- [ ] 2.2.7 Migreer `audit/llm_classifier.py` → `src/iso_audit/classification/llm.py`
- [ ] 2.2.8 Verplaats inline classifier-prompts naar `src/iso_audit/classification/prompts/<versie>.md` per requirement; refactor classifier-code om prompts uit bestand te laden

### 2.3 Source-adapters (eerlijke decompositie)

- [ ] 2.3.1 Splits Google-Workspace-client uit `audit/gws_client.py` → `src/iso_audit/clients/gws.py` (interne client-module, niet Source/Sink); shared `_gws()`-helper blijft hier
- [ ] 2.3.2 Migreer `audit/drive_ingest.py` → `src/iso_audit/sources/drive.py` als `DriveSource` (alleen read-pad); class implementeert `Source` Protocol met `naam = "drive"`; gebruikt `clients/gws.py`
- [ ] 2.3.3 Registreer `DriveSource` via `@register` decorator op module-level
- [ ] 2.3.4 Schrijf `tests/sources/test_drive.py` met DriveSource-specifieke tests; verifieer dat `tests/sources/test_protocol_contract.py` nu groene parametrized-tests heeft voor `drive`
- [ ] 2.3.5 Migreer `audit/planning_ingest.py` + `audit/gsa_client.py` → `src/iso_audit/sources/planning.py` als `PlanningSource` (Google Sheets); class implementeert `Source` Protocol met `naam = "planning"`; gebruikt `clients/gws.py` voor Sheets-API
- [ ] 2.3.6 Registreer `PlanningSource` via `@register` decorator
- [ ] 2.3.7 Schrijf `tests/sources/test_planning.py`; verifieer contract-tests groen voor `planning`
- [ ] 2.3.8 Update `audit/verify_docs.py` (gebruikt nu `gsa_client.py`) → `src/iso_audit/verify_docs.py`; pas imports aan naar `clients/gws.py`

### 2.4 Miro-consolidatie

- [ ] 2.4.1 Maak `src/iso_audit/miro/` package met `__init__.py`
- [ ] 2.4.2 Schrijf `src/iso_audit/miro/client.py` met gedeelde HTTP-laag: `_headers()`, `_post()`, `_get()`, rate-limit handling, retry-logica
- [ ] 2.4.3 Migreer `audit/miro_board_setup.py` → `src/iso_audit/miro/board_setup.py`; gebruikt `client.py` (geen eigen `_headers`/`_post`)
- [ ] 2.4.4 Migreer `audit/miro_ingest.py` → `src/iso_audit/miro/ingest.py`; gebruikt `client.py`
- [ ] 2.4.5 Migreer `audit/interview_miro.py` → `src/iso_audit/miro/interview.py`; gebruikt `client.py`
- [ ] 2.4.6 Schrijf `tests/miro/test_client.py` met rate-limit + retry-edge-cases
- [ ] 2.4.7 Visuele snapshot-test op één Miro-test-bord: JSON-export voor refactor → na refactor identiek

### 2.5 Reporting-modules (interne migratie, géén Sink-implementatie)

- [ ] 2.5.1 Migreer `audit/local_report.py` + `tabular_report.py` + `report_generation.py` + `slide_summary.py` → `src/iso_audit/reporting/`; nog géén Sink-stempel — DriveSink komt in milestone C
- [ ] 2.5.2 Migreer `audit/md_to_html.py` + `html_to_docx.py` + `html_to_pdf.py` → `src/iso_audit/reporting/`
- [ ] 2.5.3 Migreer `audit/template_setup.py` → `src/iso_audit/reporting/template_setup.py`
- [ ] 2.5.4 Migreer `audit/full_report.py` → `src/iso_audit/reporting/full_report.py`
- [ ] 2.5.5 Migreer `audit/landscape.py` → `src/iso_audit/reporting/landscape.py`
- [ ] 2.5.6 Migreer `audit/make_pptx.py` → `src/iso_audit/reporting/pptx.py`
- [ ] 2.5.7 Migreer `audit/sheets_gws.py` → `src/iso_audit/reporting/sheets_gws.py` (verwijder de "Consistent met argocd_sync"-comment, want de twee repo's zijn nu losgekoppeld)
- [ ] 2.5.8 Migreer `audit/interview.py` → `src/iso_audit/interview.py`
- [ ] 2.5.9 Migreer `audit/ingest.py` → `src/iso_audit/ingest.py`; refactor om SourceRegistry te gebruiken in plaats van directe imports
- [ ] 2.5.10 Migreer `audit/pipeline.py` → `src/iso_audit/pipeline.py`; refactor om SourceRegistry-gebaseerde `--source` flag te ondersteunen
- [ ] 2.5.11 Migreer `audit/assets/` → `src/iso_audit/assets/` (logo-SVG's)
- [ ] 2.5.12 Migreer `audit/config/` → `src/iso_audit/config/` (clause-maps, normteksten-yaml)

### 2.6 CLI en classificatie-traceability

- [ ] 2.6.1 Schrijf `src/iso_audit/cli.py` als console-script entry-point; ondersteunt `iso-audit pipeline`, `iso-audit doctor`, `iso-audit setup-template` subcommands; één `main()` waarnaar `__main__.py` en `pipeline.py`-direct-call delegeren
- [ ] 2.6.2 Implementeer `--source` flag (verplicht, multi-value, met `ISO_AUDIT_DEFAULT_SOURCE`-env-var-fallback inclusief INFO-log bij fallback-gebruik)
- [ ] 2.6.3 Voeg `classifications`-tabel toe aan `store.py` met migratie-script + indexen
- [ ] 2.6.4 Refactor classifier-code om input-hash, prompt-versie, model-versie, raw output te persisteren in `classifications`-tabel vóór consumptie van resultaat
- [ ] 2.6.5 Schrijf `tests/store/test_classifications.py` met scenario's voor traceability-velden + dedup op `(audit_id, finding_id, prompt_versie, model_versie)`

### 2.7 Verhuizing OpenSpec-changes

- [ ] 2.7.1 Verhuis `audit-rapport-management-taal` → `iso-audit/openspec/changes/`; commit-message vermeldt "Verhuisd uit Ops_to_Biz @ <sha>"
- [ ] 2.7.2 Verhuis `gsuite-iso-audit-automation` → idem
- [ ] 2.7.3 Verhuis `miro-kennissessie-generator` → idem
- [ ] 2.7.4 Verhuis `hww-2-0` → idem
- [ ] 2.7.5 Verwijder de vier verhuisde changes uit `Ops_to_Biz/openspec/changes/`

### 2.8 Acceptatie milestone B

- [ ] 2.8.1 Markeer `Ops_to_Biz/audit/` als deprecated in `Ops_to_Biz/CLAUDE.md` met pointer naar `iso-audit`; voeg óók notitie toe over `output/business_gws.py` en `output/gws.py` (handbook-pad, niet geraakt door refactor)
- [ ] 2.8.2 Verifieer: alle bestaande pipeline-runs reproduceerbaar in `iso-audit`
- [ ] 2.8.3 Verifieer: contract-tests Drive- en Planning-adapter groen
- [ ] 2.8.4 Verifieer: snapshot-tests groen op fixture-findings (byte-identiek vóór en na)
- [ ] 2.8.5 Verifieer: `classifications`-tabel gevuld voor fixture-runs met alle traceability-velden
- [ ] 2.8.6 Verifieer: Miro-features werken via gedeelde client; rate-limit-counter wordt gedeeld
- [ ] 2.8.7 Tag `v0.2.0-beta` op iso-audit; merge `Ops_to_Biz/CLAUDE.md`-update naar Ops_to_Biz main

## 3. Milestone C — Modes + Notifiers + Jira + Sink (week 6-9)

### 3.1 Modes-implementatie

- [ ] 3.1.1 Schrijf `src/iso_audit/modes/__init__.py`
- [ ] 3.1.2 Schrijf `src/iso_audit/modes/base.py` met `Mode` Protocol + `Decision` dataclass (`punt`, `context`, `voorstel`, `risico`, `audit_id`)
- [ ] 3.1.3 Voeg `decisions`-tabel toe aan `store.py` met migratie-script + indexen `idx_decisions_audit_status` en `idx_decisions_punt_resolved`
- [ ] 3.1.4 Schrijf `src/iso_audit/modes/autonoom.py` met `AutonoomMode`; selectieve persistentie (alleen `risico="hoog"` rijen schrijven)
- [ ] 3.1.5 Schrijf `src/iso_audit/modes/integer.py` met `IntegerMode`; constructor accepteert `Notifier` via DI; risico-gebaseerde escalatie-logica + low-confidence-escalatie + `vraag_bevestiging`-flag-handling
- [ ] 3.1.6 Schrijf `tests/modes/test_autonoom.py` en `tests/modes/test_integer.py`
- [ ] 3.1.7 Refactor `pipeline.py` om Decision-events te emitteren op zeven beslispunten: `ingest_scope`, `merge_drive_miro`, `classify_finding`, `assign_clausule`, `generate_report_section`, `send_report`, `delete_data`
- [ ] 3.1.8 Implementeer crash-recovery in pipeline: bij start, query op `(audit_id, status="pending")` en hervat in plaats van opnieuw escaleren

### 3.2 Notifiers-implementatie

- [ ] 3.2.1 Schrijf `src/iso_audit/notifiers/resolver.py` met `DecisionResolver`-implementatie die `decisions`-tabel updatet en pipeline-thread unblockt
- [ ] 3.2.2 Schrijf `src/iso_audit/notifiers/slack.py` met `SlackNotifier`: Block Kit message-templates, button-actions (`Goedkeuren`, `Afwijzen`, `Aanpassen`, `Afbreken`), modal-flow voor Aanpassen
- [ ] 3.2.3 Implementeer Slack Events API handler die button-callbacks parseert naar `(decision_id, action, modified_payload)` en `DecisionResolver.resolve()` aanroept
- [ ] 3.2.4 Schrijf `tests/notifiers/test_slack.py` met gemockte Slack-API; verifieer button-callback-flow end-to-end
- [ ] 3.2.5 Schrijf `src/iso_audit/notifiers/email.py` met `EmailNotifier`: SMTP-out via env-vars, magic-link-tokens met TTL
- [ ] 3.2.6 Schrijf `src/iso_audit/notifiers/portal.py` met Flask-mini-portaal: routes `/decision/<id>/{approve,reject,modify,abort}`, `/modify`-form-pagina, single-use-token-validatie, expiratie-handling (410 Gone)
- [ ] 3.2.7 Implementeer portal-startup als sub-thread of separate process bij `iso-audit pipeline --notifier email` start; configureerbare poort via `ISO_AUDIT_PORTAL_PORT`
- [ ] 3.2.8 Schrijf `tests/notifiers/test_email.py` met gemockte SMTP en Flask test-client; verifieer magic-link-flow incl. expiratie en single-use
- [ ] 3.2.9 Verifieer dat `tests/notifiers/test_protocol_contract.py` nu groene parametrized-tests heeft voor `slack` én `email`
- [ ] 3.2.10 Schrijf `docs/notifiers/slack.md` met setup-instructies (Slack-app creation, OAuth-scopes, env-vars)
- [ ] 3.2.11 Schrijf `docs/notifiers/email.md` met setup-instructies + acceptable-risk-notitie over HTTP-zonder-TLS in MVP

### 3.3 Sink-implementatie (DriveSink)

- [ ] 3.3.1 Schrijf `src/iso_audit/sinks/drive.py` met `DriveSink` die `Sink` Protocol implementeert (`naam = "drive"`)
- [ ] 3.3.2 Consolideer rapport-write-paden uit `src/iso_audit/reporting/` om via `DriveSink.send(ReportPayload)` te lopen
- [ ] 3.3.3 Schrijf `tests/sinks/test_drive.py` met scenario's voor ReportPayload + NotificationPayload
- [ ] 3.3.4 Schrijf `docs/sinks/drive.md`

### 3.4 Jira-source-adapter

- [ ] 3.4.1 Schrijf `src/iso_audit/sources/jira.py` met `JiraSource` (`naam = "jira"`); Jira Cloud REST API v3, token-auth via env-vars
- [ ] 3.4.2 Implementeer `list_documents` (issue-metadata) en `list_findings` (issues als bevindingen) met JQL-config
- [ ] 3.4.3 Registreer `JiraSource` via `@register`
- [ ] 3.4.4 Schrijf `tests/sources/test_jira.py` met gemockte Jira-API
- [ ] 3.4.5 Verifieer contract-tests groen voor `jira`
- [ ] 3.4.6 Schrijf `docs/sources/jira.md` met setup-instructies

### 3.5 CLI-uitbreiding

- [ ] 3.5.1 Implementeer `--mode <autonoom|integer>` flag (verplicht, met `ISO_AUDIT_DEFAULT_MODE`-fallback + INFO-log)
- [ ] 3.5.2 Implementeer `--notifier <naam>` flag (verplicht alleen bij `--mode integer`, met `ISO_AUDIT_DEFAULT_NOTIFIER`-fallback)
- [ ] 3.5.3 Implementeer waarschuwing wanneer `--notifier` wordt opgegeven met `--mode autonoom` (WARNING-log "notifier ignored in autonoom mode")
- [ ] 3.5.4 Update `iso-audit doctor` subcommand om `healthcheck()` op alle geregistreerde sources én notifiers aan te roepen

### 3.6 Eerste integer-run-validatie

- [ ] 3.6.1 Eerste integer-run-target: `iso-audit pipeline --norm 27001 --source jira --source drive --mode integer --notifier slack`
- [ ] 3.6.2 Tweede smoke-test: `iso-audit pipeline --norm 27001 --source drive --mode integer --notifier email`
- [ ] 3.6.3 Verifieer: alle drie hoog-risico beslispunten zichtbaar in handoffs (Slack-message én Email-magic-link)
- [ ] 3.6.4 Verifieer: auditor-besluiten persistent in `decisions`-tabel met `notifier_naam` correct gevuld (`"slack"` of `"email"`)
- [ ] 3.6.5 Verifieer: crash-recovery werkt — kill pipeline tijdens pending-state, herstart, geen dubbele Notifier-call

### 3.7 Cleanup en migratie-afsluiting

- [ ] 3.7.1 Verwijder `Ops_to_Biz/audit/` volledig
- [ ] 3.7.2 Verwijder `Ops_to_Biz/audit/archive/` volledig
- [ ] 3.7.3 Ruim `Ops_to_Biz/CLAUDE.md` op: verwijder audit-sectie volledig (behoud alleen historische CHANGELOG-pointer)
- [ ] 3.7.4 Update gedeelde Claude-memory: paden van `audit/` naar `iso-audit/`

### 3.8 Acceptatie milestone C

- [ ] 3.8.1 Tag `v1.0.0` op iso-audit
- [ ] 3.8.2 End-to-end smoke-tests groen op zowel Slack- als Email-notifier
- [ ] 3.8.3 Externe-audit-overzicht aanleveren: drie milestone-tags + commit-ranges + acceptatiecriteria
- [ ] 3.8.4 Acceptatie door Mark: eerste integer-run draaibaar in beide notifier-configuraties

## 4. Post-milestone follow-ups (eigen change-proposals)

- [ ] 4.1 `iso-audit-mirror-foundation` — capability 3 (auditor-spiegel) implementatie na minimaal vier integer-runs in `decisions`-tabel
- [ ] 4.2 `iso-audit-normteksten-yaml` — migratie van Python-data naar YAML-bestanden met loader; norm-updates door non-Python-reviewers
- [ ] 4.3 `iso-audit-mcp-source` — MCP-source-adapter implementatie
- [ ] 4.4 `iso-audit-rest-source` — REST-source-adapter implementatie
- [ ] 4.5 `iso-audit-teams-notifier` — Microsoft Teams-notifier wanneer eerste afnemer het vraagt
- [ ] 4.6 `iso-audit-mattermost-notifier` — idem voor open-source-bewuste organisaties
- [ ] 4.7 `iso-audit-near-duplicate-detection` — content-hash-based dedup voor multi-source merge wanneer near-duplicates daadwerkelijk speelt
