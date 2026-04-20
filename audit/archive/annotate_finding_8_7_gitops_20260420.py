"""
Eenmalige remediation — 8.7 NC (Bedrijfscontinuïteit tegen malware).

Conduction's continuïteitsstrategie: GitOps met Git als desired-state. Herstel
na malware of ander incident = opnieuw uitrollen vanuit de gedeclareerde staat.
Dit is bestaande architectuur-aanpak (meerdere audits uitgelegd door Ruben);
GitOps-uitrol is op dit moment in operationalisatie-fase.

NC → OFI met expliciete strategie-beschrijving.
Conform conventie: na run → `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

import requests
from dotenv import load_dotenv

from audit.miro_board_setup import maak_sticky

load_dotenv()

DB_ID = 5949
MIRO_BOARD_ID = "uXjVJbKZEmw="
MIRO_ITEM_ID = "3458764635343575352"

STICKY_TEKST = (
    "✅ OPGEPAKT 2026-04-20 — Strategie-verduidelijking\n\n"
    "Bedrijfscontinuïteit is vormgegeven via GitOps: Git is de desired "
    "state. Herstel na malware of ander incident = opnieuw uitrollen "
    "vanuit de gedeclareerde staat. De rest (runtime, data-platforms) is "
    "providerverantwoordelijkheid.\n\n"
    "Dit is geen nieuwe maatregel — Ruben heeft deze architectuur-aanpak "
    "in meerdere audits toegelicht. GitOps-uitrol is momenteel in "
    "operationalisatie-fase.\n\n"
    "Classificatie: NC → OFI (implementatie in voortgang).\n\n"
    "OFI-actie: voltooiing GitOps-uitrol + documenteren van de herstel-"
    "procedure in het handboek zodat deze aantoonbaar audit-klaar is."
)

RESOLUTIE_DB = (
    "[OPGEPAKT 2026-04-20: continuïteitsstrategie is GitOps — Git als desired "
    "state, herstel = opnieuw uitrollen. Bestaande architectuur-aanpak (door "
    "Ruben in meerdere audits toegelicht), momenteel in operationalisatie-"
    "fase. NC → OFI (implementatie in voortgang). Actie: voltooien uitrol + "
    "documenteren herstelprocedure in handboek.] "
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
    print(f"Resolutie bevinding {DB_ID} (8.7 NC — BCM GitOps) — {date.today()}")
    print()
    _plaats_miro_sticky()
    _update_db()
    print("\nKlaar. Regenereer rapport apart.")


if __name__ == "__main__":
    main()
