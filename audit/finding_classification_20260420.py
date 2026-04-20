"""
Finding classification v2 — refactor van finding_classification.py (originele
versie 2026-03-24, deze versie 2026-04-20).

Vervangt de oude module voor nieuwe runs. De oude file blijft ongewijzigd voor
audit-trail en rollback.

Verbeteringen t.o.v. de originele module
---------------------------------------
1. **System prompt met cache_control (ephemeral)**
   - Statische delen (auditor-persona, PDCA-regels, JSON-format) in system prompt
   - Eerste call schrijft cache (~1.25x input cost), elke volgende call leest cache
     (~0.1x input cost) → 5-10x besparing op de statische prompt-helft
2. **Per-call token usage + kostenlogging** (`Kostenteller`)
   - `resp.usage.input_tokens / output_tokens / cache_read_input_tokens /
     cache_creation_input_tokens` worden per call geaccumuleerd
   - Eindrapport toont calls, tokens (incl. cache-split) en $ per run
3. **Kostenschatting vooraf** (`schat_kosten`)
   - Rekent per doc het verwachte token-verbruik uit (rough char→token)
   - Werkt zonder API-call — gebruik vóór een dure run
4. **Rehash / selective re-classify**
   - UPSERT i.p.v. INSERT OR IGNORE → bestaande row wordt bijgewerkt
   - Checkpoint op (doc_id, clausule_id, norm) i.p.v. doc_id → alleen
     daadwerkelijk al gedane combinaties worden geskipt
   - Nieuwe flag `rehash_clausules: set[str] | None` dwingt herclassificatie af
5. **Configureerbaar model via `AUDIT_CLASSIFICATION_MODEL` env**
   - Default Haiku 4.5; Sonnet/Opus mogelijk voor nauwkeuriger runs

Gebruik
-------
  # Alleen kostenschatting (géén API-calls):
  python3 -m audit.finding_classification_20260420 --dry-run-cost \\
      --norm 27001 --chapter 7

  # Rehash chapter 7 (verse API-calls, bestaande rows worden vervangen):
  python3 -m audit.pipeline --norm 27001 --chapter 7 --rehash

API-compat
----------
De publieke functies (`classificeer_alle_bevindingen`, `review_en_bevestig`,
`sla_op_in_sheets`) hebben dezelfde signature als de oude module plus een
paar optionele kwargs. pipeline.py kan hiertussen switchen zonder breaking changes.
"""

import argparse
import json
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("AUDIT_CLASSIFICATION_MODEL", "claude-haiku-4-5-20251001")
MAX_TEKST = 2000
MIRO_BATCH = 20
CHARS_PER_TOKEN = 4  # ruwe schatting voor dry-run-cost

# Prijzen USD per miljoen tokens. Bron: anthropic.com/pricing (geldig 2026).
# Cache-write 5m = 1.25x input; cache-read = 0.1x input (standaard tariefstructuur).
PRIJZEN: dict[str, dict[str, float]] = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80, "output": 4.00,
        "cache_write_5m": 1.00, "cache_read": 0.08,
    },
    "claude-sonnet-4-6-20250929": {
        "input": 3.00, "output": 15.00,
        "cache_write_5m": 3.75, "cache_read": 0.30,
    },
    "claude-opus-4-7": {
        "input": 15.00, "output": 75.00,
        "cache_write_5m": 18.75, "cache_read": 1.50,
    },
}


# ---------------------------------------------------------------------------
# Token + kosten tracking
# ---------------------------------------------------------------------------

@dataclass
class Kostenteller:
    model: str = DEFAULT_MODEL
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    elapsed_s: float = 0.0
    fouten: int = 0

    def voeg_toe(self, usage, elapsed_s: float) -> None:
        self.calls += 1
        self.elapsed_s += elapsed_s
        self.input_tokens += getattr(usage, "input_tokens", 0) or 0
        self.output_tokens += getattr(usage, "output_tokens", 0) or 0
        self.cache_write_tokens += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0) or 0

    def kosten_usd(self) -> float:
        p = PRIJZEN.get(self.model)
        if not p:
            return 0.0
        return (
            self.input_tokens * p["input"]
            + self.output_tokens * p["output"]
            + self.cache_write_tokens * p["cache_write_5m"]
            + self.cache_read_tokens * p["cache_read"]
        ) / 1_000_000

    def rapport(self) -> str:
        return (
            f"model={self.model} calls={self.calls} fouten={self.fouten} | "
            f"input={self.input_tokens:,} (cache_read={self.cache_read_tokens:,} "
            f"cache_write={self.cache_write_tokens:,}) | "
            f"output={self.output_tokens:,} | "
            f"elapsed={self.elapsed_s:.1f}s | "
            f"kosten=${self.kosten_usd():.4f}"
        )


# ---------------------------------------------------------------------------
# Prompts — system (statisch, gecached) + user (variabel)
# ---------------------------------------------------------------------------

_SYSTEM_SCHERP = """Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Beoordeel elk aangeboden document strikt voor de opgegeven ISO-clausules.
- "positief": het document levert aantoonbaar bewijs dat aan de eis is voldaan.
- "OFI": de eis is gedeeltelijk gedekt, verbetering is mogelijk.
- "NC": er is geen of onvoldoende bewijs; de eis is niet aantoonbaar gedekt.

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{"clausule": "<id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}]
"""

_SYSTEM_GENUANCEERD = """Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Organisatiecontext:
- Conduction noemt een non-conformiteit een "afwijking". Er zijn gedocumenteerde
  procedures voor het vastleggen en opvolgen van afwijkingen (memo afwijking/
  tekortkoming/incident). Het bestaan van zo'n memo is aantoonbaar bewijs dat
  de NC-procedure functioneert — classificeer dit als "positief" voor clausules
  als 10.2, 8.7 en vergelijkbare corrigerende-actie-eisen.
- **Memo = sluitingsbewijs voor de onderliggende controle.** Een memo
  afwijking/incident die een technisch probleem beschrijft (bv. Kubeconfig-
  encryptie, testdata-lek, VPN-naleving) IS het bewijs dat (a) het probleem
  gedetecteerd en erkend is, (b) de NC-procedure heeft gewerkt, en (c) een
  corrigerende maatregel is genomen of gepland. Classificeer de ONDERLIGGENDE
  technische controle (bv. 8.21/8.24 crypto, 8.33 test/productie-scheiding,
  6.7 thuiswerk) op basis van zo'n memo als **"positief" of "OFI"** — NIET
  als NC. Het bestaan van de memo weerlegt een NC-classificatie voor de
  onderliggende controle. Alleen als het memo expliciet stelt dat de
  maatregel OPEN STAAT en de procedure faalt, kan NC gerechtvaardigd zijn.
- Interne auditverslagen (Interne Audit Q*) zijn bewijs van een werkend
  intern auditsysteem (9.2). Classificeer aanwezig auditverslag als "positief".
- **BYOD (5.11 / 6.5):** Conduction werkt BYOD — laptops zijn eigendom van de
  medewerker, niet van het bedrijf. Activa-retournering betreft in praktijk
  alleen klein materiaal (koptelefoon) plus data- en toegangsrechten. Het
  ontbreken van een formele retourneringsprocedure voor klein materiaal is
  **OFI, geen NC**. Alleen als ook data-verwijdering/toegangsrevocatie
  aantoonbaar ontbreekt, kan 5.11/6.5 NC zijn.
- **Informatieclassificatie intern vs. extern (5.12):** Interne documenten bij
  Conduction zijn via de handleidingen vertrouwelijkheid-geindexeerd (deze
  bevinding is vier audits bevestigd). Classificeer 5.12 intern als
  **"positief"** bij aanwezigheid van die handleidingen. Een NC op 5.12 is
  alleen gerechtvaardigd als EXTERNE documenten/communicatie (contracten,
  klantrapporten, publieke uitingen) aantoonbaar geen classificatie-
  of behandelingsindicatie hebben.

Beoordeel genuanceerd voor de opgegeven ISO-clausules. Hanteer PDCA als
uitgangspunt: intentie en richting tellen mee.
- "positief": het document levert aantoonbaar bewijs dat aan de eis is voldaan.
- "OFI": de intentie is aanwezig maar uitvoering of documentatie is onvolledig.
- "NC": ALLEEN als de norm een expliciete deliverable vereist (procedure,
  register, log, besluit) die aantoonbaar ONTBREEKT. Twijfel → OFI, niet NC.

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{"clausule": "<id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}]
"""

_SYSTEM_MIRO = """Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Classificeer elk aangeboden Miro-item voor de genoemde ISO-clausule:
- "positief": het item toont bewijs dat aan de eis is voldaan.
- "OFI": verbetering is mogelijk.
- "NC": geen of onvoldoende bewijs.

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{"id": "<item_id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}]
"""


def _systeem_voor(scherpte: float, herkomst: str = "Drive") -> str:
    if herkomst == "Miro":
        return _SYSTEM_MIRO
    return _SYSTEM_SCHERP if scherpte >= 0.75 else _SYSTEM_GENUANCEERD


def _bouw_doc_user_prompt(doc: dict, clausule_ids: list[str], clausules: dict) -> str:
    clausules_lijst = "\n".join(
        f"- {cid}: {clausules.get(cid, {}).get('titel', cid)}"
        for cid in clausule_ids
    )
    return (
        f"Document: {doc['naam']}\n\n"
        f"Tekst:\n---\n{doc['tekst'][:MAX_TEKST]}\n---\n\n"
        f"Clausules:\n{clausules_lijst}\n"
    )


def _bouw_miro_user_prompt(notities: list[dict], clausules: dict) -> str:
    regels = []
    for n in notities:
        nid = n.get("miro_item_id", n.get("id", "?"))
        cid = n.get("clausule", "?")
        titel = clausules.get(cid, {}).get("titel", "")
        tekst = (n.get("tekst") or "")[:200]
        regels.append(f"- ID: {nid} | Clausule: {cid} {titel} | Tekst: {tekst}")
    return "Items:\n" + "\n".join(regels)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _parse_json_list(tekst: str) -> list[dict]:
    start = tekst.find("[")
    eind = tekst.rfind("]") + 1
    if start == -1 or eind <= start:
        return []
    return json.loads(tekst[start:eind])


# Patronen die aangeven dat een bevinding eigenlijk een mis-tagging op Miro is
# (item verwijst naar een clausule waar het niet thuishoort) — geen echte NC
# tegen Conduction, maar data-kwaliteit van het Miro bord. Skippen uit DB.
_MIRO_MISTAG_PATRONEN = (
    "misclassificatie",
    "niet relevant voor clausule",
    "niet relevant voor deze clausule",
    "hoort niet bij clausule",
    "hoort niet bij deze clausule",
    "item verwijst naar clausule",
    "item verwijst alleen naar",  # bord-titel / topic-header
    "item noemt alleen",           # idem
    "item bevat alleen",           # idem
    "vraag over",  # bv. "Vraag over X niet relevant voor Clausule Y"
)


def _is_miro_mistag(beschrijving: str) -> bool:
    if not beschrijving:
        return False
    lower = beschrijving.lower().lstrip("*_ \t")
    return any(lower.startswith(p) or (p in lower[:60]) for p in _MIRO_MISTAG_PATRONEN)


def _maak_system_param(system_tekst: str) -> list[dict]:
    """System prompt met ephemeral cache_control voor 5m prompt caching."""
    return [{"type": "text", "text": system_tekst, "cache_control": {"type": "ephemeral"}}]


def _classificeer_doc(
    doc: dict,
    clausule_ids: list[str],
    clausules: dict,
    client: anthropic.Anthropic,
    teller: Kostenteller,
    scherpte: float = 1.0,
) -> list[dict]:
    """Eén API-call per doc (alle opgegeven clausules in één response)."""
    system = _systeem_voor(scherpte, herkomst="Drive")
    user = _bouw_doc_user_prompt(doc, clausule_ids, clausules)
    t0 = time.time()
    try:
        resp = client.messages.create(
            model=teller.model,
            max_tokens=150 * len(clausule_ids) + 64,
            system=_maak_system_param(system),
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.APIError as e:
        teller.fouten += 1
        logger.warning("API-fout (doc %s): %s", doc.get("naam", "")[:40], e)
        return []
    teller.voeg_toe(resp.usage, time.time() - t0)
    try:
        return _parse_json_list(resp.content[0].text)
    except (json.JSONDecodeError, IndexError) as e:
        teller.fouten += 1
        logger.warning("JSON-parse fout (doc %s): %s", doc.get("naam", "")[:40], e)
        return []


def _classificeer_miro_batch(
    notities: list[dict],
    clausules: dict,
    client: anthropic.Anthropic,
    teller: Kostenteller,
) -> list[dict]:
    system = _systeem_voor(scherpte=1.0, herkomst="Miro")
    user = _bouw_miro_user_prompt(notities, clausules)
    t0 = time.time()
    try:
        resp = client.messages.create(
            model=teller.model,
            max_tokens=150 * len(notities) + 64,
            system=_maak_system_param(system),
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.APIError as e:
        teller.fouten += 1
        logger.warning("API-fout (Miro batch): %s", e)
        return []
    teller.voeg_toe(resp.usage, time.time() - t0)
    try:
        return _parse_json_list(resp.content[0].text)
    except (json.JSONDecodeError, IndexError) as e:
        teller.fouten += 1
        logger.warning("JSON-parse fout (Miro batch): %s", e)
        return []


# ---------------------------------------------------------------------------
# DB helpers — nieuwe checkpoint-granulariteit
# ---------------------------------------------------------------------------

def _gedaan_per_doc(conn, norm: str) -> dict[str, set[str]]:
    """
    Return {doc_id: {clausule_id, ...}} van reeds geclassificeerde
    (doc, clausule, norm) combinaties voor Drive-docs.
    """
    result: dict[str, set[str]] = defaultdict(set)
    rows = conn.execute(
        "SELECT doc_id, clausule_id FROM bevindingen WHERE herkomst='Drive' AND norm=?",
        (norm,),
    ).fetchall()
    for doc_id, cid in rows:
        result[doc_id].add(cid)
    return result


def _gedaan_miro(conn, norm: str) -> set[str]:
    rows = conn.execute(
        "SELECT DISTINCT doc_id FROM bevindingen WHERE herkomst='Miro' AND norm=?",
        (norm,),
    ).fetchall()
    return {r[0] for r in rows}


def _upsert_bevindingen(conn, bevindingen: list[dict], norm: str) -> None:
    """UPSERT: overschrijft bestaande row bij conflict op composite key."""
    for bev in bevindingen:
        conn.execute(
            """
            INSERT INTO bevindingen
                (doc_id, herkomst, clausule_id, norm, classificatie, beschrijving,
                 onderbouwing, pre_classificatie, document_naam, classified_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(doc_id, herkomst, clausule_id, norm) DO UPDATE SET
                classificatie    = excluded.classificatie,
                beschrijving     = excluded.beschrijving,
                onderbouwing     = excluded.onderbouwing,
                pre_classificatie= excluded.pre_classificatie,
                document_naam    = excluded.document_naam,
                classified_at    = excluded.classified_at
            """,
            (
                bev["_doc_id"], bev["herkomst"], bev["clausule"], norm,
                bev["classificatie"], bev.get("beschrijving", ""),
                bev.get("onderbouwing", ""), bev.get("pre_classificatie"),
                bev["document_naam"],
            ),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Kostenschatting vooraf (geen API-calls)
# ---------------------------------------------------------------------------

def schat_kosten(
    gekoppelde_docs: list[dict],
    miro_notities: list[dict],
    clause_map: dict,
    norm: str = "beide",
    scherpte: float = 1.0,
    model: str = DEFAULT_MODEL,
    rehash: bool = False,
) -> dict:
    """
    Schat token-verbruik en kosten zonder API-calls.

    Werkwijze:
      - Systeem prompt telt als cache-write bij 1e call en cache-read daarna
      - Voor elke doc: input = user-prompt chars/4 (doc-tekst + clausules-lijst);
        output = 150 tokens × aantal clausules
      - Voor Miro: 1 call per batch van MIRO_BATCH notities

    Als rehash=False wordt (doc, clausule) die al in DB staat overgeslagen.
    """
    from audit.store import verbinding, initialiseer
    conn = verbinding()
    initialiseer(conn)
    gedaan = _gedaan_per_doc(conn, norm)
    gedaan_miro_ids = _gedaan_miro(conn, norm)
    conn.close()

    clausules = clause_map.get("clausules", {})
    system_tekst = _systeem_voor(scherpte, herkomst="Drive")
    system_tokens = max(len(system_tekst) // CHARS_PER_TOKEN, 1024)  # minimum voor cache

    miro_system_tokens = max(len(_SYSTEM_MIRO) // CHARS_PER_TOKEN, 1024)

    p = PRIJZEN.get(model, {"input": 0, "output": 0, "cache_write_5m": 0, "cache_read": 0})

    input_regulier = 0
    input_cache_read = 0
    input_cache_write = 0
    output_budget = 0
    calls = 0

    # --- Drive ---
    doc_cache_gebruikt = False
    for doc in gekoppelde_docs:
        doc_id = doc["id"]
        alle_cids = list(doc.get("clausules", []))
        if not alle_cids:
            continue
        cids_todo = alle_cids if rehash else [c for c in alle_cids if c not in gedaan.get(doc_id, set())]
        if not cids_todo:
            continue
        user_chars = len(doc.get("naam", "")) + min(len(doc.get("tekst", "")), MAX_TEKST) + 50 * len(cids_todo)
        user_tokens = user_chars // CHARS_PER_TOKEN
        if not doc_cache_gebruikt:
            input_cache_write += system_tokens
            input_regulier += user_tokens
            doc_cache_gebruikt = True
        else:
            input_cache_read += system_tokens
            input_regulier += user_tokens
        output_budget += 150 * len(cids_todo)
        calls += 1

    # --- Miro ---
    todo_miro = [
        n for n in miro_notities
        if rehash or n.get("miro_item_id", n.get("id")) not in gedaan_miro_ids
    ]
    miro_cache_gebruikt = False
    for i in range(0, len(todo_miro), MIRO_BATCH):
        batch = todo_miro[i:i + MIRO_BATCH]
        user_chars = sum(300 for _ in batch)
        user_tokens = user_chars // CHARS_PER_TOKEN
        if not miro_cache_gebruikt:
            input_cache_write += miro_system_tokens
            input_regulier += user_tokens
            miro_cache_gebruikt = True
        else:
            input_cache_read += miro_system_tokens
            input_regulier += user_tokens
        output_budget += 150 * len(batch)
        calls += 1

    kosten_usd = (
        input_regulier * p["input"]
        + input_cache_read * p["cache_read"]
        + input_cache_write * p["cache_write_5m"]
        + output_budget * p["output"]
    ) / 1_000_000

    return {
        "model": model,
        "calls": calls,
        "input_regulier": input_regulier,
        "input_cache_read": input_cache_read,
        "input_cache_write": input_cache_write,
        "output_budget": output_budget,
        "kosten_usd_schatting": round(kosten_usd, 4),
    }


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def classificeer_alle_bevindingen(
    gekoppelde_docs: list[dict],
    miro_notities: list[dict],
    clause_map: dict,
    norm: str = "beide",
    scherpte: float = 1.0,
    rehash: bool = False,
    model: str | None = None,
) -> list[dict]:
    """
    Classificeer Drive-docs en Miro-notities.

    Nieuwe semantiek t.o.v. oude module:
      - Checkpoint op (doc_id, clausule_id, norm), niet alleen op doc_id.
      - `rehash=True` ignoreert checkpoint en overschrijft via UPSERT.
      - System prompt wordt gecached (ephemeral).
      - Elk call capture-t token usage in `Kostenteller`.
    """
    from audit.store import verbinding, initialiseer

    teller = Kostenteller(model=model or DEFAULT_MODEL)
    conn = verbinding()
    initialiseer(conn)

    gedaan = _gedaan_per_doc(conn, norm)
    gedaan_miro_ids = _gedaan_miro(conn, norm)
    clausules = clause_map.get("clausules", {})
    client = anthropic.Anthropic()

    # --- Drive ---
    clausules_per_doc: dict[str, list[str]] = defaultdict(list)
    doc_map: dict[str, dict] = {}
    for doc in gekoppelde_docs:
        doc_map[doc["id"]] = doc
        for cid in doc.get("clausules", []):
            clausules_per_doc[doc["id"]].append(cid)

    todo_pairs = []
    for doc_id, cids in clausules_per_doc.items():
        if rehash:
            todo_pairs.append((doc_id, cids))
            continue
        missend = [c for c in cids if c not in gedaan.get(doc_id, set())]
        if missend:
            todo_pairs.append((doc_id, missend))

    logger.info(
        "Drive: %d/%d docs te classificeren (rehash=%s)",
        len(todo_pairs), len(clausules_per_doc), rehash,
    )

    for i, (doc_id, cids) in enumerate(todo_pairs, 1):
        doc = doc_map[doc_id]
        logger.info("[%d/%d] %s (%d clausules)", i, len(todo_pairs), doc["naam"][:50], len(cids))
        resultaten = _classificeer_doc(doc, cids, clausules, client, teller, scherpte=scherpte)
        res_map = {r["clausule"]: r for r in resultaten}
        bevs = []
        for cid in cids:
            res = res_map.get(cid, {})
            bevs.append({
                "_doc_id": doc_id,
                "herkomst": "Drive",
                "clausule": cid,
                "clausule_titel": clausules.get(cid, {}).get("titel", cid),
                "document_naam": doc["naam"],
                "classificatie": res.get("classificatie", "OFI"),
                "beschrijving": res.get("beschrijving", ""),
                "onderbouwing": res.get("onderbouwing", ""),
                "pre_classificatie": None,
            })
        _upsert_bevindingen(conn, bevs, norm)

    # --- Miro ---
    todo_miro = [
        n for n in miro_notities
        if rehash or n.get("miro_item_id", n.get("id")) not in gedaan_miro_ids
    ]
    logger.info("Miro: %d/%d notities te classificeren", len(todo_miro), len(miro_notities))

    for i in range(0, len(todo_miro), MIRO_BATCH):
        batch = todo_miro[i:i + MIRO_BATCH]
        logger.info("Miro batch %d (%d items)", i // MIRO_BATCH + 1, len(batch))
        resultaten = _classificeer_miro_batch(batch, clausules, client, teller)
        res_map = {r["id"]: r for r in resultaten}
        bevs = []
        skip_teller = 0
        mistag_teller = 0
        for notitie in batch:
            nid = notitie.get("miro_item_id", notitie.get("id", ""))
            cid = notitie.get("clausule", "")
            if not cid:
                skip_teller += 1
                continue  # NOT NULL constraint op clausule_id in DB — skip ongekoppelde items
            res = res_map.get(nid, {})
            if _is_miro_mistag(res.get("beschrijving", "")):
                mistag_teller += 1
                # Ook bestaande DB-rij opruimen zodat residual mis-taggings niet
                # blijven rondhangen tussen runs heen.
                conn.execute(
                    "DELETE FROM bevindingen WHERE doc_id=? AND herkomst='Miro' AND clausule_id=? AND norm=?",
                    (nid, cid, norm),
                )
                continue
            bevs.append({
                "_doc_id": nid,
                "herkomst": "Miro",
                "clausule": cid,
                "clausule_titel": clausules.get(cid, {}).get("titel", cid),
                "document_naam": f"Miro: {notitie.get('tekst', '')[:60]}...",
                "classificatie": res.get("classificatie", "OFI"),
                "beschrijving": res.get("beschrijving", ""),
                "onderbouwing": res.get("onderbouwing", ""),
                "pre_classificatie": notitie.get("pre_classificatie"),
            })
        if skip_teller or mistag_teller:
            logger.warning(
                "Miro batch %d: %d zonder clausule + %d mis-tagged overgeslagen",
                i // MIRO_BATCH + 1, skip_teller, mistag_teller,
            )
        _upsert_bevindingen(conn, bevs, norm)

    logger.info("Kosten-rapport: %s", teller.rapport())

    # --- Alles uit DB laden voor downstream rapportage ---
    rows = conn.execute("SELECT * FROM bevindingen WHERE norm=? ORDER BY clausule_id", (norm,)).fetchall()
    conn.close()

    alle = [{
        "clausule": r["clausule_id"],
        "clausule_titel": clausules.get(r["clausule_id"], {}).get("titel", r["clausule_id"]),
        "document_naam": r["document_naam"] or "",
        "doc_id": r["doc_id"],
        "herkomst": r["herkomst"],
        "classificatie": r["classificatie"],
        "beschrijving": r["beschrijving"] or "",
        "onderbouwing": r["onderbouwing"] or "",
        "pre_classificatie": r["pre_classificatie"],
        "id": r["id"],
    } for r in rows]

    nc = sum(1 for b in alle if b["classificatie"] == "NC")
    ofi = sum(1 for b in alle if b["classificatie"] == "OFI")
    pos = sum(1 for b in alle if b["classificatie"] == "positief")
    logger.info("Klaar: %d bevindingen — NC: %d, OFI: %d, positief: %d",
                len(alle), nc, ofi, pos)
    return alle


# ---------------------------------------------------------------------------
# Review + Sheets — delegeren naar originele module (ongewijzigd)
# ---------------------------------------------------------------------------

from audit.finding_classification import review_en_bevestig, sla_op_in_sheets  # noqa: E402,F401


# ---------------------------------------------------------------------------
# CLI — dry-run-cost zonder API-calls
# ---------------------------------------------------------------------------

def _main():
    parser = argparse.ArgumentParser(description="finding_classification v2 — kostenschatting + rehash")
    parser.add_argument("--norm", choices=["9001", "27001", "beide"], default="27001")
    parser.add_argument("--chapter", default=None, help="Beperk tot hoofdstuk (bv. 7)")
    parser.add_argument("--scherpte", type=float, default=1.0)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--rehash", action="store_true", help="Ignoreer checkpoint, overschrijf bestaand")
    parser.add_argument("--dry-run-cost", action="store_true", help="Toon alleen kostenschatting, géén API-calls")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from audit.clause_mapping import laad_clause_map, filter_clause_map, koppel_documenten
    from audit.drive_ingest import haal_documenten_op
    from audit.miro_ingest import haal_notities_op, koppel_aan_clausules

    clause_map = laad_clause_map(args.norm)
    if args.chapter:
        clause_map = filter_clause_map(clause_map, args.chapter)

    documenten, _ = haal_documenten_op()
    gekoppeld, _ = koppel_documenten(documenten, clause_map)

    miro_notities = []
    try:
        miro_raw = haal_notities_op()
        miro_notities = koppel_aan_clausules(miro_raw, clause_map)
    except Exception as e:
        logger.warning("Miro overgeslagen: %s", e)

    if args.dry_run_cost:
        schatting = schat_kosten(
            gekoppeld, miro_notities, clause_map,
            norm=args.norm, scherpte=args.scherpte,
            model=args.model, rehash=args.rehash,
        )
        print("\n=== Kostenschatting (geen API-calls) ===")
        for k, v in schatting.items():
            print(f"  {k}: {v}")
        return

    bevindingen = classificeer_alle_bevindingen(
        gekoppeld, miro_notities, clause_map,
        norm=args.norm, scherpte=args.scherpte,
        rehash=args.rehash, model=args.model,
    )
    print(f"\n{len(bevindingen)} bevindingen in DB.")


if __name__ == "__main__":
    _main()
