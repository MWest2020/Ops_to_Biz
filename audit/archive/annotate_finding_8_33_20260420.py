"""
Eenmalige remediation — 8.33 NC (VNG testdata-incident).

Drive-bevinding: geen Miro-sticky, alleen DB-update.

Context: het memo "Incident mail 15-08-2025/ geen incident" IS het proactief
opgestelde sluitingsbewijs. VNG leverde testdata met productie-e-mailadressen;
Conduction heeft dit gedetecteerd, gedocumenteerd én afgehandeld — precies
wat de NC-procedure voorschrijft. Dit is een sterke positieve bevinding, geen NC.

NC → positief.
Conform conventie: na run → `audit/archive/`.
"""

import os
import sqlite3
from datetime import date

from dotenv import load_dotenv

load_dotenv()

DB_ID = 5599

RESOLUTIE_DB = (
    "[OPGELOST 2026-04-20: dit memo ('Incident mail 15-08-2025/geen incident') "
    "IS het proactief opgestelde sluitingsbewijs. Conduction detecteerde dat "
    "VNG productiegegevens als testdata leverde, documenteerde het incident "
    "proactief en handelde het af. Dit toont aantoonbaar dat de NC-procedure "
    "werkt en dat test/productie-scheiding op eigen scope gecontroleerd is. "
    "NC → positief.] "
)


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


def main():
    print(f"Resolutie bevinding {DB_ID} (8.33 NC — VNG testdata) — {date.today()}")
    print()
    _update_db()
    print("\nGeen Miro-sticky (Drive-bevinding). Regenereer rapport apart.")


if __name__ == "__main__":
    main()
