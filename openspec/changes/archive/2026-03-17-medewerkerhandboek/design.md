## Context

Conduction heeft een bestaand "HoeWeWork@Conduction" Google Doc dat als introductiegids voor nieuwe medewerkers dient. Het document is groot, bevat toolspecifieke uitleg die snel veroudert, en wordt in de praktijk niet gelezen. De auditpipeline (`audit/`) heeft al een werkende GWS CLI-integratie met service account en impersonation. Die patronen worden hergebruikt.

De pipeline draait lokaal (geen CronJob vereist in eerste instantie) en schrijft naar de persoonlijke Drive van de eigenaar.

## Goals / Non-Goals

**Goals:**
- Bestaand document inlezen en inhoud classificeren
- Toolspecifieke inhoud vervangen door externe links
- Nieuw, compact handboek als Google Doc schrijven naar persoonlijke Drive
- Verwijderde inhoud apart documenteren voor review door eigenaar
- Structuur conform ISO 9001:2015 §7.2/7.3 en ISO 27001:2022 A.6 — zonder zichtbare clausulelabels
- Code in `handbook/` subdirectory, conform het patroon van `argocd_sync/` en `audit/`

**Non-Goals:**
- Automatische publicatie of vervanging van het originele document (eigenaar beslist)
- Vertalingen (andere talen komen later)
- CronJob of geautomatiseerde heruitvoering (eenmalige migratietool)
- Integratie met andere tools dan GWS CLI / Google Drive

## Decisions

### D1: Hergebruik van `audit/gws_client.py` en `audit/drive_ingest.py`

**Keuze:** Importeer deze modules direct vanuit `handbook/`; geen kopie.

**Reden:** Voorkomt duplicatie; updates in `audit/` werken automatisch door. De modules zijn al stabiel en getest.

**Alternatief overwogen:** Eigen GWS-wrapper in `handbook/` schrijven — verworpen wegens onnodige duplicatie.

---

### D2: Classificatie via beslisboom in Python, niet via Claude

**Keuze:** Content-classificatie (behouden / link-out / verwijderen) via een deterministische beslisboom in `content_transform.py`, gebaseerd op sectietitels en trefwoorden.

**Reden:** Reproduceerbaar, auditeerbaar, geen API-kosten per run. Conform de filosofie "boring, auditable, solid".

**Alternatief overwogen:** Claude API gebruiken om elke sectie te beoordelen — verworpen: niet deterministisch, moeilijk te reviewen, onnodige afhankelijkheid.

---

### D3: Output als Google Doc via GWS CLI (`gws docs create`)

**Keuze:** Het nieuwe handboek wordt als Google Doc aangemaakt via `gws docs create` en daarna gevuld.

**Reden:** GWS CLI is al geconfigureerd met impersonation. Consistent met de auditpipeline.

**Alternatief overwogen:** Markdown-bestand lokaal opslaan — te weinig waarde; eigenaar verwacht een Drive-document.

---

### D4: Reviewdoc voor verwijderde inhoud

**Keuze:** Alle als "verwijderen" geclassificeerde secties worden weggeschreven naar een apart Google Doc ("Ter beoordeling: verwijderde inhoud") in dezelfde Drive-map.

**Reden:** Eigenaar moet kunnen besluiten wat definitief verdwijnt; niets gaat stilzwijgend weg.

---

### D5: Geen schrijfrechten op het originele document

**Keuze:** Het bestaande document wordt alleen gelezen (Drive API read-only), nooit overschreven.

**Reden:** Veiligheid; origineel blijft beschikbaar als referentie tijdens reviewperiode.

## Risks / Trade-offs

- **Beslisboom mist context** → Classificatie is best-effort; eigenaar beoordeelt reviewdoc. Mitigation: conservatief classificeren (twijfel → behouden of reviewdoc, nooit stilzwijgend weggooien).
- **GWS CLI-sessie verloopt** → Zelfde risico als bij auditpipeline; oplossing via service account impersonation is al operationeel.
- **Documentstructuur van origineel is niet gestandaardiseerd** → Ingest werkt op basis van Docs API paragraphs/headings; sectie-detectie is heuristisch. Mitigation: output altijd door eigenaar laten reviewen vóór publicatie.

## Migration Plan

1. Run `handbook/pipeline.py` lokaal (eenmalig)
2. Pipeline leest origineel, classificeert, schrijft nieuw handboek + reviewdoc naar Drive
3. Eigenaar beoordeelt reviewdoc en keurt verwijderingen goed
4. Eigenaar vervangt link naar origineel door link naar nieuw document (handmatig)
5. Origineel blijft staan totdat eigenaar expliciet besluit het te archiveren

Geen rollback nodig: origineel wordt nooit aangeraakt.

## Open Questions

- Welke externe links worden gebruikt voor welke tools? (Nextcloud, Mattermost, etc.) → Te bepalen tijdens implementatie van `content-transform`; toollinks worden beheerd in `handbook/config/tool_links.yaml`
- Moet het nieuwe handboek in een specifieke Drive-map staan, of volstaat "Mijn Drive"? → Default: root van persoonlijke Drive; configureerbaar via `HANDBOOK_DRIVE_FOLDER_ID`
