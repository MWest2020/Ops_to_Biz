## ADDED Requirements

### Requirement: Verwijderde inhoud wegschrijven naar reviewdoc
De module SHALL alle secties met classificatie `remove` wegschrijven naar een apart Google Doc ("Ter beoordeling: verwijderde inhoud") in dezelfde Drive-map als het nieuwe handboek, zodat de eigenaar kan besluiten wat definitief verdwijnt.

#### Scenario: Secties aanwezig voor verwijdering
- **WHEN** de geclassificeerde lijst één of meer secties met `remove` bevat
- **THEN** wordt een nieuw Google Doc aangemaakt met alle verwijderde secties (inclusief originele heading en bodytekst)
- **AND** het document-ID en de URL worden teruggegeven

#### Scenario: Geen secties te verwijderen
- **WHEN** er geen secties met classificatie `remove` zijn
- **THEN** wordt géén reviewdoc aangemaakt en geeft de module `None` terug

#### Scenario: GWS CLI niet beschikbaar
- **WHEN** `gws` niet beschikbaar is of de sessie verlopen is
- **THEN** geeft de module een leesbare foutmelding en stopt zonder te schrijven

---

### Requirement: Reviewdoc bevat volledige originele inhoud
De reviewdoc SHALL de volledige originele tekst van elke verwijderde sectie bevatten, zodat de eigenaar een weloverwogen beslissing kan nemen.

#### Scenario: Sectie met bodytekst
- **WHEN** een `remove`-sectie bodytekst heeft
- **THEN** verschijnt zowel de heading als de volledige bodytekst in de reviewdoc

#### Scenario: Sectie zonder bodytekst
- **WHEN** een `remove`-sectie een lege bodytekst heeft
- **THEN** verschijnt de heading toch in de reviewdoc (niet stilzwijgend weggelaten)

---

### Requirement: Reviewdoc geplaatst in dezelfde Drive-map als het handboek
De module SHALL de reviewdoc aanmaken in dezelfde map als het nieuwe handboek (bepaald via `HANDBOOK_DRIVE_FOLDER_ID` of root van persoonlijke Drive).

#### Scenario: Map geconfigureerd
- **WHEN** `HANDBOOK_DRIVE_FOLDER_ID` is ingesteld
- **THEN** wordt de reviewdoc in diezelfde map aangemaakt

#### Scenario: Geen map geconfigureerd
- **WHEN** `HANDBOOK_DRIVE_FOLDER_ID` niet aanwezig is
- **THEN** wordt de reviewdoc in de root van persoonlijke Drive aangemaakt
