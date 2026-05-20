"""
Rooster-bord generator voor bi-weekly aanwezigheidsroosters.

Kopieert de structuur van het bronbord en past weeknummers + datums aan.

Gebruik:
  python -m sessions.rooster_builder --week1 16 --week2 17
  python -m sessions.rooster_builder --alle-2026
  python -m sessions.rooster_builder --week1 16 --week2 17 --droog
"""

import argparse
import json
import logging
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).parent / "content" / "rooster_template.json"
IMAGE_CACHE_DIR = Path(__file__).parent / "content" / "images"
MIRO_API = "https://api.miro.com/v2"

# x-positie tolerantie voor datumherkenning (px)
_POS_TOLERANCE = 60

# Verwachte x-posities van datumcellen op het bronbord
# Week A (linker rooster): Ma=30, Di=31, Wo=1, Do=2, Vr=3
# Week B (rechter rooster): Ma=6, Di=7, Wo=8, Do=9, Vr=10
_DATUM_POSITIE_A = [-152, 102, 356, 625, 861]   # Ma..Vr week A
_DATUM_POSITIE_B = [1260, 1524, 1777, 2029, 2281]  # Ma..Vr week B

# Bi-weekly sprints voor de rest van 2026 (week1, week2)
SPRINTS_2026 = [
    (16, 17), (18, 19), (20, 21), (22, 23), (24, 25),
    (26, 27), (28, 29), (30, 31), (32, 33), (34, 35),
    (36, 37), (38, 39), (40, 41), (42, 43), (44, 45),
    (46, 47), (48, 49), (50, 51),
]


# ── Miro API helpers ──────────────────────────────────────────────────────────

def _headers() -> dict:
    import os
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _post_multipart(endpoint: str, file_path: Path, fields: dict, droog: bool = False) -> dict:
    """Upload een bestand via multipart form-data."""
    if droog:
        return {"id": "dry-run"}
    import os
    token = os.environ.get("MIRO_API_TOKEN")
    hdrs = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    with file_path.open("rb") as f:
        files = {"resource": (file_path.name, f, "image/png")}
        resp = requests.post(f"{MIRO_API}{endpoint}", headers=hdrs, data=fields, files=files, timeout=60)
    if resp.status_code == 429:
        wacht = int(resp.headers.get("Retry-After", 5))
        time.sleep(wacht)
        return _post_multipart(endpoint, file_path, fields, droog)
    if not resp.ok:
        logger.error("Multipart fout %d %s: %s", resp.status_code, endpoint, resp.text[:200])
        resp.raise_for_status()
    time.sleep(0.12)
    return resp.json()


def _download_images(image_cdn: dict) -> None:
    """Download alle unieke images naar lokale cache."""
    IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for rid, cdn_url in image_cdn.items():
        pad = IMAGE_CACHE_DIR / f"{rid}.png"
        if pad.exists():
            continue
        resp = requests.get(cdn_url, timeout=30)
        if resp.ok:
            pad.write_bytes(resp.content)
            logger.debug("Image gecached: %s", rid)
        else:
            logger.warning("Image download mislukt (%d): %s", resp.status_code, rid)


def _post(endpoint: str, body: dict, droog: bool = False, _poging: int = 1) -> dict:
    if droog:
        return {"id": "dry-run"}
    resp = requests.post(f"{MIRO_API}{endpoint}", json=body, headers=_headers(), timeout=30)
    if resp.status_code == 429:
        wacht = int(resp.headers.get("Retry-After", 2 ** _poging))
        logger.warning("Rate limit (poging %d) — wacht %ds", _poging, wacht)
        time.sleep(wacht)
        return _post(endpoint, body, droog, _poging + 1)
    if not resp.ok:
        logger.error("POST fout %d %s: %s", resp.status_code, endpoint, resp.text[:200])
        resp.raise_for_status()
    time.sleep(0.12)
    return resp.json()


def _maak_bord(naam: str, droog: bool = False) -> str:
    logger.info("Nieuw bord aanmaken: %s", naam)
    result = _post("/boards", {"name": naam}, droog)
    board_id = result.get("id", "dry-run")
    logger.info("Bord id: %s", board_id)
    return board_id


# ── Datumhulpfuncties ─────────────────────────────────────────────────────────

def _maandag(jaar: int, week: int) -> date:
    return date.fromisocalendar(jaar, week, 1)


def _weekdagen(jaar: int, week: int) -> list[int]:
    """Geef de dag-nummers (1-31) voor Ma t/m Vr van de gegeven week."""
    ma = _maandag(jaar, week)
    return [(ma + timedelta(days=i)).day for i in range(5)]


# ── Variabele items detecteren ────────────────────────────────────────────────

def _is_week_titel(item: dict) -> str | None:
    """Geeft 'A' of 'B' als het item een weektitel is, anders None."""
    if item.get("type") != "text":
        return None
    content = re.sub(r"<[^>]+>", "", item.get("data", {}).get("content", "")).strip()
    if re.match(r"^Rooster Week \d+$", content):
        x = item.get("position", {}).get("x", 0)
        return "A" if x < 1000 else "B"
    return None


def _is_datum(item: dict) -> tuple[str, int] | None:
    """Geeft ('A'|'B', kolom 0-4) als het item een datumgetal is, anders None."""
    if item.get("type") != "text":
        return None
    content = re.sub(r"<[^>]+>", "", item.get("data", {}).get("content", "")).strip()
    if not re.match(r"^\d{1,2}$", content):
        return None
    x = item.get("position", {}).get("x", 0)
    for i, px in enumerate(_DATUM_POSITIE_A):
        if abs(x - px) < _POS_TOLERANCE:
            return ("A", i)
    for i, px in enumerate(_DATUM_POSITIE_B):
        if abs(x - px) < _POS_TOLERANCE:
            return ("B", i)
    return None


# ── Item aanmaken op nieuw bord ───────────────────────────────────────────────

def _maak_item(board_id: str, item: dict, image_cdn: dict, substitutie: dict, droog: bool) -> None:
    t = item.get("type")
    pos = item.get("position", {})
    geo = item.get("geometry", {})
    data = item.get("data", {})
    style = item.get("style", {})

    position = {"x": pos.get("x"), "y": pos.get("y"), "origin": "center"}
    geometry = {k: geo[k] for k in geo if geo[k] is not None}

    if t == "sticky_note":
        body = {
            "data": {"content": data.get("content", ""), "shape": data.get("shape", "square")},
            "style": style,
            "geometry": {"width": geometry.get("width", 200)},
            "position": position,
        }
        _post(f"/boards/{board_id}/sticky_notes", body, droog)

    elif t == "text":
        content = data.get("content", "")

        # Pas weeknummers aan
        label = substitutie.get("titel_" + (_is_week_titel(item) or ""))
        if label:
            content = f"<p>{label}</p>"

        # Pas datums aan
        datum_match = _is_datum(item)
        if datum_match:
            rooster, kolom = datum_match
            nieuw = substitutie.get(f"datum_{rooster}_{kolom}")
            if nieuw is not None:
                content = str(nieuw)

        body = {
            "data": {"content": content},
            "style": style,
            "geometry": geometry,
            "position": position,
        }
        _post(f"/boards/{board_id}/texts", body, droog)

    elif t == "shape":
        body = {
            "data": {"content": data.get("content", ""), "shape": data.get("shape", "rectangle")},
            "style": style,
            "geometry": geometry,
            "position": position,
        }
        _post(f"/boards/{board_id}/shapes", body, droog)

    elif t == "image":
        img_url = data.get("imageUrl", "")
        m = re.search(r"images/(\d+)", img_url)
        rid = m.group(1) if m else None
        if not rid:
            logger.warning("Geen resource-ID voor image %s — overgeslagen", item.get("id"))
            return
        pad = IMAGE_CACHE_DIR / f"{rid}.png"
        if not pad.exists():
            logger.warning("Image niet in cache: %s — overgeslagen", rid)
            return
        fields = {
            "position": json.dumps({"x": pos.get("x"), "y": pos.get("y"), "origin": "center"}),
            "geometry": json.dumps({"width": geometry.get("width")}),
        }
        _post_multipart(f"/boards/{board_id}/images", pad, fields, droog)

    elif t in ("embed", "preview"):
        logger.debug("Type '%s' overgeslagen (niet ondersteund)", t)


# ── Hoofd-builder ─────────────────────────────────────────────────────────────

def bouw_rooster(week1: int, week2: int, jaar: int = 2026, droog: bool = False) -> str:
    logger.info("Rooster aanmaken: Week %d/%d (%d)", week1, week2, jaar)

    template = json.loads(TEMPLATE_PATH.read_text())
    items = template["items"]
    image_cdn = template["image_cdn"]

    # Datums berekenen
    datums_a = _weekdagen(jaar, week1)
    datums_b = _weekdagen(jaar, week2)

    substitutie = {
        "titel_A": f"Rooster Week {week1}",
        "titel_B": f"Rooster Week {week2}",
    }
    for i, dag in enumerate(datums_a):
        substitutie[f"datum_A_{i}"] = dag
    for i, dag in enumerate(datums_b):
        substitutie[f"datum_B_{i}"] = dag

    logger.info(
        "Week %d: %s | Week %d: %s",
        week1, datums_a, week2, datums_b,
    )

    _download_images(image_cdn)

    board_naam = f"Rooster Week {week1}/{week2} {jaar}"
    board_id = _maak_bord(board_naam, droog)

    totaal = len(items)
    for i, item in enumerate(items):
        if (i + 1) % 50 == 0:
            logger.info("  %d/%d items...", i + 1, totaal)
        _maak_item(board_id, item, image_cdn, substitutie, droog)

    logger.info("Klaar: %s (id: %s)", board_naam, board_id)
    return board_id


def bouw_alle_2026(droog: bool = False) -> None:
    logger.info("Alle resterende 2026-sprints aanmaken (%d boards)", len(SPRINTS_2026))
    for week1, week2 in SPRINTS_2026:
        board_id = bouw_rooster(week1, week2, droog=droog)
        logger.info("  → %s", board_id)
    logger.info("Klaar — %d boards aangemaakt", len(SPRINTS_2026))


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Genereer een aanwezigheidsrooster op Miro")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--week1", type=int, help="Eerste weeknummer")
    group.add_argument("--alle-2026", action="store_true", help="Genereer alle resterende 2026-sprints")
    parser.add_argument("--week2", type=int, help="Tweede weeknummer (vereist met --week1)")
    parser.add_argument("--jaar", type=int, default=2026)
    parser.add_argument("--droog", action="store_true", help="Dry-run: geen API-calls")
    args = parser.parse_args()

    if args.alle_2026:
        bouw_alle_2026(droog=args.droog)
    else:
        if not args.week2:
            parser.error("--week1 vereist ook --week2")
        bouw_rooster(args.week1, args.week2, jaar=args.jaar, droog=args.droog)


if __name__ == "__main__":
    main()
