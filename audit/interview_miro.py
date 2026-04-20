"""
Interview-voorbereiding op Miro — frames per interview-sessie.

Per sessie:
  - Frame met concept-uitnodigingstekst bovenaan
  - Per clausule twee stickies:
      1. Interviewvragen   (lichtblauw)
      2. Bewijslast        (lichtgeel)

Gebruik:
  python3 -m audit.interview_miro --droog        # dry-run, geen API
  python3 -m audit.interview_miro --bord-id <id> # schrijf naar bestaand bord
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

# Layout
FRAME_W       = 3200
FRAME_H       = 1800
FRAME_GAP_Y   = 300
FRAME_PAD     = 100
STICKY_W      = 400
STICKY_H      = 400
STICKY_GAP_X  = 40
STICKY_GAP_Y  = 30

# Kleur per sticky-type
KLEUR_VRAGEN    = "light_blue"
KLEUR_BEWIJS    = "light_yellow"
KLEUR_UITNODIGING = "light_pink"

# ── Interview-sessies ─────────────────────────────────────────────────────────
# Statische groepering: eigenaar + thema per sessie.
# De clausules worden dynamisch uit de DB gehaald (alleen echt open).
SESSIE_DEFINITIES = [
    (
        "Interview 1 — Beleid & Strategie",
        "Directie / Managementteam",
        [("9001", "5.2")],
    ),
    (
        "Interview 2 — Ondersteuning & Competenties",
        "HR / Operationeel verantwoordelijke",
        [("9001", "7.2"), ("9001", "7.3")],
    ),
    (
        "Interview 3 — Ontwerp & Ontwikkeling",
        "DevLead / CTO",
        [("9001", "8.3")],
    ),
    (
        "Interview 4 — Leveranciersbeheer (27001)",
        "Remco Damhuis",
        [("27001", "5.22")],
    ),
]


def _open_clausules() -> set[tuple[str, str]]:
    """Geeft {(norm, clausule_id)} van clausules die nog geen geldig interview hebben."""
    from audit.store import verbinding
    from audit.clause_mapping import laad_clause_map
    conn = verbinding()
    open_set = set()
    for norm in ("9001", "27001"):
        cm = laad_clause_map(norm).get("clausules", {})
        gedekt = set(r[0] for r in conn.execute(
            'SELECT DISTINCT clausule_id FROM clause_matches cm '
            'JOIN documents d ON d.id=cm.doc_id '
            'WHERE cm.norm IN (?, "beide") AND d.scope="in" AND cm.sub_punt = ""',
            (norm,)
        ).fetchall())
        interviews = {r["clausule_id"]: r["bevinding"] for r in conn.execute(
            "SELECT clausule_id, bevinding FROM interviews WHERE norm IN (?, 'beide')",
            (norm,)
        ).fetchall()}
        for cid in cm:
            if cid not in gedekt:
                bev = interviews.get(cid)
                if not bev or bev == "overgeslagen":
                    open_set.add((norm, cid))
    conn.close()
    return open_set


def _actieve_sessies() -> list[tuple]:
    """Geeft alleen sessies met minstens één open clausule."""
    open_set = _open_clausules()
    sessies = []
    for naam, eigenaar, clausule_lijst in SESSIE_DEFINITIES:
        open_in_sessie = [(n, c) for n, c in clausule_lijst if (n, c) in open_set]
        if open_in_sessie:
            sessies.append((naam, eigenaar, open_in_sessie))
    return sessies


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
        logger.debug("DRY POST %s", endpoint)
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
    time.sleep(0.15)
    return resp.json()


def _maak_frame(board_id, titel, x, y, droog):
    body = {
        "data": {"title": titel, "format": "custom", "showContent": True},
        "style": {"fillColor": "#e8f4fd"},
        "geometry": {"width": FRAME_W, "height": FRAME_H},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    return _post(f"/boards/{board_id}/frames", body, droog).get("id", "dry-run")


def _maak_tekstvak(board_id, tekst, x, y, breedte, hoogte, droog):
    body = {
        "data": {"content": tekst},
        "style": {"fontSize": 14, "textAlign": "left"},
        "geometry": {"width": breedte},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    return _post(f"/boards/{board_id}/texts", body, droog).get("id", "dry-run")


def _maak_sticky(board_id, tekst, x, y, kleur, droog):
    body = {
        "data": {"content": tekst, "shape": "square"},
        "style": {"fillColor": kleur, "textAlign": "left", "textAlignVertical": "top"},
        "geometry": {"width": STICKY_W},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    return _post(f"/boards/{board_id}/sticky_notes", body, droog).get("id", "dry-run")


def _vragen_voor_clausule(clausule_id: str, norm: str, normteksten: dict) -> list[str]:
    """Zet bewijslast-items om naar concrete auditorvragen."""
    nt = normteksten.get(clausule_id, {})
    bewijslast = nt.get("bewijslast", [])
    vragen = []
    for bewijs in bewijslast:
        # Eenvoudige transformatie: bewijslast → vraag
        b = bewijs.rstrip(".")
        if b.lower().startswith("bewijs") or b.lower().startswith("aantoon"):
            vragen.append(f"Kun je {b[6:].strip().lower()}?")
        else:
            vragen.append(f"Heb je {b[0].lower() + b[1:]}? Kun je het laten zien?")
    return vragen if vragen else ["Hoe geeft de organisatie hier invulling aan?",
                                   "Welke documentatie is beschikbaar?"]


def _uitnodiging_tekst(sessie_naam: str, eigenaar: str, clausules: list[tuple]) -> str:
    clausule_lijst = ", ".join(f"{norm} {cid}" for norm, cid in clausules)
    return (
        f"<strong>{sessie_naam}</strong>\n\n"
        f"<strong>Gesprekspartner:</strong> {eigenaar}\n"
        f"<strong>Clausules:</strong> {clausule_lijst}\n"
        f"<strong>Duur:</strong> ±45 minuten\n\n"
        f"Geen voorbereiding nodig — we kijken samen wat er al is en "
        f"wat nog gedocumenteerd moet worden. Neem eventueel relevante "
        f"documenten bij de hand."
    )


def bouw_interview_frames(board_id: str, droog: bool = False) -> None:
    from audit.normteksten import NORMTEKSTEN_9001, NORMTEKSTEN_27001
    from audit.clause_mapping import laad_clause_map

    normteksten = {**NORMTEKSTEN_9001, **NORMTEKSTEN_27001}
    cm_9001  = laad_clause_map("9001").get("clausules", {})
    cm_27001 = laad_clause_map("27001").get("clausules", {})

    # Rij 1: y=0..FRAME_HEIGHT; Rij 2: y=(FRAME_HEIGHT+FRAME_GAP_Y)..(2*FRAME_HEIGHT+FRAME_GAP_Y)
    # Interview-frames komen onder rij 2 zodat er geen overlap is
    from audit.miro_board_setup import FRAME_HEIGHT, FRAME_GAP_Y
    y_start = 2 * FRAME_HEIGHT + 2 * FRAME_GAP_Y  # = 6600 met standaard layout

    for sessie_idx, (sessie_naam, eigenaar, clausule_lijst) in enumerate(_actieve_sessies()):
        logger.info("Sessie: %s", sessie_naam)

        frame_x = FRAME_W // 2
        frame_y = y_start + sessie_idx * (FRAME_H + FRAME_GAP_Y) + FRAME_H // 2

        _maak_frame(board_id, sessie_naam, frame_x, frame_y, droog)

        # Uitnodigingstekstvak bovenaan in het frame
        tekst_x = FRAME_PAD + 600
        tekst_y = frame_y - FRAME_H // 2 + FRAME_PAD + 80
        _maak_tekstvak(
            board_id,
            _uitnodiging_tekst(sessie_naam, eigenaar, clausule_lijst),
            tekst_x, tekst_y, 1100, 300, droog,
        )

        # Stickies per clausule
        sticky_x_start = FRAME_PAD + STICKY_W // 2 + 1300
        sticky_y_vragen = frame_y - FRAME_H // 2 + FRAME_PAD + STICKY_H // 2 + 40
        sticky_y_bewijs = sticky_y_vragen + STICKY_H + STICKY_GAP_Y

        for col, (norm, cid) in enumerate(clausule_lijst):
            cm = cm_9001 if norm == "9001" else cm_27001
            titel = cm.get(cid, {}).get("titel", cid)
            nt = normteksten.get(cid, {})
            bewijslast = nt.get("bewijslast", [])
            vragen = _vragen_voor_clausule(cid, norm, normteksten)

            sx = sticky_x_start + col * (STICKY_W + STICKY_GAP_X)

            # Sticky 1: vragen
            vragen_tekst = (
                f"<strong>[{norm}] {cid} — {titel}</strong>\n\n"
                + "\n".join(f"• {v}" for v in vragen)
            )
            _maak_sticky(board_id, vragen_tekst, sx, sticky_y_vragen, KLEUR_VRAGEN, droog)

            # Sticky 2: bewijslast
            bewijs_tekst = (
                f"<strong>Bewijslast {cid}</strong>\n\n"
                + "\n".join(f"☐ {b}" for b in bewijslast)
            ) if bewijslast else f"<strong>Bewijslast {cid}</strong>\n\n(geen specificatie beschikbaar)"
            _maak_sticky(board_id, bewijs_tekst, sx, sticky_y_bewijs, KLEUR_BEWIJS, droog)

            logger.info("  [%s] %s — %d vragen, %d bewijspunten", norm, cid, len(vragen), len(bewijslast))

    logger.info("Interview-frames klaar: https://miro.com/app/board/%s", board_id)


def main():
    parser = argparse.ArgumentParser(description="Interview-frames aanmaken op Miro")
    parser.add_argument("--droog", action="store_true", help="Dry-run — geen API-calls")
    parser.add_argument("--bord-id", default=None, help="Bestaand Miro bord-ID")
    args = parser.parse_args()

    if not args.bord_id and not args.droog:
        parser.error("Geef --bord-id op of gebruik --droog")

    board_id = args.bord_id or "dry-run"
    bouw_interview_frames(board_id=board_id, droog=args.droog)


if __name__ == "__main__":
    main()
