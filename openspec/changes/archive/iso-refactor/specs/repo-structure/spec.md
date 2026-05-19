## ADDED Requirements

### Requirement: Standalone `iso-audit` repo met fresh git-history

Het systeem SHALL een nieuwe GitHub-repo `MWest2020/iso-audit` hebben met fresh git-history (niet via filter-repo of subtree-split uit `Ops_to_Biz`).

De repo SHALL private zijn met de volgende beveiliging-instellingen:
- Branch protection op `main`: required pull-request reviews (minimaal 1), required status checks (alle CI-jobs), no force-push, no direct pushes
- Required signed commits (GPG of SSH-signing)
- GitHub Audit Log access wanneer Enterprise-tier beschikbaar is; anders een `compensating-control.md` document dat beschrijft hoe audit-trail-eis op andere wijze wordt geborgd

De repo-naam SHALL `iso-audit` zijn (kebab-case); de Python-package-naam SHALL `iso_audit` zijn (snake_case, PEP 8).

#### Scenario: Initiële commit-graph

- **WHEN** de repo wordt aangemaakt
- **THEN** de eerste commit MUST de scaffolding bevatten zonder verwijzing naar `Ops_to_Biz`-history
- **AND** branch-protection-instellingen MUST verifieerbaar zijn via GitHub API of UI screenshot in milestone-A acceptatie

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

### Requirement: Linting, formatting, typing en security-scanning infrastructuur

Het systeem SHALL `ruff` gebruiken voor linting en formatting met configuratie in `pyproject.toml`.

Het systeem SHALL `mypy --strict` gebruiken op `src/`. Tests MAY een lossere config gebruiken (`--ignore-missing-imports`).

Het systeem SHALL `bandit` gebruiken voor obvious Python-security-smells, geconfigureerd in `pyproject.toml` of `.bandit.yaml`.

Pre-commit-hooks SHALL bevatten: `ruff check`, `ruff format --check` (NOT `--write`), `mypy`, `gitleaks`, `bandit`.

#### Scenario: Code voldoet niet aan ruff-regels

- **WHEN** code committed wordt die `ruff check` faalt
- **THEN** de pre-commit-hook MUST de commit blokkeren met de specifieke regel-violations

#### Scenario: Code introduceert security-smell

- **WHEN** code committed wordt met `subprocess.call(user_input, shell=True)` of equivalent
- **THEN** bandit MUST in pre-commit OR CI dit signaleren
- **AND** de commit/PR MUST geblokkeerd zijn

#### Scenario: Pre-commit format-on-write valkuil

- **WHEN** ontwikkelaars de pre-commit-config aanpassen
- **THEN** de hook MUST nooit `ruff format --write` of equivalent gebruiken — alleen `--check`
- **AND** rationale MUST in `.pre-commit-config.yaml` als comment vermeld staan: voorkomt silent CI-falen

### Requirement: GitHub Actions CI met parallelle jobs

Een `.github/workflows/ci.yml` SHALL parallel jobs definiëren voor:

- `lint`: `ruff check .`
- `format`: `ruff format --check .`
- `typecheck`: `mypy --strict src/`
- `security`: `bandit -r src/`
- `test`: `pytest --cov=iso_audit --cov-report=term-missing --cov-fail-under=<gate>`

CI SHALL draaien op pull-requests naar `main` en op pushes naar `main`.

CI SHALL groen zijn voor merge.

Coverage `<gate>` SHALL bepaald worden in milestone B na baseline-meting: gate = max(baseline + 5%, 70%), plafond bij 85%. Vóór milestone B is een tijdelijke gate van 60% acceptabel.

#### Scenario: PR met failing tests

- **WHEN** een PR-branch test-failures bevat
- **THEN** de `test` job MUST falen
- **AND** PR MUST geblokkeerd zijn voor merge totdat alle jobs groen zijn

#### Scenario: PR met coverage onder gate

- **WHEN** een PR de line-coverage onder de huidige gate drukt
- **THEN** de `test` job MUST falen op de `--cov-fail-under` check

### Requirement: Issue-templates inclusief source-adapter en notifier-adapter contributions

`.github/ISSUE_TEMPLATE/` SHALL vier templates bevatten:

- `bug.md`
- `feature.md`
- `source-adapter.md` — verplichte checklist voor nieuwe Source-adapters: protocol-conformance, contract-tests groen, docs-pagina aangemaakt, healthcheck geïmplementeerd, immutability-test groen
- `notifier-adapter.md` — verplichte checklist voor nieuwe Notifier-adapters: protocol-conformance, contract-tests groen, docs-pagina aangemaakt, DecisionResolver-integratie geverifieerd, healthcheck geïmplementeerd

Een `pull_request_template.md` SHALL aanwezig zijn met checklist voor: tests toegevoegd, CHANGELOG bijgewerkt, breaking changes gemarkeerd, missie-impact overwogen (verandert deze PR de drie capabilities-hooks?).

#### Scenario: Nieuwe source-adapter PR zonder docs

- **WHEN** een PR een nieuwe Source-adapter toevoegt zonder `docs/sources/<naam>.md`
- **THEN** de PR-checklist MUST een onaangevinkt item tonen
- **AND** reviewers MUST dit als blocking-comment markeren

#### Scenario: Nieuwe notifier-adapter PR zonder DecisionResolver-integratie

- **WHEN** een PR een nieuwe Notifier-adapter toevoegt die `DecisionResolver` niet aanroept
- **THEN** de PR-checklist MUST een onaangevinkt item tonen
- **AND** review MUST dit als blocking markeren

### Requirement: Source-, Sink-, Notifier-, Mode-packages volgen consistent patroon

Het systeem SHALL vier protocol-package-directories hebben in `src/iso_audit/`:

- `sources/` met `base.py` (Protocol + Registry), `__init__.py` (export), concrete adapters
- `sinks/` met `base.py` (Protocol + Payload-hierarchy), `__init__.py` (export), concrete sinks vanaf milestone C
- `notifiers/` met `base.py` (Protocol + DecisionResolver + Registry), `__init__.py` (export), concrete adapters
- `modes/` met `base.py` (Protocol + Decision dataclass), concrete modes (`autonoom.py`, `integer.py`)

Het patroon SHALL identiek zijn over de vier packages: zelfde naam-conventie, zelfde Registry-shape (waar van toepassing), zelfde issue-template-structuur, zelfde contract-test-patroon.

Consistentie maakt de codebase uitlegbaar aan externe code-reviewer (zie missie §6 risico).

#### Scenario: Nieuwe protocol-laag toegevoegd zonder consistent patroon

- **WHEN** een PR een vijfde protocol-laag toevoegt (bv. `transformers/`) met afwijkende structuur
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar deze requirement

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

### Requirement: Classifications-tabel ondersteunt traceability voor patroondetectie

Het systeem SHALL een `classifications`-tabel beheren in `iso_audit.db` met schema:

```sql
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY,
    audit_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    prompt_versie TEXT NOT NULL,
    model_versie TEXT NOT NULL,
    raw_output TEXT NOT NULL,
    parsed_klasse TEXT NOT NULL,
    parsed_clausule TEXT,
    confidence REAL,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_classifications_audit ON classifications(audit_id);
CREATE INDEX idx_classifications_finding ON classifications(finding_id);
```

Elke classificatie van een document of bevinding SHALL gepersisteerd worden met deze velden vóórdat de pipeline het classificatie-resultaat consumeert.

Een classificatie zonder deze velden SHALL niet als basis voor patroondetectie (toekomstige spiegel-laag) gebruikt worden.

Bij prompt- of model-wijzigingen SHALL classificaties opnieuw gegenereerd worden; oude rijen blijven staan voor historische traceability.

`prompt_versie` SHALL een string zijn die overeenkomt met een prompt-bestand in `src/iso_audit/classification/prompts/<versie>.md` of equivalent — geen inline prompts, voor reviewbaarheid.

#### Scenario: Classifier persisteert traceability

- **WHEN** de pipeline een document classificeert
- **THEN** een rij MUST in `classifications` worden geschreven met alle verplichte velden gevuld
- **AND** de `decisions`-rij voor dit `classify_finding`-Decision MUST `classificatie_id` correct refereren

#### Scenario: Inline prompt zonder versionering

- **WHEN** een PR een classifier-prompt direct in Python-string definieert
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar deze requirement
- **AND** de prompt MUST verplaatst worden naar `src/iso_audit/classification/prompts/<versie>.md`

### Requirement: Documentatie in markdown, geen Sphinx

`docs/` SHALL alleen markdown-bestanden bevatten:

- `docs/missie.md` — ankerdocument met drie capabilities, PDCA-rol, scope buiten Conduction, beperkingen (versie van `Tool-ontwerp_audit-tool_2026-05-05.md`)
- `docs/sources/{drive,planning,jira,mcp,rest}.md`
- `docs/notifiers/{slack,email,teams,mattermost}.md` (laatste twee placeholder met "TODO: implementatie via eigen change-proposal")
- `docs/modes.md` — inclusief sectie "Modi en de missie" die uitlegt dat autonoom-runs geen capability-3-data leveren
- `docs/sinks/<naam>.md` (vanaf milestone C)
- README.md, ARCHITECTURE.md, CHANGELOG.md, CLAUDE.md in repo-root

Sphinx, MkDocs of andere doc-generatoren SHALL NOT gebruikt worden.

#### Scenario: PR voegt Sphinx toe

- **WHEN** een PR `sphinx` of `mkdocs` als dependency toevoegt
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar deze requirement

#### Scenario: Modes-doc mist missie-sectie

- **WHEN** `docs/modes.md` geen sectie heeft die uitlegt wat autonoom- versus integer-modus betekent voor capability 3
- **THEN** review MUST dit als incomplete markeren onder verwijzing naar deze requirement

### Requirement: CLI biedt zowel `iso-audit` console-script als `python -m iso_audit`

Het systeem SHALL een console-script entry-point hebben in `pyproject.toml` (`iso-audit = "iso_audit.cli:main"`).

Het systeem SHALL óók aanroepbaar zijn via `python -m iso_audit.pipeline` voor backwards-compatibility met cron- en systemd-gebruikers.

Beide aanroep-vormen SHALL identiek gedrag hebben — één `main()` in `iso_audit.cli` waarnaar zowel het entry-point als `__main__.py` als `iso_audit.pipeline` delegeren. Geen duplicate argparse-config.

#### Scenario: Console-script aanroep

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source drive --mode autonoom` draait
- **THEN** de CLI MUST starten en de pipeline executen

#### Scenario: Module-form aanroep

- **WHEN** een gebruiker `python -m iso_audit.pipeline --norm 27001 --source drive --mode autonoom` draait
- **THEN** identiek gedrag MUST optreden als bij console-script
- **AND** geen deprecation-warning MUST verschijnen

#### Scenario: Argparse-config gedupliceerd

- **WHEN** een PR aparte argparse-config introduceert in `__main__.py` en `cli.py`
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar deze requirement

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

`Ops_to_Biz/CLAUDE.md` SHALL óók een notitie bevatten dat `output/business_gws.py` en `output/gws.py` (handbook-pad) niet door deze refactor geraakt worden — die gebruiken Drive voor non-audit-doeleinden en blijven in `Ops_to_Biz`.

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

Per change SHALL de eerste regel van de proposal-Why aangevuld worden met: "Verhuisd uit Ops_to_Biz @ <commit-sha>" als traceability-anker.

`Ops_to_Biz/openspec/changes/` SHALL deze vier changes na milestone B niet meer bevatten.

#### Scenario: Change-rename leesbare diff

- **WHEN** `audit-rapport-management-taal` wordt verhuisd
- **THEN** de migratie-commit in `iso-audit` MUST alleen path-updates en de "Verhuisd uit"-regel bevatten
- **AND** de overige inhoud (proposal, design, specs, tasks) MUST byte-identiek zijn aan de Ops_to_Biz-versie

### Requirement: `iso-audit/CLAUDE.md` documenteert nieuwe project-conventies

Een nieuwe `iso-audit/CLAUDE.md` SHALL aanwezig zijn vanaf milestone A met:

- "What this repo is" (audit-pipeline scope, ISO 9001 + 27001)
- Verwijzing naar `docs/missie.md` als ankerdocument voor de drie capabilities
- Source-protocol uitleg (kort, link naar `ARCHITECTURE.md`)
- Sink-protocol uitleg (kort, link naar `ARCHITECTURE.md`)
- Notifier-protocol uitleg (kort, link naar `ARCHITECTURE.md`)
- Modes-uitleg (kort, link naar `docs/modes.md`)
- OpenSpec-workflow sectie
- Boring & auditable-principe expliciet
- Standaard `uv` workflow (geen `pip`)

#### Scenario: Verse Claude-sessie in iso-audit

- **WHEN** een Claude-sessie wordt gestart in de `iso-audit`-repo
- **THEN** `CLAUDE.md` MUST geladen worden met alle bovengenoemde secties
- **AND** Claude MUST `docs/missie.md` als referentie kennen voor capability-vragen
- **AND** Claude MUST `uv` als default workflow gebruiken voor Python-acties

### Requirement: Missie-document `docs/missie.md` als ankerdocument

`docs/missie.md` SHALL aanwezig zijn vanaf milestone A.

Het document SHALL bevatten (verbatim of licht-geredigeerd uit `Tool-ontwerp_audit-tool_2026-05-05.md`):
- Missie-statement
- Drie capabilities (onafhankelijke bronnen, patroondetectie, auditor-spiegel)
- Architectuur-overview op hoog niveau
- Verschil met bestaande GRC-tools
- PDCA-rol
- Beperkingen en risico's
- Open-source-pad als mitigatie voor tool-eigenaar-single-point-of-failure

Het document SHALL versie- en datum-gestempeld zijn; updates SHALL via dedicated PR's verlopen die expliciet gerefereerd worden in CHANGELOG.

#### Scenario: Missie-update zonder PR

- **WHEN** een commit `docs/missie.md` wijzigt zonder dedicated PR-titel "missie:"
- **THEN** review MUST dit als off-process markeren onder verwijzing naar deze requirement

#### Scenario: Code-PR refereert aan missie

- **WHEN** een PR een feature toevoegt die capability 1, 2 of 3 raakt
- **THEN** de PR-beschrijving MUST expliciet aangeven welke capability geraakt wordt
- **AND** een verwijzing naar het relevante deel van `docs/missie.md` MUST aanwezig zijn
