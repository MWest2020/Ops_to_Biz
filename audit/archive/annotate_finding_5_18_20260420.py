"""
Eenmalige remediation — bevinding 5.18 NC (RBAC op logging).

Plaatst een nieuwe light-green sticky op Miro met het ingediende voorstel
(risicogestuurd logging-beleid, PDCA plan gedeeld), en degradeert de
DB-row van NC → OFI met een resolutie-note.

Conform project-conventie: na run verplaatsen naar `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 5947
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764635343364266"

STICKY_TEKST = (
    "✅ OPGEPAKT 2026-04-20 — Voorstel (ter vaststelling MT)\n\n"
    "Conduction legt security-relevante gebeurtenissen vast voor alle "
    "beheerde omgevingen. Scope + inrichting zijn risicogestuurd en "
    "proportioneel aan aard en omvang van de organisatie.\n\n"
    "Applicatieniveau (minimaal):\n"
    "• authenticatie-events\n"
    "• toegang tot gevoelige data\n"
    "• applicatiefouten\n"
    "Toegang tot logbestanden: rol-gebaseerd.\n\n"
    "Infrastructuur (DB / cluster):\n"
    "• voorbehouden aan beperkt aantal geautoriseerde beheerders\n"
    "• persoonsgebonden credentials\n\n"
    "Componenten ontwikkeld door Conduction beschikken over eigen logging; "
    "proactief beschikbaar gesteld aan klanten als onderdeel van de dienst.\n\n"
    "Aanvullend: Google Workspace auditlogs (organisatie-brede auth/beheer-"
    "events) — toegang beperkt tot MT.\n\n"
    "Scope + retentie: jaarlijks herijken door MT.\n\n"
    "Indien nodig: PDCA-plan gedeeld."
)

RESOLUTIE_DB = (
    "[OPGEPAKT 2026-04-20: scope RBAC op logging ter discussie — voorstel "
    "ingediend (risicogestuurd, proportioneel): applicatie-events + "
    "rolgebaseerde logtoegang; infra-toegang beperkt + persoonsgebonden "
    "credentials; GWS auditlogs op MT-niveau; jaarlijks herijken. "
    "PDCA-plan beschikbaar. Zie Miro-sticky naast originele bevinding.] "
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
    print(f"Resolutie voor bevinding {DB_ID} (5.18 NC — RBAC logging) — datum: {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print()
    print("Klaar. Regenereer rapport apart om de resolutie in de output te tonen.")


if __name__ == "__main__":
    main()
