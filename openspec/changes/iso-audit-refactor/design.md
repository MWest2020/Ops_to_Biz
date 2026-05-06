## Context

Het ISO-audit-tool leeft sinds eind 2025 als `audit/` directory binnen `Ops_to_Biz` naast `argocd_sync/`. Beide subsystemen zijn bedrijfskritisch maar zonder code-overlap: geen gedeelde imports, eigen `output/` paden, eigen requirements. Het audit-tool is in 2026 substantieel gegroeid (~7000 regels, 12 bestaande pipeline-stappen, drie rapport-formats).

Drie ontwikkelingen forceren nu een refactor:

1. **Audit-trail-eis.** Het tool zelf is onder ISO 27001-scope bij Conduction. Mengen van audit-tooling-code met onverwante ops-scripts in één repo bemoeilijkt herleidbaarheid van wijzigingen. Eigen repo + eigen CI + eigen versie-beheer is een traceability-vereiste, geen luxe.
2. **Bron-pluggability blokker.** Drive is hard-coded in drie modules. Jira-ingest is gepland voor de juni-run. Daarna komen MCP- en REST-adapters in beeld. Zonder een Source-abstractie-laag wordt elke nieuwe bron een vergelijkbaar one-off project, en de cumulatieve consolidatie-kost groeit met elke iteratie.
3. **Modes-architectuur is greenfield.** De huidige pipeline runt één pad. Voor de juni-run is een `integer`-modus nodig waarbij de auditor op kritieke beslismomenten in-the-loop is (ISO 19011-conformiteit). Tegelijk moet `autonoom` blijven voor cron-/CI-runs. Eén codepad, twee gedragingen — vereist contract-design vóór implementatie.

Stakeholders: Mark Westerweel (auditor + tool-owner), Conduction-MT (rapportage-consumer), externe certificeerder (audit-trail-consumer). Tijdsdruk: milestone C moet juni-run halen.

## Goals / Non-Goals

**Goals:**

- Standalone `iso-audit` repo met fresh git, Python `>=3.12`, volledig maintainability-fundament (uv, ruff, mypy, pytest, CI, pre-commit, gitleaks).
- `Source` Protocol dat alle vier toekomstige adapters (Drive, Jira, MCP, REST) zonder code-changes in de pipeline laat plug-and-playen.
- `Mode` Protocol met `autonoom` en `integer` runmodes; pipeline emitteert `Decision`-events op zes vooraf-vastgelegde beslispunten; integer-modus persisteert pauze-staat in SQLite.
- Drive-adapter en Jira-adapter implementeren `Source`; contract-tests draaien tegen beide.
- Miro sub-package consolideert drie bestaande clients in één gedeelde HTTP-laag.
- Drie milestones met drie merges; tussenstaten zijn werkbaar (geen big-bang).
- Snapshot-tests garanderen dat LLM-classificatie-gedrag identiek is voor en na refactor.

**Non-Goals:**

- MCP- en REST-adapter-implementaties (alleen het Protocol staat klaar; implementaties via eigen change-proposals).
- Migratie van `~/projects/miro-incident-board` en `~/projects/miro-desired-state` naar `iso-audit/miro/` (eigen change-proposal).
- Recidive-tracking, trend-grafiek, HR-event-koppeling (zie `project_audit_volgende_stappen.md`).
- Teams handoff-kanaal (alleen Slack Block Kit in scope; Teams via aparte change als/wanneer een klant het vraagt).
- Wijzigingen aan `argocd_sync/` of de andere `Ops_to_Biz`-subsystemen.
- Migratie van `audit/archive/`-scripts (eenmalige remediation, geen herbruikbare code).

## Decisions

### Decision 1: Source-protocol is read-only; write-back via aparte `Sink`

Drive en Miro zijn in de huidige architectuur bidirectioneel — bevindingen worden gelezen, rapporten worden geschreven. De vraag: hoort write in `Source` of is het een aparte abstractie?

**Keuze:** Source is read-only (`list_documents`, `fetch_content`, `list_findings`, `healthcheck`). Schrijven gaat via apart `Sink` Protocol dat in milestone C wordt gedefinieerd. Een adapter mag zowel `Source` als `Sink` implementeren — `DriveSource` en `DriveSink` worden onafhankelijk geregistreerd.

**Alternatieven overwogen:**
- *Eén Protocol met `read`/`write`-methodes:* korter contract, maar elke adapter zou writes moeten implementeren ook al doet de meeste alleen reads (Jira, MCP). Forceert nutteloos werk en maakt contract-tests messy.
- *Source met optionele `write`-methode:* breekt LSP — consumers kunnen niet vertrouwen op de aanwezigheid van write zonder runtime-check.

**Why:** Aparte Source/Sink is boring, conform Single Responsibility, en sluit aan bij hoe REST-API's typisch gemodelleerd worden (read en write zijn aparte concerns met verschillende permissies).

### Decision 2: Mode-Protocol via `Decision`-events op zes vaste beslispunten

De pipeline doet een sequentie van stappen (ingest, classificatie, rapport, verzending). Sommige stappen zijn risicovol (rapport verzenden, data verwijderen) en horen in `integer`-modus mens-bevestiging te krijgen. Andere zijn veilig (Drive↔Miro merge) en blijven autonoom.

**Keuze:** Pipeline emitteert `Decision(punt, context, voorstel, risico)` op zes vooraf gedefinieerde plekken. Mode-implementatie ontvangt het Decision-object en geeft een definitief besluit terug. `autonoom` accepteert het voorstel; `integer` escaleert hoog-risico-decisions naar de auditor en accepteert laag/midden-risico-decisions.

| Punt | Risico | Autonoom-gedrag | Integer-gedrag |
|---|---|---|---|
| `classify_finding` | midden | LLM-output accepteren | tonen, bevestigen of overschrijven via Slack |
| `merge_drive_miro` | laag | auto | auto |
| `assign_clausule` | midden | regel-based, anders default | bij low-confidence: tonen |
| `generate_report_section` | hoog | LLM-output direct in rapport | concept naar mens, review verplicht |
| `send_report` | hoog | direct verzenden | sign-off vereist |
| `delete_data` | hoog | nooit autonoom — pipeline faalt | mens-bevestigd |

**Alternatieven overwogen:**
- *Per-stap callback-functies:* concreter maar koppelt mode aan pipeline-internals; nieuwe beslispunten vereisen pipeline-changes overal.
- *Globale flag "ask-on-everything":* simpel maar ofwel onbruikbaar (te veel onderbrekingen) of nutteloos (alles auto). Geen middenweg.
- *Externe workflow-engine (bv. Temporal):* overengineering voor één auditor.

**Why:** Decision-events zijn het lichtste contract dat blast-radius beperkt. Pipeline kent de beslispunten, Mode kent het beleid — separation of concerns.

### Decision 3: Integer-modus state persisteert in `decisions`-tabel binnen bestaande SQLite

Wanneer integer-modus een hoog-risico-decision escaleert via Slack, moet de pipeline pauzeren totdat de auditor antwoordt. Waar leeft die staat?

**Keuze:** Nieuwe tabel `decisions` in de bestaande `store.py` SQLite-database (`iso_audit.db`). Schema:

```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    audit_id TEXT NOT NULL,
    punt TEXT NOT NULL,
    context_json TEXT NOT NULL,
    voorstel_json TEXT NOT NULL,
    status TEXT NOT NULL,           -- 'pending' | 'resolved' | 'cancelled'
    besluit_json TEXT,
    risico TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
```

**Alternatieven overwogen:**
- *In-memory met process-lock:* breekt zodra de pipeline crashed of langer pauzeert dan een sessie.
- *Aparte Redis-instance:* infrastructure-overhead voor één auditor, één tool.
- *File-based JSON:* werkt maar mist transactionele garanties bij concurrent runs.

**Why:** SQLite is al onderdeel van de stack, transactioneel, en werkt voor één-gebruiker-tool. Geen nieuwe operationele afhankelijkheid.

### Decision 4: Drie milestones, drie merges — geen big-bang

Refactor raakt code-paden door het hele tool. Eén grote merge betekent weken zonder werkbaar audit-tool, terwijl maandelijkse audits doorlopen.

**Keuze:**
- **Milestone A** (week 1-2): nieuwe repo + Source Protocol + lege contract-test. `Ops_to_Biz/audit/` blijft draaien.
- **Milestone B** (week 3-5): code-migratie + Drive-adapter + Miro-consolidatie + finding_classification merge. Feature-pariteit met `Ops_to_Biz/audit/`. Deprecation-marker in oude repo.
- **Milestone C** (week 6-8): Modes + Jira-adapter + Slack Block Kit handoff. Juni-run-target. `Ops_to_Biz/audit/` verwijderd.

Tussen milestones is het tool werkbaar in (oude of nieuwe) repo. Cherry-pick eenrichting: P0-bugs in `Ops_to_Biz/audit/` worden ook gefixt in `iso-audit` zolang B niet voltooid is. Geen reverse cherry-pick.

**Alternatieven overwogen:**
- *Big-bang:* sneller op papier maar onaccepteerbare blast-radius. Eén bug betekent rollback van weken werk en een gemiste audit.
- *Vier milestones (split B in code-migratie en Drive-adapter):* meer overhead, verwaarloosbare extra veiligheid; Drive-adapter is gewoon de eerste klant van het Source Protocol.

**Why:** Drie merges geeft drie demo/rollback-punten. Past bij de "iteratieve cadans" die in `project_audit_volgende_stappen.md` is afgesproken.

### Decision 5: `--source` flag is verplicht (breaking change)

Huidig gedrag: pipeline gebruikt impliciet Drive. Nieuw gedrag: `--source drive` (of `jira` etc.) is verplicht; pipeline faalt met error die beschikbare adapters toont.

**Why:** ISO-tooling-principe: expliciet > impliciet. Een geautomatiseerde maandelijkse run mag niet stilzwijgend naar Drive vallen wanneer de Jira-adapter faalt te initialiseren. Migratie-pijn is eenmalig (1 regel in cron), foutpreventie is permanent.

### Decision 6: Maintainability-stack zonder Sphinx, zonder Docker (MVP)

**Keuze tooling:** `pyproject.toml` + `uv` (packaging), `ruff` (lint+format), `mypy --strict` (typing), `pytest`+`pytest-cov` (tests, 70% line-coverage gate), `pre-commit` met `gitleaks` (secrets-scan), GitHub Actions CI met parallel jobs.

**Niet opgenomen:**
- *Sphinx-docs:* markdown in `docs/` is genoeg voor de scope. Sphinx-infra die niemand draait is een klassieke valkuil.
- *Docker in MVP:* dit is een CLI-tool, geen service. Containerfile komt pas wanneer deployment-vorm dat vraagt.
- *Pre-commit hooks die formatten in plaats van checken:* voorkomt silent CI-falen.

**Why:** Boring & auditable. Tooling die direct werkt zonder ceremonies, en die bij elke uitbreiding (nieuwe adapter, nieuwe mode) groene CI laat zien voordat het mergeable is.

### Decision 7: `audit/archive/` blijft achter, gaat niet mee

`Ops_to_Biz/audit/archive/` bevat eenmalige remediation-scripts (`annotate_finding_*.py`, `regenerate_with_recommendation_*.py`) — datestamped, niet herbruikbaar in een herhaalbare pipeline.

**Why:** Code blijft in `Ops_to_Biz` git-history voor herleidbaarheid. Geen meerwaarde in `iso-audit`. Wordt verwijderd bij `audit/` cleanup in milestone C.

## Risks / Trade-offs

**Risk: Source-protocol blijkt te krap (bv. paginated-listing, partial-fetch, write-back-met-context).** → Design-fase: schrijf use-cases voor alle vier adapters (Drive, Jira, MCP, REST) en voor write-back-via-Sink voordat het Protocol gepind wordt. Eerste milestone-A-task is een protocol-review met die use-cases als input.

**Risk: Modes-beslispunten zijn te grof (te weinig escalatie) of te fijn (auditor verzuipt).** → Implementeer met de zes uit de tabel; eerste juni-run levert feedback; iteratie via eigen change-proposal. De zes punten zijn een gefundeerde beste-gok, niet een definitief contract.

**Risk: LLM-classifier gedrag verandert door refactor (anders prompt-rendering, andere imports, andere cache-handling).** → Snapshot-tests op fixture-findings vóór refactor; exact match vereist na refactor. Failing snapshot-test blokkeert merge.

**Risk: Miro-consolidatie breekt `interview_miro` (audit-specifieke board-layout).** → Contract-test op gedeelde HTTP-laag (rate-limit, auth, retry); visuele snapshot-test op één bord (JSON-export voor en na vergelijken); manual smoke-test door auditor op test-bord vóór merge.

**Risk: Modes-werk vertraagt juni-run-deadline.** → Milestone C is parallel splitsbaar — Jira-adapter (één persoon) en Modes-implementatie (andere persoon) kunnen tegelijk. Slack Block Kit handoff is de laatste stap; als die niet af is, draait juni-run in autonoom-modus en levert dat alsnog feedback voor C.2-iteratie.

**Risk: `Ops_to_Biz/audit/` en `iso-audit/` divergeren tijdens refactor.** → Milestone B is freeze: na merge geen nieuwe features in `Ops_to_Biz/audit/`. Alleen P0-bugs worden gespiegeld via cherry-pick in beide repos zolang B niet voltooid is. Reverse cherry-pick is verboden.

**Risk: Memory / `CLAUDE.md` verwijst naar oude paden.** → Eén PR per repo direct na merge B (één voor `Ops_to_Biz/CLAUDE.md` cleanup, één voor `iso-audit/CLAUDE.md` aanmaak). Gedeelde Claude-memory wordt geupdate in de eerste sessie ná merge B.

**Risk: Externe certificeerder kan refactor-periode niet beoordelen.** → Voor de externe audit (Q3) wordt een markdown-overzicht aangeleverd: drie milestone-tags in beide repos, per milestone een commit-range en acceptatiecriterium. Reproduceerbaarheid van runs in beide repos blijft mogelijk via `examples/fixture-audit-2026-q1/`.

## Migration Plan

### Milestone A — repo-skeleton + Source Protocol (week 1-2)

1. Maak nieuwe GitHub-repo `MWest2020/iso-audit` (private, audit-trail enabled).
2. Initialiseer met `uv init` + `pyproject.toml` + `uv.lock`.
3. Voeg CI (`.github/workflows/ci.yml`) toe met parallel jobs voor `ruff check`, `ruff format --check`, `mypy --strict`, `pytest`.
4. Voeg pre-commit-config toe met ruff, ruff-format, mypy, gitleaks.
5. Maak issue-templates (`bug.md`, `feature.md`, `source-adapter.md`) — laatste forceert protocol-conformance + tests + docs.
6. Schrijf `src/iso_audit/sources/base.py` met `Source` Protocol + `Document` / `Finding` dataclasses.
7. Schrijf `tests/sources/test_protocol_contract.py` met fixture-set; geen adapter geregistreerd, dus test draait leeg-groen.
8. Schrijf `ARCHITECTURE.md` met source-protocol + modes-contract uitwerking + reference naar deze design-doc.
9. Schrijf `iso-audit/CLAUDE.md` per memory-migratieplan (sectie hieronder).
10. Acceptatie: CI groen, contract-test groen, ARCHITECTURE.md goedgekeurd door auditor.

### Milestone B — verhuizing + Drive-adapter + Miro-consolidatie (week 3-5)

1. Migreer alle `Ops_to_Biz/audit/`-modules naar `src/iso_audit/` per doel-architectuur.
2. Merge `drive_ingest.py` + `gws_client.py` + `planning_ingest.py` in `src/iso_audit/sources/drive.py`; implementeert `Source`.
3. Merge drie Miro-modules in `src/iso_audit/miro/` met gedeelde `client.py`.
4. Merge `finding_classification.py` en `_20260420.py` — kies de nieuwere als basis, behoud relevante delen uit de oude.
5. Pas pipeline aan voor source-registry: `pipeline --source drive`.
6. Schrijf snapshot-tests op fixture-findings vóór en na refactor; exact match vereist.
7. Markeer `Ops_to_Biz/audit/` als deprecated in `Ops_to_Biz/CLAUDE.md` met pointer naar `iso-audit`.
8. Verhuis vier audit-OpenSpec-changes (`audit-rapport-management-taal`, `gsuite-iso-audit-automation`, `miro-kennissessie-generator`, `hww-2-0`) — één commit per change-rename voor leesbare diff.
9. Acceptatie: alle bestaande pipeline-runs reproduceerbaar in `iso-audit`; Miro-features werken; contract-tests Drive-adapter groen; snapshot-tests groen.

### Milestone C — Modes + Jira-adapter (week 6-8, juni-run)

1. Implementeer `src/iso_audit/modes/` met `Mode` Protocol, `autonoom`, `integer`.
2. Pas pipeline aan om `Decision`-events te emitteren op de zes beslispunten.
3. Implementeer Slack Block Kit handoff voor de drie hoog-risico-punten in integer-modus.
4. Voeg `decisions`-tabel toe aan `store.py` met migratie-script.
5. Implementeer `src/iso_audit/sources/jira.py`; contract-tests groen.
6. Eerste juni-run-target: `iso-audit pipeline --norm 27001 --source jira --source drive --mode integer`.
7. Verwijder `Ops_to_Biz/audit/` en `audit/archive/`; ruim `Ops_to_Biz/CLAUDE.md` op.
8. Acceptatie: end-to-end juni-audit gedraaid in integer-modus met Jira als primaire en Drive als secundaire bron; alle drie hoog-risico beslispunten zichtbaar in Slack-handoffs; auditor-besluiten persistent in `decisions`-tabel.

### Rollback-strategie

- **Milestone A**: rollback = repo deleten of unmerged laten. Geen impact op `Ops_to_Biz`.
- **Milestone B**: rollback = revert merge-commit in `iso-audit`; `Ops_to_Biz/audit/` is niet aangeraakt buiten deprecation-comment, dus blijft werkend.
- **Milestone C**: rollback = revert milestone-C-merge; modes/Jira verdwijnen, Drive-only-pipeline blijft werken in `iso-audit`. Voor juni-run terugvallen op autonoom-mode.

## Open Questions

1. **Source-protocol — pagination en partial-fetch.** Drive- en Jira-API's leveren paginated. Hoort dat in het Protocol (`list_documents` returnt `Iterator`) of erbuiten (adapter doet het impliciet)? **Voorstel:** `Iterator[Document]` is voldoende voor lazy iteration; concrete pagination is adapter-private. Te valideren in milestone-A-design-review.

2. **Source-protocol — write-back via Sink.** Definitie van het `Sink` Protocol is in milestone C nodig (Slack-handoff schrijft naar Slack, eventueel write-back naar Jira). **Voorstel:** definieer Sink als read-only-omgekeerde van Source: `send(Notification|Finding)` + `healthcheck()`. Concretere shape pas wanneer twee Sinks geïdentificeerd zijn.

3. **Modes-handoff-kanaal pluggable vanaf dag 1?** Eerste implementatie Slack Block Kit. Teams later? **Voorstel:** Handoff-protocol gedefinieerd in C maar alleen Slack-implementatie geschreven; Teams via losse change-proposal als/wanneer een klant het vraagt. YAGNI tot dan.

4. **Versionering tijdens refactor.** Tijdens milestone B is `Ops_to_Biz/audit/` feature-frozen. Hoe ver gaan we met bug-fixes? **Voorstel:** alleen P0-bugs, gespiegeld in beide repos via eenrichtings-cherry-pick (`Ops_to_Biz` → `iso-audit`). Geen reverse cherry-pick. P1+-bugs wachten op merge B.

5. **OpenSpec-changes meeverhuizen — als-is of opnieuw uitschrijven?** Vier changes (`audit-rapport-management-taal`, `gsuite-iso-audit-automation`, `miro-kennissessie-generator`, `hww-2-0`) zijn geschreven tegen `Ops_to_Biz/audit/`-paden. **Voorstel:** meeverhuizen, paden updaten in dezelfde commit, geen herschrijving. Eén commit per change-rename voor leesbare diff.

6. **`normteksten.py` (132 KB, 2600+ regels) splitsen?** Huidig: één bestand met ISO 9001 + 27001 normteksten als Python-data. **Voorstel:** splitsen naar `src/iso_audit/data/normteksten/iso9001.py` + `iso27001.py` + `__init__.py` met re-export. Voordeel: kleinere diffs bij norm-updates, betere blame. Te beslissen in milestone-B-design-review.

7. **CLI-naam: `iso-audit` of `python -m iso_audit`?** **Voorstel:** beide. Console-script entry-point in `pyproject.toml` levert `iso-audit` als binary; `python -m iso_audit.pipeline` blijft werken voor module-form-gebruikers. Geen breaking change voor cron-/systemd-gebruikers die het patroon `python -m audit.pipeline` gewend zijn.
