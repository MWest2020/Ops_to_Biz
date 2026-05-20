## Why

Het huidige "HoeWeWork@Conduction" document is groot, verouderd en wordt in de praktijk niet gelezen. Toolspecifieke uitleg (bijv. hoe Nextcloud werkt) raakt snel achterhaald zodra de tool een update krijgt. Er is behoefte aan een compact, onderhoudbaar medewerkerhandboek dat inhoud leent uit officiële brondocumentatie in plaats van die te kopiëren — en dat structureel conform is aan ISO 9001:2015 en ISO 27001:2022.

## What Changes

- Nieuw geautomatiseerd handboek dat het bestaande "HoeWeWork@Conduction" Google Doc vervangt
- Bestaande inhoud wordt ingelezen, geclassificeerd en ofwel behouden, vervangen door een externe link, of gemarkeerd voor verwijdering
- Toolspecifieke secties (bijv. Nextcloud, Mattermost) verwijzen naar de officiële documentatie van die tool — geen eigen kopie van die informatie
- Het nieuwe handboek wordt als Google Doc aangemaakt in de persoonlijke Drive van de eigenaar via de GWS CLI
- Alle content die wordt verwijderd uit het huidige document wordt apart gedocumenteerd in een reviewdoc, zodat de eigenaar deze kan beoordelen voor definitieve verwijdering
- De structuur is conform ISO 9001:2015 (§7.2 competentie, §7.3 bewustzijn) en ISO 27001:2022 (A.6 people controls) — zonder zichtbare clausulelabels
- Code staat in een nieuwe subdirectory `handbook/`, conform het patroon van `argocd_sync/` en `audit/`

## Capabilities

### New Capabilities

- `doc-ingest`: Bestaand Google Doc inlezen via GWS CLI (impersonation als markwesterweel@conduction.nl) en de inhoud structureren voor verwerking
- `content-transform`: Bestaande secties classificeren als behouden / vervangen-door-link / markeren-voor-verwijdering op basis van een vaste beslisboom
- `handbook-output`: Nieuw medewerkerhandboek schrijven als Google Doc naar de persoonlijke Drive via GWS CLI
- `removal-report`: Verwijderde inhoud wegschrijven naar een afzonderlijke reviewdoc in Drive, zodat de eigenaar kan beoordelen wat verdwijnt

### Modified Capabilities

- (geen — volledig nieuwe pipeline)

## Impact

- **Nieuwe subdirectory**: `handbook/` met eigen pipeline, config en tests
- **Hergebruik**: `audit/gws_client.py` en `audit/drive_ingest.py` als basis; geen aanpassingen aan die modules
- **Nieuwe dependencies**: geen — GWS CLI en service account zijn al operationeel
- **Secrets**: zelfde service account en impersonation-config als de auditpipeline (`GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_IMPERSONATE_USER`)
- **Taal**: alle output in het Nederlands
- **Bestaand document**: wordt alleen gelezen, nooit overschreven; de originele URL blijft bereikbaar tijdens de reviewperiode
