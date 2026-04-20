"""
Audit ingest — Drive + Miro → lokale SQLite DB.

Geen LLM nodig. Slaat alle tekst op zodat je later in Claude Code
direct kunt zoeken en vragen kunt stellen zonder API-kosten.

Gebruik:
  python -m audit.ingest                  # Drive + Miro, beide normen
  python -m audit.ingest --only drive     # alleen Drive
  python -m audit.ingest --only miro      # alleen Miro
  python -m audit.ingest --norm 9001      # alleen 9001-clausules matchen
"""

import argparse
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def ingest_drive(norm: str) -> None:
    from audit.store import verbinding, initialiseer, upsert_document, upsert_clause_match, log_ingest
    from audit.drive_ingest import haal_documenten_op
    from audit.clause_mapping import laad_clause_map, koppel_documenten

    folder_id = os.environ.get("AUDIT_SOURCE_FOLDER_ID") or os.environ.get("AUDIT_DRIVE_FOLDER_ID")

    logger.info("=== Drive ingest gestart ===")
    documenten, handmatige_review = haal_documenten_op()

    logger.info("Clausule-mapping laden...")
    clause_map = laad_clause_map(norm)
    gekoppeld, niet_geclassificeerd = koppel_documenten(documenten, clause_map)

    conn = verbinding()
    initialiseer(conn)

    # Alle ingelezen documenten opslaan (ook zonder clausule-match)
    alle_docs = gekoppeld + niet_geclassificeerd
    for doc in alle_docs:
        upsert_document(conn, doc)
        for clausule_id in doc.get("clausules", []):
            upsert_clause_match(conn, doc["id"], "Drive", clausule_id, norm)
        for clausule_id, sub_punt_id in doc.get("sub_punt_matches", []):
            upsert_clause_match(conn, doc["id"], "Drive", clausule_id, norm, sub_punt_id)

    # Handmatige review items ook opslaan (zonder tekst)
    for item in handmatige_review:
        upsert_document(conn, {
            "id": item["id"],
            "naam": item["naam"],
            "tekst": f"[Handmatige review vereist: {item['reden']}]",
            "herkomst": "Drive",
            "mime_type": item.get("reden", ""),
        })

    conn.commit()
    log_ingest(conn, "drive", folder_id, len(alle_docs))
    conn.close()

    logger.info(
        "Drive ingest klaar: %d documenten opgeslagen (%d gekoppeld, %d zonder match, %d handmatige review)",
        len(alle_docs), len(gekoppeld), len(niet_geclassificeerd), len(handmatige_review),
    )


def ingest_miro(norm: str) -> None:
    from audit.store import verbinding, initialiseer, upsert_miro_note, upsert_clause_match, log_ingest
    from audit.miro_ingest import haal_notities_op, koppel_aan_clausules
    from audit.clause_mapping import laad_clause_map

    board_id = os.environ.get("MIRO_BOARD_ID")
    if not board_id:
        logger.warning("MIRO_BOARD_ID niet ingesteld — Miro overgeslagen.")
        return

    logger.info("=== Miro ingest gestart (board: %s) ===", board_id)

    clause_map = laad_clause_map(norm)
    notities_raw = haal_notities_op()
    notities = koppel_aan_clausules(notities_raw, clause_map)

    conn = verbinding()
    initialiseer(conn)

    for notitie in notities:
        notitie_met_board = {**notitie, "board_id": board_id}
        upsert_miro_note(conn, notitie_met_board)
        if notitie.get("clausule"):
            upsert_clause_match(conn, notitie["miro_item_id"], "Miro", notitie["clausule"], norm)

    conn.commit()
    log_ingest(conn, "miro", board_id, len(notities))
    conn.close()

    logger.info("Miro ingest klaar: %d notities opgeslagen", len(notities))


def main():
    parser = argparse.ArgumentParser(description="Audit ingest — Drive + Miro naar lokale DB")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
    )
    parser.add_argument(
        "--only",
        choices=["drive", "miro"],
        default=None,
        help="Alleen Drive of alleen Miro inlezen (default: beide)",
    )
    args = parser.parse_args()

    if args.only != "miro":
        ingest_drive(args.norm)
    if args.only != "drive":
        try:
            ingest_miro(args.norm)
        except Exception as e:
            logger.warning("Miro ingest mislukt (niet kritiek): %s", e)

    logger.info("=== Ingest klaar — DB: %s ===", os.environ.get("AUDIT_DB_PATH", "output/audit.db"))


if __name__ == "__main__":
    main()
