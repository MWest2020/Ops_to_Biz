"""
Taak 8: Google Slides executive summary aanmaken via gws CLI.

5 verplichte slides:
  1. Titelpagina
  2. Auditscope & doel
  3. Resultaatoverzicht
  4. Top-3 bevindingen
  5. Aanbevolen actiepunten

Alleen uitgevoerd als AUDIT_TEMPLATE_DOC_ID geconfigureerd is.
"""

import logging
import os
from datetime import date

from audit.gws_client import _gws

logger = logging.getLogger(__name__)


def _top3_bevindingen(bevindingen: list[dict]) -> list[dict]:
    nc_items = [b for b in bevindingen if b["classificatie"] == "NC"]
    ofi_items = [b for b in bevindingen if b["classificatie"] == "OFI"]
    return (nc_items + ofi_items)[:3]


def _slide_requests(bevindingen: list[dict], norm: str) -> list[dict]:
    nc_count = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi_count = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    pos_count = sum(1 for b in bevindingen if b["classificatie"] == "positief")
    top3 = _top3_bevindingen(bevindingen)

    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)

    slide_inhoud = [
        {
            "titel": f"Auditrapport\n{norm_label}",
            "body": f"Datum: {date.today()}\nInterne audit — Vertrouwelijk",
        },
        {
            "titel": "Auditscope & Doel",
            "body": (
                f"Norm: {norm_label}\n"
                "Doel: Beoordeling van conformiteit met de norm-eisen\n"
                "Scope: Procedures, werkinstructies en beleidsdocumenten"
            ),
        },
        {
            "titel": "Resultaatoverzicht",
            "body": (
                f"Non-conformiteiten (NC): {nc_count}\n"
                f"Kansen voor verbetering (OFI): {ofi_count}\n"
                f"Positieve bevindingen: {pos_count}\n\n"
                f"Totaal beoordeeld: {len(bevindingen)} bevindingen"
            ),
        },
        {
            "titel": "Top-3 Bevindingen",
            "body": "\n\n".join(
                f"{i+1}. [{b['classificatie']}] Clausule {b['clausule']}\n"
                f"   {b['beschrijving'][:150]}"
                for i, b in enumerate(top3)
            ) or "Geen kritieke bevindingen.",
        },
        {
            "titel": "Aanbevolen Actiepunten",
            "body": "\n".join(
                f"{i+1}. Clausule {b['clausule']}: {b['beschrijving'][:120]}"
                for i, b in enumerate(top3)
            ) or "Geen openstaande actiepunten.",
        },
    ]

    requests: list[dict] = []
    slide_ids = [f"slide_{i+1}" for i in range(5)]

    requests.append({"deleteObject": {"objectId": "p"}})

    for idx, (slide_id, inhoud) in enumerate(zip(slide_ids, slide_inhoud)):
        titel_id = f"{slide_id}_title"
        body_id = f"{slide_id}_body"

        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": idx,
                "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
            }
        })
        requests += [
            {
                "createShape": {
                    "objectId": titel_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 6000000, "unit": "EMU"},
                            "height": {"magnitude": 1000000, "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1, "scaleY": 1,
                            "translateX": 457200, "translateY": 274638,
                            "unit": "EMU",
                        },
                    },
                }
            },
            {"insertText": {"objectId": titel_id, "text": inhoud["titel"]}},
            {
                "createShape": {
                    "objectId": body_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 6000000, "unit": "EMU"},
                            "height": {"magnitude": 3500000, "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1, "scaleY": 1,
                            "translateX": 457200, "translateY": 1600000,
                            "unit": "EMU",
                        },
                    },
                }
            },
            {"insertText": {"objectId": body_id, "text": inhoud["body"]}},
        ]

    return requests


def genereer_slides(
    bevindingen: list[dict],
    norm: str,
    folder_id: str | None = None,
) -> str:
    """
    Taken 8.1–8.3: Maak Google Slides presentatie aan via gws CLI.
    Retourneert het presentatie-ID.
    """
    folder_id = folder_id or os.environ.get("AUDIT_DRIVE_FOLDER_ID")
    norm_labels = {"9001": "ISO9001", "27001": "ISO27001", "beide": "ISO9001-27001"}
    bestandsnaam = f"AuditSummary_{norm_labels.get(norm, norm)}_{date.today()}"

    presentatie = _gws("slides", "presentations", "create", body={"title": bestandsnaam})
    presentatie_id = presentatie["presentationId"]

    requests = _slide_requests(bevindingen, norm)
    if requests:
        _gws(
            "slides", "presentations", "batchUpdate",
            params={"presentationId": presentatie_id},
            body={"requests": requests},
        )

    if folder_id:
        _gws(
            "drive", "files", "update",
            params={
                "fileId": presentatie_id,
                "addParents": folder_id,
                "removeParents": "root",
                "fields": "id,parents",
            },
            body={},
        )

    logger.info("Slides aangemaakt: %s (ID: %s)", bestandsnaam, presentatie_id)
    return presentatie_id
