"""
Eenmalige remediation — 5.5 NC ("situationeel leiderschap").

Situationeel leiderschap is een AANBEVELING (best practice), geen ISO-eis.
Noch de norm (5.5 Contact met autoriteiten / Rollen) noch de interne
handboeken van Conduction stelt dit als verplichting. De organisatie
verkent actief betere manieren van leidinggeven — dit Miro-item is daar
een reflectie van, geen bewijs van een tekortkoming.

Degradeert NC → OFI met contextuele motivatie. Plaatst light-green sticky
op Miro. Conform conventie: na run → `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 7982
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764650588448879"

STICKY_TEKST = (
    "✅ OPGEPAKT 2026-04-20 — Scope-verduidelijking\n\n"
    "Situationeel leiderschap is een AANBEVELING (best practice), geen "
    "ISO-eis. Noch de norm (5.5) noch de handboeken van Conduction "
    "stellen dit als verplichting.\n\n"
    "De organisatie verkent actief betere manieren van leidinggeven; dit "
    "Miro-item reflecteert die exploratie. Geen bewijs van een "
    "tekortkoming in rollen/verantwoordelijkheden of autoriteitscontact.\n\n"
    "Classificatie: NC → OFI (ruimte voor verdere uitwerking)."
)

RESOLUTIE_DB = (
    "[OPGEPAKT 2026-04-20: situationeel leiderschap is een aanbeveling, geen "
    "ISO-eis. Noch norm noch Conduction-handboeken stellen dit verplicht. "
    "Organisatie verkent actief leiderschapsvormen — geen tekortkoming. "
    "NC → OFI.] "
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
    print(f"[DB]  id={DB_ID} NC→OFI, resolutie-note toegevoegd")


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
    print(f"Resolutie bevinding {DB_ID} (5.5 NC — situationeel leiderschap) — {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print()
    print("Klaar. Regenereer rapport apart.")


if __name__ == "__main__":
    main()
