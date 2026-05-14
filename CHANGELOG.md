# Changelog

Alle relevante wijzigingen aan dit project worden hier vastgelegd.
Format volgt [Keep a Changelog](https://keepachangelog.com/nl/1.1.0/).

## [Unreleased]

### Changed — 2026-05-14 — iso-refactor: §3.1.3-6 (Modes + decisions-tabel)

Eén trunk-commit op `refactor/iso-audit-milestone-b` start Milestone C:

- **§3.1.3** `decisions`-tabel + helpers in `store.py` (append-only audit-trail).
- **§3.1.4** `AutonoomMode` — selectieve persistentie, `delete_data` skip.
- **§3.1.5** `IntegerMode` — Notifier-DI, risico-escalatie, polling met commit-per-iteratie, 24h timeout default.
- **§3.1.6** 18 tests (8 autonoom + 10 integer); threaded resolver-mock met per-thread sqlite-connecties. Cumulatief: 600 tests passed; 80% overall cov.

### Changed — 2026-05-14 — iso-refactor: §2.7 + §2.8 (M-B acceptatie + verhuizing)

Twee commits sluiten milestone B af:

- **§2.7** Vier openspec change-dirs verhuisd naar `MWest2020/iso-audit` (waren hier untracked):
  - `audit-rapport-management-taal/`
  - `gsuite-iso-audit-automation/`
  - `miro-kennissessie-generator/`
  - `hww-2-0/`
- **§2.8.1** `CLAUDE.md` aangepast: `audit/` als DEPRECATED gemarkeerd met pointer naar `iso-audit`-repo; running-section verwijst naar `uv run iso-audit pipeline`. Noot toegevoegd dat `output/business_gws.py`/`output/gws.py` (handbook-pad) niet zijn geraakt.
- **§2.8.2** Pipeline-reproduceerbaarheid verifieerd via gemockte tests in `test_cli.py` + `test_pipeline.py`; geen integratie-run om bestaande `output/`-artefacten niet te overschrijven.
- **§2.8.3** Contract-tests Drive + Planning groen.

### Changed — 2026-05-14 — iso-refactor: §2.6.3-5 (classifications traceability)

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.6.3** `classifications`-tabel toegevoegd aan `store.py` — additief, dedup-key `(audit_id, finding_id, prompt_versie, model_versie)`; indexen op audit_id/finding_id.
- **§2.6.4** `log_classification()` helper + wiring in `_classificeer_doc`/`_classificeer_miro_batch`: schrijven voor JSON-parsing. `_maak_audit_id()` produceert per-run UTC-tijdstempel.
- **§2.6.5** 14 tests in `tests/store/test_classifications.py`. Cumulatief 582 tests passed.

### Changed — 2026-05-14 — iso-refactor: §2.6.1 + §2.6.2 (CLI subcommands + --source)

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.6.1** `cli.py` herschreven naar argparse-met-subparsers (`pipeline`, `doctor`, `setup-template`); `__main__.py` delegeert naar `cli.main`; 15 tests.
- **§2.6.2** `--source` flag verplicht voor `pipeline`, multi-value, met `ISO_AUDIT_DEFAULT_SOURCE`-env-var-fallback (INFO-log) en validatie tegen `beschikbare_bronnen()`. Cumulatief: 568 tests passed.

### Changed — 2026-05-14 — iso-refactor: §2.5.11 + §2.5.12 (assets + config layout)

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.5.11** `assets/` — 3 Conduction-logo-SVG's gekopieerd; `importlib.resources`-toegang.
- **§2.5.12** layout-aanpassing — clause-maps + normteksten + report-template-yaml leven onder `data/` (niet `config/` zoals oorspronkelijk gepland); `service_account.json` niet gemigreerd (credentials horen in `.env`).
- **§2.5.3** taskstatus gefixed (code was al gecommit als `e52c9da`, vinkje vergeten).

### Changed — 2026-05-14 — iso-refactor: §2.5.10 pipeline orchestrator

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.5.10** `pipeline.py` — top-level orchestrator gemigreerd; imports vernieuwd naar `iso_audit.*`; HTML/DOCX/PDF-keten als private helper; `main(argv)` voor testbaarheid; specifieke `OSError`-vangst voor Miro; bandit nosec voor `gws auth status`-subprocess; 21 tests, 79% overall cov. Cumulatief: 553 tests passed.

### Changed — 2026-05-14 — iso-refactor: §2.5.8 + §2.5.9 (interview + ingest)

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.5.9** `ingest.py` — top-level orchestrator; `beschikbare_bronnen()` combineert Source-registry met pseudo-bron `miro`; `--only` valideert tegen die lijst (13 tests, 95% cov).
- **§2.5.8** `interview.py` — interactieve clausule-doorloop; ANSI-helpers, `_vraag_bevinding` met EOF/quit-handling (13 tests, 68% cov; overall gate 82%).

Cumulatief op refactor-branch: **532 tests passed**, alle quality gates groen.

### Changed — 2026-05-14 — iso-refactor: §2.5.6 make_pptx snapshot

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.5.6** `reporting/make_pptx.py` — verbatim-migratie van de hardcoded MT-snapshot-presentatie (2026-03-24); dode imports verwijderd, type-hints toegevoegd; `python-pptx>=1.0.2` runtime-dep; mypy `no-untyped-call` per-module disabled; 5 tests, 96% cov. Cumulatief: 506 tests passed.

### Changed — 2026-05-14 — iso-refactor: §2.5.1 rest (tabular_report + slide_summary + report_generation)

Eén trunk-commit op `refactor/iso-audit-milestone-b`:

- **§2.5.1** `reporting/tabular_report.py` (21 tests, 87% cov) — CSV/Excel-export met thema-grouping; gebruikt `iso_audit.classification.thema` als bron-of-truth (geen duplicatie); `openpyxl` toegevoegd als runtime-dep.
- **§2.5.1** `reporting/slide_summary.py` (8 tests, 98% cov) — Google Slides 5-slide executive summary via `clients/gws._gws`.
- **§2.5.1** `reporting/report_generation.py` (18 tests, 84% cov) — Google Docs template-fill; `_oordeel_zin`/`_oordeel_instructie`-helpers met strikt sjabloon (voorkomt LLM-hedging); management-summary via Anthropic met optionele basis-document fallback (`AUDIT_BASIS_SUMMARY`).
- **verify_docs.py** — bandit `nosec B608` markers op de twee `DELETE … WHERE id IN ({placeholders})` queries (placeholders zijn `?,?,…` zonder user input).
- **Mypy override** — `openpyxl.*` toegevoegd aan `ignore_missing_imports`.

Cumulatief op refactor-branch: **501 tests passed**, alle quality gates groen.

### Changed — 2026-05-14 — iso-refactor: §2.3 source-adapters (gws + Drive + Planning)

Drie trunk-commits op `refactor/iso-audit-milestone-b`:

- **§2.3.1** `clients/gws.py` — verhuisd uit `audit/gws_client.py`; type-hints, bandit-nosec, retry-paden gemockt in 15 tests.
- **§2.3.2-2.3.4** `sources/drive.py` — `DriveSource` adapter implementeert het `Source`-protocol; `@register` decorator zorgt voor auto-discovery; legacy `haal_documenten_op` blijft voor backwards-compat; 29 tests. Protocol-contract-tests voor `drive` nu groen. `conftest.lege_registries` re-importeert bundled adapters bij teardown.
- **§2.3.5-2.3.7** `sources/planning.py` — `PlanningSource` adapter, parsing van auditplanning-tabs (jaar × norm × maand-kolommen); `gws_lees_sheet`/`gws_lees_alle_tabs` toegevoegd aan `clients/gws`; service-account-modus uit `gsa_client.py` geschrapt (consistent met DriveSource via `gws auth login`); 33 tests.

Cumulatief op refactor-branch: **430 tests passed**, alle quality gates groen.

**Nog open in §2.3**: `verify_docs.py` migratie (§2.3.8) — gebruikt nu `gsa_client.py` Sheets-functies; switchen naar `clients/gws.py` is een kleine vervolgcommit.

### Changed — 2026-05-14 — iso-refactor: §2.2.5 finding_classification consolidatie

Eén commit op `refactor/iso-audit-milestone-b`:

- **§2.2.5** `classification/findings.py` — consolidatie van v1 (`finding_classification.py`) + v2 (`finding_classification_20260420.py`). v2 als basis (caching, `Kostenteller`, rehash, dry-run-cost, mis-tag-filter, sharpness-prompts). `review_en_bevestig` uit v1 inline. Legacy `sla_op_in_sheets`-wrapper geschrapt (callers gaan rechtstreeks naar `iso_audit.reporting.sheets_gws`). 43 tests; lazy imports voor `store` / `clause_mapping` / `data.normteksten`; Drive-CLI valt via `importlib` graceful terug als §2.3.2 nog niet beschikbaar is.

Cumulatief op refactor-branch: **349 tests passed**, alle quality gates groen.

### Changed — 2026-05-14 — iso-refactor: §2.5 reporting batch (vier modules)

Vier trunk-commits op `refactor/iso-audit-milestone-b`:

- **§2.5.7** `reporting/sheets_gws.py` — `gws` CLI gemockt; bandit-nosec op subprocess; "Consistent met argocd_sync"-comment verwijderd. 24 tests.
- **§2.5.5** `reporting/landscape.py` — clausule-dekking + interview-grouping + FTS5-zoek; `documents.scope`-kolom-fallback via `OperationalError`-catch. 11 tests.
- **§2.5.4** `reporting/full_report.py` — volledig rapport met normtekst + bewijs + interview + planning; scope + audit_planning beide gracefully gemist als schema-extensies. 15 tests.
- **§2.5.1 (deels)** `reporting/local_report.py` — markdown-rapport met §1-§8 secties + aanbevelingen-tabel; `_THEMA_AANBEVELING` constante; thema-grouping via gemigreerde `iso_audit.classification.thema.bepaal_thema`. 20 tests.

Cumulatief op refactor-branch: **306 tests passed**, alle quality gates groen.

### Changed — 2026-05-14 — iso-refactor: §2.4 + §2.2.7 voltooid op refactor-branch

Vier trunk-commits op `refactor/iso-audit-milestone-b` na de PR-consolidatie:

- **§2.4.4** `miro/ingest.py` — paginatie via MiroClient.paginated_get; 24 tests over kleurconventie, HTML-strip, sticky+text combineren.
- **§2.4.3** `miro/board_setup.py` — HTTP via MiroClient; lazy imports naar `iso_audit.{classification,data,store}`; `MIRO_ISO_PROJECT_ID` env-override; schema-extensies gracefully gemist via `sqlite3.OperationalError`-catch; 20 tests.
- **§2.4.5** `miro/interview.py` — sluit §2.4 af; 13 tests over `_vragen_voor_clausule`/`_uitnodiging_tekst`/`_actieve_sessies` (mocked) + factories.
- **§2.2.7** `classification/llm.py` — was eerder geblokkeerd op store + normteksten; nu unblocked. `SUB_OVERZICHT` + `SYSTEM_PROMPT` lazy gebouwd; 9 tests over batch-flow + error-paden.

Cumulatief op refactor-branch: **236 tests passed**, alle quality gates groen.

### Changed — 2026-05-14 — iso-refactor: 8 PRs geconsolideerd op `refactor/iso-audit-milestone-b`

Trunk-based correctie op de M-B aanpak: 8 feature-branches/PR's was overhead
voor een solo-private repo. Alle 8 zijn nu samengevoegd op één lang-lopende
refactor-branch.

- Branch: `refactor/iso-audit-milestone-b` op `MWest2020/iso-audit`
- Lokaal: 170 tests passed, mypy --strict + ruff + bandit allemaal schoon
- 8 PR's gesloten met verwijzing naar de branch (content behouden)
- Pyproject.toml-conflicten op merge-volgorde opgelost: alle deps geconsolideerd
  alfabetisch in één `dependencies`-lijst; mypy-overrides samengevouwen tot één
  block (`googleapiclient.*`, `google.oauth2.*`, `htmldocx`).

Toekomstig M-B werk gaat **direct op deze branch** of op main (per feedback
[trunk_based]: solo-private repo's = trunk-based, geen PR-per-task).

### Changed — 2026-05-14 — Milestone B van iso-refactor: +2 PRs op iso-audit (totaal 8)

Vervolg-PRs op de iso-refactor (zie eerdere entries voor PR #1-#6):

- **PR #7** `feat/milestone-b-miro-client` — `src/iso_audit/miro/` package met `client.py` (§2.4.1 + §2.4.2 + §2.4.6). `MiroClient` typed wrapper rond `requests`: stateless token-fetch, één-retry-bij-429 + Retry-After, vriendelijke throttle, `paginated_get` generator. `MiroError`/`MiroRateLimitError`. `droog`-mode voor POST. 21 tests, coverage 97% op module.
- **PR #8** `feat/milestone-b-reporting-converters` — `src/iso_audit/reporting/{md_to_html,html_to_docx,html_to_pdf}.py` (§2.5.2). Drie format-converters, geen internal-iso_audit cross-deps. Path-based padresolutie, type-hints over alle signatures, bandit `# nosec` op Chrome-subprocess. 16 tests. Runtime-deps: `markdown`, `python-docx`, `htmldocx`. Mypy-override voor `htmldocx`.

**Blocked op upstream-merges** (zelfde wall als gisteren):
- §2.4.3/§2.4.5 Miro board_setup + interview (lazy-importeren clause_mapping + normteksten)
- §2.4.4 Miro ingest (standalone — kan na PR #7 merge)
- §2.5.1 tabular_report/local_report/report_generation (deps op normteksten + thema)
- §2.5.4/§2.5.5 full_report + landscape (lazy-importeren store + clause_mapping)
- §2.5.3/§2.5.6/§2.5.7 template_setup/make_pptx/sheets_gws — laatste drie zijn standalone qua iso_audit-deps maar het PR-tempo is afhankelijk van merge-pace.

### Changed — 2026-05-13 — Milestone B van iso-refactor: +2 PRs op iso-audit (totaal 6)

Vervolg-PRs op de iso-refactor (zie eerdere entry voor PR #1-#4):

- **PR #5** `feat/milestone-b-auth-notification` — `audit/auth.py` + `audit/notification.py` → `src/iso_audit/` (§2.2.2). 39 tests, `google-api-python-client` + `google-auth` runtime-deps, mypy overrides voor packages zonder `py.typed` marker.
- **PR #6** `feat/milestone-b-thema-classifier` — `audit/thema_classifier.py` → `src/iso_audit/classification/thema.py` (§2.2.6). 24 tests. `THEMA_LIJST` + `THEMA_REGELS` + `bepaal_thema()` geconsolideerd uit `tabular_report.py` — `thema.py` is nu de bron-of-truth voor de taxonomie. `anthropic` + `python-dotenv` runtime-deps.

**Blocked tot upstream-merges**: §2.2.5 finding_classification consolidatie (vereist PR #2 store + PR #4 clause_mapping + §2.3 drive_ingest + §2.4 miro_ingest), §2.2.7 llm_classifier migratie (vereist PR #2 + PR #3 normteksten). §2.2.8 prompts→bestanden pending op §2.2.5/2.2.7.

### Changed — 2026-05-13 — Milestone B van iso-refactor: 4 PRs op iso-audit repo

Voortgang van de iso-refactor in de standalone `MWest2020/iso-audit` repo
(zie `~/projects/iso-audit/`). Vier PR's geopend, alle CI groen:

- **PR #1** `feat/milestone-b-baseline` — fixture-data + snapshot-tests (§2.1.1, §2.1.2)
  + coverage-baseline gemeten (0% op huidig `audit/`, geen tests) (§2.1.3)
  + CI gate 60→70% (§2.1.4).
- **PR #2** `feat/milestone-b-store-migration` — `audit/store.py` → `src/iso_audit/store.py`
  (§2.2.1). Schema-stabiel, 12 unit-tests, 98% coverage op module.
- **PR #3** `feat/milestone-b-normteksten-split` — `audit/normteksten.py` (2956 regels)
  → `data/normteksten/{iso9001,iso27001}.py` + `__init__.py` re-export (§2.2.3).
  22 tests + `lookup()`/`available()` API. Bekende data-gap: 27001 §10.2 ontbreekt
  in bron-dict.
- **PR #4** `feat/milestone-b-clause-mapping` — `audit/clause_mapping.py`
  → `classification/clause_mapping.py` (§2.2.4). 13 tests + `pyyaml` runtime-dep
  + `types-PyYAML` dev-dep + `importlib.resources` voor padresolutie.

`tasks.md` bijgewerkt: §2.1 alles afgevinkt; §2.2.1, §2.2.3, §2.2.4 afgevinkt;
§2.2.2 (auth+notification), §2.2.5 (classifier consolidatie), §2.2.6-2.2.8 open.

### Fixed — 2026-05-13 — `.gitignore` mist `output/` als directory

`.gitignore` had alleen `output/__pycache__/` staan; de hele `output/`-tree was
**untracked maar niet ignored**. Een `git add .` of `git add output/` zou
audit-databases, PDF-rapporten en logs (potentieel met persoonsgegevens) hebben
gecommit. Regel toegevoegd: `output/` (vervangt `output/__pycache__/`). Bestaande
untracked items in `output/` worden nu correct genegeerd (`git check-ignore` bevestigd).

### Changed — 2026-05-13 — Auditmemo management v2 (feedback Marianne Poot)

Tweede versie van de auditmemo voor MT-bespreking, gebaseerd op feedback van
Marianne Poot (hoofd ISO) op v1. Nieuw bestand
`output/audit_reports/management_memo_2026-05-06/Auditmemo_management_2026-05-06_v2.{html,pdf}`
(v1 + PDF blijven naast v2 staan voor audit-trail).

- **Nieuwe Context-sectie** — auditcyclus, geaudite scope (9001 §4-10 + 27001
  §4-10 incl. Annex A), geraadpleegde bronnen, voorbehoud toolscope (Jira/Calendar/
  Notion/Slack buiten Drive) met oplossing (aanvullend interview), bespreking
  6 mei 2026 met hoofd ISO.
- **NC 1** — "Aanbeveling" → "Vereiste corrigerende maatregel"; norm + letterlijke
  tekst van ISO 9001/27001 §10.2 toegevoegd; effectiviteits-evaluatie als ontbrekend
  element expliciet benoemd (Marianne's eigen observatie).
- **NC 2** — Alex-casus verwijderd (niet onderbouwd in audit-data); alleen Goya;
  norm + letterlijke tekst van ISO 27001 §6.5, §5.11 en §5.18 toegevoegd; drie
  ontbrekende elementen concreet uitgesplitst.
- **Verbeterpunt logging** — norm + letterlijke tekst van Annex A §8.15 en §8.16
  toegevoegd; expliciet blok "Waarom verbeterpunt en geen NC?".
- **Nieuwe sectie "Status eerder geconstateerde NC's"** — tabel met externe
  controles 2023 + 2024 en v3.3 NC's voor afvinken in volgende MT.

### Changed — 2026-05-05 — Audit-rapport v2.5 — bug-fixes op v2 review

Zeven correcties op `audit/v2_handmatig.py` na review-feedback op v2-rapport.
Output naar nieuwe directory `output/audit_reports/audit_2026-05-04_handmatig_v25/`
zodat v2 als audit-trail blijft bestaan.

- **§4 / §5 norm-split gefixt**: `klopt_norm()` filterde op clausule-prefix 4–10,
  waardoor alle 27001 Annex A bevindingen (5.x–8.x) ook in §4 (9001) belandden
  en §5 leeg bleef. Nu wordt op de `norm`-kolom uit CSV gefilterd; "beide" gaat
  naar §5. Resultaat: §4 toont nu 10 9001-clausules, §5 toont 69 27001-controls.
- **Aanbevelingen — clausule-sortering** (`render_aanbevelingen`): clausules
  per thema werden alfabetisch gesorteerd, waardoor "10.x" voor "4.x" kwam en
  truncatie op 6 items toevallig identieke lijsten gaf voor de top-2 thema's.
  Nu sortering op aantal OFI's per clausule, met aantal in de output ("10.2 (11),
  8.16 (6), ..."). Lost ook "...." (4 dots) op door cleane "+ N andere" suffix.
- **Voorbeelden in §3 verwijzen naar §-anker**: was "Voorbeeldbevindingen in
  §4 / §5"; nu top-2 clausules met aantal en juiste sectie-nummer ("§4 clausule
  10.2 (11 OFI's) en §4 clausule 8.16 (6 OFI's)").
- **Aanbeveling 6 voor 'Overig'**: 110 niet-thematisch-geclusterde OFI's kregen
  in v2 alleen een verwijzing naar de Excel; nu een eigen SMART-aanbeveling met
  KAM-coördinator als eigenaar voor handmatige triage richting v3.
- **§6.1 confidence-tabel**: kop "Onderbouwing per OFI" + intro "44% van OFI's"
  was inconsistent met tabel die ook positief + geen-bevinding telde. Tabel nu
  alleen OFI's; totalen kloppen 1-op-1 met aanbevelingen-cijfers.
- **§6.2 NC-trigger-rule kandidaten zichtbaar**: was alleen beleidsstatement;
  nu altijd berekend (54 kandidaten op 4-mei CSV) en als tabel getoond met
  expliciete auditor-afweging-tekst (geen retroactieve promotie naar NC, met
  reden volgens ISO 19011). Geeft Marianne en externe certificeerder het
  audit-spoor. `detect_nc_triggers()` toegevoegd naast `reclassify_nc()` — die
  laatste muteert wel, eerste niet.
- **§6.2 traceerbaarheid per kandidaat**: generieke groepsverklaring vervangen
  door per-item-afweging. Tool leest `SRC_DIR/NC_afwegingen_2026-05-04.csv`
  (kolommen: `clausule`, `document_naam`, `triggers`, `auditor_nc_review`,
  `auditor_nc_note`). Bestand wordt automatisch als lege template aangemaakt
  bij eerste run; auditor vult per kandidaat in, tool merget bij volgende run.
  §6.2 toont nu "X van 54 beoordeeld, Y nog open" + tabel met afweging-kolom.
  Standaard-beoordelingsgronden (ISO 19011) expliciet vermeld: "Bewijs aanwezig
  elders" / "Correctieve actie reeds in gang" / "Procedureel — werking
  aantoonbaar" / "Geen feitelijk hiaat".
- **AI-jargon 'formalisering'**: vijf voorkomens in onderbouwing-tekst uit v1.
  `sanitize_jargon()` toegevoegd: render-time vervanging van "formalisering" →
  "vastlegging" (case-preserved). CSV/XLSX behouden raw v1-tekst voor audit-trail.
  Ook `formalisering` toegevoegd aan `VERBODEN_AI_WOORDEN` als drift-vangnet.
- **Footer**: "_Gegenereerd door geautomatiseerd audit-systeem (v2)_" verwijderd
  ten gunste van neutraal "_Document datum: ... · Versie: v2.5_". Reviewer-tip:
  expliciete AI-markering bevestigt Mariannes "lijkt door AI gegenereerd"-kritiek;
  ondertekening door auditor is wat telt.

Telling ongewijzigd: 0 NC, 299 OFI, 122 positief, 15 geen bevinding (totaal 436).

### Changed — 2026-05-04 — Audit-rapport: structurele herziening (Fase 3)

Op basis van Marks tips A/B/C: aanbevelingen vooraan, in 4-veld-format, summary
ingekort. Doel: management krijgt eerst de acties, niet pas na 90 pagina's
bevindingen.

- **Nieuwe §3 Aanbevelingen** (`audit/local_report.py:_render_aanbevelingen`):
  geprioriteerde tabel vóór de bevindingen-secties. Kolommen: # / Thema (aantal)
  / Wat (deliverable) + Toets-criterium / Wie / Wanneer.
  - NC-rijen eerst, gegroepeerd per documentbron (b.v. één rij voor alle 8
    NC's uit `incidentrapport-2026-04-21-v0.9.docx`). Voorkomt onbruikbare
    "Overig"-clustering die `bepaal_thema()` voor NC-beschrijvingen gaf.
  - Top-5 OFI-rijen daarna, met data-gegrond `wat` en `toets` uit nieuwe dict
    `_THEMA_AANBEVELING` (12 thema's × 4 velden: wat / wie / wanneer / toets +
    norm-eis-koppeling).
  - **Wie / Wanneer** worden bewust open gelaten als "(rol in te vullen)" /
    "(deadline in te vullen)" — die staan niet in de auditdata en horen door
    het MT te worden vastgesteld in de directiebeoordeling. Geen verzonnen
    eigenaars meer.
- **Sectie-nummering** verschoven: §1 Summary → §2 Resultaten → §2a OFI-uitleg
  → §3 Aanbevelingen → §4 Bevindingen 9001 → §5 Bevindingen 27001 → §6
  Ontbrekend → §7 Gearchiveerd → §8 Handtekening.
- **§2a Wat zijn OFI's** ingekort tot alleen de definitie + verwijzing naar §3.
  De Top-5 thema-tabel is verhuisd naar §3 in 4-veld-format.
- **Management summary inkort** in `_management_summary_prompt`:
  geen "drie verbetergebieden"-paragrafen meer (die staan in §3). Summary
  beperkt tot intro + 1 alinea verwijzing → §3 + positieve bevindingen + 1
  bridging-zin + 1 oordeel-zin. Max 200 woorden.
- **Strikt oordeel** via `_oordeel_zin()`: bij NC > 0 schrijft de prompt nu
  letterlijk voor: "De organisatie voldoet niet aan de norm vanwege N
  geconstateerde non-conformiteiten; correctieve maatregelen vereist (zie §3)."
  Voorheen kon het LLM hedgen met "voldoet onder voorbehoud" terwijl de
  meta-tabel "**onvoldoende**" zei. Inconsistentie weg.
- **Revisie-modus** (`_revise_summary_prompt`): naast cijfer-update ook expliciete
  oordeel-update-instructie. Voorheen behield het LLM "voldoet aan de norm"
  uit s05 ondanks dat de actuele DB 14 NC's heeft.
- **Lead-auditor sectie** in s05 (Softwarecatalogus + Innovatie/AI) wordt in
  revisie-modus verwijderd uit de summary; die acties zitten nu in §3.

Verificatie via 8 geautomatiseerde checks (cijfers, §3+4-veld, §4 nummering,
strikt oordeel, geen 'prominent', geen NC-woorden in §3, data-kwaliteit, auditor-
frame). Alle 8 groen op beide outputs (`audit_2026-05-04_marianne` en
`audit_2026-05-04_fulltest`). Beide hebben alle 6 formaten (md, html, docx, pdf,
csv, xlsx).

### Fixed — 2026-05-04 — Audit-rapport: 6 bugs uit handmatige review

Na de eerste rapport-revisie heeft Mark zes structurele bugs in de outputs
geïdentificeerd. Alle gefixt en geverifieerd via geautomatiseerde checks.

- **Bug 1 (clausule_titel)** — `pipeline.py:run_report_only` had `clausules =
  laad_clause_map(norm)` waar het `clause_map.get("clausules", {})` moest zijn.
  Daardoor was elke titel-lookup een miss, met fallback op clausule_id zelf.
  Resultaat: "Clausule 10.1: 10.1" in elke kop. Nu correct: "Clausule 10.1:
  Algemeen (verbetering)".
- **Bug 2 (lege OFI's)** — `audit/local_report.py:_render_clausules_met_themas`
  toonde 142 OFI's zonder beschrijving + onderbouwing als losse bullets met
  "_(geen beschrijving)_". Nu per thema/clausule samengevat: "X bevinding(en)
  zonder inhoudelijke onderbouwing — geclassificeerd op basis van documenttitel;
  vereist handmatige review" + bullet-lijst van Drive-links.
- **Bug 3 (tel-inconsistentie)** — `local_report.py:schrijf_rapport` toonde
  "Totaal" als `len(bevindingen)` (raw row count incl. 'geen bevinding'-rijen)
  terwijl de classificatie-rijen NC+OFI+pos optelden. Nu aparte rij voor 'Geen
  bevinding (uit data, niet geclassificeerd)' en totaal als som van alle vier
  classificaties — sluit precies aan op het CSV-rijen-aantal.
- **Bug 4 (Drive-rommel)** — documenten met "VERWIJDEREN", "TEMPLATE KOPIE
  MAKEN" of "OUD:"-prefix verschenen als bevindingen. `pipeline.py` heeft nu
  `_filter_ruis()` dat in `run_audit` én `run_report_only` deze documenten uit
  de rapport-stream weert. DB blijft raw; alleen de rendering filtert. Resultaat:
  487 → 476 bevindingen in rapport/CSV/XLSX (11 ruis-items weggefilterd).
- **Bug H (dubbele kop)** — als titel == clausule_id (oude data): "Clausule X.Y:
  X.Y". Nu: alleen "Clausule X.Y" in dat geval.
- **Bug bonus (cijfer-mismatch revisie-modus)** — bij `AUDIT_BASIS_SUMMARY`
  hield het LLM de cijfers uit s05 vast (309 OFI / 0 NC) terwijl de huidige DB
  iets anders toonde. Revisie-prompt krijgt nu een ACTUELE CIJFERS-blok mee
  (totalen + top-8 clusters per classificatie) met expliciete instructie de
  cijfers te updaten. Tekstuele structuur en formuleringen blijven, alleen
  cijfers worden ververst.
- **Tip G (data-kwaliteit-disclaimer)** — `local_report.py` voegt nu een regel
  toe aan de management summary: "X van Y OFI's (Z%) zijn geclassificeerd op
  basis van documenttitel zonder inhoudelijke analyse. Deze vereisen handmatige
  review voordat ze in een actieplan worden opgenomen." Eerlijkheid over
  audit-grond.
- **Bug bonus (HTML/DOCX/PDF in run_audit)** — eerder zaten deze conversies
  alleen in `run_report_only`. Nu ook in `run_audit`, zodat full-pipeline-runs
  alle 6 formaten produceren zonder handmatige naconversie.

Verificatie via `output/audit_reports/audit_2026-05-04_marianne/` (revisie) en
`audit_2026-05-04_fulltest/` (data-modus). Alle 6 checks groen.

### Changed — 2026-05-04 — Audit-rapport taal voor management (n.a.v. feedback Marianne)

Marianne heeft op 2026-05-04 op rapport s05 (2026-04-20) zes punten teruggegeven:
auditor-frame i.p.v. organisatie-frame, SMART-eis per thema, bridging bij gemengde
clusters, ISO-jargon vertalen, OFI uitleggen + aggregeren, geen NC-woorden in
aanbevelingen. Doel: management krijgt handelingsperspectief uit het rapport.

- `audit/report_generation.py`:
  - `_management_summary_prompt` herschreven: auditor-frame ("uit de audit blijkt"),
    SMART-blok per thema (constatering met concrete documenten + actie + eigenaar/
    horizon), verplichte bridging-zin als clausule >5 OFI én >5 positief heeft,
    jargon-vertaling expliciet (8.16 → "diensten van derden"; 4.1 → "inzicht in
    markt/klanten/stakeholders"), verbod op woorden "prominent", "drie kritieke
    gebieden", placeholders zoals `[rol]`/`[datum]`.
  - `_genereer_management_summary`: `max_tokens` verhoogd naar 2000 zodat
    SMART-blokken niet afgekapt worden.
  - `_top3_aanbevelingen` herschreven naar LLM-call met positieve template ("doe X
    om Y te bereiken"), met fallback op feitelijke top-3 bij API-failure.
  - `check_verboden_woorden()` + `VERBODEN_AANBEVELING_WOORDEN`: post-validatie van
    NC-woorden in aanbevelingen-output (logging-warning).
- `audit/local_report.py`:
  - Nieuwe sectie 2a "Wat zijn OFI's" met definitie + Top-5 thema-aggregatie­tabel
    (thema, aantal, voorgestelde aanpak) bovenaan de bevindingen-secties. "Overig"
    fallback-bucket uitgesloten uit top-5; aparte voetnoot.
  - `_THEMA_AANPAK` mapping voor voorgestelde aanpak per thema.
- `audit/pipeline.py`:
  - Nieuwe flag `--report-only`: regenereert rapport vanuit bestaande
    bevindingen-DB (`output/audit.db`) zonder Drive/Miro/classificatie. Eén
    Claude-call (~5 cent) i.p.v. volledige re-classificatie. Doel: snel itereren
    op rapport-taal zonder kosten op classificatie-laag.
- `openspec/changes/audit-rapport-management-taal/`: change-proposal, tasks,
  spec-deltas voor `report-generation`-capability.
- `output/audit_reports/before_after_management_summary.md`: voor- en na-tekst
  per kritiekpunt op basis van echte s05-cijfers (309 OFI / 0 NC / 123 positief);
  basis voor overleg met Marianne.
- `output/audit_reports/audit_2026-05-04/`: nieuwe rapport-subfolder. Bevat alle
  formaten (md, html, docx, pdf, csv, xlsx). Sheets-sync wordt uitgevoerd als
  `AUDIT_SHEETS_ID` env var gezet is.
- Per-run subfolder: `audit/local_report.py` en `audit/tabular_report.py` schrijven
  output nu in `output/audit_reports/audit_<datum>/`. Override via `AUDIT_RUN_ID`
  (alleen subfolder-naam, vrij formaat) of `LOCAL_REPORT_DIR` (volledig pad).
  Bestaande s05-output verplaatst naar `audit_2026-04-20_s05/`.
- Haiku review-loop (10 iteraties, ~30 cent totaal): convergentie bereikt — alle
  6 Marianne-criteria onafgebroken VOLDAAN sinds iter 4. Iter 8 en 10 oordeel
  KLAAR/VERBETER met alleen micro-restpunten. Logbestanden in
  `output/haiku_iteraties/iter_03.txt` t/m `iter_10.txt` voor audit-trail.
- `audit/_haiku_review.py`: tijdelijk hulpmiddel voor de loop. Stuur huidig
  rapport door Haiku, vergelijk met Marianne's feedback, geef VOLDAAN/DEELS/NIET
  per punt + KLAAR/VERBETER eindoordeel. Niet onderdeel van de pipeline.

**Validatie**: één test-run met `--report-only --norm beide` succesvol. Rapport
bevat de zes correcties die Marianne vroeg. Volledige re-classificatie (full
pipeline-run) bewust niet uitgevoerd: feedback raakt taal, niet classificatie;
herclassificatie van 309 OFI's zou onnodig duur zijn.

**Open**: Marianne-akkoord op nieuwe vorm tijdens overleg vóór archivering van
de OpenSpec-change. Eén minor restpunt: LLM-summary noemt soms `[datum audit]`
als metadata-veld bovenaan; datum staat al in de meta-tabel — kan eventueel
post-fix met regex strip of expliciete prompt-instructie.

### Changed — 2026-05-01 — argocd_sync schrijft Sheets via service account (geen `gws` CLI meer)

De dagelijkse browser-verificatie van de derde-partij `gws` CLI was de
laatste werkelijke afhankelijkheid waardoor de timer regelmatig in een
SKIP eindigde. De Sheets-uitvoer maakt nu rechtstreeks gebruik van de
Google Sheets API met een service account + domain-wide delegation —
zelfde patroon als de audit-pipeline (`audit/gsa_client.py`).

- `argocd_sync/sheets_client.py` (nieuw) — minimale Sheets API wrapper
  met `lru_cache`'d credentials/service. Functies: `get_values`,
  `ensure_tab`, `clear_range`, `batch_update_values`, `col_letter`.
  Subsystemen blijven onafhankelijk (per `CLAUDE.md`-conventie); geen
  import van `audit/`.
- `argocd_sync/output/gws.py` — herschreven, geen `subprocess`-calls
  naar `gws` meer. Module-naam blijft `gws.py` zodat `OUTPUT_MODE=gws`
  en `sync.sh` ongewijzigd werken.
- `argocd_sync/output/business_gws.py` — idem; importeert `_col_letter`
  / `ensure_tab_exists` niet meer uit `output.gws` maar uit
  `sheets_client`.
- **Env-vars (volgorde van prioriteit):**
  - `GOOGLE_SERVICE_ACCOUNT_FILE` (voorkeur, gelijk aan audit-pipeline)
  - `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` (legacy alias, blijft werken)
  - `GOOGLE_IMPERSONATE_USER` (verplicht; zelfde gebruiker als audit)
- **Vereist eenmalige actie:** de SA die argocd_sync gebruikt moet in
  Google Workspace admin (Security → API controls → Domain-wide
  delegation) de scope `https://www.googleapis.com/auth/spreadsheets`
  hebben. Snelste route: zet `GOOGLE_SERVICE_ACCOUNT_FILE=audit/config/
  service_account.json` in `.env` — die SA heeft Sheets DWD al
  geautoriseerd voor de audit-pipeline. Alternatief: voeg de scope toe
  aan de legacy `gws-credentials.json` SA in Workspace admin.
- **Test (gedeeltelijk, 2026-05-01 13:14):** handmatige run faalde nog
  op `unauthorized_client: ... not authorized for any of the scopes
  requested` — dat is precies het scope-config-issue hierboven, niet
  een codebug. Soft-fail werkt: service exit `0/SUCCESS`, één SKIP-regel
  in journal, geen broadcast. Eerdere stappen (fetch 193 apps, enrich
  101 rijen) zijn wel goed gegaan.
- **Vervolgstap voor de gebruiker:** kies optie A of B uit de
  Workspace-admin-config hierboven, dan opnieuw
  `systemctl --user start argocd-sheets-sync.service` om end-to-end te
  bevestigen.
- `.env.example` — gws-sectie bijgewerkt: oude "GCP service account
  JSON key file" comment vervangen door uitleg dat argocd_sync nu via
  de Sheets API werkt en dezelfde `GOOGLE_SERVICE_ACCOUNT_FILE` /
  `GOOGLE_IMPERSONATE_USER` env-vars gebruikt als de audit-pipeline.
  `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` blijft als legacy alias.
- `~/.claude/hooks/pre-tool-use.sh` (buiten dit repo) — allowlist
  toegevoegd voor `.env.example` / `.env.sample` / `.env.template` (en
  dash-varianten) zodat template-bestanden bewerkt mogen worden;
  echte `.env` en `.env.local`-achtigen blijven geblokkeerd.

### Fixed — 2026-05-01 — mcc-login wacht op werkende DNS bij boot

Tijdens hetzelfde incident bleek de eigenlijke onderliggende oorzaak:
`mcc-login.service` (waar `argocd-sheets-sync.service` met
`After=mcc-login.service` aan vasthangt) draaide bij boot om 07:51
nadat de timer met `Persistent=true` de gemiste 05:00-run inhaalde,
maar `network-online.target` is op deze workstation al ready voordat
DNS via het corp/VPN-pad werkelijk bereikbaar is. De `mcc` CLI kreeg
`network is unreachable` op `api.emk.fuga.cloud`. De python-wrapper
logde `Warning: ... (partial success possible)` en exit'te 0, dus
systemd zag de service als geslaagd terwijl de kubeconfig nooit
ververst werd — daardoor faalde `enrich.py` later op een lege
`kubectl get pvc` output.

- `~/.config/systemd/user/mcc-login.service` — `ExecStartPre=` regel
  toegevoegd die in een `for`-loop tot 60 seconden wacht op
  `getent hosts api.emk.fuga.cloud`. Bij timeout exit 1 met een duidelijk
  journal-bericht; main `ExecStart` wordt dan niet uitgevoerd. Geen
  `OnFailure=` ingesteld, dus een timeout is een stille failure
  (alleen status-flag in `systemctl status`).
- `systemctl --user daemon-reload` uitgevoerd.
- **Test 1:** handmatige `systemctl --user start mcc-login.service` —
  `[mcc] Daily signin completed successfully!` in journal, alle drie
  clusters (test-accept, conductionprod, con-prod) toegevoegd, kubeconfig
  bijgewerkt.
- **Test 2:** end-to-end, handmatige `systemctl --user start
  argocd-sheets-sync.service` — fetch (193 apps) + enrich (685 PVCs,
  258 Nextcloud-PVCs, 101 rijen verrijkt) draaiden zonder fouten. De
  `gws`-output stap viel om op een verlopen `gws` auth-token, en de
  soft-fail uit het eerdere changelog-item ving dat netjes op met één
  regel `SKIP: output/gws.py exited 1`. Service exit `0/SUCCESS`, geen
  broadcasts. Hele keten gedraagt zich nu zoals bedoeld.
- **Niet gewijzigd:** de python-wrapper `~/CONDUCTION/toolchain/mcc/cli.py`
  zelf — die slikt nog steeds netwerkfouten en exit 0 met een warning.
  Voor nu acceptabel omdat de `ExecStartPre` precies dat scenario
  voorkomt; eventueel later strakker maken in de toolchain repo.

### Changed — 2026-05-01 — argocd-sync timer faalt nu stil

Na een incident waarbij het dagelijkse `argocd-sheets-sync.timer` de
gebruikerssessie verstoorde (oorzaak: `OnFailure=` triggerde
`wall --nobanner` naar alle TTYs/pty's bij elke transient fout — stale
`gws` token op 2026-04-30, niet-bereikbare ArgoCD-host op 2026-05-01
boot voordat het netwerk klaar was) zijn de volgende wijzigingen
doorgevoerd zodat de timer "convenience-friendly" wordt: geen broadcasts,
audit-trail blijft volledig in journald.

- `~/.config/systemd/user/argocd-sheets-sync.service` — `OnFailure=
  argocd-sync-failed-notify.service` regel verwijderd.
- `~/.config/systemd/user/argocd-sync-failed-notify.service` — verwijderd
  (`wall`-broadcast was de oorzaak van de sessie-verstoring).
- `argocd_sync/sync.sh` — elke python-stap (`fetch.py`, `enrich.py`,
  `output/{local,gws,business_local,business_gws}.py`) wordt nu omhuld
  met een `set +e` / `rc=$?` / `set -e` blok plus een `skip_if_failed`
  helper. Bij non-zero exit logt het script één regel
  `"[sync] SKIP: <step> exited <rc>..."` en exit 0. De volledige
  stack-trace blijft in journald via `StandardError=journal`.
- `systemctl --user daemon-reload` uitgevoerd.
- **Test:** `bash -n sync.sh` (syntax OK). Eerstvolgende geplande run is
  `*-*-* 06:00:00` (volgende ochtend); journal moet dan een SKIP- of
  succes-regel tonen, geen `wall`-broadcast meer.
- **Niet gewijzigd:** `.bak.20260428` files in `~/.config/systemd/user/`
  (eerdere baseline, niet aangeraakt).

### Added — 2026-04-29 — Nextcloud storage usage in argocd-sync

Nieuwe kolom `nextcloud_storage_used` (bv `4.2G`) in zowel `Deployments`
als `Business` tab van de gekoppelde Google Sheet, voor inzicht in actueel
data-gebruik per Nextcloud-installatie.

- `argocd_sync/storage.py` (nieuw) — haalt PVC-usage uit kubelet
  `/stats/summary` voor CSI-volumes en uit `du -sh pvc-*` op
  `nfs-server-provisioner-0` voor NFS-volumes; aggregeert alle PVCs
  met "nextcloud" in de naam (excl. sidecars: mariadb, redis, postgres,
  pgbouncer, imaginary, collabora, onlyoffice, elasticsearch) per
  namespace.
- `argocd_sync/enrich.py` (nieuw) — leest fetch-output, vult
  `nextcloud_storage_used` op rijen die als Nextcloud-app classificeren
  (`nc-{customer}-{env}` of legacy `*nextcloud*`). Aborteert hard als de
  cluster-lookup faalt, zodat een verlopen kubeconfig geen lege strings
  naar de Sheet schrijft.
- `argocd_sync/upsert.py` — kolom toegevoegd aan `OWNED_COLUMNS`.
- `argocd_sync/transform.py` — `pivot()` geeft `nextcloud_storage_used`
  door naar de business view.
- `argocd_sync/output/business_{gws,local}.py` — kolom toegevoegd
  tussen product-booleans en versie-kolommen.
- `argocd_sync/sync.sh` — extra enrich-stap tussen fetch en
  output-writers; tmp-cleanup uitgebreid met `ENRICHED_FILE`.
- **Test:** handmatige run `OUTPUT_MODE=gws ./argocd_sync/sync.sh` —
  201 rijen naar `Deployments`, 107 naar `Business`. 101 Nextcloud-rijen
  hebben een waarde, 5 leeg (namespaces bestaan niet meer in cluster:
  acato, io, opengemeenten, openpdd-gooisemeren, tilburg-preprod;
  identiek aan de bestaande versions-check failures).
- **Bekende beperking:** in legacy namespaces met meerdere envs in één
  ns (bv `alkmaar` met zowel accept als prod) krijgen alle business
  rows van die namespace dezelfde waarde — de som van alle Nextcloud
  PVCs in de ns. Voor nieuwe `nc-{customer}-{env}` namespaces is het
  1-op-1 correct. Op te lossen door per PVC op app-naam te matchen
  i.p.v. per namespace te aggregeren.

### Fixed — 2026-04-28 — argocd-sheets-sync systemd unit

`argocd-sheets-sync.service` faalde sinds een onbekende datum met exit
203/EXEC: `Unable to locate executable /home/gongoeloe/projects/Ops_to_Biz/sync.sh`.
Oorzaak: `sync.sh` is bij eerdere reorganisatie verhuisd naar
`argocd_sync/sync.sh`, maar de unit-files (zowel actieve user-unit als
in-repo) wezen nog naar het oude pad.

- `argocd_sync/systemd/argocd-sheets-sync.service`
  - `ExecStart` → `…/Ops_to_Biz/argocd_sync/sync.sh` (was `…/Ops_to_Biz/sync.sh`).
  - `After=` aangevuld met `mcc-login.service` zodat kubeconfig-refresh
    eerst draait.
  - `OnFailure=argocd-sync-failed-notify.service` toegevoegd. Beide stonden
    wél in de actieve user-unit, niet in de in-repo bron.
- `~/.config/systemd/user/argocd-sheets-sync.{service,timer}` — vervangen
  door symlinks naar `argocd_sync/systemd/…`. Originele files bewaard als
  `*.bak.20260428`. Source-of-truth nu in repo (consistent met dagcheck).
- **Test:** `systemctl --user daemon-reload && systemctl --user start
  argocd-sheets-sync.service` — `sync.sh` start nu correct, fetcht 193
  ArgoCD apps. Faalt daarna in `argocd_sync/output/gws.py:25` op
  `gws sheets values get` (CalledProcessError exit 1) — separate Google
  Sheets/`gws` CLI issue, niet onderdeel van deze fix.

### Added — 2026-04-20 — Finding classification v2 (refactor)

- **`audit/finding_classification_20260420.py`** (nieuw, originele file ongewijzigd)
  - **System prompt met `cache_control` (ephemeral)** — statische delen (auditor-
    persona, PDCA-regels, JSON-format) gecached; user prompt bevat alleen
    variabele per-call data. 5-10x goedkoper op de statische helft bij herhaalde
    calls binnen 5 min.
  - **Per-call token usage tracking** via `Kostenteller` dataclass
    (`resp.usage.input_tokens / output_tokens / cache_read_input_tokens /
    cache_creation_input_tokens`). Eindrapport toont calls, tokens,
    cache-split en $ per run.
  - **Kostenschatting vooraf** (`schat_kosten()` + `--dry-run-cost` flag) —
    rekent per doc het verwachte token-verbruik uit (chars/4) en houdt
    rekening met cache-write-then-read patroon. Geen API-calls nodig.
  - **Checkpoint op (doc_id, clausule_id, norm)** in plaats van alleen `doc_id`.
    Voorheen: doc ooit geclassificeerd → nooit meer aangeraakt (ook niet voor
    nieuwe clausules). Nu: alleen de daadwerkelijk al gedane combinaties
    worden geskipt.
  - **`rehash=True` + UPSERT** — dwingt herclassificatie af, bestaande rows
    worden overschreven via `ON CONFLICT(...) DO UPDATE SET`.
  - **Configureerbaar model** via `AUDIT_CLASSIFICATION_MODEL` env (default
    Haiku 4.5; Sonnet/Opus mogelijk).
  - `review_en_bevestig` en `sla_op_in_sheets` gere-exporteerd uit originele
    module (ongewijzigd gedrag).

- **`audit/pipeline.py`**
  - Switched naar `finding_classification_20260420` (v2 classifier).
  - Nieuwe flags `--rehash` en `--dry-run-cost`.
  - `run_audit()` accepteert `rehash` + `dry_run_cost` kwargs.

### Why

Oude module had drie problemen (gediagnosticeerd tijdens chapter-7 run):
1. `INSERT OR IGNORE` + doc-level checkpoint = geen re-run mogelijk zonder
   handmatig DB-sleutelen. Chapter-switch skipte onterecht docs.
2. Geen `resp.usage` capture = kostenschattingen op basis van guess i.p.v.
   werkelijke token-counts (memory: "centen → dollars").
3. Geen prompt caching = statische prompt (persona + rules) werd voor elke
   call opnieuw volledig gerekend.

v2 lost alle drie op zonder breaking API — `classificeer_alle_bevindingen()`
heeft dezelfde signature plus optionele `rehash` en `model` kwargs.

### Test

- `python3 -m audit.pipeline --norm 27001 --chapter 7 --rehash --dry-run-cost`
  toont kostenschatting zonder API-calls
- Imports en `--help` schonen correct
- Refactor is side-by-side: originele `finding_classification.py` blijft intact
- **Volledige rehash-run `--norm beide --scherpte 0.5 --rehash --thema-llm`**
  (2026-04-20): 75 calls / 451 findings / 19.5 min / **$0.39** / 0 fouten.
  Prompt caching was niet actief: system prompt ~600 tokens < 1024-minimum.
  Aanpak voor vervolg: verrijk system prompt (Conduction-profiel, norm-
  referenties) naar >1024 tokens om cache te activeren.

### Fix — 2026-04-20 — Miro zonder clausule skip

- `finding_classification_20260420.py`: Miro-notities zonder `clausule` worden
  overgeslagen met warning (voorkomt NOT NULL constraint crash bij UPSERT).
  Oorzaak: Miro board bevat sticky notes die niet aan een clausule-clausule-
  frame gebonden zijn. 139 van 170 notities waren zo in de huidige run.

### Changed — 2026-04-20 — Classifier context + misclassificatie filter + management summary

Drie fixes naar aanleiding van review van de management summary:

1. **Conduction-specifieke context in `_SYSTEM_GENUANCEERD`**
   - BYOD: laptops zijn eigendom van de medewerker — formele retournering
     (5.11 / 6.5) beperkt tot klein materiaal. Ontbreken formele procedure
     → OFI, niet NC (tenzij ook data-/toegangsrevocatie ontbreekt).
   - Informatieclassificatie (5.12): interne documenten zijn
     vertrouwelijkheid-geindexeerd in de handleidingen (4 audits bevestigd).
     5.12 intern = positief; NC alleen voor externe documenten/communicatie.

2. **Miro mis-tagging filter** (`_is_miro_mistag`)
   - Items waar de LLM-classificatie begint met "Misclassificatie", "niet
     relevant voor clausule", "Vraag over X niet relevant voor", of "Item
     verwijst naar clausule X maar" worden uit de DB geweerd. Het betreft
     tagging-fouten op het Miro bord — geen werkelijke NCs tegen Conduction.

3. **Management summary op basis van clusters, niet samples** (`report_generation.py`)
   - Prompt ontvangt nu top-8 NC-clausule-clusters mét aantallen en voorbeeld,
     plus top-5 OFI en top-5 positief.
   - Conduction-context (BYOD, 5.12 intern/extern) ingebed in prompt.
   - Expliciete instructie: gebruik UITSLUITEND de data, geen bevestigings-
     taal als "drie kritieke gebieden" tenzij er exact drie prominente clusters
     zijn. Vermeldt werkelijke aantallen per cluster.

Why: De v1 summary noemde "drie kritieke gebieden" op basis van de eerste drie
NCs in de lijst — willekeurig. 5.11 werd ten onrechte als kritiek gepresenteerd
terwijl Conduction BYOD-werkt. 5.12 was een Miro mis-tagging die als
"classificatiefout in de norm" werd uitgelegd — vier audits lang onterecht.

### Added — 2026-04-20 — Memo-als-sluitingsbewijs context + remediation Miro-note

Vierde classifier-context uitbreiding in `_SYSTEM_GENUANCEERD`:
- Memo afwijking/tekortkoming/incident = sluitingsbewijs voor de ONDERLIGGENDE
  technische controle (8.21/8.24 crypto, 8.33 test/prod-scheiding, 6.7 VPN).
  Aanwezigheid van memo → "positief" of "OFI", niet NC. Alleen als memo
  expliciet stelt dat maatregel OPEN STAAT kan NC gerechtvaardigd zijn.

Resultaat v4 rehash: **NC 12 → 10** (memo-context) → **9** (na remediation 5.14).

**Remediation Miro-sticky + DB-update**:
- `audit/archive/annotate_finding_20260420.py` — patch-script dat:
  1. Een nieuwe light-green sticky plaatst op het Miro-auditbord naast
     item `3458764658906182642` (5.14 "Discussie eindigt niet...") met
     "✅ OPGEPAKT 2026-04-20" + resolutietekst over OpenRegister CI/CD.
     Gebruikt `maak_sticky` uit `miro_board_setup.py` — nieuwe sticky,
     bestaand item NIET aangepast (per memory-regel).
  2. DB-row `bevindingen.id=6018` wordt bijgewerkt: NC → OFI, en de
     resolutie-note wordt voor de beschrijving geplakt zodat het
     auditrapport de behandeling en openstaande OFI toont.
- Verificatie via `gh api repos/ConductionNL/openregister/contents/.github/workflows`:
  branch protection + staged releases (dev→beta→release) + PR lint zijn
  actief; quality-gate, coverage-gate en PHP-tests staan `if: false`
  (OFI-kanttekening, opgenomen in resolutie-tekst).

### Added — 2026-04-20 — Audit tabulaire output + thema-bundeling

- **`audit/tabular_report.py`** (nieuw)
  - CSV-export (`Bevindingen_<norm>_<datum>.csv`) — platte tabel, alle findings
  - Excel-export (`.xlsx`) met drie tabs:
    - `Samenvatting` — totalen per classificatie, per thema, per norm
    - `Bevindingen` — alle findings met conditional formatting op NC/OFI/positief
    - `Per clausule` — NC/OFI/positief counts per clausule
  - Heuristische thema-toekenning (route A): 24 thema-regels + "Overig" fallback,
    keyword-match over beschrijving + onderbouwing, first-match-wins
  - Norm-detectie per clausule via `normteksten` lookup (9001 / 27001 / beide)
  - Standalone CLI: `python3 -m audit.tabular_report --norm beide`

- **`audit/thema_classifier.py`** (nieuw — route B)
  - LLM-gebaseerde thema-verfijning met Haiku 4.5, batch ~50 findings per call
  - Prompt caching op system prompt (ephemeral)
  - `verfijn_overig()` — hybride: classificeert alleen bevindingen die
    heuristisch 'Overig' kregen (minimaliseert kosten/tokens)
  - `classificeer_themas()` — volledige LLM-toekenning
  - Valideert output tegen vaste taxonomie (`THEMA_LIJST`)
  - Graceful fallback: lege dict bij fout, caller gebruikt heuristiek

- **`audit/local_report.py`** — thema-bundeling binnen clausule-secties
  - Nieuwe helper `_render_clausules_met_themas()`
  - Per clausule: findings gegroepeerd per thema, grootste groep eerst,
    'Overig' altijd laatst
  - Thema-kop toont telling: `_(6 OFI · 15 positief)_`
  - Als een clausule maar één thema heeft → thema-kop weggelaten (geen ruis)

- **`audit/pipeline.py`**
  - Nieuwe flag `--thema-llm` (route B inschakelen)
  - `run_audit()` roept na classificatie heuristiek + optioneel LLM aan,
    hangt `thema` aan elke bevinding → markdown gebruikt zelfde bundeling
  - `run_local_only()` genereert nu ook CSV + Excel (naast markdown)

### Why

- Markdown-rapport was 3143 regels plat door 449 findings heen. Bundeling per
  thema maakt review hanteerbaar (top-5 thema's dekken nu ~40% van findings).
- CSV/Excel output laat filteren, sorteren en sheets-import zonder markdown-parsing.
- Route B (LLM-thema) is bewust gescheiden van de geplande refactor van
  `finding_classification.py` — thema-toekenning is aparte verantwoordelijkheid
  en draait in enkele batches (niet per-finding).

### Test

- `python3 -m audit.pipeline --local-only --norm 9001` — markdown + CSV + Excel OK
- Regeneratie op bestaande DB (449 findings): 24% 'Overig' met heuristiek;
  geldige Excel met 3 tabs, conditional formatting en samenvatting.
