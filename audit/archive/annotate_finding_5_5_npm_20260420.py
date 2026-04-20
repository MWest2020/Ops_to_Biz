"""
Eenmalige remediation — 5.5 NC (NPM/Vue3-afhankelijkheden).

Opgelost: geautomatiseerde flows + AI — één call van ~4.5 uur elimineert
ALLE criticals en highs uit de NPM-dependency audit. Daarmee is het
dependency-managementproces aantoonbaar operationeel; classificatie
wijzigt naar **positief**.

Plaatst light-green Miro-sticky + DB-update (NC → positief).
Conform conventie: na run → `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 7988
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764658906323363"

STICKY_TEKST = (
    "✅ OPGELOST 2026-04-20 — POSITIEF\n\n"
    "Dependency-audit is geautomatiseerd via AI-ondersteunde flow:\n"
    "één call van ~4.5 uur elimineert ALLE criticals en highs uit de "
    "NPM/Vue3-dependency scan.\n\n"
    "Dit toont een werkend en schaalbaar proces voor kwetsbaarheids-"
    "beheer op third-party dependencies. Geen NC — sterke positieve "
    "bevinding."
)

RESOLUTIE_DB = (
    "[OPGELOST 2026-04-20: AI-ondersteunde flow elimineert in één call "
    "(~4.5 uur) ALLE criticals en highs uit de NPM/Vue3-dependency audit. "
    "Werkend schaalbaar proces voor kwetsbaarheidsbeheer. NC → positief.] "
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
        "UPDATE bevindingen SET classificatie='positief', beschrijving=? WHERE id=?",
        (nieuwe, DB_ID),
    )
    conn.commit()
    conn.close()
    print(f"[DB]  id={DB_ID} NC→positief, resolutie-note toegevoegd")


def _plaats_miro_sticky():
    x, y = _miro_positie(MIRO_ITEM_ID)
    sticky_id = maak_sticky(
        MIRO_BOARD_ID,
        tekst=STICKY_TEKST,
        x=int(x + 250),
        y=int(y),
        kleur="light_green",
    )
    print(f"[Miro] nieuwe sticky geplaatst: id={sticky_id} naast {MIRO_ITEM_ID}")


def main():
    print(f"Resolutie bevinding {DB_ID} (5.5 NC — NPM dependencies) — {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print("\nKlaar. Regenereer rapport apart.")


if __name__ == "__main__":
    main()
