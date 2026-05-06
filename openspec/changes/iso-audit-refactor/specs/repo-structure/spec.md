## ADDED Requirements

### Requirement: Standalone `iso-audit` repo met fresh git-history

Het systeem SHALL een nieuwe GitHub-repo `MWest2020/iso-audit` hebben met fresh git-history (niet via filter-repo of subtree-split uit `Ops_to_Biz`).

De repo SHALL private zijn met audit-trail features ingeschakeld in GitHub-settings.

De repo-naam SHALL `iso-audit` zijn (kebab-case); de Python-package-naam SHALL `iso_audit` zijn (snake_case, PEP 8).

#### Scenario: Initiële commit-graph

- **WHEN** de repo wordt aangemaakt
- **THEN** de eerste commit MUST de scaffolding bevatten zonder verwijzing naar `Ops_to_Biz`-history
- **AND** de repo-instellingen MUST audit-trail (branch protection, signed commits) ingeschakeld hebben

### Requirement: Python-packaging via `pyproject.toml` en `uv`

Het systeem SHALL `pyproject.toml` als single source of truth voor packaging gebruiken met:

- `requires-python = ">=3.12"`
- `[project]` metadata (naam, versie via semver, description, authors)
- `[project.scripts]` met `iso-audit = "iso_audit.cli:main"` voor console-script entry-point
- `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` configuraties

Een `uv.lock` SHALL gecommit zijn voor reproduceerbare installs.

`pip` SHALL NOT direct gebruikt worden in workflows, scripts of documentatie — alleen `uv`.

#### Scenario: Verse install van repo

- **WHEN** een ontwikkelaar `uv sync` uitvoert in een verse clone
- **THEN** alle dependencies MUST geïnstalleerd worden met versies uit `uv.lock`
- **AND** `iso-audit --help` MUST een geldige help-tekst tonen

#### Scenario: Dependency-update zonder uv.lock

- **WHEN** een PR voegt een dependency toe in `pyproject.toml` zonder `uv.lock` te updaten
- **THEN** CI MUST falen op een `uv lock --check` step

### Requirement: Linting, formatting en typing-infrastructuur

Het systeem SHALL `ruff` gebruiken voor linting en formatting met configuratie in `pyproject.toml`.

Het systeem SHALL `mypy --strict` gebruiken op `src/`. Tests MAY een lossere config gebruiken (`--ignore-missing-imports`).

Pre-commit-hooks SHALL bevatten: `ruff check`, `ruff format --check` (NOT `--write`), `mypy`, `gitleaks`.

#### Scenario: Code voldoet niet aan ruff-regels

- **WHEN** code committed wordt die `ruff check` faalt
- **THEN** de pre-commit-hook MUST de commit blokkeren met de specifieke regel-violations

#### Scenario: Pre-commit format-on-write valkuil

- **WHEN** ontwikkelaars de pre-commit-config aanpassen
- **THEN** de hook MUST nooit `ruff format --write` of equivalent gebruiken — alleen `--check`
- **AND** rationale MUST in `.pre-commit-config.yaml` als comment vermeld staan: voorkomt silent CI-falen

### Requirement: GitHub Actions CI met parallelle jobs

Een `.github/workflows/ci.yml` SHALL parallel jobs definiëren voor:

- `lint`: `ruff check .`
- `format`: `ruff format --check .`
- `typecheck`: `mypy --strict src/`
- `test`: `pytest --cov=iso_audit --cov-report=term-missing --cov-fail-under=70`

CI SHALL draaien op pull-requests naar `main` en op pushes naar `main`.

CI SHALL groen zijn voor merge.

Coverage SHALL minimaal 70% line-coverage zijn (CI-gate).

#### Scenario: PR met failing tests

- **WHEN** een PR-branch test-failures bevat
- **THEN** de `test` job MUST falen
- **AND** PR MUST geblokkeerd zijn voor merge totdat alle jobs groen zijn

#### Scenario: PR met coverage onder 70%

- **WHEN** een PR de line-coverage onder 70% drukt
- **THEN** de `test` job MUST falen op de `--cov-fail-under` check

### Requirement: Issue-templates inclusief source-adapter contributions

`.github/ISSUE_TEMPLATE/` SHALL drie templates bevatten:

- `bug.md`
- `feature.md`
- `source-adapter.md` — verplicht checklist voor nieuwe Source-adapters: protocol-conformance, contract-tests groen, docs-pagina aangemaakt, healthcheck geïmplementeerd.

Een `pull_request_template.md` SHALL aanwezig zijn met checklist voor: tests toegevoegd, CHANGELOG bijgewerkt, breaking changes gemarkeerd.

#### Scenario: Nieuwe source-adapter PR zonder docs

- **WHEN** een PR een nieuwe adapter toevoegt zonder `docs/sources/<naam>.md`
- **THEN** de PR-checklist MUST een onaangevinkt item tonen
- **AND** reviewers MUST dit als blocking-comment markeren

### Requirement: Miro sub-package consolideert drie clients in gedeelde HTTP-laag

Een `src/iso_audit/miro/` package SHALL bestaan met:

- `client.py`: gedeelde HTTP-laag met `_headers()`, `_post()`, `_get()`, rate-limit handling, retry-logica
- `board_setup.py`: bord-creatie (uit `Ops_to_Biz/audit/miro_board_setup.py`)
- `ingest.py`: bord uitlezen (uit `Ops_to_Biz/audit/miro_ingest.py`)
- `interview.py`: interview-frames (uit `Ops_to_Biz/audit/interview_miro.py`)

Alle drie consumer-modules SHALL `client.py` gebruiken; geen duplicate HTTP-code.

#### Scenario: Twee Miro-modules instantiëren één client

- **WHEN** `board_setup.py` en `ingest.py` allebei een Miro-call doen in dezelfde run
- **THEN** beide MUST dezelfde rate-limit-counter delen
- **AND** geen module MUST eigen `_headers()` of `_post()` definiëren

### Requirement: Documentatie in markdown, geen Sphinx

`docs/` SHALL alleen markdown-bestanden bevatten:

- `docs/sources/{drive,jira,mcp,rest}.md`
- `docs/modes.md`
- README.md, ARCHITECTURE.md, CHANGELOG.md, CLAUDE.md in repo-root

Sphinx, MkDocs of andere doc-generatoren SHALL NOT gebruikt worden.

#### Scenario: PR voegt Sphinx toe

- **WHEN** een PR `sphinx` of `mkdocs` als dependency toevoegt
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar deze requirement

### Requirement: CLI biedt zowel `iso-audit` console-script als `python -m iso_audit`

Het systeem SHALL een console-script entry-point hebben in `pyproject.toml` (`iso-audit = "iso_audit.cli:main"`).

Het systeem SHALL óók aanroepbaar zijn via `python -m iso_audit.pipeline` voor backwards-compatibility met cron- en systemd-gebruikers.

Beide aanroep-vormen SHALL identiek gedrag hebben.

#### Scenario: Console-script aanroep

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source drive --mode autonoom` draait
- **THEN** de CLI MUST starten en de pipeline executen

#### Scenario: Module-form aanroep

- **WHEN** een gebruiker `python -m iso_audit.pipeline --norm 27001 --source drive --mode autonoom` draait
- **THEN** identiek gedrag MUST optreden als bij console-script
- **AND** geen deprecation-warning MUST verschijnen

### Requirement: Examples-directory met geanonimiseerde fixture

Een `examples/fixture-audit-2026-q1/` SHALL geanonimiseerde test-data bevatten:

- Een sample bevindingen-CSV (klein, ≤20 rijen)
- Een sample audit-rapport (markdown)
- Een README dat de fixture beschrijft en gebruik in tests/docs uitlegt

De fixture SHALL gebruikt worden door snapshot-tests en docs-voorbeelden.

Echte audit-data SHALL NIET in de repo staan — alleen geanonimiseerde fixtures.

#### Scenario: Snapshot-test gebruikt fixture

- **WHEN** een snapshot-test draait tegen `examples/fixture-audit-2026-q1/bevindingen.csv`
- **THEN** de output MUST byte-identiek zijn aan de gecommitte snapshot
- **AND** wijziging in classifier-gedrag MUST de snapshot-test breken

#### Scenario: Echte audit-data committed

- **WHEN** een PR een bestand met echte klant-namen toevoegt onder `examples/`
- **THEN** gitleaks MUST in pre-commit OR CI dit signaleren
- **AND** review MUST de PR blokkeren

### Requirement: `Ops_to_Biz/audit/` deprecation en cleanup

Bij milestone-B-merge SHALL `Ops_to_Biz/CLAUDE.md` een sectie hebben:

> **ISO Audit pipeline is verhuisd naar [`MWest2020/iso-audit`](https://github.com/MWest2020/iso-audit) per milestone B (mei 2026). `audit/` directory wordt verwijderd in milestone C.**

Bij milestone-C-merge SHALL `Ops_to_Biz/audit/` volledig verwijderd zijn, inclusief `audit/archive/`.

`Ops_to_Biz/CLAUDE.md` SHALL na milestone C de audit-sectie volledig verwijderd hebben (alleen de pointer-historische-zin in CHANGELOG behouden voor herleidbaarheid).

#### Scenario: Milestone-B-merge

- **WHEN** milestone-B-PR mergeerd in `Ops_to_Biz`
- **THEN** `Ops_to_Biz/CLAUDE.md` MUST de verhuispointer bevatten
- **AND** `Ops_to_Biz/audit/` MUST nog aanwezig zijn (alleen feature-frozen)

#### Scenario: Milestone-C-cleanup

- **WHEN** milestone-C-PR mergeerd in `Ops_to_Biz`
- **THEN** `Ops_to_Biz/audit/` MUST volledig verwijderd zijn
- **AND** geen broken imports MUST overblijven in `Ops_to_Biz`

### Requirement: Vier audit-OpenSpec-changes verhuizen mee

Bij milestone B SHALL de volgende OpenSpec-changes meeverhuizen van `Ops_to_Biz/openspec/changes/` naar `iso-audit/openspec/changes/`:

- `audit-rapport-management-taal`
- `gsuite-iso-audit-automation`
- `miro-kennissessie-generator`
- `hww-2-0`

Per change SHALL er één commit in `iso-audit` zijn die de change toevoegt met paden geupdate naar `iso-audit`-locaties; geen herschrijving van inhoud.

`Ops_to_Biz/openspec/changes/` SHALL deze vier changes na milestone B niet meer bevatten.

#### Scenario: Change-rename leesbare diff

- **WHEN** `audit-rapport-management-taal` wordt verhuisd
- **THEN** de migratie-commit in `iso-audit` MUST alleen path-updates bevatten
- **AND** de inhoud (proposal, design, specs, tasks) MUST byte-identiek zijn aan de Ops_to_Biz-versie behalve geupdate paden

### Requirement: `iso-audit/CLAUDE.md` documenteert nieuwe project-conventies

Een nieuwe `iso-audit/CLAUDE.md` SHALL aanwezig zijn vanaf milestone A met:

- "What this repo is" (audit-pipeline scope, ISO 9001 + 27001)
- Source-protocol uitleg (kort, link naar `ARCHITECTURE.md`)
- Modes-uitleg (kort, link naar `docs/modes.md`)
- OpenSpec-workflow sectie
- Boring & auditable-principe expliciet
- Standaard `uv` workflow (geen `pip`)

#### Scenario: Verse Claude-sessie in iso-audit

- **WHEN** een Claude-sessie wordt gestart in de `iso-audit`-repo
- **THEN** `CLAUDE.md` MUST geladen worden met alle bovengenoemde secties
- **AND** Claude MUST `uv` als default workflow gebruiken voor Python-acties
