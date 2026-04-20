"""
Miro board setup — gestructureerd auditbord aanmaken.

Maakt een nieuw bord in de ISO-space met:
  - Eén frame per ISO-hoofdstuk (9001 hfst 4-10, 27001 hfst 5-8)
  - Per clausule een template sticky note (kleur = nog te beoordelen)
  - Kleurconventie:
      light_yellow  = nog te beoordelen / open
      green         = positief / gedekt
      yellow        = OFI (verbeterpunt)
      red           = NC (non-conformiteit)

Gebruik:
  python -m audit.miro_board_setup                    # nieuw bord aanmaken
  python -m audit.miro_board_setup --droog            # dry-run, print plan
  python -m audit.miro_board_setup --bord-id <id>     # gebruik bestaand bord
"""

import argparse
import logging
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

MIRO_API = "https://api.miro.com/v2"
ISO_PROJECT_ID = "3458764519029876453"

# Layout constanten (px)
FRAME_WIDTH = 2400
FRAME_HEIGHT = 3000        # verhoogd: ruimte voor header + sub-punten + docs
FRAME_GAP_X = 200
FRAME_GAP_Y = 300
STICKY_W = 228
HEADER_H = 110             # compact header sticky per clausule
SUB_H = 170                # sub-punt sticky hoogte
DOC_STICKY_H = 220         # doc-links sticky
STICKY_GAP = 16
STICKY_COLS = 8
FRAME_PADDING = 80
MAX_SUB_PUNTEN = 5         # max sub-punten in HLS clausules (7.1 heeft 5)

# HLS-hoofdstukken 4–10 — gedeeld door ISO 9001 én ISO 27001 (Annex SL)
HOOFDSTUKKEN_HLS = [
    ("4", "Organisatiecontext"),
    ("5", "Leiderschap"),
    ("6", "Planning"),
    ("7", "Ondersteuning"),
    ("8", "Uitvoering"),
    ("9", "Evaluatie"),
    ("10", "Verbetering"),
]

# ISO 27001 Annex A thema's — uniek voor 27001 (operationele controls)
ANNEX_A_27001 = [
    ("5", "Organisatorische maatregelen"),
    ("6", "Personeelsmaatregelen"),
    ("7", "Fysieke maatregelen"),
    ("8", "Technische maatregelen"),
]

# Kleuren per status
KLEUREN = {
    "open":     "light_yellow",
    "positief": "light_green",
    "OFI":      "yellow",
    "NC":       "red",
}


def _headers() -> dict:
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _post(endpoint: str, body: dict, droog: bool = False) -> dict:
    if droog:
        logger.debug("DRY-RUN POST %s: %s", endpoint, list(body.keys()))
        return {"id": "dry-run"}
    resp = requests.post(f"{MIRO_API}{endpoint}", json=body, headers=_headers(), timeout=30)
    if resp.status_code == 429:
        wait = int(resp.headers.get("Retry-After", 5))
        logger.warning("Rate limit — wacht %ds", wait)
        time.sleep(wait)
        return _post(endpoint, body, droog)
    if not resp.ok:
        logger.error("Miro API fout %d: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
    time.sleep(0.15)  # vriendelijk voor de API
    return resp.json()


def maak_bord(naam: str, droog: bool = False) -> str:
    logger.info("Bord aanmaken: %s", naam)
    body = {
        "name": naam,
        "description": "Gegenereerd door ISO audit pipeline — Conduction",
        "project": {"id": ISO_PROJECT_ID},
        "sharingPolicy": {
            "access": "edit",
            "teamAccess": "edit",
        },
    }
    result = _post("/boards", body, droog)
    board_id = result.get("id", "dry-run")
    logger.info("Bord aangemaakt: %s (id: %s)", naam, board_id)
    return board_id


def maak_frame(board_id: str, titel: str, x: int, y: int, droog: bool = False) -> str:
    body = {
        "data": {"title": titel, "format": "custom", "showContent": True},
        "style": {"fillColor": "#f0f0f0"},
        "geometry": {"width": FRAME_WIDTH, "height": FRAME_HEIGHT},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = _post(f"/boards/{board_id}/frames", body, droog)
    return result.get("id", "dry-run")


def maak_sticky(
    board_id: str,
    tekst: str,
    x: int,
    y: int,
    kleur: str = "light_yellow",
    droog: bool = False,
) -> str:
    body = {
        "data": {"content": tekst, "shape": "square"},
        "style": {"fillColor": kleur, "textAlign": "left", "textAlignVertical": "top"},
        "geometry": {"width": STICKY_W},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = _post(f"/boards/{board_id}/sticky_notes", body, droog)
    return result.get("id", "dry-run")


def _clausules_voor_hoofdstuk(clause_map: dict, prefix: str) -> list[tuple[str, str]]:
    """Geeft gesorteerde (id, titel) paren voor een hoofdstukprefix."""
    return sorted(
        (cid, data.get("titel", ""))
        for cid, data in clause_map.get("clausules", {}).items()
        if cid.startswith(prefix + ".") or cid == prefix
    )


def _kleur_voor_clausule(clausule_id: str, matched_ids: set, interviews: dict) -> str:
    """
    Prioriteit:
      1. Interview-bevinding (NC/OFI/positief) overschrijft alles
      2. Gedekt door documenten → groen
      3. Niets → geel (open, audit inplannen)
    """
    iv = interviews.get(clausule_id)
    if iv:
        return KLEUREN.get(iv["bevinding"], "light_yellow")
    if clausule_id in matched_ids:
        return KLEUREN["positief"]
    return KLEUREN["open"]


def bouw_bord(droog: bool = False, bord_id: str | None = None) -> str:
    from audit.clause_mapping import laad_clause_map
    from audit.store import verbinding, laad_interviews

    conn = verbinding()
    interviews = {r["clausule_id"]: dict(r) for r in laad_interviews(conn)}

    matched_ids = set(
        r[0] for r in conn.execute(
            "SELECT DISTINCT clausule_id FROM clause_matches WHERE sub_punt = ''"
        ).fetchall()
    )

    # Drive-documenten per clausule: (naam, link) — max 6
    def _drive_link(doc_id, mime):
        if mime == "application/vnd.google-apps.document":
            return f"https://docs.google.com/document/d/{doc_id}"
        if mime == "application/vnd.google-apps.spreadsheet":
            return f"https://docs.google.com/spreadsheets/d/{doc_id}"
        return f"https://drive.google.com/file/d/{doc_id}"

    # Drive-documenten per clausule (clausule-niveau, max 4 voor residuele docs)
    bewijs_met_id: dict[str, list[tuple]] = {}  # cid → [(naam, link)]
    for row in conn.execute("""
        SELECT cm.clausule_id, d.id, d.naam, d.mime_type
        FROM clause_matches cm
        JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
        WHERE d.scope = 'in' AND cm.sub_punt = ''
        ORDER BY cm.clausule_id, d.modified_at DESC, d.naam
    """).fetchall():
        cid = row["clausule_id"]
        link = _drive_link(row["id"], row["mime_type"])
        bewijs_met_id.setdefault(cid, [])
        if len(bewijs_met_id[cid]) < 4:
            bewijs_met_id[cid].append((row["naam"], link))

    # Drive-documenten per sub-punt: (cid, sub_punt_id) → [(naam, link)]
    bewijs_sub: dict[tuple, list[tuple]] = {}  # (cid, sp_id) → [(naam, link)]
    for row in conn.execute("""
        SELECT cm.clausule_id, cm.sub_punt, d.id, d.naam, d.mime_type
        FROM clause_matches cm
        JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
        WHERE d.scope = 'in' AND cm.sub_punt != ''
        ORDER BY cm.clausule_id, cm.sub_punt, d.modified_at DESC, d.naam
    """).fetchall():
        key = (row["clausule_id"], row["sub_punt"])
        link = _drive_link(row["id"], row["mime_type"])
        bewijs_sub.setdefault(key, [])
        if len(bewijs_sub[key]) < 4:
            bewijs_sub[key].append((row["naam"], link))

    # Planning 2025: clausule_id → kommagescheiden maanden
    planning: dict[str, str] = {}
    for row in conn.execute(
        "SELECT clausule_id, kwartaal FROM audit_planning WHERE jaar=2025 AND kwartaal != ''"
    ).fetchall():
        planning[row["clausule_id"]] = row["kwartaal"]

    conn.close()

    cm_9001 = laad_clause_map("9001")
    cm_27001 = laad_clause_map("27001")

    if bord_id:
        logger.info("Bestaand bord gebruiken: %s", bord_id)
        board_id = bord_id
    else:
        board_id = maak_bord("ISO Audit Landschap 9001 + 27001", droog)

    if droog:
        logger.info("DRY-RUN — geen echte API-calls naar Miro")

    from audit.normteksten import NORMTEKSTEN_9001, NORMTEKSTEN_27001
    _normteksten_map = {**NORMTEKSTEN_9001, **NORMTEKSTEN_27001}

    # Label per norm
    _NORM_LABEL = {"9001": "KMS", "27001": "ISMS"}

    def _vul_frame(clausules, x, y_offset, norm_label):
        sx_start = x + FRAME_PADDING + STICKY_W // 2
        # Rij-hoogte: header + MAX sub-punten + doc + gaps
        rij_hoogte = HEADER_H + MAX_SUB_PUNTEN * (SUB_H + STICKY_GAP) + DOC_STICKY_H + STICKY_GAP * 3
        sy_start = y_offset + FRAME_PADDING + HEADER_H // 2 + 80

        label = _NORM_LABEL.get(norm_label, norm_label)

        for i, (cid, titel) in enumerate(clausules):
            col = i % STICKY_COLS
            row = i // STICKY_COLS
            sx = sx_start + col * (STICKY_W + STICKY_GAP)
            sy_header = sy_start + row * rij_hoogte

            kleur = _kleur_voor_clausule(cid, matched_ids, interviews)

            # ── Header-sticky (compact, gekleurd) ─────────────────────────
            tekst = f"<strong>[{label}] {cid}</strong>\n{titel}"
            iv = interviews.get(cid)
            if iv:
                bevinding_label = {"NC": "🔴 NC", "OFI": "🟡 OFI", "positief": "🟢 OK",
                                   "overgeslagen": "⚪ n.v.t."}.get(iv["bevinding"], iv["bevinding"])
                tekst += f"\n{bevinding_label}"
                if iv.get("notitie"):
                    tekst += f": {iv['notitie'][:50]}"
            plan = planning.get(cid)
            if plan:
                tekst += f"\n📅 {plan}"
            maak_sticky(board_id, tekst, sx, sy_header, kleur, droog)

            # ── Sub-punt stickies (lichtblauw) ────────────────────────────
            nt = _normteksten_map.get(cid, {})
            sub_punten = nt.get("sub_punten", [])
            for j, sp in enumerate(sub_punten):
                sy_sub = sy_header + HEADER_H // 2 + STICKY_GAP + j * (SUB_H + STICKY_GAP) + SUB_H // 2
                sp_docs = bewijs_sub.get((cid, sp["id"]), [])
                if sp_docs:
                    # Echte Drive-documenten voor dit sub-punt
                    regels = "\n".join(
                        f'<a href="{link}">{naam[:38]}</a>'
                        for naam, link in sp_docs
                    )
                    sp_tekst = f"<strong>{sp['id']}) {sp['eis'][:70]}</strong>\n{regels}"
                else:
                    # Geen bewijs gevonden: toon bewijslast als checklist
                    sp_bewijslast = "\n".join(
                        f"☐ {b[:55]}" for b in sp.get("bewijslast", [])[:2]
                    )
                    sp_tekst = (
                        f"<strong>{sp['id']}) {sp['eis'][:70]}</strong>"
                        + (f"\n{sp_bewijslast}" if sp_bewijslast else "\n☐ _(geen bewijs gevonden)_")
                    )
                maak_sticky(board_id, sp_tekst, sx, sy_sub, "light_blue", droog)

            # ── Doc-links sticky (grijs) — clausule-niveau bewijs zonder sub-punt ──
            sub_hoogte = len(sub_punten) * (SUB_H + STICKY_GAP) if sub_punten else 0
            sy_docs = sy_header + HEADER_H // 2 + STICKY_GAP + sub_hoogte + DOC_STICKY_H // 2

            doc_namen = bewijs_met_id.get(cid, [])
            if doc_namen:
                doc_regels = "\n".join(
                    f'<a href="{link}">{naam[:40]}</a>'
                    for naam, link in doc_namen
                )
                doc_tekst = f"<strong>Overig bewijs</strong>\n{doc_regels}"
            else:
                doc_tekst = "<strong>Overig bewijs</strong>\n_(geen aanvullende docs)_"
            maak_sticky(board_id, doc_tekst, sx, sy_docs, "gray", droog)

    # ── Rij 1: HLS-hoofdstukken 4–10 (ISO 9001 + ISO 27001 body) ─────────
    logger.info("Frames aanmaken voor HLS-hoofdstukken (9001 + 27001)...")
    x = 0
    for prefix, naam in HOOFDSTUKKEN_HLS:
        cl_9001 = _clausules_voor_hoofdstuk(cm_9001, prefix)
        # 27001 HLS-body (hoofdstukken 4-10) zitten niet in Annex A YAML —
        # 9001-clausules dekken de gedeelde HLS-eisen; label maakt dit zichtbaar
        if not cl_9001:
            continue

        frame_titel = f"HLS Hfst {prefix}: {naam}  |  ISO 9001 + 27001"
        frame_x = x + FRAME_WIDTH // 2
        frame_y = FRAME_HEIGHT // 2
        maak_frame(board_id, frame_titel, frame_x, frame_y, droog)
        logger.info("  Frame: %s (%d clausules)", frame_titel, len(cl_9001))
        _vul_frame(cl_9001, x, 0, "9001")
        x += FRAME_WIDTH + FRAME_GAP_X

    # ── Rij 2: ISO 27001 Annex A thema's (operationele controls) ─────────
    logger.info("Frames aanmaken voor ISO 27001 Annex A...")
    x = 0
    y_offset = FRAME_HEIGHT + FRAME_GAP_Y
    for prefix, naam in ANNEX_A_27001:
        clausules = _clausules_voor_hoofdstuk(cm_27001, prefix)
        if not clausules:
            continue

        CHUNK = 20
        chunks = [clausules[i:i+CHUNK] for i in range(0, len(clausules), CHUNK)]

        for chunk_idx, chunk in enumerate(chunks):
            suffix = f" ({chunk_idx+1}/{len(chunks)})" if len(chunks) > 1 else ""
            frame_titel = f"27001 Annex A — Thema {prefix}: {naam}{suffix}"
            frame_x = x + FRAME_WIDTH // 2
            frame_y = y_offset + FRAME_HEIGHT // 2
            maak_frame(board_id, frame_titel, frame_x, frame_y, droog)
            logger.info("  Frame: %s (%d clausules)", frame_titel, len(chunk))
            _vul_frame(chunk, x, y_offset, "27001")
            x += FRAME_WIDTH + FRAME_GAP_X

    logger.info("Bord klaar: https://miro.com/app/board/%s", board_id)
    return board_id


def main():
    parser = argparse.ArgumentParser(description="Miro auditbord aanmaken")
    parser.add_argument("--droog", action="store_true", help="Dry-run — geen API-calls")
    parser.add_argument("--bord-id", default=None, help="Gebruik bestaand bord-ID")
    args = parser.parse_args()
    board_id = bouw_bord(droog=args.droog, bord_id=args.bord_id)
    if not args.droog:
        print(f"\nBord: https://miro.com/app/board/{board_id}")


if __name__ == "__main__":
    main()
