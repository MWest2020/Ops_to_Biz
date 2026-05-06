## ADDED Requirements

### Requirement: Mode Protocol definieert uniform contract voor pipeline-runmodes

Het systeem SHALL een `Mode` Protocol bieden in `src/iso_audit/modes/base.py` met:

- `naam: str` (uniek class-attribute, kebab-case)
- `beslis(decision: Decision) -> dict` (retourneert het definitieve besluit)

Een `Decision` SHALL als dataclass gedefinieerd zijn met de velden `punt: str`, `context: dict`, `voorstel: dict`, `risico: str` (waarden: `"laag"`, `"midden"`, `"hoog"`).

#### Scenario: Mode implementeert Protocol-conformance

- **WHEN** een nieuwe Mode wordt toegevoegd in `src/iso_audit/modes/`
- **THEN** mypy `--strict` MUST geen fouten geven op Protocol-implementatie
- **AND** de Mode MUST een unieke `naam` hebben

### Requirement: Pipeline emitteert Decision-events op zes vooraf vastgelegde punten

De pipeline SHALL `Decision`-events emitteren op de volgende beslispunten:

| Punt | Risico |
|---|---|
| `classify_finding` | midden |
| `merge_drive_miro` | laag |
| `assign_clausule` | midden |
| `generate_report_section` | hoog |
| `send_report` | hoog |
| `delete_data` | hoog |

Elke Decision SHALL voldoende context bevatten zodat de Mode-implementatie autonoom of mens-bevestigd kan beslissen zonder verdere queries.

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

### Requirement: Autonoom-modus accepteert alle voorstellen zonder onderbreking

Een `AutonoomMode` SHALL bestaan in `src/iso_audit/modes/autonoom.py` met `naam = "autonoom"`.

Voor elke `Decision` SHALL `AutonoomMode.beslis()` het `voorstel`-veld als definitief besluit retourneren — geen onderbreking, geen externe call.

`AutonoomMode` SHALL bij `risico="hoog"` voor `delete_data` een uitzondering maken: de pipeline blokkeert deletion altijd in autonoom-modus.

#### Scenario: Autonoom besluit voor classify_finding

- **WHEN** de pipeline `Decision(punt="classify_finding", voorstel={"klasse": "OFI"})` aanbiedt aan AutonoomMode
- **THEN** `beslis()` MUST `{"klasse": "OFI"}` retourneren zonder externe call

#### Scenario: Autonoom blokkeert delete_data

- **WHEN** de pipeline `Decision(punt="delete_data", risico="hoog", ...)` aanbiedt aan AutonoomMode
- **THEN** `beslis()` MUST `{"actie": "skip", "reden": "delete_data niet toegestaan in autonoom-modus"}` retourneren

### Requirement: Integer-modus escaleert hoog-risico beslissingen via Slack Block Kit

Een `IntegerMode` SHALL bestaan in `src/iso_audit/modes/integer.py` met `naam = "integer"`.

Voor `Decision` met `risico="laag"` SHALL `IntegerMode.beslis()` het voorstel autonoom accepteren (geen onderbreking).

Voor `Decision` met `risico="midden"` SHALL `IntegerMode.beslis()` het voorstel autonoom accepteren tenzij de context een `confidence < 0.7` veld bevat — dan wordt geescaleerd.

Voor `Decision` met `risico="hoog"` SHALL `IntegerMode.beslis()` altijd escaleren naar de auditor via Slack Block Kit.

Tijdens escalatie SHALL de Decision in de SQLite `decisions`-tabel worden gepersisteerd met `status="pending"` en de pipeline-thread blokkeren tot een resolved-status binnenkomt.

#### Scenario: Integer-modus escaleert send_report

- **WHEN** de pipeline `Decision(punt="send_report", risico="hoog", ...)` aanbiedt aan IntegerMode
- **THEN** een Slack Block Kit message MUST naar het geconfigureerde kanaal worden gestuurd
- **AND** de Decision MUST in de `decisions`-tabel worden gepersisteerd met `status="pending"`
- **AND** de pipeline-thread MUST blokkeren tot de status `resolved` is

#### Scenario: Integer-modus accepteert merge_drive_miro autonoom

- **WHEN** de pipeline `Decision(punt="merge_drive_miro", risico="laag", ...)` aanbiedt aan IntegerMode
- **THEN** `beslis()` MUST het voorstel direct retourneren
- **AND** geen Slack-message MUST verstuurd worden
- **AND** geen rij MUST in de `decisions`-tabel geschreven worden

#### Scenario: Integer-modus escaleert classify_finding bij low-confidence

- **WHEN** de pipeline `Decision(punt="classify_finding", risico="midden", context={"confidence": 0.55}, ...)` aanbiedt
- **THEN** een Slack Block Kit message MUST naar de auditor worden gestuurd

### Requirement: Integer-modus state persistent in SQLite `decisions`-tabel

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
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
```

Status-waarden SHALL zijn: `pending`, `resolved`, `cancelled`.

Een pipeline die hervat na crash SHALL pending Decisions detecteren en hervatten in plaats van opnieuw escaleren.

#### Scenario: Decision wordt persistent gemaakt bij escalatie

- **WHEN** IntegerMode een hoog-risico Decision escaleert
- **THEN** een rij MUST in `decisions` worden geschreven met `status="pending"` en alle context
- **AND** de rij MUST een unieke `id` hebben

#### Scenario: Pipeline hervat na crash met pending Decision

- **WHEN** de pipeline restart en een rij met `status="pending"` voor de huidige `audit_id` bestaat
- **THEN** de pipeline MUST de bestaande Decision hervatten in plaats van een nieuwe te emitteren
- **AND** geen dubbele Slack-message MUST gestuurd worden

### Requirement: Mode-selectie via verplichte `--mode` flag

De CLI SHALL een `--mode <autonoom|integer>` flag accepteren. De flag SHALL verplicht zijn (geen default).

Wanneer de flag ontbreekt SHALL de CLI exit-code 2 geven met een foutmelding die de twee modes opsomt.

#### Scenario: Run zonder mode-flag

- **WHEN** `iso-audit pipeline --norm 27001 --source drive` zonder `--mode`
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** stderr MUST "missing required argument: --mode" bevatten met opties `autonoom` en `integer`

#### Scenario: Run met `--mode integer`

- **WHEN** `iso-audit pipeline --norm 27001 --source drive --mode integer`
- **THEN** de pipeline MUST IntegerMode als actieve Mode gebruiken
- **AND** Decision-events bij hoog-risico-punten MUST naar Slack escaleren

### Requirement: Slack Block Kit handoff biedt structured response-mogelijkheden

De Slack Block Kit message SHALL voor elke geescaleerde Decision bevatten:

- Een header met het beslispunt en risico-niveau
- De context als formatted code-block (JSON, leesbaar)
- Het voorgesteld besluit als formatted code-block
- Action-buttons voor minimaal: `Goedkeuren`, `Afwijzen`, `Aanpassen` (laatste opent een modal)
- Een unieke decision-id als button-value zodat de response-handler de juiste rij kan updaten

De handoff-channel SHALL configureerbaar zijn via env-var `SLACK_AUDIT_CHANNEL`.

#### Scenario: Auditor klikt Goedkeuren

- **WHEN** de auditor op de `Goedkeuren`-button klikt
- **THEN** de response-handler MUST de `decisions`-rij updaten naar `status="resolved"` met `besluit_json` gelijk aan het voorstel
- **AND** de pipeline-thread MUST hervatten met dat besluit

#### Scenario: Auditor klikt Aanpassen en submit modal

- **WHEN** de auditor op `Aanpassen` klikt en een gewijzigd besluit submit
- **THEN** de response-handler MUST `besluit_json` updaten met de gewijzigde waarde
- **AND** `status` MUST op `resolved` gezet worden

### Requirement: Modes en Sources zijn orthogonaal

Een Mode SHALL niet afhankelijk zijn van welke Source actief is.

Een Source SHALL niet afhankelijk zijn van welke Mode actief is.

Pipeline orchestratie SHALL Mode en Source onafhankelijk resolven.

#### Scenario: Jira-source met integer-mode

- **WHEN** `iso-audit pipeline --source jira --mode integer` draait
- **THEN** alle Decision-events MUST gewoon werken — Jira-bevindingen escaleren via dezelfde Slack-flow als Drive-bevindingen

#### Scenario: Drive-source met autonoom-mode

- **WHEN** `iso-audit pipeline --source drive --mode autonoom` draait
- **THEN** alle Decisions MUST autonoom afgehandeld worden — geen Slack-traffic
