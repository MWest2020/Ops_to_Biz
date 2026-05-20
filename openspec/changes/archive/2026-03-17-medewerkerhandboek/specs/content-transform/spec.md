## ADDED Requirements

### Requirement: Secties classificeren via beslisboom
De module SHALL elke sectie classificeren als `keep`, `link-out`, of `remove` op basis van sectietitel en trefwoorden in de bodytekst, via een deterministische beslisboom in `content_transform.py`.

#### Scenario: Toolspecifieke sectie → link-out
- **WHEN** de sectietitel een bekende toolnaam bevat (bijv. "Nextcloud", "Mattermost", "GitHub", "Jira")
- **THEN** wordt de sectie geclassificeerd als `link-out` en wordt de bijbehorende externe URL opgehaald uit `config/tool_links.yaml`

#### Scenario: Onbekende tool → remove
- **WHEN** de sectietitel een toolnaam bevat die niet voorkomt in `config/tool_links.yaml`
- **THEN** wordt de sectie geclassificeerd als `remove`

#### Scenario: Generieke inhoudssectie → keep
- **WHEN** de sectietitel geen toolnaam bevat en de bodytekst geen verouderd-marker bevat
- **THEN** wordt de sectie geclassificeerd als `keep`

#### Scenario: Lege bodytekst
- **WHEN** een sectie een lege bodytekst heeft
- **THEN** wordt de sectie geclassificeerd als `keep` (twijfel → behouden, nooit stilzwijgend weggooien)

---

### Requirement: Toollinks beheren via YAML-config
De module SHALL toolspecifieke externe links ophalen uit `handbook/config/tool_links.yaml`, zodat links beheerd kunnen worden zonder codewijzigingen.

#### Scenario: Tool gevonden in config
- **WHEN** een toolnaam uit de sectietitel overeenkomt met een sleutel in `tool_links.yaml`
- **THEN** wordt de bijbehorende URL gebruikt in de `link-out`-classificatie

#### Scenario: Tool niet in config
- **WHEN** een toolnaam niet voorkomt in `tool_links.yaml`
- **THEN** wordt de sectie geclassificeerd als `remove` (niet als `link-out`)

---

### Requirement: Gestructureerde output met classificatie
De module SHALL een lijst van geclassificeerde secties teruggeven, elk met de velden `title`, `level`, `body`, `classification` (`keep`/`link-out`/`remove`), en optioneel `external_url`.

#### Scenario: link-out sectie heeft URL
- **WHEN** een sectie geclassificeerd is als `link-out`
- **THEN** bevat het resulterende dict het veld `external_url` met de URL uit `tool_links.yaml`

#### Scenario: keep/remove sectie heeft geen URL
- **WHEN** een sectie geclassificeerd is als `keep` of `remove`
- **THEN** ontbreekt het veld `external_url` of is het `None`
