## ADDED Requirements

### Requirement: Nieuw handboek schrijven als Google Doc via GWS CLI
De module SHALL het nieuwe medewerkerhandboek aanmaken als Google Doc in de persoonlijke Drive van de eigenaar via `gws docs create`, gebruikmakend van de bestaande GWS CLI-integratie met service account impersonation.

#### Scenario: Succesvol aanmaken
- **WHEN** `handbook-output` wordt aangeroepen met een lijst van geclassificeerde secties
- **THEN** wordt een nieuw Google Doc aangemaakt in de geconfigureerde Drive-map (standaard: root van persoonlijke Drive)
- **AND** het document-ID en de URL worden teruggegeven

#### Scenario: GWS CLI niet beschikbaar
- **WHEN** `gws` niet beschikbaar is of de sessie verlopen is
- **THEN** geeft de module een leesbare foutmelding en stopt zonder te schrijven

---

### Requirement: Secties verwerken per classificatie
De module SHALL alleen `keep`- en `link-out`-secties opnemen in het nieuwe handboek; `remove`-secties worden weggelaten.

#### Scenario: keep-sectie opgenomen
- **WHEN** een sectie classificatie `keep` heeft
- **THEN** wordt de volledige bodytekst opgenomen in het nieuwe doc onder de originele heading

#### Scenario: link-out sectie verwijst naar externe URL
- **WHEN** een sectie classificatie `link-out` heeft
- **THEN** wordt de sectie opgenomen als een kort blok met de heading en een verwijzing naar de externe URL (geen eigen kopie van de inhoud)

#### Scenario: remove-sectie weggelaten
- **WHEN** een sectie classificatie `remove` heeft
- **THEN** verschijnt die sectie niet in het nieuwe handboek

---

### Requirement: Drive-map configureerbaar via omgevingsvariabele
De module SHALL de doelmap in Drive ophalen uit de omgevingsvariabele `HANDBOOK_DRIVE_FOLDER_ID`; indien niet ingesteld, wordt de root van persoonlijke Drive gebruikt.

#### Scenario: HANDBOOK_DRIVE_FOLDER_ID ingesteld
- **WHEN** `HANDBOOK_DRIVE_FOLDER_ID` een geldig folder-ID bevat
- **THEN** wordt het nieuwe doc aangemaakt in die map

#### Scenario: HANDBOOK_DRIVE_FOLDER_ID niet ingesteld
- **WHEN** `HANDBOOK_DRIVE_FOLDER_ID` niet aanwezig is in de omgeving
- **THEN** wordt het nieuwe doc aangemaakt in de root van persoonlijke Drive zonder fout
