## Context

Het ISO-audit-tool leeft sinds eind 2025 als `audit/` directory binnen `Ops_to_Biz` naast `argocd_sync/`. Beide subsystemen zijn bedrijfskritisch maar zonder code-overlap: geen gedeelde imports, eigen `output/` paden, eigen requirements. Het audit-tool is in 2026 substantieel gegroeid (~7000 regels, 12 bestaande pipeline-stappen, drie rapport-formats).

Vier ontwikkelingen forceren nu een refactor:

1. **Missie-helderheid (mei 2026).** Het ontwerpdocument `Tool-ontwerp_audit-tool_2026-05-05.md` herpositioneert het tool: niet als efficiency-tool die de auditor automatiseert, maar als onafhankelijkheids-instrument dat blinde vlekken van de auditor signaleert. Drie capabilities (onafhankelijke bronnen, patroondetectie, auditor-spiegel) sturen het ontwerp. De refactor moet hooks zetten voor capability 2 en 3, zonder die capabilities nu te bouwen.
2. **Audit-trail-eis.** Het tool zelf is onder ISO 27001-scope bij Conduction. Mengen van audit-tooling-code met onverwante ops-scripts in één repo bemoeilijkt herleidbaarheid van wijzigingen. Eigen repo + eigen CI + eigen versie-beheer is een traceability-vereiste, geen luxe.
3. **Bron- en handoff-pluggability blokker.** Drive is hard-coded in drie modules. Jira-ingest is gepland. Daarna komen MCP- en REST-adapters. Slack als handoff-kanaal werkt voor Conduction maar niet voor gemeentelijke afnemers (M365/Teams). Zonder Source- en Notifier-abstractie-lagen wordt elke nieuwe bron of kanaal een vergelijkbaar one-off project; cumulatieve consolidatie-kost groeit met elke iteratie. **Beide protocollen vóór de eerste echte tweede-bron- of tweede-kanaal-implementatie.**
4. **Modes-architectuur is greenfield.** De huidige pipeline runt één pad. Voor integer-runs is een modus nodig waarbij de auditor op kritieke beslismomenten in-the-loop is (ISO 19011-conformiteit én capability 3-data-bron). Tegelijk moet `autonoom` blijven voor cron-/CI-runs. Eén codepad, twee gedragingen — vereist contract-design vóór implementatie.

Stakeholders: Mark Westerweel (auditor + tool-owner), Conduction-MT (rapportage-consumer), externe certificeerder (audit-trail-consumer), toekomstige afnemers buiten Conduction (zie missie §4).

Tijdsdruk: geen harde deadline. De eerste integer-run is een wens, geen contractuele verplichting. "Boring & auditable" weegt zwaarder dan snelheid. Drie milestones met natuurlijke cadens.

## Goals / Non-Goals

**Goals:**

- Standalone `iso-audit` repo met fresh git, Python `>=3.12`, volledig maintainability-fundament (uv, ruff, mypy, pytest, CI, pre-commit, gitleaks).
- `Source` Protocol dat alle vier toekomstige adapters (Drive, Jira, MCP, REST) zonder code-changes in de pipeline laat plug-and-playen; configuratie immutable binnen audit-run.
- `Sink` Protocol als spec-only in milestone A (paden voor Drive-Sink in C). Voorkomt dat Source-only beslissingen in milestone B het schrijfpad ongedefinieerd laten.
- `Mode` Protocol met `autonoom` en `integer` runmodes; pipeline emitteert `Decision`-events op zeven vooraf-vastgelegde beslispunten; integer-modus persisteert pauze-staat in SQLite; `decisions`-tabel ontworpen als rapporteerbare data, niet alleen runtime-state.
- `Notifier` Protocol met `Slack` en `Email` adapters; `DecisionResolver` kanaal-agnostisch; pluggable vanaf dag 1.
- Drive-, Planning- en Jira-adapters implementeren `Source`; contract-tests draaien tegen alle drie.
- Slack- en Email-adapters implementeren `Notifier`; contract-tests draaien tegen beide.
- Miro sub-package consolideert drie bestaande clients in één gedeelde HTTP-laag.
- Drie milestones met drie merges; tussenstaten zijn werkbaar (geen big-bang).
- Snapshot-tests garanderen dat LLM-classificatie-gedrag identiek is voor en na refactor.
- Classificatie-output is reproduceerbaar en uitlegbaar (input-hash, prompt-versie, model-versie, raw output).

**Non-Goals:**

- MCP- en REST-source-adapter-implementaties (alleen het Protocol staat klaar; implementaties via eigen change-proposals).
- Teams- en Mattermost-Notifier-implementaties (alleen Protocol + Slack/Email; latere change-proposals als afnemer vraagt).
- Spiegel-laag-implementatie (capability 3): eigen change-proposal `iso-audit-mirror-foundation` na minimaal vier integer-runs.
- Migratie van `~/projects/miro-incident-board` en `~/projects/miro-desired-state` naar `iso-audit/miro/` (eigen change-proposal).
- Recidive-tracking, trend-grafiek, HR-event-koppeling (zie `project_audit_volgende_stappen.md`).
- Wijzigingen aan `argocd_sync/` of de andere `Ops_to_Biz`-subsystemen.
- Migratie van `audit/archive/`-scripts (eenmalige remediation, geen herbruikbare code).

## Decisions

### Decision 1: Source-protocol is read-only met immutable runtime-configuratie

Drie issues vallen samen: hoort write-back in Source of in een aparte abstractie? Mag de Source tijdens een run worden bijgesteld? En hoe verhoudt het Protocol zich tot capability 1 uit de missie (onafhankelijke bronnen, geen curated input)?

**Keuze:**
- Source is read-only (`list_documents`, `fetch_content`, `list_findings`, `healthcheck`). Schrijven gaat via apart `Sink` Protocol.
- Source-configuratie SHALL immutable zijn binnen een audit-run: geconfigureerd uit env-vars of config-bestand bij pipeline-start, geen runtime-wijzigingen via API of CLI-flags. Een adapter mag geen `set_folder()`, `set_filter()` of equivalent bieden.
- Een adapter mag zowel `Source` als `Sink` implementeren als aparte class-instanties (bv. `DriveSource` en `DriveSink`).

**Alternatieven overwogen:**
- *Eén Protocol met `read`/`write`-methodes:* korter contract, maar Jira- en MCP-adapters zouden writes moeten implementeren ook al doen ze meestal alleen reads. Forceert nutteloos werk en maakt contract-tests messy.
- *Source met optionele `write`-methode:* breekt LSP — consumers kunnen niet vertrouwen op de aanwezigheid van write zonder runtime-check.
- *Mutable runtime-configuratie:* opent de deur voor de exacte curatie-valkuil die capability 1 wil voorkomen — een auditor of operator die tijdens een run scope versmalt.

**Why:** Aparte Source/Sink is conform Single Responsibility en sluit aan bij hoe REST-API's typisch gemodelleerd worden. Immutability is een directe vertaling van missie §2.1 ("toegang van tevoren ingericht en daarna onveranderlijk binnen een audit-periode") naar een gedragscontract dat falsifieerbaar is in tests.

### Decision 2: Sink-protocol gespecificeerd in milestone A, geïmplementeerd in milestone C

Bij Source-only-beslissing in milestone B krijg je twee ongedefinieerde paden: waar gaat `report_generation.py` heen, en wat doet `gws_client.py` (gedeeld door read en write)?

**Keuze:**
- `Sink` Protocol gedefinieerd in `src/iso_audit/sinks/base.py` in milestone A: `send(payload: SinkPayload) -> SinkResult` + `healthcheck() -> dict`.
- `SinkPayload` is een dataclass-hierarchy: `ReportPayload`, `NotificationPayload`, `MirrorPayload` (placeholder voor toekomstige spiegel-laag, niet implementeren).
- Geen Sink-implementaties in A of B. Eerste implementatie (`DriveSink`) in milestone C; consolideert `report_generation.py` + `slide_summary.py` + `template_setup.py`.
- In milestone B blijven `gws_client.py`, `report_generation.py`, `slide_summary.py`, `template_setup.py` als interne modules in `src/iso_audit/clients/` en `src/iso_audit/reporting/` zonder Sink-stempel. Migratie naar Sink gebeurt in C.

**Alternatieven overwogen:**
- *Sink pas in milestone C definiëren:* migreert `gws_client.py` in milestone B zonder duidelijk eindplaatje; risico dat schrijfpaden suboptimaal landen en in C herwerk vragen.
- *Sink in A definiëren én eerste implementatie meteen in B:* sneller eindplaatje maar verbreedt milestone B onnodig en raakt code-paden tijdens de meest risicovolle migratie-fase.
- *Symmetrisch met Source ontwerpen (`list_targets`, `send`, etc.):* asymmetrie is hier eerlijk — Source enumereert + fetcht, Sink levert one-shot. Symmetrie afdwingen voegt complexiteit toe zonder use-case.

**Why:** Spec-only in A geeft milestone B een eindplaatje zonder dat B implementatie-werk inneemt. Boring & auditable: bouw geen code waar geen runtime-eis tegenover staat, maar wel de naam-reservering die latere consolidatie eenvoudig maakt.

### Decision 3: Mode-Protocol via `Decision`-events op zeven vaste beslispunten

De pipeline doet een sequentie van stappen (ingest, classificatie, rapport, verzending). Sommige stappen zijn risicovol (rapport verzenden, data verwijderen) en horen in `integer`-modus mens-bevestiging te krijgen. Andere zijn veilig (Drive↔Miro merge) en blijven autonoom. Eén stap (ingest-scope) staat erbuiten in de huidige pipeline maar is precies waar curatie-fouten ontstaan.

**Keuze:** Pipeline emitteert `Decision(punt, context, voorstel, risico)` op zeven vooraf gedefinieerde plekken. Mode-implementatie ontvangt het Decision-object en geeft een definitief besluit terug.

| Punt | Risico | Autonoom-gedrag | Integer-gedrag |
|---|---|---|---|
| `ingest_scope` | laag | accepteer geconfigureerde scope | tonen bij flag in context (counts), bevestigen |
| `merge_drive_miro` | laag | auto | auto |
| `classify_finding` | midden | LLM-output accepteren | autonoom tenzij `confidence < 0.7` — dan escaleren |
| `assign_clausule` | midden | regel-based, anders default | autonoom tenzij `confidence < 0.7` — dan escaleren |
| `generate_report_section` | hoog | LLM-output direct in rapport | concept naar mens, review verplicht |
| `send_report` | hoog | direct verzenden via Sink | sign-off vereist via Notifier |
| `delete_data` | hoog | nooit autonoom — pipeline skipt + logt | mens-bevestigd via Notifier |

`ingest_scope` is toegevoegd ten opzichte van eerdere zes-puntenversie omdat curatie-fouten typisch vóór de eerste echte beslissing ontstaan; capability 1 vereist verifieerbaarheid van wat in scope kwam, niet alleen wat geclassificeerd werd. Het is laag-risico maar levert in integer-modus optioneel een count-bevestiging als de context-flag `vraag_scope_bevestiging` aanwezig is.

**Alternatieven overwogen:**
- *Per-stap callback-functies:* concreter maar koppelt mode aan pipeline-internals; nieuwe beslispunten vereisen pipeline-changes overal.
- *Globale flag "ask-on-everything":* simpel maar ofwel onbruikbaar (te veel onderbrekingen) of nutteloos (alles auto). Geen middenweg.
- *Externe workflow-engine (bv. Temporal):* overengineering voor één auditor.

**Why:** Decision-events zijn het lichtste contract dat blast-radius beperkt. Pipeline kent de beslispunten, Mode kent het beleid — separation of concerns. Zeven punten dekt zowel de operationele beslismomenten als de scope-momenten waar curatie-bias kan ontstaan.

### Decision 4: `decisions`-tabel is rapporteerbare data, niet alleen runtime-state

Capability 3 uit de missie (auditor-spiegel) vraagt cross-run analyse van auditor-besluiten: welke voorstellen werden geaccepteerd, welke afgewezen, welke aangepast, welke genegeerd. De huidige tabel-vormgeving is geframed als pauze-staat ("blokkeer pipeline tot resolved"), niet als analyse-data.

**Keuze:** Behoud het schema, herframe de semantiek. Nieuwe tabel `decisions` in de bestaande `store.py` SQLite-database (`iso_audit.db`). Schema:

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
    classificatie_id INTEGER,       -- FK naar classifications-tabel (nullable)
    notifier_naam TEXT,             -- welk kanaal escaleerde, NULL bij autonoom
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE INDEX idx_decisions_audit_status ON decisions(audit_id, status);
CREATE INDEX idx_decisions_punt_resolved ON decisions(punt, resolved_at);
```

Toegevoegd ten opzichte van eerdere versie:
- `classificatie_id` koppelt het besluit aan de onderliggende classificatie (zie Decision 5) voor traceability.
- `notifier_naam` registreert via welk kanaal werd geescaleerd; nodig voor cross-organisatie-vergelijking als afnemers verschillende kanalen gebruiken.
- Indexen op `(audit_id, status)` voor crash-recovery-query en `(punt, resolved_at)` voor patroon-analyse over tijd.

**Invarianten:**
- De pipeline SHALL geen rijen verwijderen of overschrijven na `status="resolved"` of `status="cancelled"`. Append-only-discipline.
- AutonoomMode SHALL alleen rijen schrijven voor `risico="hoog"` beslispunten; laag- en midden-risico besluiten in autonome modus genereren geen tabel-data omdat er geen analytische waarde is in voorstel == besluit zonder mens.

**Alternatieven overwogen:**
- *In-memory met process-lock:* breekt zodra de pipeline crashed of langer pauzeert dan een sessie; geen cross-run analyse mogelijk.
- *Aparte Redis-instance:* infrastructure-overhead voor één auditor, één tool.
- *File-based JSON:* werkt maar mist transactionele garanties bij concurrent runs én indexen voor patroon-queries.
- *Alle beslissingen persisteren ongeacht risico of modus:* polluteert de tabel met null-data (autonoom-runs accepteren altijd het voorstel) die capability 3 later moet uitfilteren.

**Why:** SQLite is al onderdeel van de stack, transactioneel, en indexen geven goedkope cross-run-queries. Append-only + selectieve persistentie maakt de tabel een audit-trail én bruikbare analyse-bron, zonder dat de spiegel-laag nu wordt gebouwd.

### Decision 5: Classificatie-output is reproduceerbaar en uitlegbaar

Capability 2 (patroondetectie) en 3 (spiegel) vragen dat elke classificatie traceerbaar is naar zijn redenering — anders kun je geen patroon onderbouwen tegenover een auditor die het patroon betwist. De huidige `finding_classification.py` slaat alleen het eindresultaat op.

**Keuze:** Nieuwe tabel `classifications` in `iso_audit.db`:

```sql
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY,
    audit_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    input_hash TEXT NOT NULL,         -- SHA-256 van input-tekst
    prompt_versie TEXT NOT NULL,      -- e.g. "classify_v3"
    model_versie TEXT NOT NULL,       -- e.g. "claude-sonnet-4-5-20250929"
    raw_output TEXT NOT NULL,         -- volledig LLM-antwoord
    parsed_klasse TEXT NOT NULL,      -- 'NC' | 'OFI' | 'positief'
    parsed_clausule TEXT,
    confidence REAL,
    created_at TEXT NOT NULL
);
```

Een classificatie zonder deze velden SHALL niet als basis voor patroondetectie gebruikt worden. Bij prompt- of model-wijzigingen worden classificaties opnieuw gegenereerd; oude rijen blijven staan voor historische traceability.

**Why:** ISO 17025-achtige traceability-eis. Voor de spiegel-missie moet de tool kunnen uitleggen waarom hij iets flagde — anders is het zelf een blackbox-tool die het probleem reproduceert dat het wil oplossen. Boring & auditable: de hook is goedkoop nu, een bottleneck later als hij ontbreekt.

### Decision 6: Notifier-protocol vanaf dag 1, met Slack én Email als eerste adapters

Slack als hard-coded handoff-kanaal werkt voor Conduction maar niet voor gemeentelijke afnemers (M365/Teams-standaard) of organisaties op andere stacks. Dezelfde valkuil als bij sources, andere laag.

**Keuze:**
- `Notifier` Protocol in `src/iso_audit/notifiers/base.py` met:
  - `naam: str` (uniek class-attribute, kebab-case)
  - `vraag_besluit(decision: Decision) -> str` (return: decision_id voor latere correlatie)
  - `healthcheck() -> dict`
- Aparte `DecisionResolver`-protocol parseert kanaal-respons naar kanaal-agnostische shape `(decision_id, action, modified_payload | None)`. Slack-buttons, Email-replies, Teams-cards leveren dezelfde resolver-output.
- Twee adapters in milestone C: `SlackNotifier` (Block Kit + button-callback) en `EmailNotifier` (SMTP-out + magic-link-portaal voor response).
- `--notifier` CLI-flag verplicht bij `--mode integer`; symmetrisch met `--source` en `--mode`.
- `NotifierRegistry` analoog aan `SourceRegistry`.

**EmailNotifier-implementatie:** magic-link-variant. E-mail bevat link naar lokaal-draaiend Flask-mini-portaal (poort configureerbaar via `ISO_AUDIT_PORTAL_PORT`); auditor klikt knop in browser; portaal schrijft direct naar `decisions`-tabel. Geen IMAP, geen reply-parsing. Auditable trail: outbound mail + HTTP-request-log.

**Alternatieven overwogen:**
- *Email-reply-parsing:* fragiel, multi-line auditor-responses parser-hel.
- *IMAP-polling:* IMAP-credentials-state-machine, niet boring.
- *Eén adapter (alleen Slack) in C, Email later:* mist de validatie-waarde van twee adapters tegen het Protocol; één adapter is nog geen bewijs van orthogonaliteit. En houdt de rolconflict-mitigatie buiten Conduction-context onbereikbaar.
- *Notifier als "subset van Mode":* koppelt kanaal aan mode-implementatie, breekt zodra je twee modes met verschillende kanalen wilt of één mode met meerdere kanalen.

**Why:** Drie protocol-lagen (Source/Mode/Notifier) met identiek patroon (registry, kebab-case naam, contract-tests, verplichte CLI-flag) is consistent en uitlegbaar aan externe code-reviewer (zie missie §6 risico). Slack + Email valideert het Protocol tegen variatie zonder Teams- of Mattermost-implementaties te bouwen.

### Decision 7: Drie milestones, drie merges — geen big-bang

Refactor raakt code-paden door het hele tool. Eén grote merge betekent weken zonder werkbaar audit-tool, terwijl maandelijkse audits doorlopen.

**Keuze:**
- **Milestone A** (week 1-2): nieuwe repo + Source Protocol + Sink Protocol (spec-only) + Notifier Protocol + lege contract-tests + `docs/missie.md`. `Ops_to_Biz/audit/` blijft draaien.
- **Milestone B** (week 3-5): code-migratie + Drive/Planning-adapters + Miro-consolidatie + finding_classification ontvlechting + classificatie-traceability-tabel. Feature-pariteit met `Ops_to_Biz/audit/`. Deprecation-marker in oude repo.
- **Milestone C** (week 6-9): Modes + Jira-adapter + Slack/Email-Notifiers + DriveSink. Eerste integer-run-target. `Ops_to_Biz/audit/` verwijderd.

Tussen milestones is het tool werkbaar in (oude of nieuwe) repo. Cherry-pick eenrichting: P0-bugs in `Ops_to_Biz/audit/` worden ook gefixt in `iso-audit` zolang B niet voltooid is. Geen reverse cherry-pick.

P0 = bevinding mist in rapport, classificatie demonstreerbaar fout, credentials lekken, audit-deadline gemist door tool-fout. P1+ wacht op merge B.

Freeze-einddatum: 5 weken vanaf start milestone B. Loopt B uit dan heroverwegen, niet automatisch verlengen.

**Alternatieven overwogen:**
- *Big-bang:* sneller op papier maar onaccepteerbare blast-radius. Eén bug betekent rollback van weken werk en een gemiste audit.
- *Vier milestones (split B in code-migratie en Drive-adapter):* meer overhead, verwaarloosbare extra veiligheid; Drive-adapter is gewoon de eerste klant van het Source Protocol.

**Why:** Drie merges geeft drie demo/rollback-punten. Past bij de "iteratieve cadans" die in `project_audit_volgende_stappen.md` is afgesproken. Milestone C verlengd van 3 naar 4 weken vanwege Notifier-laag + DriveSink + Jira-adapter; juni-run is wens, geen must.

### Decision 8: `--source`, `--mode`, `--notifier` flags zijn verplicht; defaults via env-vars in cron-context

Huidig gedrag: pipeline gebruikt impliciet Drive. Nieuw gedrag: `--source <naam>` is verplicht; `--mode autonoom|integer` is verplicht; `--notifier <naam>` is verplicht alleen wanneer `--mode integer`. Pipeline faalt met error die beschikbare opties toont.

Voor cron-context: `ISO_AUDIT_DEFAULT_SOURCE`, `ISO_AUDIT_DEFAULT_MODE`, `ISO_AUDIT_DEFAULT_NOTIFIER` env-vars. Wanneer een vlag ontbreekt én de bijbehorende env-var is gezet, gebruikt de CLI die waarde — maar logt expliciet dat dit gebeurt. Wanneer beide ontbreken, faalt de pipeline.

**Why:** Expliciet > impliciet, conform ISO-tooling-principe. Een geautomatiseerde maandelijkse run mag niet stilzwijgend naar Drive vallen wanneer Jira-adapter faalt. Env-vars in cron-unit-files zijn auditable (staan in versiebeheer); CLI-defaults zijn dat niet.

### Decision 9: Maintainability-stack zonder Sphinx, zonder Docker (MVP)

**Keuze tooling:** `pyproject.toml` + `uv` (packaging), `ruff` (lint+format), `mypy --strict` (typing), `pytest`+`pytest-cov` (tests, coverage-gate na meting in milestone B vastgesteld), `pre-commit` met `gitleaks` + `bandit` (secrets en obvious Python-security-smells), GitHub Actions CI met parallel jobs.

Coverage-gate-bepaling: meet baseline op gemigreerde code in milestone B; gate op baseline + 5%, of minimaal 70% — wat hoger is. Gate vooraf zetten op een ongemeten getal is ofwel triviaal of blokkerend zonder reden.

**Niet opgenomen:**
- *Sphinx-docs:* markdown in `docs/` is genoeg voor de scope. Sphinx-infra die niemand draait is een klassieke valkuil.
- *Docker in MVP:* dit is een CLI-tool, geen service. Containerfile komt pas wanneer deployment-vorm dat vraagt.
- *Pre-commit hooks die formatten in plaats van checken:* voorkomt silent CI-falen.

**Why:** Boring & auditable. Tooling die direct werkt zonder ceremonies, en die bij elke uitbreiding (nieuwe adapter, nieuwe mode, nieuwe notifier) groene CI laat zien voordat het mergeable is. `bandit` toegevoegd ten opzichte van eerdere versie omdat security-smells in een ISO-tool niet via reviewer-aandacht alleen gevangen mogen worden.

### Decision 10: `audit/archive/` blijft achter, gaat niet mee

`Ops_to_Biz/audit/archive/` bevat eenmalige remediation-scripts (`annotate_finding_*.py`, `regenerate_with_recommendation_*.py`) — datestamped, niet herbruikbaar in een herhaalbare pipeline.

**Why:** Code blijft in `Ops_to_Biz` git-history voor herleidbaarheid. Geen meerwaarde in `iso-audit`. Wordt verwijderd bij `audit/` cleanup in milestone C.

## Risks / Trade-offs

**Risk: Source-protocol blijkt te krap (paginated-listing, partial-fetch, write-back-met-context).** → Design-fase: schrijf use-cases voor alle vier adapters (Drive, Planning, Jira, MCP, REST) en voor write-back-via-Sink voordat het Protocol gepind wordt. Eerste milestone-A-task is een protocol-review met die use-cases als input.

**Risk: Notifier-protocol blijkt te smal voor Email magic-link-flow.** → EmailNotifier-design-review als eerste task in milestone C. Slack-implementatie als sanity-check op de andere kant van de variatie. Als magic-link-portaal raar past, dan niet forceren — refactor het Protocol vóór tweede adapter, niet erna.

**Risk: Modes-beslispunten zijn te grof of te fijn.** → Implementeer met de zeven uit de tabel; eerste integer-run levert feedback; iteratie via eigen change-proposal. De zeven punten zijn een gefundeerde beste-gok, niet een definitief contract.

**Risk: Spiegel-laag-hooks (decisions-tabel, classificatie-tabel) blijken niet voldoende voor capability 3.** → Acceptabel risico: deze refactor bouwt geen spiegel-laag, alleen hooks. Eerste echte capability-3-werk komt na vier integer-runs en kan eigen schema-uitbreidingen voorstellen via change-proposal `iso-audit-mirror-foundation`.

**Risk: LLM-classifier gedrag verandert door refactor.** → Snapshot-tests op fixture-findings vóór refactor; exact match vereist na refactor. Failing snapshot-test blokkeert merge. Classificatie-traceability-tabel maakt regressie-detectie ook over runs heen mogelijk.

**Risk: Miro-consolidatie breekt `interview_miro` (audit-specifieke board-layout).** → Contract-test op gedeelde HTTP-laag (rate-limit, auth, retry); visuele snapshot-test op één bord (JSON-export voor en na vergelijken); manual smoke-test door auditor op test-bord vóór merge.

**Risk: Modes/Notifier-werk vertraagt eerste integer-run.** → Geen contractuele deadline; integer-run is een wens. Liever boring-and-auditable af dan haastig ontworpen. Eventueel C in twee sub-merges: C1 (Modes + Jira-adapter + DriveSink) als feature-pariteit + Sink, C2 (Notifiers + integer-flow) als spiegel-hooks-completeer.

**Risk: `Ops_to_Biz/audit/` en `iso-audit/` divergeren tijdens refactor.** → Milestone B is freeze met einddatum (5 weken vanaf start B). Alleen P0-bugs gespiegeld via cherry-pick één richting. Reverse cherry-pick verboden.

**Risk: Memory / `CLAUDE.md` verwijst naar oude paden.** → Eén PR per repo direct na merge B (één voor `Ops_to_Biz/CLAUDE.md` cleanup, één voor `iso-audit/CLAUDE.md` aanmaak). Gedeelde Claude-memory wordt geupdate in de eerste sessie ná merge B.

**Risk: Externe certificeerder kan refactor-periode niet beoordelen.** → Markdown-overzicht aangeleverd: drie milestone-tags in beide repos, per milestone een commit-range en acceptatiecriterium. Reproduceerbaarheid van runs in beide repos blijft mogelijk via `examples/fixture-audit-2026-q1/`.

**Risk: Tool-eigenaar wordt zelf single-point-of-failure (uit missie §6).** → Beperkt mitigeerbaar binnen scope van deze refactor. Geadresseerd door: open-source-pad expliciet in `docs/missie.md`, geen geheime classificatie-logica (alle prompts in `src/iso_audit/classification/prompts/`), code-reviews door externen mogelijk gemaakt door publieke repo-structuur. Volledige mitigatie vraagt tweede tool-onderhouder; buiten refactor-scope.

## Migration Plan

### Milestone A — repo-skeleton + drie protocollen + missie (week 1-2)

1. Maak nieuwe GitHub-repo `MWest2020/iso-audit` (private; branch protection, signed commits, required reviews; Audit Log via Enterprise tier indien beschikbaar — anders documenteren als compensating control).
2. Initialiseer met `uv init` + `pyproject.toml` + `uv.lock`.
3. Voeg CI (`.github/workflows/ci.yml`) toe met parallel jobs voor `ruff check`, `ruff format --check`, `mypy --strict`, `pytest`.
4. Voeg pre-commit-config toe met ruff, ruff-format, mypy, gitleaks, bandit.
5. Maak issue-templates (`bug.md`, `feature.md`, `source-adapter.md`, `notifier-adapter.md`).
6. Schrijf `src/iso_audit/sources/base.py` met `Source` Protocol + `Document` / `Finding` dataclasses + `SourceRegistry`.
7. Schrijf `src/iso_audit/sinks/base.py` met `Sink` Protocol + `SinkPayload`-hierarchy (`ReportPayload`, `NotificationPayload`, `MirrorPayload`-placeholder). Geen implementaties.
8. Schrijf `src/iso_audit/notifiers/base.py` met `Notifier` Protocol + `DecisionResolver` Protocol + `NotifierRegistry`.
9. Schrijf `tests/sources/test_protocol_contract.py`, `tests/notifiers/test_protocol_contract.py` met fixture-sets; geen adapters geregistreerd, dus tests draaien leeg-groen.
10. Schrijf `docs/missie.md` (verbatim uit `Tool-ontwerp_audit-tool_2026-05-05.md` met versionering).
11. Schrijf `ARCHITECTURE.md` met source/sink/notifier-protocollen + modes-contract uitwerking + reference naar deze design-doc + verwijzing naar `docs/missie.md`.
12. Schrijf `iso-audit/CLAUDE.md` per memory-migratieplan.
13. Acceptatie: CI groen, alle drie contract-tests groen, `docs/missie.md` aanwezig, ARCHITECTURE.md goedgekeurd door auditor.

### Milestone B — verhuizing + Source-adapters + Miro + classificatie-traceability (week 3-5)

1. Migreer alle `Ops_to_Biz/audit/`-modules naar `src/iso_audit/` per doel-architectuur.
2. Splits `gws_client.py` → `src/iso_audit/clients/gws.py` (interne client, niet Source/Sink).
3. Migreer `drive_ingest.py` → `src/iso_audit/sources/drive.py` als `DriveSource`; gebruikt `clients/gws.py`.
4. Migreer `planning_ingest.py` + `gsa_client.py` → `src/iso_audit/sources/planning.py` als `PlanningSource`; gebruikt `clients/gws.py` voor Sheets-API.
5. Merge drie Miro-modules in `src/iso_audit/miro/` met gedeelde `client.py`.
6. Ontvlecht `finding_classification.py` en `_20260420.py` (eerste importeert uit tweede via regel 645): documenteer feitelijke afhankelijkheid in commit-message; consolideer naar `src/iso_audit/classification/findings.py`.
7. Voeg `classifications`-tabel toe aan `store.py` met migratie-script; pas classifier aan om input-hash, prompt-versie, model-versie, raw output te persisteren.
8. Pas pipeline aan voor source-registry: `pipeline --source drive` of `--source jira --source drive`.
9. Schrijf snapshot-tests op fixture-findings vóór en na refactor; exact match vereist op `parsed_klasse` en `parsed_clausule`.
10. Markeer `Ops_to_Biz/audit/` als deprecated in `Ops_to_Biz/CLAUDE.md` met pointer naar `iso-audit`.
11. Verhuis vier audit-OpenSpec-changes — één commit per change-rename voor leesbare diff.
12. Acceptatie: alle bestaande pipeline-runs reproduceerbaar in `iso-audit`; Miro-features werken; contract-tests Drive- en Planning-adapter groen; snapshot-tests groen; classifications-tabel gevuld voor fixture-runs.

### Milestone C — Modes + Notifiers + Jira + Sink (week 6-9)

1. Implementeer `src/iso_audit/modes/` met `Mode` Protocol, `autonoom`, `integer`.
2. Pas pipeline aan om `Decision`-events te emitteren op de zeven beslispunten.
3. Voeg `decisions`-tabel toe aan `store.py` met migratie-script + indexen.
4. Implementeer `src/iso_audit/notifiers/slack.py` (`SlackNotifier`) met Block Kit + button-callback.
5. Implementeer `src/iso_audit/notifiers/email.py` (`EmailNotifier`) met SMTP + Flask-mini-portaal voor magic-link-response.
6. Implementeer `DecisionResolver` als kanaal-agnostische response-handler.
7. Implementeer `src/iso_audit/sinks/drive.py` (`DriveSink`) consolideert `report_generation.py` + `slide_summary.py` + `template_setup.py`.
8. Implementeer `src/iso_audit/sources/jira.py` (`JiraSource`); contract-tests groen.
9. Eerste integer-run-target: `iso-audit pipeline --norm 27001 --source jira --source drive --mode integer --notifier slack`.
10. Tweede smoke-test: `iso-audit pipeline --norm 27001 --source drive --mode integer --notifier email`.
11. Verwijder `Ops_to_Biz/audit/` en `audit/archive/`; ruim `Ops_to_Biz/CLAUDE.md` op.
12. Acceptatie: end-to-end integer-run gedraaid met Jira als primaire en Drive als secundaire bron via Slack-notifier; smoke-test idem via Email-notifier; alle drie hoog-risico beslispunten zichtbaar in handoffs; auditor-besluiten persistent in `decisions`-tabel met `notifier_naam` correct gevuld.

### Rollback-strategie

- **Milestone A**: rollback = repo deleten of unmerged laten. Geen impact op `Ops_to_Biz`.
- **Milestone B**: rollback = revert merge-commit in `iso-audit`; `Ops_to_Biz/audit/` is niet aangeraakt buiten deprecation-comment, dus blijft werkend.
- **Milestone C**: rollback = revert milestone-C-merge; Modes/Notifiers/Jira/Sink verdwijnen, Drive/Planning-only-pipeline blijft werken in `iso-audit` in autonoom-modus.

## Open Questions

1. **`normteksten.py` (132 KB) splitsen in milestone B of in eigen change?** Huidig: één bestand met ISO 9001 + 27001 normteksten als Python-data. **Voorstel:** korte termijn in milestone B splitsen naar `src/iso_audit/data/normteksten/iso9001.py` + `iso27001.py` + `__init__.py`. Lange termijn (eigen change na milestone C): migreren naar YAML met loader, zodat norm-updates door non-Python-reviewers gedaan kunnen worden. Beslissen in milestone-B-design-review.

2. **Multi-source merge-semantiek.** `pipeline --source jira --source drive` moet documents en findings van beide adapters mergen vóór classificatie. Dedup op `(bron, id)`-tuple of op content-hash? **Voorstel:** `(bron, id)` is voldoende voor uniciteit (twee bronnen kunnen niet hetzelfde finding leveren want `bron`-veld verschilt); content-hash voor *near-duplicate-detection* is een eigen change-proposal als dat ooit speelt.

3. **Coverage-gate-niveau.** Voorstel meet baseline in milestone B en zet gate op baseline + 5%. Maar wat als baseline al hoog is (>85%)? **Voorstel:** plafond bij 85% — daarboven geeft strikter geen extra waarde voor een audit-tool. Beslissen in milestone B.

4. **EmailNotifier-portaal — TLS in MVP?** Lokaal Flask-portaal voor magic-link-respons. **Voorstel:** HTTP zonder TLS in MVP, omdat het lokaal draait op pipeline-host en magic-link tokens single-use + tijd-gelimiteerd zijn. Bij multi-host-deployment (ooit) TLS verplichten via reverse-proxy. Te documenteren als acceptable risk in `docs/notifiers/email.md`.

5. **Notifier-naam voor MCP-handoff later?** Als toekomstige MCP-server een handoff-channel wordt (bv. iemand bouwt `mcp-teams-notifier`), past die in de NotifierRegistry of is dat een andere abstractie? **Voorstel:** zelfde registry, `naam = "mcp:teams"`. Open vraag of de dubbele-punt-naamgeving acceptabel is voor zowel Source als Notifier — moet symmetrisch worden besloten over beide registries tegelijk.

6. **Patch ook `Ops_to_Biz/output/business_gws.py` en `output/gws.py`?** Deze parent-repo-bestanden gebruiken Drive voor non-audit-uitvoer (handbook). Niet gemigreerd naar `iso-audit`. **Voorstel:** out-of-scope — handbook-pad is eigen capability in `Ops_to_Biz`. Wel documenteren in `Ops_to_Biz/CLAUDE.md` dat deze bestanden niet door de iso-audit-refactor geraakt worden.

7. **`docs/missie.md` versioneren als de tool buiten Conduction wordt gebruikt?** Ontwerpdocument is Conduction-specifiek (interne auditor + team lead). **Voorstel:** behouden als historisch ankerdocument; bij eerste externe afnemer een `docs/missie-generic.md` afsplitsen die de drie capabilities en het rolconflict-frame los van Conduction-context beschrijft. Niet nu doen — speculatieve scope.
