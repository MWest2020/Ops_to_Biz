## 1. Projectstructuur

- [x] 1.1 Maak `handbook/` directory aan met `__init__.py`
- [x] 1.2 Maak `handbook/config/tool_links.yaml` aan met toollinks voor bekende tools (Nextcloud, Mattermost, GitHub, etc.)

## 2. doc-ingest

- [x] 2.1 Implementeer `handbook/doc_ingest.py`: lees Google Doc via GWS CLI en retourneer lijst van secties als `{"title", "level", "body"}`
- [x] 2.2 Verwerk Docs API structuur (HEADING_1, HEADING_2, PARAGRAPH) naar secties; lege secties opnemen, nooit weggooien

## 3. content-transform

- [x] 3.1 Implementeer `handbook/content_transform.py`: beslisboom op basis van sectietitel en `tool_links.yaml`
- [x] 3.2 Retourneer geclassificeerde secties met velden `title`, `level`, `body`, `classification`, `external_url`

## 4. handbook-output

- [x] 4.1 Implementeer `handbook/handbook_output.py`: schrijf `keep`- en `link-out`-secties als nieuw Google Doc via GWS CLI
- [x] 4.2 Gebruik `HANDBOOK_DRIVE_FOLDER_ID` als doelmap; fallback naar root van persoonlijke Drive

## 5. removal-report

- [x] 5.1 Implementeer `handbook/removal_report.py`: schrijf `remove`-secties naar apart reviewdoc via GWS CLI
- [x] 5.2 Sla reviewdoc op in dezelfde map als het handboek; retourneer `None` als er niets te verwijderen is

## 6. Pipeline

- [x] 6.1 Implementeer `handbook/pipeline.py`: koppel doc-ingest → content-transform → handbook-output + removal-report
- [x] 6.2 Voeg CLI-entrypoint toe zodat de pipeline aanroepbaar is via `python3 -m handbook.pipeline --doc-id <ID>`
