# ISO Audit Automatisering

Geautomatiseerde audit-pipeline voor ISO 9001:2015 en ISO 27001:2022, geïntegreerd met GSuite en Miro.

## Vereiste OAuth Scopes

### Google Workspace (service account)

| Scope | Gebruik |
|-------|---------|
| `https://www.googleapis.com/auth/drive` | Documenten lezen uit Google Drive |
| `https://www.googleapis.com/auth/documents` | Template kopiëren en rapport schrijven |
| `https://www.googleapis.com/auth/spreadsheets` | Bevindingen wegschrijven naar Sheets |
| `https://www.googleapis.com/auth/presentations` | Slides-presentatie aanmaken |
| `https://www.googleapis.com/auth/gmail.send` | Optionele rapportnotificatie |
| `https://www.googleapis.com/auth/calendar` | Audit-uitnodigingen via Calendar |

Maak een service account aan via Google Cloud Console en activeer domain-wide delegation
voor de bovenstaande scopes.

### Miro (REST API token)

| Scope | Gebruik |
|-------|---------|
| `boards:read` | Sticky notes en tekstvakken ophalen |

Genereer een token via: Miro Dashboard → Profile → Apps → Create new app → OAuth scopes.

## Configuratie

Kopieer `.env.example` naar `.env` en vul de waarden in:

```bash
cp .env.example .env
```

## Drive-structuur

De pipeline verwacht de volgende mappenstructuur in Google Drive:

```
Interne Audits/
├── Templates/
│   └── Auditrapport_Template_v1.0   ← aangemaakt door setup-stap
└── <jaar>/
    ├── Auditrapport_ISO9001_2026-03-13
    └── AuditSummary_ISO9001_2026-03-13
```

Procedures, werkinstructies en beleid mogen elders in Drive staan;
de ingest-stap zoekt op basis van configureerbare map-ID's.

## Eerste keer instellen

1. Installeer dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Kopieer `.env.example` naar `.env` en vul in:
   - `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` — pad naar service account JSON
   - `MIRO_API_TOKEN` — Miro API token (boards:read)
   - `MIRO_BOARD_ID` — standaard: `uXjVJbKZEmw`
   - `AUDIT_DRIVE_FOLDER_ID` — ID van de "Interne Audits"-map in Drive

3. Maak het rapporttemplate aan (éénmalig):
   ```bash
   python -m audit.pipeline --setup-template
   ```
   Kopieer het geretourneerde Doc-ID naar `AUDIT_TEMPLATE_DOC_ID` in `.env`.

## Pipeline uitvoeren

```bash
python -m audit.pipeline --norm 9001
python -m audit.pipeline --norm 27001
python -m audit.pipeline --norm beide
```

## Bestandsnaamconventie (taak 10.4)

| Bestand | Patroon |
|---------|---------|
| Auditrapport | `Auditrapport_ISO9001_2026-03-13` |
| Slides | `AuditSummary_ISO9001_2026-03-13` |
| Template | `Auditrapport_Template_ISO9001+ISO27001_v1.0` |

## Miro kleurconventie

| Kleur | Classificatie |
|-------|---------------|
| Groen | Positief / conform |
| Oranje | NC (non-conformiteit) |
| Rood | NC (non-conformiteit) |
| Overig | Geen pre-classificatie |
