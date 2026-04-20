# Changelog

Alle relevante wijzigingen aan dit project worden hier vastgelegd.
Format volgt [Keep a Changelog](https://keepachangelog.com/nl/1.1.0/).

## [Unreleased]

### Added — 2026-04-20 — Finding classification v2 (refactor)

- **`audit/finding_classification_20260420.py`** (nieuw, originele file ongewijzigd)
  - **System prompt met `cache_control` (ephemeral)** — statische delen (auditor-
    persona, PDCA-regels, JSON-format) gecached; user prompt bevat alleen
    variabele per-call data. 5-10x goedkoper op de statische helft bij herhaalde
    calls binnen 5 min.
  - **Per-call token usage tracking** via `Kostenteller` dataclass
    (`resp.usage.input_tokens / output_tokens / cache_read_input_tokens /
    cache_creation_input_tokens`). Eindrapport toont calls, tokens,
    cache-split en $ per run.
  - **Kostenschatting vooraf** (`schat_kosten()` + `--dry-run-cost` flag) —
    rekent per doc het verwachte token-verbruik uit (chars/4) en houdt
    rekening met cache-write-then-read patroon. Geen API-calls nodig.
  - **Checkpoint op (doc_id, clausule_id, norm)** in plaats van alleen `doc_id`.
    Voorheen: doc ooit geclassificeerd → nooit meer aangeraakt (ook niet voor
    nieuwe clausules). Nu: alleen de daadwerkelijk al gedane combinaties
    worden geskipt.
  - **`rehash=True` + UPSERT** — dwingt herclassificatie af, bestaande rows
    worden overschreven via `ON CONFLICT(...) DO UPDATE SET`.
  - **Configureerbaar model** via `AUDIT_CLASSIFICATION_MODEL` env (default
    Haiku 4.5; Sonnet/Opus mogelijk).
  - `review_en_bevestig` en `sla_op_in_sheets` gere-exporteerd uit originele
    module (ongewijzigd gedrag).

- **`audit/pipeline.py`**
  - Switched naar `finding_classification_20260420` (v2 classifier).
  - Nieuwe flags `--rehash` en `--dry-run-cost`.
  - `run_audit()` accepteert `rehash` + `dry_run_cost` kwargs.

### Why

Oude module had drie problemen (gediagnosticeerd tijdens chapter-7 run):
1. `INSERT OR IGNORE` + doc-level checkpoint = geen re-run mogelijk zonder
   handmatig DB-sleutelen. Chapter-switch skipte onterecht docs.
2. Geen `resp.usage` capture = kostenschattingen op basis van guess i.p.v.
   werkelijke token-counts (memory: "centen → dollars").
3. Geen prompt caching = statische prompt (persona + rules) werd voor elke
   call opnieuw volledig gerekend.

v2 lost alle drie op zonder breaking API — `classificeer_alle_bevindingen()`
heeft dezelfde signature plus optionele `rehash` en `model` kwargs.

### Test

- `python3 -m audit.pipeline --norm 27001 --chapter 7 --rehash --dry-run-cost`
  toont kostenschatting zonder API-calls
- Imports en `--help` schonen correct
- Refactor is side-by-side: originele `finding_classification.py` blijft intact
- **Volledige rehash-run `--norm beide --scherpte 0.5 --rehash --thema-llm`**
  (2026-04-20): 75 calls / 451 findings / 19.5 min / **$0.39** / 0 fouten.
  Prompt caching was niet actief: system prompt ~600 tokens < 1024-minimum.
  Aanpak voor vervolg: verrijk system prompt (Conduction-profiel, norm-
  referenties) naar >1024 tokens om cache te activeren.

### Fix — 2026-04-20 — Miro zonder clausule skip

- `finding_classification_20260420.py`: Miro-notities zonder `clausule` worden
  overgeslagen met warning (voorkomt NOT NULL constraint crash bij UPSERT).
  Oorzaak: Miro board bevat sticky notes die niet aan een clausule-clausule-
  frame gebonden zijn. 139 van 170 notities waren zo in de huidige run.

### Changed — 2026-04-20 — Classifier context + misclassificatie filter + management summary

Drie fixes naar aanleiding van review van de management summary:

1. **Conduction-specifieke context in `_SYSTEM_GENUANCEERD`**
   - BYOD: laptops zijn eigendom van de medewerker — formele retournering
     (5.11 / 6.5) beperkt tot klein materiaal. Ontbreken formele procedure
     → OFI, niet NC (tenzij ook data-/toegangsrevocatie ontbreekt).
   - Informatieclassificatie (5.12): interne documenten zijn
     vertrouwelijkheid-geindexeerd in de handleidingen (4 audits bevestigd).
     5.12 intern = positief; NC alleen voor externe documenten/communicatie.

2. **Miro mis-tagging filter** (`_is_miro_mistag`)
   - Items waar de LLM-classificatie begint met "Misclassificatie", "niet
     relevant voor clausule", "Vraag over X niet relevant voor", of "Item
     verwijst naar clausule X maar" worden uit de DB geweerd. Het betreft
     tagging-fouten op het Miro bord — geen werkelijke NCs tegen Conduction.

3. **Management summary op basis van clusters, niet samples** (`report_generation.py`)
   - Prompt ontvangt nu top-8 NC-clausule-clusters mét aantallen en voorbeeld,
     plus top-5 OFI en top-5 positief.
   - Conduction-context (BYOD, 5.12 intern/extern) ingebed in prompt.
   - Expliciete instructie: gebruik UITSLUITEND de data, geen bevestigings-
     taal als "drie kritieke gebieden" tenzij er exact drie prominente clusters
     zijn. Vermeldt werkelijke aantallen per cluster.

Why: De v1 summary noemde "drie kritieke gebieden" op basis van de eerste drie
NCs in de lijst — willekeurig. 5.11 werd ten onrechte als kritiek gepresenteerd
terwijl Conduction BYOD-werkt. 5.12 was een Miro mis-tagging die als
"classificatiefout in de norm" werd uitgelegd — vier audits lang onterecht.

### Added — 2026-04-20 — Memo-als-sluitingsbewijs context + remediation Miro-note

Vierde classifier-context uitbreiding in `_SYSTEM_GENUANCEERD`:
- Memo afwijking/tekortkoming/incident = sluitingsbewijs voor de ONDERLIGGENDE
  technische controle (8.21/8.24 crypto, 8.33 test/prod-scheiding, 6.7 VPN).
  Aanwezigheid van memo → "positief" of "OFI", niet NC. Alleen als memo
  expliciet stelt dat maatregel OPEN STAAT kan NC gerechtvaardigd zijn.

Resultaat v4 rehash: **NC 12 → 10** (memo-context) → **9** (na remediation 5.14).

**Remediation Miro-sticky + DB-update**:
- `audit/archive/annotate_finding_20260420.py` — patch-script dat:
  1. Een nieuwe light-green sticky plaatst op het Miro-auditbord naast
     item `3458764658906182642` (5.14 "Discussie eindigt niet...") met
     "✅ OPGEPAKT 2026-04-20" + resolutietekst over OpenRegister CI/CD.
     Gebruikt `maak_sticky` uit `miro_board_setup.py` — nieuwe sticky,
     bestaand item NIET aangepast (per memory-regel).
  2. DB-row `bevindingen.id=6018` wordt bijgewerkt: NC → OFI, en de
     resolutie-note wordt voor de beschrijving geplakt zodat het
     auditrapport de behandeling en openstaande OFI toont.
- Verificatie via `gh api repos/ConductionNL/openregister/contents/.github/workflows`:
  branch protection + staged releases (dev→beta→release) + PR lint zijn
  actief; quality-gate, coverage-gate en PHP-tests staan `if: false`
  (OFI-kanttekening, opgenomen in resolutie-tekst).

### Added — 2026-04-20 — Audit tabulaire output + thema-bundeling

- **`audit/tabular_report.py`** (nieuw)
  - CSV-export (`Bevindingen_<norm>_<datum>.csv`) — platte tabel, alle findings
  - Excel-export (`.xlsx`) met drie tabs:
    - `Samenvatting` — totalen per classificatie, per thema, per norm
    - `Bevindingen` — alle findings met conditional formatting op NC/OFI/positief
    - `Per clausule` — NC/OFI/positief counts per clausule
  - Heuristische thema-toekenning (route A): 24 thema-regels + "Overig" fallback,
    keyword-match over beschrijving + onderbouwing, first-match-wins
  - Norm-detectie per clausule via `normteksten` lookup (9001 / 27001 / beide)
  - Standalone CLI: `python3 -m audit.tabular_report --norm beide`

- **`audit/thema_classifier.py`** (nieuw — route B)
  - LLM-gebaseerde thema-verfijning met Haiku 4.5, batch ~50 findings per call
  - Prompt caching op system prompt (ephemeral)
  - `verfijn_overig()` — hybride: classificeert alleen bevindingen die
    heuristisch 'Overig' kregen (minimaliseert kosten/tokens)
  - `classificeer_themas()` — volledige LLM-toekenning
  - Valideert output tegen vaste taxonomie (`THEMA_LIJST`)
  - Graceful fallback: lege dict bij fout, caller gebruikt heuristiek

- **`audit/local_report.py`** — thema-bundeling binnen clausule-secties
  - Nieuwe helper `_render_clausules_met_themas()`
  - Per clausule: findings gegroepeerd per thema, grootste groep eerst,
    'Overig' altijd laatst
  - Thema-kop toont telling: `_(6 OFI · 15 positief)_`
  - Als een clausule maar één thema heeft → thema-kop weggelaten (geen ruis)

- **`audit/pipeline.py`**
  - Nieuwe flag `--thema-llm` (route B inschakelen)
  - `run_audit()` roept na classificatie heuristiek + optioneel LLM aan,
    hangt `thema` aan elke bevinding → markdown gebruikt zelfde bundeling
  - `run_local_only()` genereert nu ook CSV + Excel (naast markdown)

### Why

- Markdown-rapport was 3143 regels plat door 449 findings heen. Bundeling per
  thema maakt review hanteerbaar (top-5 thema's dekken nu ~40% van findings).
- CSV/Excel output laat filteren, sorteren en sheets-import zonder markdown-parsing.
- Route B (LLM-thema) is bewust gescheiden van de geplande refactor van
  `finding_classification.py` — thema-toekenning is aparte verantwoordelijkheid
  en draait in enkele batches (niet per-finding).

### Test

- `python3 -m audit.pipeline --local-only --norm 9001` — markdown + CSV + Excel OK
- Regeneratie op bestaande DB (449 findings): 24% 'Overig' met heuristiek;
  geldige Excel met 3 tabs, conditional formatting en samenvatting.
