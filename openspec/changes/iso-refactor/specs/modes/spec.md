## ADDED Requirements

### Requirement: Mode Protocol definieert uniform contract voor pipeline-runmodes

Het systeem SHALL een `Mode` Protocol bieden in `src/iso_audit/modes/base.py` met:

- `naam: str` (uniek class-attribute, kebab-case)
- `beslis(decision: Decision) -> dict` (retourneert het definitieve besluit)

Een `Decision` SHALL als dataclass gedefinieerd zijn met de velden `punt: str`, `context: dict`, `voorstel: dict`, `risico: str` (waarden: `"laag"`, `"midden"`, `"hoog"`), en `audit_id: str`.

#### Scenario: Mode implementeert Protocol-conformance

- **WHEN** een nieuwe Mode wordt toegevoegd in `src/iso_audit/modes/`
- **THEN** mypy `--strict` MUST geen fouten geven op Protocol-implementatie
- **AND** de Mode MUST een unieke `naam` hebben

### Requirement: Pipeline emitteert Decision-events op zeven vooraf vastgelegde punten

De pipeline SHALL `Decision`-events emitteren op de volgende beslispunten:

| Punt | Risico |
|---|---|
| `ingest_scope` | laag |
| `merge_drive_miro` | laag |
| `classify_finding` | midden |
| `assign_clausule` | midden |
| `generate_report_section` | hoog |
| `send_report` | hoog |
| `delete_data` | hoog |

Elke Decision SHALL voldoende context bevatten zodat de Mode-implementatie autonoom of mens-bevestigd kan beslissen zonder verdere queries.

`ingest_scope` SHALL geëmitteerd worden direct na Source-instantiation maar vóór de eerste `list_documents()`-call; context bevat counts per source en eventuele filter-samenvatting.

Toevoeging van nieuwe beslispunten SHALL via een eigen change-proposal verlopen.

#### Scenario: Pipeline-stap classify_finding emitteert Decision

- **WHEN** de pipeline een document classificeert via LLM
- **THEN** een `Decision(punt="classify_finding", risico="midden", ...)` MUST aan de actieve Mode worden voorgelegd
- **AND** het besluit van de Mode MUST de definitieve classificatie bepalen

#### Scenario: Pipeline-stap delete_data zonder Mode-acceptatie

- **WHEN** een pipeline-stap data-verwijdering vereist
- **AND** de actieve Mode geeft geen besluit met `actie="delete"`
- **THEN** de pipeline MUST de verwijdering overslaan en doorgaan
- **AND** een log-entry MUST de overgeslagen verwijdering registreren

#### Scenario: Pipeline emitteert ingest_scope vóór eerste fetch

- **WHEN** de pipeline een Source instantieert
- **THEN** een `Decision(punt="ingest_scope", risico="laag", context={"sources": [{"naam": "drive", "count": 145}, ...]}, ...)` MUST geëmitteerd worden vóór `list_documents()` wordt geconsumeerd
- **AND** het besluit MUST bepalen of de pipeline doorgaat (`actie="proceed"`) of stopt (`actie="abort"`)

### Requirement: Autonoom-modus accepteert voorstellen zonder onderbreking, persisteert selectief

Een `AutonoomMode` SHALL bestaan in `src/iso_audit/modes/autonoom.py` met `naam = "autonoom"`.

Voor elke `Decision` met `risico` in `["laag", "midden"]` SHALL `AutonoomMode.beslis()` het `voorstel`-veld als definitief besluit retourneren — geen onderbreking, geen externe call, geen rij in `decisions`-tabel.

Voor `Decision` met `risico="hoog"` SHALL `AutonoomMode.beslis()`:
- Voor `delete_data`: een uitzondering — pipeline blokkeert deletion altijd in autonoom-modus, retourneert `{"actie": "skip", "reden": "delete_data niet toegestaan in autonoom-modus"}`.
- Voor andere hoog-risico-punten (`generate_report_section`, `send_report`): het voorstel als besluit retourneren.
- In alle hoog-risico gevallen: een rij in `decisions`-tabel schrijven met `status="resolved"`, `notifier_naam=NULL`, `besluit_json` gelijk aan het besluit.

Selectieve persistentie voorkomt dat de `decisions`-tabel pollutet met laag- en midden-risico-rijen waar voorstel == besluit zonder mens, omdat die rijen geen analytische waarde hebben voor capability 3 (auditor-spiegel).

#### Scenario: Autonoom besluit voor classify_finding

- **WHEN** de pipeline `Decision(punt="classify_finding", voorstel={"klasse": "OFI"})` aanbiedt aan AutonoomMode
- **THEN** `beslis()` MUST `{"klasse": "OFI"}` retourneren zonder externe call
- **AND** GEEN rij MUST in de `decisions`-tabel geschreven worden

#### Scenario: Autonoom blokkeert delete_data

- **WHEN** de pipeline `Decision(punt="delete_data", risico="hoog", ...)` aanbiedt aan AutonoomMode
- **THEN** `beslis()` MUST `{"actie": "skip", "reden": "delete_data niet toegestaan in autonoom-modus"}` retourneren
- **AND** een rij MUST in `decisions`-tabel geschreven worden met `status="resolved"`, `notifier_naam=NULL`

#### Scenario: Autonoom accepteert send_report en logt

- **WHEN** de pipeline `Decision(punt="send_report", risico="hoog", voorstel={...})` aanbiedt aan AutonoomMode
- **THEN** `beslis()` MUST het voorstel retourneren
- **AND** een rij MUST in `decisions`-tabel geschreven worden met `status="resolved"`, `notifier_naam=NULL`, `besluit_json` gelijk aan voorstel

### Requirement: Integer-modus escaleert hoog-risico beslissingen via Notifier

Een `IntegerMode` SHALL bestaan in `src/iso_audit/modes/integer.py` met `naam = "integer"`.

`IntegerMode` SHALL bij constructie een `Notifier` instance accepteren via dependency injection; de mode SHALL geen kennis hebben van het concrete kanaal (Slack, Email, etc.).

Voor `Decision` met `risico="laag"` SHALL `IntegerMode.beslis()`:
- Standaard het voorstel autonoom accepteren (geen onderbreking, geen rij in tabel).
- Uitzondering: wanneer de context een flag `vraag_bevestiging=True` bevat (relevant voor `ingest_scope`), via Notifier escaleren.

Voor `Decision` met `risico="midden"` SHALL `IntegerMode.beslis()`:
- Het voorstel autonoom accepteren tenzij de context een `confidence` veld < 0.7 bevat — dan via Notifier escaleren.

Voor `Decision` met `risico="hoog"` SHALL `IntegerMode.beslis()`:
- Altijd via Notifier escaleren naar de auditor.

Tijdens escalatie SHALL de Decision in de SQLite `decisions`-tabel worden gepersisteerd met `status="pending"`, `notifier_naam` gelijk aan `notifier.naam`, en de pipeline-thread blokkeren tot een resolved-status binnenkomt.

#### Scenario: Integer-modus escaleert send_report

- **WHEN** de pipeline `Decision(punt="send_report", risico="hoog", ...)` aanbiedt aan IntegerMode
- **THEN** de Notifier MUST `vraag_besluit(decision)` aangeroepen worden
- **AND** de Decision MUST in de `decisions`-tabel worden gepersisteerd met `status="pending"` en `notifier_naam` correct gevuld
- **AND** de pipeline-thread MUST blokkeren tot de status `resolved` is

#### Scenario: Integer-modus accepteert merge_drive_miro autonoom

- **WHEN** de pipeline `Decision(punt="merge_drive_miro", risico="laag", ...)` aanbiedt aan IntegerMode
- **THEN** `beslis()` MUST het voorstel direct retourneren
- **AND** geen Notifier-call MUST plaatsvinden
- **AND** geen rij MUST in de `decisions`-tabel geschreven worden

#### Scenario: Integer-modus escaleert classify_finding bij low-confidence

- **WHEN** de pipeline `Decision(punt="classify_finding", risico="midden", context={"confidence": 0.55}, ...)` aanbiedt
- **THEN** de Notifier MUST `vraag_besluit(decision)` aangeroepen worden

#### Scenario: Integer-modus escaleert ingest_scope met flag

- **WHEN** de pipeline `Decision(punt="ingest_scope", risico="laag", context={"sources": [...], "vraag_bevestiging": True}, ...)` aanbiedt aan IntegerMode
- **THEN** de Notifier MUST `vraag_besluit(decision)` aangeroepen worden
- **AND** de pipeline MUST blokkeren tot bevestiging

### Requirement: `decisions`-tabel is rapporteerbare audit-trail data

Het systeem SHALL een `decisions`-tabel beheren in `iso_audit.db` met schema:

```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    audit_id TEXT NOT NULL,
    punt TEXT NOT NULL,
    context_json TEXT NOT NULL,
    voorstel_json TEXT NOT NULL,
    status TEXT NOT NULL,
    besluit_json TEXT,
    risico TEXT NOT NULL,
    classificatie_id INTEGER,
    notifier_naam TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (classificatie_id) REFERENCES classifications(id)
);

CREATE INDEX idx_decisions_audit_status ON decisions(audit_id, status);
CREATE INDEX idx_decisions_punt_resolved ON decisions(punt, resolved_at);
```

Status-waarden SHALL zijn: `pending`, `resolved`, `cancelled`.

De pipeline SHALL geen rijen verwijderen of overschrijven na `status="resolved"` of `status="cancelled"`. Append-only-discipline.

Een pipeline die hervat na crash SHALL pending Decisions detecteren en hervatten in plaats van opnieuw escaleren.

De tabel SHALL ontworpen zijn voor cross-run analyse: toekomstige spiegel-laag (eigen change-proposal `iso-audit-mirror-foundation`) MAY queries doen op `(punt, risico, audit_id)` om patronen te detecteren in auditor-besluiten over runs heen.

#### Scenario: Decision wordt persistent gemaakt bij escalatie

- **WHEN** IntegerMode een hoog-risico Decision escaleert
- **THEN** een rij MUST in `decisions` worden geschreven met `status="pending"`, `notifier_naam` gelijk aan de actieve notifier, en alle context
- **AND** de rij MUST een unieke `id` hebben

#### Scenario: Pipeline hervat na crash met pending Decision

- **WHEN** de pipeline restart en een rij met `status="pending"` voor de huidige `audit_id` bestaat
- **THEN** de pipeline MUST de bestaande Decision hervatten in plaats van een nieuwe te emitteren
- **AND** geen dubbele Notifier-call MUST gestuurd worden

#### Scenario: Resolved rij wordt overschreven

- **WHEN** een PR code toevoegt die een `resolved` rij update of verwijdert
- **THEN** review MUST dit als off-spec markeren onder verwijzing naar de append-only-invariant

### Requirement: Mode-selectie via verplichte `--mode` flag

De CLI SHALL een `--mode <autonoom|integer>` flag accepteren. De flag SHALL verplicht zijn (geen CLI-default).

Wanneer de flag ontbreekt en `ISO_AUDIT_DEFAULT_MODE` env-var niet gezet is SHALL de CLI exit-code 2 geven met een foutmelding die de twee modes opsomt.

Wanneer `--mode integer` is gekozen SHALL `--notifier <naam>` óók verplicht zijn (zie notifier-spec).

#### Scenario: Run zonder mode-flag

- **WHEN** `iso-audit pipeline --norm 27001 --source drive` zonder `--mode` en zonder env-var
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** stderr MUST "missing required argument: --mode" bevatten met opties `autonoom` en `integer`

#### Scenario: Run met `--mode integer` zonder `--notifier`

- **WHEN** `iso-audit pipeline --norm 27001 --source drive --mode integer` zonder `--notifier`
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** stderr MUST "missing required argument when --mode integer: --notifier" bevatten

#### Scenario: Run met `--mode integer --notifier slack`

- **WHEN** `iso-audit pipeline --norm 27001 --source drive --mode integer --notifier slack`
- **THEN** de pipeline MUST IntegerMode als actieve Mode gebruiken
- **AND** SlackNotifier MUST geïnjecteerd worden in IntegerMode
- **AND** Decision-events bij hoog-risico-punten MUST naar Slack escaleren

### Requirement: Modes en Sources en Notifiers zijn orthogonaal

Een Mode SHALL niet afhankelijk zijn van welke Source actief is.
Een Source SHALL niet afhankelijk zijn van welke Mode actief is.
Een Mode SHALL niet afhankelijk zijn van welke Notifier actief is (alleen via Protocol).
Een Notifier SHALL niet afhankelijk zijn van welke Mode actief is.

Pipeline orchestratie SHALL Source, Mode en Notifier onafhankelijk resolven.

#### Scenario: Jira-source met integer-mode en email-notifier

- **WHEN** `iso-audit pipeline --source jira --mode integer --notifier email` draait
- **THEN** alle Decision-events MUST gewoon werken — Jira-bevindingen escaleren via dezelfde Notifier-flow als Drive-bevindingen
- **AND** EmailNotifier MUST aangeroepen worden ongeacht welke source de Decision triggerde

#### Scenario: Drive-source met autonoom-mode

- **WHEN** `iso-audit pipeline --source drive --mode autonoom` draait
- **THEN** alle Decisions MUST autonoom afgehandeld worden — geen Notifier-traffic
- **AND** geen `--notifier` flag MUST vereist zijn
