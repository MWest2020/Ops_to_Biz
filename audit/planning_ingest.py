"""
Auditplanning ingest — leest het auditplanning Spreadsheet (6 tabs) naar de lokale DB.

Tabs: 3 jaar × 2 normen (9001 + 27001), elk met clausules, eigenaren en datums.

Gebruik:
  python -m audit.planning_ingest
  python -m audit.planning_ingest --droog    # print wat er gevonden wordt
"""

import argparse
import logging
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PLANNING_SHEETS_ID = os.environ.get(
    "AUDIT_PLANNING_SHEETS_ID",
    "1BV2yajU7tQWU4dJPGc79V-mnH_-bQWCHKzhcU7XY37A"
)


def _initialiseer_planning_tabel(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_planning (
            clausule_id   TEXT NOT NULL,
            norm          TEXT NOT NULL,
            jaar          INTEGER,
            kwartaal      TEXT,
            eigenaar      TEXT,
            status        TEXT,   -- 'gepland' | 'uitgevoerd' | 'open'
            notitie       TEXT,
            bron_tab      TEXT,   -- naam van de Sheets-tab
            bijgewerkt_op TEXT NOT NULL,
            PRIMARY KEY (clausule_id, norm, jaar)
        )
    """)
    conn.commit()


MAANDEN = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]


def _norm_uit_tabnaam(tab_naam: str) -> str:
    naam_lower = tab_naam.lower()
    if "27001" in naam_lower:
        return "27001"
    if "9001" in naam_lower:
        return "9001"
    return "beide"


def _jaar_uit_tabnaam(tab_naam: str) -> int | None:
    # Neem het LAATSTE jaar in de naam — "9001:2015 2025" → 2025
    treffers = re.findall(r"20\d{2}", tab_naam)
    return int(treffers[-1]) if treffers else None


def _normaliseer_clausule(raw: str) -> str | None:
    """
    Normaliseert clausule-ID naar X.Y formaat.
    "4.4.1" → "4.4", "5.1.2" → "5.1", "4.1 Organisatiecontext" → "4.1"
    Geeft None terug als het geen geldig nummer is.
    """
    import re
    m = re.match(r"(\d+\.\d+)", str(raw).strip())
    return m.group(1) if m else None


def _detecteer_maandkolommen(rijen: list[list]) -> tuple[int, dict[int, str]]:
    """
    Zoekt de rij met maandnamen en geeft (rij_index, {col_index: maandnaam}) terug.
    Geeft (-1, {}) als er geen maandrij gevonden wordt.
    """
    for i, rij in enumerate(rijen):
        cellen = [str(c).strip().lower() for c in rij]
        if any(m in cellen for m in MAANDEN):
            maand_cols = {
                j: str(rij[j]).strip().lower()
                for j, c in enumerate(cellen)
                if c in MAANDEN
            }
            logger.debug("Maandrij gevonden op rij %d: %s", i, maand_cols)
            return i, maand_cols
    return -1, {}


def _verwerk_tab(conn, tab_naam: str, rijen: list[list], droog: bool) -> int:
    import re

    if not rijen or len(rijen) < 2:
        logger.info("Tab '%s': leeg of alleen header — overgeslagen", tab_naam)
        return 0

    norm = _norm_uit_tabnaam(tab_naam)
    jaar = _jaar_uit_tabnaam(tab_naam)

    # Zoek de maand-header rij en bouw kolom → maand mapping
    maand_rij_idx, maand_cols = _detecteer_maandkolommen(rijen)
    if not maand_cols:
        logger.warning("Tab '%s': geen maandkolommen gevonden — tab overgeslagen", tab_naam)
        return 0

    logger.info(
        "Tab '%s': norm=%s jaar=%s, maandkolommen=%s",
        tab_naam, norm, jaar, list(maand_cols.values())
    )

    nu = datetime.utcnow().isoformat()
    verwerkt = 0

    # Verwerk alle rijen NA de maand-header rij
    for rij in rijen[maand_rij_idx + 1:]:
        if not rij:
            continue

        def cel(idx):
            return str(rij[idx]).strip() if idx is not None and idx < len(rij) else ""

        # Clausule zit in kolom B (index 1)
        clausule_raw = cel(1)
        clausule_id = _normaliseer_clausule(clausule_raw)
        if not clausule_id:
            continue

        # Notitie/thema in kolom E (index 4)
        notitie = cel(4)

        # Maanden waar 'x' staat = geplande maanden
        gepland_maanden = [
            maand_cols[j]
            for j in maand_cols
            if j < len(rij) and str(rij[j]).strip().lower() == "x"
        ]
        kwartaal = ", ".join(gepland_maanden) if gepland_maanden else ""
        status = "gepland" if gepland_maanden else "open"
        eigenaar = ""  # auditplanning sheet heeft geen eigenaarkolom

        if droog:
            print(
                f"  [{tab_naam}] {clausule_id} | {norm} | {jaar} | "
                f"gepland={gepland_maanden} | {notitie[:40]}"
            )
        else:
            conn.execute("""
                INSERT INTO audit_planning
                    (clausule_id, norm, jaar, kwartaal, eigenaar, status, notitie, bron_tab, bijgewerkt_op)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(clausule_id, norm, jaar) DO UPDATE SET
                    kwartaal      = excluded.kwartaal,
                    eigenaar      = excluded.eigenaar,
                    status        = excluded.status,
                    notitie       = excluded.notitie,
                    bron_tab      = excluded.bron_tab,
                    bijgewerkt_op = excluded.bijgewerkt_op
            """, (clausule_id, norm, jaar, kwartaal, eigenaar, status, notitie, tab_naam, nu))

        verwerkt += 1

    if not droog:
        conn.commit()

    return verwerkt


def run(droog: bool = False) -> None:
    from audit.gsa_client import lees_alle_tabs
    from audit.store import verbinding, initialiseer

    conn = verbinding()
    initialiseer(conn)
    _initialiseer_planning_tabel(conn)

    logger.info("Auditplanning inlezen uit Sheets: %s", PLANNING_SHEETS_ID)
    tabs = lees_alle_tabs(PLANNING_SHEETS_ID)

    if not tabs:
        logger.error("Geen tabs gevonden — controleer auth en spreadsheet-ID")
        conn.close()
        return

    totaal = 0
    for tab_naam, rijen in tabs.items():
        n = _verwerk_tab(conn, tab_naam, rijen, droog)
        totaal += n
        logger.info("Tab '%s': %d planningregels verwerkt", tab_naam, n)

    conn.close()
    actie = "gevonden (dry-run)" if droog else "opgeslagen in DB"
    logger.info("Klaar: %d planningregels %s", totaal, actie)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Auditplanning inlezen uit Google Sheets")
    parser.add_argument("--droog", action="store_true", help="Dry-run — print regels, schrijf niets")
    args = parser.parse_args()
    run(droog=args.droog)


if __name__ == "__main__":
    main()
