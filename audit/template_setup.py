"""
Taak 2: Audit report template aanmaken in Google Docs via gws CLI.

Werking:
1. Maakt een nieuw Google Docs-template aan met alle verplichte secties
2. Slaat het Doc-ID op — stel AUDIT_TEMPLATE_DOC_ID in .env in na eerste run
"""

import os
import yaml
from datetime import date

from audit.gws_client import _gws

TEMPLATE_STRUCTURE_FILE = os.path.join(
    os.path.dirname(__file__), "config", "report_template_structure.yaml"
)


def _load_structure() -> dict:
    with open(TEMPLATE_STRUCTURE_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _find_existing_report(folder_id: str) -> str | None:
    """Zoek een bestaand auditrapport in Drive als referentie (taak 2.1)."""
    result = _gws(
        "drive", "files", "list",
        params={
            "q": (
                f"'{folder_id}' in parents "
                "and mimeType='application/vnd.google-apps.document' "
                "and name contains 'Auditrapport' "
                "and trashed=false"
            ),
            "fields": "files(id, name)",
            "pageSize": 5,
        },
    )
    files = result.get("files", [])
    if files:
        print(f"Referentierapport gevonden: {files[0]['name']} ({files[0]['id']})")
        return files[0]["id"]
    return None


def _build_template_requests(structure: dict) -> list[dict]:
    full_text_parts = [
        f"AUDITRAPPORT\n"
        f"Template versie: {structure['versie']}  |  Norm(en): "
        f"{', '.join(structure['normen'])}  |  Aangemaakt: {date.today()}\n\n"
    ]
    for sectie in structure["secties"]:
        full_text_parts.append(f"{sectie['titel']}\n")
        if "omschrijving" in sectie:
            full_text_parts.append(f"{sectie['omschrijving']}\n")
        for ph in sectie.get("placeholders", []):
            full_text_parts.append(
                f"[{ph['naam']}]\n"
                f"{{{{  {ph['naam']}  }}}}\n\n"
            )
        full_text_parts.append("\n")

    return [{"insertText": {"location": {"index": 1}, "text": "".join(full_text_parts)}}]


def create_template(folder_id: str) -> str:
    """
    Maakt het auditrapport-template aan in Google Drive via gws CLI.
    Retourneert het Doc-ID van het nieuwe template.
    """
    structure = _load_structure()

    audit_folder = os.environ.get("AUDIT_DRIVE_FOLDER_ID", "")
    if audit_folder:
        ref = _find_existing_report(audit_folder)
        if ref:
            print(f"Tip: open het referentierapport ({ref}) in Drive om de structuur te vergelijken.")

    norm_label = "+".join(n.split(":")[0].replace(" ", "") for n in structure["normen"])
    doc_title = f"Auditrapport_Template_{norm_label}_v{structure['versie']}"

    # Nieuw Doc aanmaken via Drive (gws docs heeft geen create-commando)
    doc = _gws(
        "drive", "files", "create",
        body={"name": doc_title, "mimeType": "application/vnd.google-apps.document"},
    )
    doc_id = doc["id"]

    # Inhoud invullen
    requests = _build_template_requests(structure)
    _gws(
        "docs", "documents", "batchUpdate",
        params={"documentId": doc_id},
        body={"requests": requests},
    )

    # Verplaatsen naar de juiste Drive-map
    if folder_id:
        _gws(
            "drive", "files", "update",
            params={
                "fileId": doc_id,
                "addParents": folder_id,
                "removeParents": "root",
                "fields": "id,parents",
            },
            body={},
        )

    print(f"Template aangemaakt: {doc_title}")
    print(f"Doc-ID: {doc_id}")
    print(f"Stel in .env in: AUDIT_TEMPLATE_DOC_ID={doc_id}")
    return doc_id


def verify_placeholders(doc_id: str) -> list[str]:
    """Controleer of alle verwachte placeholders aanwezig zijn."""
    structure = _load_structure()
    doc = _gws("docs", "documents", "get", params={"documentId": doc_id})

    full_text = ""
    for elem in doc.get("body", {}).get("content", []):
        for item in elem.get("paragraph", {}).get("elements", []):
            full_text += item.get("textRun", {}).get("content", "")

    expected = [
        ph["naam"]
        for sectie in structure["secties"]
        for ph in sectie.get("placeholders", [])
    ]
    missing = [name for name in expected if f"{{{{{name}}}}}" not in full_text]

    if missing:
        print(f"Waarschuwing: {len(missing)} placeholder(s) ontbreken: {missing}")
    else:
        print("Alle placeholders aanwezig in template.")

    return missing
