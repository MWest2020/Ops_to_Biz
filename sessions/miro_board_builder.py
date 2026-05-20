"""
Miro-bord generator voor kennissessies.

Leest een YAML-sessiedefinitie en genereert een Miro-bord met:
  - Horizontale tijdlijn bovenaan (intro + 1 stop per blok)
  - 4 frames in een 2×2 grid (één per blok)
  - Gekleurde stickies per item

Gebruik:
  python -m sessions.miro_board_builder --sessie claude_code_kennissessie
  python -m sessions.miro_board_builder --sessie claude_code_kennissessie --droog
  python -m sessions.miro_board_builder --sessie claude_code_kennissessie --bord-id <id>
"""

import argparse
import logging
import os
from pathlib import Path

import yaml

from sessions.miro_client import maak_bord, maak_frame, maak_sticky, reset_bord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Layout constanten (px)
TIJDLIJN_Y = -200          # y-positie van tijdlijn-stickies
TIJDLIJN_STICKY_W = 220
TIJDLIJN_STICKY_H = 80
TIJDLIJN_GAP_X = 260

FRAME_W = 2200
FRAME_H = 1800
FRAME_GAP_X = 250
FRAME_GAP_Y = 250
FRAME_START_Y = 200        # y-start van eerste rij frames (onder tijdlijn)

STICKY_W = 200
STICKY_GAP = 20
STICKY_COLS = 4
FRAME_PADDING = 80

# Standaard kleur per tijdlijn-stop
TIJDLIJN_KLEUR = "light_blue"


def _laad_sessie(naam: str) -> dict:
    pad = Path(__file__).parent / "content" / f"{naam}.yaml"
    if not pad.exists():
        raise FileNotFoundError(
            f"Sessie-YAML niet gevonden: {pad}\n"
            f"Beschikbare sessies: {[p.stem for p in (Path(__file__).parent / 'content').glob('*.yaml')]}"
        )
    with pad.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    verplicht = ["naam", "blokken"]
    for veld in verplicht:
        if veld not in data:
            raise ValueError(f"Verplicht veld ontbreekt in YAML: '{veld}'")
    return data


def _bouw_tijdlijn(board_id: str, sessie: dict, droog: bool) -> None:
    blokken = sessie["blokken"]
    stops = [{"label": "Intro", "kleur": TIJDLIJN_KLEUR}] + [
        {"label": f"{i+1}. {b['titel']}", "kleur": b.get("tijdlijn_kleur", TIJDLIJN_KLEUR)}
        for i, b in enumerate(blokken)
    ]
    totaal = len(stops)
    start_x = -(totaal - 1) * TIJDLIJN_GAP_X // 2

    logger.info("Tijdlijn aanmaken (%d stops)", totaal)
    for i, stop in enumerate(stops):
        x = start_x + i * TIJDLIJN_GAP_X
        maak_sticky(
            board_id,
            stop["label"],
            x=x,
            y=TIJDLIJN_Y,
            kleur=stop["kleur"],
            breedte=TIJDLIJN_STICKY_W,
            droog=droog,
        )


def _bouw_frames(board_id: str, sessie: dict, droog: bool) -> None:
    blokken = sessie["blokken"]
    kolommen = 2
    rijen = (len(blokken) + 1) // 2  # ceil(n/2)

    # Bereken startpunt zodat de grid gecentreerd staat
    grid_breedte = kolommen * FRAME_W + (kolommen - 1) * FRAME_GAP_X
    start_x = -(grid_breedte - FRAME_W) // 2

    for i, blok in enumerate(blokken):
        rij = i // kolommen
        kolom = i % kolommen
        x = start_x + kolom * (FRAME_W + FRAME_GAP_X)
        y = FRAME_START_Y + rij * (FRAME_H + FRAME_GAP_Y) + FRAME_H // 2

        duur = blok.get("duur_min", "")
        label = f"{blok['titel']} ({duur} min)" if duur else blok["titel"]
        logger.info("Frame %d: %s", i + 1, label)

        frame_id = maak_frame(
            board_id,
            titel=label,
            x=x + FRAME_W // 2,
            y=y,
            breedte=FRAME_W,
            hoogte=FRAME_H,
            droog=droog,
        )
        _vul_frame(board_id, frame_id, blok, x, y - FRAME_H // 2, droog)


def _vul_frame(
    board_id: str,
    frame_id: str,
    blok: dict,
    frame_x: int,
    frame_y: int,
    droog: bool,
) -> None:
    standaard_kleur = blok.get("standaard_kleur", "light_yellow")
    items = blok.get("items", [])

    sticky_x_start = frame_x + FRAME_PADDING + STICKY_W // 2
    sticky_y_start = frame_y + FRAME_PADDING + STICKY_W // 2  # stickies zijn vierkant

    for idx, item in enumerate(items):
        rij = idx // STICKY_COLS
        kolom = idx % STICKY_COLS
        x = sticky_x_start + kolom * (STICKY_W + STICKY_GAP)
        y = sticky_y_start + rij * (STICKY_W + STICKY_GAP)
        kleur = item.get("kleur", standaard_kleur)
        tekst = item.get("tekst", "")

        maak_sticky(board_id, tekst, x=x, y=y, kleur=kleur, breedte=STICKY_W, droog=droog)


def bouw_bord(
    sessie_naam: str,
    droog: bool = False,
    bord_id: str | None = None,
    reset: bool = False,
) -> str:
    sessie = _laad_sessie(sessie_naam)
    naam = sessie["naam"]

    if bord_id:
        logger.info("Gebruik bestaand bord: %s", bord_id)
        if reset:
            reset_bord(bord_id, droog)
    else:
        bord_id = maak_bord(naam, droog)

    _bouw_tijdlijn(bord_id, sessie, droog)
    _bouw_frames(bord_id, sessie, droog)

    if not droog:
        logger.info("Klaar — bord id: %s", bord_id)
    else:
        logger.info("Dry-run klaar — geen API-calls uitgevoerd")

    return bord_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Genereer een Miro-bord voor een kennissessie")
    parser.add_argument("--sessie", required=True, help="Naam van de sessie-YAML (zonder .yaml)")
    parser.add_argument("--droog", action="store_true", help="Dry-run: geen API-calls")
    parser.add_argument("--bord-id", dest="bord_id", help="Gebruik een bestaand Miro-bord")
    parser.add_argument("--reset", action="store_true", help="Verwijder alle items van het bord voor het opbouwen (vereist --bord-id)")
    args = parser.parse_args()

    if args.reset and not args.bord_id:
        parser.error("--reset vereist --bord-id")

    bouw_bord(args.sessie, droog=args.droog, bord_id=args.bord_id, reset=args.reset)


if __name__ == "__main__":
    main()
