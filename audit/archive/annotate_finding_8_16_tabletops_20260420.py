"""
Eenmalige remediation — 8.16 NC (Tabletops monitoring-oefeningen).

Tabletops voor monitoring-incidenten zijn NIET voorgeschreven door norm
of handboeken. Daarom geen NC; wel een sterke aanbeveling om deze praktijk
in te voeren omdat het monitoring-effectiviteit aantoonbaar maakt.

NC → OFI met nadrukkelijke aanbeveling-formulering.
Conform conventie: na run → `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 5948
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764635343457821"

STICKY_TEKST = (
    "⚠️ AANBEVELING 2026-04-20 — Scope-verduidelijking\n\n"
    "Tabletops voor monitoring-incidenten zijn NIET voorgeschreven door de "
    "ISO-norm of de interne handboeken van Conduction. Het ontbreken is "
    "daarmee geen non-conformiteit.\n\n"
    "Wél een STRAKKE AANBEVELING:\n"
    "Voer tabletops periodiek uit om monitoring-effectiviteit, override-"
    "beleid en incident-response-paden aantoonbaar te toetsen. Ontwikkelt "
    "zich in deze organisatie tot best-practice — opnemen in MT-planning."
)

RESOLUTIE_DB = (
    "[OPGEPAKT 2026-04-20: tabletops zijn niet voorgeschreven door norm of "
    "Conduction-handboeken — geen NC. Wel STRAKKE AANBEVELING (OFI): "
    "tabletops inplannen om monitoring-effectiviteit en incident-response "
    "aantoonbaar te toetsen. Opnemen in MT-planning.] "
)


def _miro_token() -> str:
    t = os.environ.get("MIRO_API_TOKEN")
    if not t:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return t


def _miro_positie(item_id: str) -> tuple[float, float]:
    resp = requests.get(
        f"https://api.miro.com/v2/boards/{MIRO_BOARD_ID}/items/{item_id}",
        headers={"Authorization": f"Bearer {_miro_token()}", "Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    pos = resp.json().get("position", {})
    return float(pos.get("x", 0)), float(pos.get("y", 0))


def _update_db():
    pad = os.environ.get("AUDIT_DB_PATH", "output/audit.db")
    conn = sqlite3.connect(pad)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT classificatie, beschrijving FROM bevindingen WHERE id=?", (DB_ID,)).fetchone()
    if not row:
        raise RuntimeError(f"DB-row {DB_ID} niet gevonden")
    nieuwe = RESOLUTIE_DB + (row["beschrijving"] or "")
    conn.execute(
        "UPDATE bevindingen SET classificatie='OFI', beschrijving=? WHERE id=?",
        (nieuwe, DB_ID),
    )
    conn.commit()
    conn.close()
    print(f"[DB]  id={DB_ID} NC→OFI (aanbeveling), resolutie-note toegevoegd")


def _plaats_miro_sticky():
    x, y = _miro_positie(MIRO_ITEM_ID)
    sticky_id = maak_sticky(
        MIRO_BOARD_ID,
        tekst=STICKY_TEKST,
        x=int(x + 250),
        y=int(y),
        kleur="light_yellow",  # geel = aandacht/aanbeveling, niet groen (niet afgedaan)
    )
    print(f"[Miro] nieuwe sticky geplaatst: id={sticky_id} naast {MIRO_ITEM_ID}")


def main():
    print(f"Resolutie bevinding {DB_ID} (8.16 NC — Tabletops) — {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print("\nKlaar. Regenereer rapport apart.")


if __name__ == "__main__":
    main()
