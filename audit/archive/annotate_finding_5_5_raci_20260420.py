"""
Eenmalige remediation — 5.5 NC (RACI / CI-CD dev-branch).

Degradeert NC → OFI met contextuele motivatie: de uitval betrof de
development-branch ("een bouwput, geen gebouw in dienst"). Beta en stable
zijn nooit bedreigd. Breken door testen is verwacht gedrag in
development-omgevingen; rollen/verantwoordelijkheden voor beheerde
omgevingen (beta/stable) blijven gedefinieerd.

Plaatst nieuwe light-green sticky op Miro + DB-update.
Conform conventie: na run naar `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 6013
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764658905196416"

STICKY_TEKST = (
    "✅ OPGEPAKT 2026-04-20 — Scope-verduidelijking\n\n"
    "De CI/CD-uitval betrof uitsluitend de development-branch.\n\n"
    "Analogie: development is een bouwput — geen gebouw in dienst. "
    "Breken door testen is daar verwacht gedrag en geen ongecontroleerd "
    "risico op de bedrijfsvoering.\n\n"
    "Rollen & verantwoordelijkheden voor de beheerde omgevingen (beta en "
    "stable) zijn gedefinieerd en van kracht — deze zijn nooit bedreigd:\n"
    "• Main branch protection\n"
    "• Staged releases: development → beta → release\n"
    "• PR-review gates\n\n"
    "Classificatie voor 5.5 op dit item wijzigt van NC naar OFI: RACI voor "
    "specifiek development-branch experimenten kan aanvullend worden "
    "geëxpliciteerd, maar geen ISMS-risico voor beheerde omgevingen."
)

RESOLUTIE_DB = (
    "[OPGEPAKT 2026-04-20: scope-verduidelijking — de CI/CD-uitval betrof "
    "uitsluitend de development-branch (geen beheerde omgeving; vergelijkbaar "
    "met een bouwput). Beta en stable zijn nooit bedreigd dankzij main "
    "branch protection + staged releases. Rollen/verantwoordelijkheden voor "
    "beheerde omgevingen blijven gedefinieerd. RACI voor development-"
    "experimenten is OFI, geen NC.] "
)


def _miro_token() -> str:
    token = os.environ.get("MIRO_API_TOKEN")
    if not token:
        raise EnvironmentError("MIRO_API_TOKEN niet ingesteld in .env")
    return token


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
    print(f"Resolutie voor bevinding {DB_ID} (5.5 NC — RACI dev-branch) — datum: {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print()
    print("Klaar. Regenereer rapport apart om de resolutie in de output te tonen.")


if __name__ == "__main__":
    main()
