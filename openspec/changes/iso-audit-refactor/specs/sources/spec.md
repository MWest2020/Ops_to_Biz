## ADDED Requirements

### Requirement: Source Protocol defines uniform contract for finding-bronnen

Het systeem SHALL een `Source` Protocol bieden in `src/iso_audit/sources/base.py` met de volgende methodes:

- `list_documents(filter: dict | None = None) -> Iterator[Document]`
- `fetch_content(doc: Document) -> str`
- `list_findings(sessie_id: str) -> Iterator[Finding]`
- `healthcheck() -> dict`

Het Protocol SHALL `naam: str` als class-level attribuut vereisen (uniek, lowercase, kebab-case voor multi-woord, e.g. `"drive"`, `"jira"`, `"mcp:asana"`).

`Document` en `Finding` SHALL als frozen dataclasses gedefinieerd zijn met de velden uit de doel-architectuur.

#### Scenario: Adapter implementeert volledige Source-contract

- **WHEN** een nieuwe adapter wordt toegevoegd in `src/iso_audit/sources/`
- **THEN** mypy `--strict` MUST geen fouten rapporteren op het Protocol-conformance check
- **AND** de adapter MUST een `naam` attribuut hebben dat uniek is binnen de geregistreerde set

#### Scenario: Adapter mist verplichte methode

- **WHEN** een adapter een van de vier methodes niet implementeert
- **THEN** mypy `--strict` MUST een Protocol-violation error geven
- **AND** de adapter MUST NOT in CI groen worden

### Requirement: Pipeline selecteert source via verplichte `--source` flag

De CLI SHALL een `--source <naam>` flag accepteren. De flag SHALL verplicht zijn (geen default).

Wanneer de flag ontbreekt SHALL de CLI exit-code 2 geven met een foutmelding die de beschikbare adapters opsomt.

Wanneer de flag een onbekende waarde heeft SHALL de CLI exit-code 2 geven met een lijst van geregistreerde adapters.

De flag SHALL meerdere keren gebruikt mogen worden voor multi-source runs (bv. `--source jira --source drive`).

#### Scenario: Run zonder source-flag

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001` uitvoert zonder `--source`
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** de stderr MUST de tekst "missing required argument: --source" bevatten
- **AND** de stderr MUST een lijst van beschikbare adapters tonen

#### Scenario: Run met onbekende source

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source asdf` uitvoert
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** de stderr MUST aangeven dat `asdf` geen geregistreerde adapter is

#### Scenario: Run met twee sources

- **WHEN** een gebruiker `iso-audit pipeline --norm 27001 --source jira --source drive` uitvoert
- **THEN** de pipeline MUST documenten en findings van beide adapters mergen vóór classificatie

### Requirement: Drive-adapter implementeert Source Protocol

Een `DriveSource` SHALL bestaan in `src/iso_audit/sources/drive.py` die `Source` implementeert en feature-pariteit biedt met de huidige `Ops_to_Biz/audit/drive_ingest.py` + `gws_client.py` + `planning_ingest.py`.

De adapter SHALL `naam = "drive"` hebben.

De adapter SHALL Google Workspace Service-Account-authenticatie gebruiken via dezelfde scopes als de huidige `audit/gws_client.py` (Drive, Docs, Sheets).

#### Scenario: Drive-adapter haalt documenten op

- **WHEN** de Drive-adapter `list_documents()` aanroept
- **THEN** alle documenten in de geconfigureerde Shared Drive (env: `AUDIT_SOURCE_FOLDER_ID`) MUST geretourneerd worden
- **AND** elk Document MUST de velden `id`, `titel`, `bron="drive"`, `type`, `laatst_gewijzigd`, `inhoud_uri` correct bevatten

#### Scenario: Drive-adapter healthcheck zonder credentials

- **WHEN** de Drive-adapter `healthcheck()` aanroept zonder geldige credentials
- **THEN** de geretourneerde dict MUST `status: "fail"` bevatten
- **AND** een `reden`-veld dat naar de ontbrekende credentials verwijst

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

Het `Source` Protocol SHALL geen write-methodes bevatten. Schrijfacties (rapport publiceren, Miro-bord aanmaken, Jira-issue aanmaken) SHALL via een apart `Sink` Protocol verlopen dat in milestone C wordt gedefinieerd.

Een adapter MAY zowel `Source` als `Sink` implementeren als aparte class-instanties (bv. `DriveSource` en `DriveSink` worden onafhankelijk geregistreerd).

#### Scenario: Read-only adapter implementeert geen Sink

- **WHEN** de Jira-adapter alleen `Source` implementeert
- **THEN** de pipeline MUST de adapter accepteren voor read-paden
- **AND** write-paden (zoals rapport-verzending naar Jira) MUST NOT op deze adapter routeren
