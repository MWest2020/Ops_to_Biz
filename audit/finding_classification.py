"""
Taak 6: Bevindingen classificatie via Claude API.

Classificeert documenten per stuk (alle clausules in één call) en
Miro-notities in batches per hoofdstuk.

Checkpoint: bevindingen worden per document/batch naar de DB geschreven
zodat een onderbroken run hervat kan worden.
"""

import json
import logging
import os

import anthropic

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
MAX_TEKST = 2000
MIRO_BATCH = 20


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_DOC_PROMPT_SCHERP = """\
Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Document: {naam}
Tekst:
---
{tekst}
---

Beoordeel dit document strikt voor elk van de onderstaande ISO-clausules.
- "positief": het document levert aantoonbaar bewijs dat aan de eis is voldaan.
- "OFI": de eis is gedeeltelijk gedekt, verbetering is mogelijk.
- "NC": er is geen of onvoldoende bewijs; de eis is niet aantoonbaar gedekt.

Clausules:
{clausules_lijst}

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{{"clausule": "<id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}}]
"""

_DOC_PROMPT_GENUANCEERD = """\
Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Organisatiecontext:
- Conduction noemt een non-conformiteit een "afwijking". Er zijn gedocumenteerde
  procedures voor het vastleggen en opvolgen van afwijkingen (memo afwijking/
  tekortkoming/incident). Het bestaan van zo'n memo is aantoonbaar bewijs dat
  de NC-procedure functioneert — classificeer dit als "positief" voor clausules
  als 10.2, 8.7 en vergelijkbare corrigerende-actie-eisen.
- Interne auditverslagen (Interne Audit Q*) zijn bewijs van een werkend
  intern auditsysteem (9.2). Classificeer aanwezig auditverslag als "positief".

Document: {naam}
Tekst:
---
{tekst}
---

Beoordeel dit document genuanceerd voor elk van de onderstaande ISO-clausules.
Hanteer PDCA als uitgangspunt: intentie en richting tellen mee.
- "positief": het document levert aantoonbaar bewijs dat aan de eis is voldaan.
- "OFI": de intentie is aanwezig maar uitvoering of documentatie is onvolledig.
- "NC": ALLEEN als de norm een expliciete deliverable vereist (procedure, register,
  log, besluit) die aantoonbaar ONTBREEKT. Twijfel → OFI, niet NC.

Clausules:
{clausules_lijst}

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{{"clausule": "<id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}}]
"""

_MIRO_PROMPT = """\
Je bent een ervaren ISO-auditor bij Conduction, een Nederlands softwarebedrijf.

Classificeer elk onderstaand Miro-item voor de genoemde ISO-clausule.

Items:
{items}

Retourneer uitsluitend geldig JSON (geen toelichting buiten JSON):
[{{"id": "<item_id>", "classificatie": "NC"|"OFI"|"positief", "beschrijving": "<Nederlands, max 80 woorden>", "onderbouwing": "<norm-eis>"}}]
"""


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _parse_json_list(tekst: str) -> list[dict]:
    start = tekst.find("[")
    eind = tekst.rfind("]") + 1
    if start == -1:
        return []
    return json.loads(tekst[start:eind])


def _classificeer_doc(
    doc: dict,
    clausule_ids: list[str],
    clausules: dict,
    client: anthropic.Anthropic,
    scherpte: float = 1.0,
) -> list[dict]:
    """1 API-call voor alle clausules van één document."""
    clausules_lijst = "\n".join(
        f"- {cid}: {clausules.get(cid, {}).get('titel', cid)}"
        for cid in clausule_ids
    )
    template = _DOC_PROMPT_SCHERP if scherpte >= 0.75 else _DOC_PROMPT_GENUANCEERD
    prompt = template.format(
        naam=doc["naam"],
        tekst=doc["tekst"][:MAX_TEKST],
        clausules_lijst=clausules_lijst,
    )
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=150 * len(clausule_ids) + 64,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return _parse_json_list(resp.content[0].text)
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning("JSON-parse fout (doc %s): %s", doc["naam"][:40], e)
        return []


def _classificeer_miro_batch(
    notities: list[dict],
    clausules: dict,
    client: anthropic.Anthropic,
) -> list[dict]:
    """1 API-call voor een batch Miro-notities."""
    items_tekst = "\n".join(
        f"- ID: {n.get('miro_item_id', n.get('id', '?'))} | "
        f"Clausule: {n.get('clausule', '?')} {clausules.get(n.get('clausule',''), {}).get('titel','')} | "
        f"Tekst: {n.get('tekst','')[:200]}"
        for n in notities
    )
    prompt = _MIRO_PROMPT.format(items=items_tekst)
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=150 * len(notities) + 64,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return _parse_json_list(resp.content[0].text)
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning("JSON-parse fout (Miro batch): %s", e)
        return []


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _laad_gedane_docs(conn) -> set[str]:
    """Doc-IDs die al volledig geclassificeerd zijn (alle clausules in één call)."""
    rows = conn.execute(
        "SELECT DISTINCT doc_id FROM bevindingen WHERE herkomst='Drive'"
    ).fetchall()
    return {r[0] for r in rows}


def _laad_gedane_miro(conn) -> set[str]:
    rows = conn.execute(
        "SELECT DISTINCT doc_id FROM bevindingen WHERE herkomst='Miro'"
    ).fetchall()
    return {r[0] for r in rows}


def _sla_bevindingen_op(conn, bevindingen: list[dict], norm: str) -> None:
    for bev in bevindingen:
        conn.execute("""
            INSERT OR IGNORE INTO bevindingen
                (doc_id, herkomst, clausule_id, norm, classificatie, beschrijving,
                 onderbouwing, pre_classificatie, document_naam, classified_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
        """, (
            bev["_doc_id"], bev["herkomst"], bev["clausule"], norm,
            bev["classificatie"], bev.get("beschrijving", ""),
            bev.get("onderbouwing", ""), bev.get("pre_classificatie"),
            bev["document_naam"],
        ))
    conn.commit()


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def classificeer_alle_bevindingen(
    gekoppelde_docs: list[dict],
    miro_notities: list[dict],
    clause_map: dict,
    norm: str = "beide",
    scherpte: float = 1.0,
) -> list[dict]:
    """
    Classificeer alle documenten en Miro-notities.

    Drive: 1 API-call per document (alle clausules tegelijk).
    Miro:  1 API-call per batch van MIRO_BATCH notities.

    Checkpoint: al-geclassificeerde docs/notities worden overgeslagen.
    Retourneert volledige lijst (nieuw + eerder opgeslagen).
    """
    from audit.store import verbinding, initialiseer

    conn = verbinding()
    initialiseer(conn)
    gedane_docs = _laad_gedane_docs(conn)
    gedane_miro = _laad_gedane_miro(conn)

    clausules = clause_map.get("clausules", {})
    client = anthropic.Anthropic()

    # --- Drive-documenten ---
    doc_map: dict[str, dict] = {doc["id"]: doc for doc in gekoppelde_docs}
    # Groepeer clausules per doc
    from collections import defaultdict
    clausules_per_doc: dict[str, list[str]] = defaultdict(list)
    for doc in gekoppelde_docs:
        for cid in doc.get("clausules", []):
            clausules_per_doc[doc["id"]].append(cid)

    totaal_docs = len([d for d in clausules_per_doc if d not in gedane_docs])
    logger.info("Drive: %d docs te classificeren (%d al gedaan)", totaal_docs, len(gedane_docs))

    for i, (doc_id, cids) in enumerate(clausules_per_doc.items(), 1):
        if doc_id in gedane_docs:
            continue
        doc = doc_map[doc_id]
        logger.info("[%d/%d] %s (%d clausules)", i, totaal_docs, doc["naam"][:50], len(cids))
        resultaten = _classificeer_doc(doc, cids, clausules, client, scherpte=scherpte)

        # Koppel resultaten terug aan doc_id
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
        _sla_bevindingen_op(conn, bevs, norm)

    # --- Miro-notities ---
    te_doen_miro = [
        n for n in miro_notities
        if n.get("miro_item_id", n.get("id")) not in gedane_miro
    ]
    logger.info("Miro: %d notities te classificeren (%d al gedaan)",
                len(te_doen_miro), len(miro_notities) - len(te_doen_miro))

    for i in range(0, len(te_doen_miro), MIRO_BATCH):
        batch = te_doen_miro[i:i + MIRO_BATCH]
        logger.info("Miro batch %d/%d", i // MIRO_BATCH + 1,
                    -(-len(te_doen_miro) // MIRO_BATCH))
        resultaten = _classificeer_miro_batch(batch, clausules, client)
        res_map = {r["id"]: r for r in resultaten}

        bevs = []
        for notitie in batch:
            nid = notitie.get("miro_item_id", notitie.get("id", ""))
            cid = notitie.get("clausule", "")
            res = res_map.get(nid, {})
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
        _sla_bevindingen_op(conn, bevs, norm)

    # --- Laad alles uit DB voor rapport ---
    alle_rows = conn.execute(
        "SELECT * FROM bevindingen ORDER BY clausule_id"
    ).fetchall()
    conn.close()

    alle_bevindingen = [{
        "clausule": r["clausule_id"],
        "clausule_titel": clausules.get(r["clausule_id"], {}).get("titel", r["clausule_id"]),
        "document_naam": r["document_naam"] or "",
        "doc_id": r["doc_id"],
        "herkomst": r["herkomst"],
        "classificatie": r["classificatie"],
        "beschrijving": r["beschrijving"] or "",
        "onderbouwing": r["onderbouwing"] or "",
        "pre_classificatie": r["pre_classificatie"],
    } for r in alle_rows]

    nc = sum(1 for b in alle_bevindingen if b["classificatie"] == "NC")
    ofi = sum(1 for b in alle_bevindingen if b["classificatie"] == "OFI")
    pos = sum(1 for b in alle_bevindingen if b["classificatie"] == "positief")
    logger.info("Klaar: %d bevindingen — NC: %d, OFI: %d, positief: %d",
                len(alle_bevindingen), nc, ofi, pos)
    return alle_bevindingen


# ---------------------------------------------------------------------------
# Review + Sheets (ongewijzigd)
# ---------------------------------------------------------------------------

def review_en_bevestig(bevindingen: list[dict], auto_accept: bool = False) -> list[dict]:
    VOLGORDE = {"NC": 0, "OFI": 1, "positief": 2}
    gesorteerd = sorted(bevindingen, key=lambda b: VOLGORDE.get(b["classificatie"], 9))

    nc = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    pos = sum(1 for b in bevindingen if b["classificatie"] == "positief")

    if auto_accept:
        logger.info("Auto-accept: %d bevindingen (NC: %d, OFI: %d, positief: %d)",
                    len(bevindingen), nc, ofi, pos)
        return list(bevindingen)

    print("\n" + "=" * 70)
    print("REVIEW BEVINDINGEN")
    print("=" * 70)
    print(f"Totaal: {len(bevindingen)} | NC: {nc} | OFI: {ofi} | Positief: {pos}\n")

    gecorrigeerd = []
    for i, bev in enumerate(gesorteerd, 1):
        print(f"[{i}/{len(gesorteerd)}] {bev['clausule']}: {bev['clausule_titel']}")
        print(f"  {bev['herkomst']} — {bev['document_naam'][:60]}")
        print(f"  {bev['classificatie']} — {bev['beschrijving'][:100]}")
        invoer = input("  [Enter=ok | nc/ofi/p=corrigeer | s=sla over]: ").strip().lower()
        if invoer == "nc":
            bev = {**bev, "classificatie": "NC"}
        elif invoer == "ofi":
            bev = {**bev, "classificatie": "OFI"}
        elif invoer in ("p", "pos", "positief"):
            bev = {**bev, "classificatie": "positief"}
        elif invoer == "s":
            continue
        gecorrigeerd.append(bev)

    print(f"\nReview klaar: {len(gecorrigeerd)} bevindingen.\n")
    return gecorrigeerd


def sla_op_in_sheets(
    bevindingen: list[dict],
    ontbrekende_clausules: list[dict],
    sheets_id: str | None = None,
) -> str:
    from audit.sheets_gws import sla_op_in_sheets as _gws_schrijf
    return _gws_schrijf(bevindingen, ontbrekende_clausules, sheets_id)
