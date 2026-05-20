"""
Miro API client voor de sessions-module.

Basisoperaties: bord aanmaken, frame aanmaken, sticky aanmaken.
Ondersteunt dry-run modus en exponentiële backoff bij rate limiting.
"""

import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MIRO_API = "https://api.miro.com/v2"
_MAX_RETRIES = 3


def _headers() -> dict:
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _post(endpoint: str, body: dict, droog: bool = False, _poging: int = 1) -> dict:
    if droog:
        logger.info("DRY-RUN POST %s — velden: %s", endpoint, list(body.keys()))
        return {"id": "dry-run"}

    resp = requests.post(
        f"{MIRO_API}{endpoint}", json=body, headers=_headers(), timeout=30
    )

    if resp.status_code == 429:
        if _poging > _MAX_RETRIES:
            logger.error("Rate limit bereikt na %d pogingen — stopt", _MAX_RETRIES)
            resp.raise_for_status()
        wacht = int(resp.headers.get("Retry-After", 2 ** _poging))
        logger.warning("Rate limit (poging %d/%d) — wacht %ds", _poging, _MAX_RETRIES, wacht)
        time.sleep(wacht)
        return _post(endpoint, body, droog, _poging + 1)

    if not resp.ok:
        logger.error("Miro API fout %d: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()

    time.sleep(0.15)
    return resp.json()


def _get(endpoint: str, params: dict | None = None) -> dict:
    resp = requests.get(
        f"{MIRO_API}{endpoint}", params=params, headers=_headers(), timeout=30
    )
    if not resp.ok:
        logger.error("Miro API fout %d: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
    return resp.json()


def _delete(endpoint: str, droog: bool = False) -> None:
    if droog:
        logger.info("DRY-RUN DELETE %s", endpoint)
        return
    resp = requests.delete(f"{MIRO_API}{endpoint}", headers=_headers(), timeout=30)
    if resp.status_code == 429:
        wacht = int(resp.headers.get("Retry-After", 5))
        logger.warning("Rate limit bij delete — wacht %ds", wacht)
        time.sleep(wacht)
        _delete(endpoint, droog)
        return
    if not resp.ok and resp.status_code != 404:
        logger.error("Delete fout %d: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
    time.sleep(0.1)


def reset_bord(board_id: str, droog: bool = False) -> None:
    """Verwijder alle items van het bord (frames, stickies, shapes, tekst, etc.)."""
    logger.info("Bord resetten: %s", board_id)
    cursor = None
    totaal = 0

    while True:
        params = {"limit": 50}
        if cursor:
            params["cursor"] = cursor
        data = _get(f"/boards/{board_id}/items", params)
        items = data.get("data", [])
        for item in items:
            _delete(f"/boards/{board_id}/items/{item['id']}", droog)
            totaal += 1

        cursor = data.get("cursor")
        if not cursor or not items:
            break

    logger.info("Reset klaar — %d items verwijderd", totaal)


def maak_bord(naam: str, droog: bool = False) -> str:
    logger.info("Bord aanmaken: %s", naam)
    body = {
        "name": naam,
        "description": "Gegenereerd door sessions pipeline",
        "sharingPolicy": {
            "access": "edit",
            "teamAccess": "edit",
        },
    }
    result = _post("/boards", body, droog)
    board_id = result.get("id", "dry-run")
    logger.info("Bord aangemaakt: %s (id: %s)", naam, board_id)
    return board_id


def maak_frame(
    board_id: str,
    titel: str,
    x: int,
    y: int,
    breedte: int,
    hoogte: int,
    droog: bool = False,
) -> str:
    logger.info("  Frame: %s @ (%d, %d)", titel, x, y)
    body = {
        "data": {"title": titel, "format": "custom", "showContent": True},
        "style": {"fillColor": "#f5f5f5"},
        "geometry": {"width": breedte, "height": hoogte},
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
    breedte: int = 200,
    droog: bool = False,
) -> str:
    logger.debug("    Sticky '%s…' kleur=%s @ (%d, %d)", tekst[:30], kleur, x, y)
    body = {
        "data": {"content": tekst, "shape": "square"},
        "style": {"fillColor": kleur, "textAlign": "left", "textAlignVertical": "top"},
        "geometry": {"width": breedte},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = _post(f"/boards/{board_id}/sticky_notes", body, droog)
    return result.get("id", "dry-run")
