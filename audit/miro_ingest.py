"""
Taak 3: Miro-ingest — sticky notes en tekstvakken ophalen als audit-input.

Kleurconventie (organisatiestandaard):
  groen  → positief / conform
  oranje → NC (non-conformiteit)
  rood   → NC (non-conformiteit)
  overig → geen pre-classificatie

Board-ID: configureerbaar via MIRO_BOARD_ID (.env)
"""

import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

MIRO_API_BASE = "https://api.miro.com/v2"

# Miro kleur hex-codes → classificatie
KLEUR_CLASSIFICATIE: dict[str, str] = {
    # Groen-tinten
    "#d5e8d4": "positief",
    "#82b366": "positief",
    "#00cc00": "positief",
    "light_green": "positief",
    "green": "positief",
    # Oranje-tinten
    "#ffe6cc": "NC",
    "#f0a30a": "NC",
    "#d79b00": "NC",
    "yellow": "NC",   # Miro gebruikt soms geel/oranje door elkaar
    "orange": "NC",
    # Rood-tinten
    "#f8cecc": "NC",
    "#b85450": "NC",
    "#ff0000": "NC",
    "red": "NC",
    "light_red": "NC",
    "dark_red": "NC",
}


def _get_headers() -> dict:
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _kleur_naar_classificatie(kleur: str | None) -> str | None:
    if not kleur:
        return None
    kleur_lower = kleur.lower().strip()
    return KLEUR_CLASSIFICATIE.get(kleur_lower) or KLEUR_CLASSIFICATIE.get(
        kleur.strip()
    )


def _haal_items_op(board_id: str, item_type: str) -> list[dict]:
    """Pagineer door alle items van een bepaald type op een bord."""
    items = []
    cursor = None
    headers = _get_headers()

    while True:
        params = {"limit": 50, "type": item_type}
        if cursor:
            params["cursor"] = cursor

        url = f"{MIRO_API_BASE}/boards/{board_id}/items"
        resp = requests.get(url, headers=headers, params=params, timeout=30)

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 5))
            logger.warning("Miro rate limit — wacht %ds", wait)
            time.sleep(wait)
            continue

        resp.raise_for_status()
        data = resp.json()
        items.extend(data.get("data", []))

        cursor = data.get("cursor")
        if not cursor:
            break

    return items


def _tekst_uit_item(item: dict) -> str:
    """Extraheer platte tekst uit een Miro-item."""
    content = item.get("data", {})
    # sticky_note en text widgets
    tekst = content.get("content", "") or content.get("text", "")
    # Strip basis HTML-tags die Miro soms meestuurt
    import re
    return re.sub(r"<[^>]+>", "", tekst).strip()


def haal_notities_op(board_id: str | None = None) -> list[dict]:
    """
    Taak 3.1: Haal alle sticky notes en tekstvakken op uit het Miro-bord.

    Retourneert een lijst van dicts:
      {
        "tekst": str,
        "pre_classificatie": str | None,  # "NC" / "positief" / None
        "herkomst": "Miro",
        "miro_item_id": str,
        "kleur": str | None,
      }
    """
    board_id = board_id or os.environ.get("MIRO_BOARD_ID")
    if not board_id:
        raise EnvironmentError("MIRO_BOARD_ID niet ingesteld in .env")

    logger.info("Miro-ingest gestart voor bord %s", board_id)

    sticky_notes = _haal_items_op(board_id, "sticky_note")
    text_items = _haal_items_op(board_id, "text")

    notities = []
    for item in sticky_notes + text_items:
        tekst = _tekst_uit_item(item)
        if not tekst:
            continue

        kleur = (
            item.get("style", {}).get("fillColor")
            or item.get("data", {}).get("backgroundColor")
        )
        pre_class = _kleur_naar_classificatie(kleur)

        notities.append({
            "tekst": tekst,
            "pre_classificatie": pre_class,
            "herkomst": "Miro",
            "miro_item_id": item.get("id"),
            "kleur": kleur,
        })

    logger.info("Miro-ingest: %d notities opgehaald", len(notities))
    return notities


def koppel_aan_clausules(notities: list[dict], clause_map: dict) -> list[dict]:
    """
    Taak 3.2: Koppel notities aan norm-clausules via tekstanalyse (best-effort).
    Taak 3.3: Pre-classificatie via kleur is al gedaan in haal_notities_op().

    Voegt 'clausule' toe aan elke notitie; None als geen match gevonden.
    """
    clausules = clause_map.get("clausules", {})

    for notitie in notities:
        tekst_lower = notitie["tekst"].lower()
        gevonden = None

        for clausule_id, data in clausules.items():
            zoektermen = data.get("zoektermen", [])
            if any(term.lower() in tekst_lower for term in zoektermen):
                gevonden = clausule_id
                break

        notitie["clausule"] = gevonden

        if gevonden is None:
            logger.debug(
                "Miro-notitie zonder clausule-match: '%s...'",
                notitie["tekst"][:60],
            )

    return notities


def merge_met_drive_bevindingen(
    miro_notities: list[dict], drive_bevindingen: list[dict]
) -> list[dict]:
    """
    Taak 3.4: Combineer Miro-notities en Drive-bevindingen tot één lijst.
    Elke entry heeft een 'herkomst'-label: 'Miro' of 'Drive'.
    """
    return drive_bevindingen + miro_notities
