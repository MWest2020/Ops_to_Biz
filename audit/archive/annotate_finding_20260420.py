"""
Eenmalige remediation-script: markeer specifieke auditbevinding als "opgepakt".

Acties:
  1. Plaats een nieuwe sticky (groen) op het Miro-bord direct rechts van het
     bronitem — met uitleg wat er opgepakt is en hoe. Bestaand item wordt
     NIET aangepast (per memory-regel: Miro writes = altijd nieuw).
  2. Update de DB-row: classificatie NC → OFI, prepend "OPGEPAKT <datum>: ..."
     aan de beschrijving, zodat het auditrapport de resolutie toont.
  3. Rapport + tabular + HTML worden daarna apart geregenereerd.

Eenmalig uit te voeren voor DB-id 6018 (5.14 NC — "Discussie eindigt niet in
gecontroleerde testen"). Na uitvoering verplaatsen naar
`audit/archive/` volgens de patch-script-conventie.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 6018
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764658906182642"

RESOLUTIE_TEKST = (
    "✅ OPGEPAKT 2026-04-20\n\n"
    "Gecontroleerde test- en toepassingsketen is geïmplementeerd in de "
    "GitHub workflows van OpenRegister:\n"
    "• Main branch protection (pull-request-from-branch-check)\n"
    "• Staged releases (development → beta → release)\n"
    "• PR lint check\n\n"
    "Kanttekening (OFI): quality-gate, coverage-gate en PHP-tests zijn op dit "
    "moment uitgeschakeld (`if: false`). Reactiveren is gewenst."
)

RESOLUTIE_DB = (
    f"[OPGEPAKT 2026-04-20 via CI/CD workflows in ConductionNL/openregister: "
    f"branch protection + staged releases (dev→beta→release) + PR lint. "
    f"Openstaand (OFI): quality-gate, coverage-gate en PHP-tests staan "
    f"uitgeschakeld — reactiveren gewenst.] "
)


def _miro_token() -> str:
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return token


def _miro_positie(item_id: str) -> tuple[float, float]:
    """Haal (x, y) positie op van een bestaand Miro item."""
    resp = requests.get(
        f"https://api.miro.com/v2/boards/{MIRO_BOARD_ID}/items/{item_id}",
        headers={"Authorization": f"Bearer {_miro_token()}", "Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    pos = data.get("position", {})
    return float(pos.get("x", 0)), float(pos.get("y", 0))


def _update_db():
    pad = os.environ.get("AUDIT_DB_PATH", "output/audit.db")
    conn = sqlite3.connect(pad)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT classificatie, beschrijving FROM bevindingen WHERE id=?", (DB_ID,)).fetchone()
    if not row:
        raise RuntimeError(f"DB-row {DB_ID} niet gevonden")
    nieuwe_beschrijving = RESOLUTIE_DB + (row["beschrijving"] or "")
    conn.execute(
        "UPDATE bevindingen SET classificatie='OFI', beschrijving=? WHERE id=?",
        (nieuwe_beschrijving, DB_ID),
    )
    conn.commit()
    conn.close()
    print(f"[DB]  id={DB_ID} NC→OFI, resolutie-note toegevoegd")


def _plaats_miro_sticky():
    x, y = _miro_positie(MIRO_ITEM_ID)
    # Plaats rechts naast origineel (sticky is ~200 breed; +250 voor leesruimte)
    sticky_id = maak_sticky(
        MIRO_BOARD_ID,
        tekst=RESOLUTIE_TEKST,
        x=int(x + 250),
        y=int(y),
        kleur="light_green",
    )
    print(f"[Miro] nieuwe sticky geplaatst: id={sticky_id} naast {MIRO_ITEM_ID}")


def main():
    print(f"Resolutie voor bevinding {DB_ID} (5.14 NC) — datum: {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print()
    print("Klaar. Regenereer rapport apart om de resolutie in de output te tonen.")


if __name__ == "__main__":
    main()
