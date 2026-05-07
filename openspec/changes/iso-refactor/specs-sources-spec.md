## ADDED Requirements

### Requirement: Source Protocol defines uniform contract for finding-bronnen

Het systeem SHALL een `Source` Protocol bieden in `src/iso_audit/sources/base.py` met de volgende methodes:

- `list_documents(filter: dict | None = None) -> Iterator[Document]`
- `fetch_content(doc: Document) -> str`
- `list_findings(sessie_id: str) -> Iterator[Finding]`
- `healthcheck() -> dict`

Het Protocol SHALL `naam: str` als class-level attribuut vereisen (uniek, lowercase, kebab-case voor multi-woord, e.g. `"drive"`, `"planning"`, `"jira"`, `"mcp-asana"`).

`Document` en `Finding` SHALL als frozen dataclasses gedefinieerd zijn met de velden uit de doel-architectuur.

`list_documents` SHALL een `Iterator[Document]` returnen (geen lijst); adapters MAY intern paginated API-calls doen, maar deze pagination SHALL adapter-private zijn.

#### Scenario: Adapter implementeert volledige Source-contract

- **WHEN** een nieuwe adapter wordt toegevoegd in `src/iso_audit/sources/`
- **THEN** mypy `--strict` MUST geen fouten rapporteren op het Protocol-conformance check
- **AND** de adapter MUST een `naam` attribuut hebben dat uniek is binnen de geregistreerde set

#### Scenario: Adapter mist verplichte methode

- **WHEN** een adapter een van de vier methodes niet implementeert
- **THEN** mypy `--strict` MUST een Protocol-violation error geven
- **AND** de adapter MUST NOT in CI groen worden

#### Scenario: list_documents returnt Iterator, geen lijst

- **WHEN** een adapter `list_documents()` aanroept
- **THEN** het returnvalue MUST een Iterator zijn (lazy evaluation mogelijk)
- **AND** consumers MUST verantwoordelijk zijn voor materialisatie wanneer nodig

### Requirement: Source-configuratie is immutable binnen een audit-run

Een Source SHALL geconfigureerd worden uit env-vars of een config-bestand bij pipeline-start. De Source SHALL geen API hebben om configuratie tijdens een run te wijzigen — geen runtime `set_folder()`, `set_filter()`, `update_scope()` of equivalent.

Dit garandeert dat de pipeline-operator of auditor geen tussentijdse curatie kan doen, conform missie capability 1 (onafhankelijke bronnen, geen curated input).

#### Scenario: Adapter biedt runtime-mutatie-methode

- **WHEN** een adapter een methode bevat die runtime-configuratie muteert (bijvoorbeeld `set_folder_id()`)
- **THEN** review MUST dit als off-spec markeren
- **AND** de PR MUST geblokkeerd worden tot de mutatie-methode is verwijderd

#### Scenario: Adapter herleest config uit env tijdens run

- **WHEN** een adapter midden in `list_documents()` opnieuw env-vars uitleest
- **THEN** dit MUST als runtime-mutatie geclassificeerd worden
- **AND** de adapter MUST geweigerd worden door contract-tests die env-mutatie tijdens iteration detecteren

### Requirement: Pipeline selecteert source via verplichte `--source` flag

De CLI SHALL een `--source <naam>` flag accepteren. De flag SHALL verplicht zijn (geen CLI-default).

Wanneer de flag ontbreekt en `ISO_AUDIT_DEFAULT_SOURCE` env-var niet gezet is SHALL de CLI exit-code 2 geven met een foutmelding die de beschikbare adapters opsomt.

Wanneer de flag ontbreekt maar `ISO_AUDIT_DEFAULT_SOURCE` gezet is SHALL de CLI de env-var-waarde gebruiken én loggen op INFO-niveau dat de default uit env wordt gebruikt.

Wanneer de flag een onbekende waarde heeft SHALL de CLI exit-code 2 geven met een lijst van geregistreerde adapters.

De flag SHALL meerdere keren gebruikt mogen worden voor multi-source runs (bv. `--source jira --source drive`).

#### Scenario: Run zonder source-flag en zonder env-var

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --mode autonoom` uitvoert zonder `--source` en zonder `ISO_AUDIT_DEFAULT_SOURCE`
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** de stderr MUST de tekst "missing required argument: --source" bevatten
- **AND** de stderr MUST een lijst van beschikbare adapters tonen

#### Scenario: Run zonder source-flag maar met env-var

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --mode autonoom` uitvoert met `ISO_AUDIT_DEFAULT_SOURCE=drive`
- **THEN** de pipeline MUST drive als source gebruiken
- **AND** een INFO-log MUST melden "using ISO_AUDIT_DEFAULT_SOURCE=drive"

#### Scenario: Run met onbekende source

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source asdf` uitvoert
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** de stderr MUST aangeven dat `asdf` geen geregistreerde adapter is

#### Scenario: Run met twee sources

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source jira --source drive` uitvoert
- **THEN** de pipeline MUST documenten en findings van beide adapters mergen vóór classificatie
- **AND** dedup MUST plaatsvinden op `(bron, id)`-tuple

### Requirement: Drive-adapter implementeert Source Protocol

Een `DriveSource` SHALL bestaan in `src/iso_audit/sources/drive.py` die `Source` implementeert en feature-pariteit biedt met de huidige `Ops_to_Biz/audit/drive_ingest.py`.

De adapter SHALL `naam = "drive"` hebben.

De adapter SHALL Google Workspace Service-Account-authenticatie gebruiken via `src/iso_audit/clients/gws.py` (interne client-module, niet zelf een Source of Sink).

De adapter SHALL alleen het read-pad implementeren; schrijven van rapporten naar Drive SHALL via `DriveSink` (milestone C) verlopen.

#### Scenario: Drive-adapter haalt documenten op

- **WHEN** de Drive-adapter `list_documents()` aanroept
- **THEN** alle documenten in de geconfigureerde Shared Drive (env: `AUDIT_SOURCE_FOLDER_ID`) MUST geretourneerd worden
- **AND** elk Document MUST de velden `id`, `titel`, `bron="drive"`, `type`, `laatst_gewijzigd`, `inhoud_uri` correct bevatten

#### Scenario: Drive-adapter healthcheck zonder credentials

- **WHEN** de Drive-adapter `healthcheck()` aanroept zonder geldige credentials
- **THEN** de geretourneerde dict MUST `status: "fail"` bevatten
- **AND** een `reden`-veld dat naar de ontbrekende credentials verwijst

### Requirement: Planning-adapter implementeert Source Protocol

Een `PlanningSource` SHALL bestaan in `src/iso_audit/sources/planning.py` die `Source` implementeert.

De adapter SHALL `naam = "planning"` hebben.

De adapter SHALL Google Sheets API gebruiken via `src/iso_audit/clients/gws.py`; consolideert de huidige `Ops_to_Biz/audit/planning_ingest.py` + `gsa_client.py`.

De adapter is conceptueel een aparte bron van Drive, niet een sub-bron, omdat Sheets-data andere semantiek heeft (rij-georiënteerde planning) dan Drive-documenten (file-georiënteerde policies).

#### Scenario: Planning-adapter haalt planning-tabbladen op

- **WHEN** de Planning-adapter `list_documents()` aanroept
- **THEN** alle geconfigureerde planning-tabbladen (env: `AUDIT_PLANNING_SHEET_ID`) MUST als Document geretourneerd worden
- **AND** elk Document MUST `bron="planning"` hebben

### Requirement: Jira-adapter implementeert Source Protocol

Een `JiraSource` SHALL bestaan in `src/iso_audit/sources/jira.py` die `Source` implementeert.

De adapter SHALL `naam = "jira"` hebben.

De adapter SHALL Jira Cloud REST API v3 gebruiken met token-authenticatie via env-vars (`JIRA_TOKEN`, `JIRA_EMAIL`, `JIRA_BASE_URL`).

De adapter SHALL Jira-issues mappen naar `Document` (issue-metadata) en `Finding` (issue als bevinding) waar passend.

#### Scenario: Jira-adapter haalt open incidents op

- **WHEN** de Jira-adapter `list_findings(sessie_id="2026-06")` aanroept met JQL `project = INCIDENTS AND status != Closed`
- **THEN** alle matching issues MUST als `Finding` geretourneerd worden
- **AND** elk Finding MUST `bron="jira"` hebben en `clausule_ids` afgeleid van issue-labels of -componenten

#### Scenario: Jira-adapter healthcheck met geldige token

- **WHEN** de Jira-adapter `healthcheck()` aanroept met geldige credentials
- **THEN** de geretourneerde dict MUST `status: "ok"` bevatten
- **AND** een `tenant`-veld met de Jira-instance-URL

### Requirement: Contract-tests draaien tegen elke geregistreerde adapter

Een `tests/sources/test_protocol_contract.py` SHALL een fixture-set bevatten die identiek is voor alle adapters.

Voor elke geregistreerde adapter SHALL pytest een parametrized test-suite draaien die de volgende invarianten controleert:

- `list_documents()` returnt een `Iterator[Document]` (geen list)
- Alle Documents hebben de juiste `bron`-waarde overeenkomstig `adapter.naam`
- `healthcheck()` returnt een dict met minimaal de keys `status` en `tenant`
- `fetch_content(doc)` returnt een non-empty string voor een geldige Document
- Configuratie is immutable: het opnieuw aanroepen van `list_documents()` met dezelfde input levert hetzelfde resultaat (idempotency-check)

Een nieuwe adapter SHALL pas mergeable zijn wanneer alle contract-tests groen zijn.

#### Scenario: Drive-adapter passeert contract-tests

- **WHEN** `pytest tests/sources/test_protocol_contract.py -k drive` draait
- **THEN** alle parametrized tests MUST groen zijn

#### Scenario: Nieuwe adapter mist `naam` attribuut

- **WHEN** een ontwikkelaar een adapter toevoegt zonder `naam` class-attribute
- **THEN** de contract-test MUST falen op de "adapter has unique naam" assertion
- **AND** CI MUST de PR blokkeren

### Requirement: Source-registry beheert lifecycle van geregistreerde adapters

Een `SourceRegistry` SHALL bestaan in `src/iso_audit/sources/__init__.py` die:

- Adapters registreert via een `@register` decorator of expliciete `register(adapter_class)` call
- `available()` methode biedt die een lijst van geregistreerde namen returnt
- `get(naam)` methode biedt die een geconfigureerde adapter-instance returnt of `KeyError` werpt

De registry SHALL idempotent zijn: dubbele registratie van dezelfde adapter-naam SHALL een `ValueError` werpen.

#### Scenario: Adapter wordt geregistreerd via decorator

- **WHEN** een adapter-class wordt voorzien van `@register`
- **THEN** `SourceRegistry.available()` MUST de adapter-naam bevatten

#### Scenario: Dubbele registratie

- **WHEN** twee adapters proberen dezelfde `naam` te registreren
- **THEN** de tweede registratie MUST een `ValueError` werpen
- **AND** de eerste registratie blijft actief

### Requirement: Source-protocol blijft read-only; write-back gaat via aparte Sink

Het `Source` Protocol SHALL geen write-methodes bevatten. Schrijfacties (rapport publiceren, Miro-bord aanmaken, Jira-issue aanmaken) SHALL via een apart `Sink` Protocol verlopen, gespecificeerd in milestone A in `src/iso_audit/sinks/base.py`.

Een adapter MAY zowel `Source` als `Sink` implementeren als aparte class-instanties (bv. `DriveSource` en `DriveSink` worden onafhankelijk geregistreerd).

`Sink` Protocol SHALL bevatten:
- `naam: str` (uniek, kebab-case)
- `send(payload: SinkPayload) -> SinkResult`
- `healthcheck() -> dict`

`SinkPayload` SHALL een dataclass-hierarchy zijn met minimaal `ReportPayload`, `NotificationPayload`, `MirrorPayload` (laatste als placeholder voor toekomstige spiegel-laag).

Sink-implementaties SHALL niet vóór milestone C bestaan; in milestone A en B is het Protocol spec-only.

#### Scenario: Read-only adapter implementeert geen Sink

- **WHEN** de Jira-adapter alleen `Source` implementeert
- **THEN** de pipeline MUST de adapter accepteren voor read-paden
- **AND** write-paden (zoals rapport-verzending naar Jira) MUST NOT op deze adapter routeren

#### Scenario: Sink-implementatie in milestone A of B

- **WHEN** een PR een concrete Sink-implementatie toevoegt vóór milestone C
- **THEN** review MUST dit als off-milestone markeren onder verwijzing naar deze requirement
- **AND** alleen het `base.py`-Protocol en de `SinkPayload`-dataclasses MAY in milestone A of B bestaan
