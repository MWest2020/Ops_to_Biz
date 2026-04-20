"""
Taak 4: Google Drive-ingest — documenten ophalen en tekst extraheren via gws CLI.

Zoekt in de geconfigureerde Drive-map (AUDIT_SOURCE_FOLDER_ID) naar
procedures, werkinstructies en beleidsdocumenten. Verwerkt in batches van 20.
"""

import logging
import os

from audit.gws_client import gws_lijst_bestanden, gws_exporteer_google_doc, gws_download_bestand

logger = logging.getLogger(__name__)

BATCH_SIZE = 20

# Referentiedocumenten die geen organisatie-bewijs zijn — uitsluiten van classificatie
UITGESLOTEN_NAAM_PREFIXEN = (
    "NEN-EN-ISO",
    "ISO_IEC",
    "About the Sample Files",
)

ONDERSTEUNDE_MIME_TYPES = {
    "application/vnd.google-apps.document": "google_doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}
NIET_TEKSTUEEL = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/tiff",
    "application/vnd.google-apps.presentation",
}


def _verwerk_batch(batch: list[dict]) -> tuple[list[dict], list[dict]]:
    documenten = []
    handmatige_review = []

    for bestand in batch:
        naam = bestand["name"]
        file_id = bestand["id"]
        mime = bestand["mimeType"]

        if any(naam.startswith(p) for p in UITGESLOTEN_NAAM_PREFIXEN):
            logger.info("Uitgesloten (referentiedocument): %s", naam)
            continue

        if mime in NIET_TEKSTUEEL:
            handmatige_review.append({
                "naam": naam,
                "id": file_id,
                "reden": f"Niet-tekstueel formaat: {mime}",
                "herkomst": "Drive",
            })
            logger.info("Handmatige review vereist: %s (%s)", naam, mime)
            continue

        if mime not in ONDERSTEUNDE_MIME_TYPES:
            logger.debug("Onbekend mime-type overgeslagen: %s (%s)", naam, mime)
            continue

        try:
            if mime == "application/vnd.google-apps.document":
                tekst = gws_exporteer_google_doc(file_id)
            else:
                inhoud = gws_download_bestand(file_id)
                if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    import io
                    import docx
                    doc = docx.Document(io.BytesIO(inhoud))
                    tekst = "\n".join(p.text for p in doc.paragraphs)
                else:
                    tekst = inhoud.decode("utf-8", errors="replace")

            documenten.append({
                "naam": naam,
                "id": file_id,
                "mime_type": mime,
                "tekst": tekst,
                "herkomst": "Drive",
                "modified_at": bestand.get("modifiedTime"),
            })
            logger.debug("Ingelezen: %s", naam)

        except Exception as e:
            logger.warning("Fout bij inlezen %s: %s", naam, e)
            handmatige_review.append({
                "naam": naam,
                "id": file_id,
                "reden": f"Leesfout: {e}",
                "herkomst": "Drive",
            })

    return documenten, handmatige_review


def haal_documenten_op(folder_id: str | None = None) -> tuple[list[dict], list[dict]]:
    """
    Taken 4.1–4.4: Haal documenten op uit Drive-map en submappen via gws CLI.

    Retourneert:
      (documenten, handmatige_review)
    """
    folder_id = folder_id or os.environ.get("AUDIT_SOURCE_FOLDER_ID") \
        or os.environ.get("AUDIT_DRIVE_FOLDER_ID")

    if not folder_id:
        raise EnvironmentError(
            "Geen Drive-map geconfigureerd. "
            "Stel AUDIT_SOURCE_FOLDER_ID of AUDIT_DRIVE_FOLDER_ID in .env in."
        )

    # Strip eventuele URL-parameters (bv. ?hl=nl die uit Drive-URL gekopieerd zijn)
    folder_id = folder_id.split("?")[0].strip()

    # Shared Drive roots hebben een ID dat begint met "0A"
    drive_id = folder_id if folder_id.startswith("0A") else None

    logger.info("Drive-ingest gestart vanuit map %s (shared_drive=%s)", folder_id, bool(drive_id))
    alle_bestanden = gws_lijst_bestanden(folder_id, drive_id=drive_id)

    if not alle_bestanden:
        raise RuntimeError(
            f"Geen bestanden gevonden in Drive-map {folder_id}. "
            "Controleer de map-ID en gws-authenticatie (`gws auth login`)."
        )

    logger.info("Totaal gevonden: %d bestanden", len(alle_bestanden))

    alle_documenten: list[dict] = []
    alle_handmatige_review: list[dict] = []

    for i in range(0, len(alle_bestanden), BATCH_SIZE):
        batch = alle_bestanden[i: i + BATCH_SIZE]
        logger.info(
            "Verwerken batch %d/%d (%d bestanden)",
            i // BATCH_SIZE + 1,
            -(-len(alle_bestanden) // BATCH_SIZE),
            len(batch),
        )
        docs, review = _verwerk_batch(batch)
        alle_documenten.extend(docs)
        alle_handmatige_review.extend(review)

    logger.info(
        "Drive-ingest klaar: %d documenten ingelezen, %d voor handmatige review",
        len(alle_documenten),
        len(alle_handmatige_review),
    )
    return alle_documenten, alle_handmatige_review
