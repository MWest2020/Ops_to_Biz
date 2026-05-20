## ADDED Requirements

### Requirement: Bestaand Google Doc inlezen via GWS CLI
De module SHALL het bestaande "HoeWeWork@Conduction" Google Doc inlezen via de Google Docs API, gebruikmakend van de bestaande GWS CLI-integratie met service account impersonation.

#### Scenario: Succesvol inlezen
- **WHEN** `doc-ingest` wordt aangeroepen met een geldig document-ID
- **THEN** retourneert de module een gestructureerde lijst van secties, elk met een titel (heading) en bijbehorende bodytekst

#### Scenario: Document niet bereikbaar
- **WHEN** het document-ID ongeldig is of de service account geen toegang heeft
- **THEN** geeft de module een leesbare foutmelding en stopt de pipeline zonder te schrijven

---

### Requirement: Secties structureren op basis van Docs-headings
De module SHALL de Docs API-structuur (HEADING_1, HEADING_2, PARAGRAPH) gebruiken om het document op te splitsen in logische secties.

#### Scenario: Heading gevolgd door bodytekst
- **WHEN** een HEADING_1 of HEADING_2 wordt gevolgd door één of meer PARAGRAPH-elementen
- **THEN** worden die paragrafen gebundeld als de bodytekst van die sectie

#### Scenario: Lege sectie
- **WHEN** een heading geen bodytekst heeft vóór de volgende heading
- **THEN** wordt de sectie toch opgenomen met een lege bodytekst (niet stilzwijgend weggelaten)

---

### Requirement: Gestructureerde output als Python-datastructuur
De ingested inhoud SHALL worden teruggegeven als een lijst van dicts met de sleutels `title`, `level` (1 of 2), en `body` (plaintext).

#### Scenario: Correcte structuur
- **WHEN** het document één HEADING_1 "Welkom" bevat met twee paragrafen
- **THEN** bevat de output één dict: `{"title": "Welkom", "level": 1, "body": "<beide paragrafen samengevoegd>"}`
