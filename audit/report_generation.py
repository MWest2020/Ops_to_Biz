"""
Taak 7: Rapportgeneratie — template kopiëren en vullen in Google Docs via gws CLI.

Genereert het volledige auditrapport op basis van bevestigde bevindingen.
Alleen uitgevoerd als AUDIT_TEMPLATE_DOC_ID geconfigureerd is.
"""

import logging
import os
import re
from collections import defaultdict
from datetime import date

import anthropic

from audit.gws_client import _gws

logger = logging.getLogger(__name__)

VOLGORDE = {"NC": 0, "OFI": 1, "positief": 2}
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


_MANAGEMENT_CONTEXT = """\
Organisatiecontext Conduction:
- Nederlands softwarebedrijf (open-source, publieke sector).
- BYOD: laptops eigendom medewerker. Formele activa-retournering (5.11/6.5)
  beperkt tot klein materiaal; data/toegangsrevocatie is het relevante punt.
- Interne documenten zijn vertrouwelijkheid-geindexeerd in de handleidingen
  (5.12 intern = positief). NC op 5.12 betreft uitsluitend externe
  documenten/communicatie.
- Afwijkingsprocedure is gedocumenteerd via memo's (10.2/8.7 vaak positief).
"""


def _management_summary_prompt(bevindingen: list[dict]) -> str:
    from collections import Counter

    nc_count = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi_count = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    pos_count = sum(1 for b in bevindingen if b["classificatie"] == "positief")

    # Top-N NC-clusters per clausule (niet sample-based)
    nc_per_clausule = Counter(b["clausule"] for b in bevindingen if b["classificatie"] == "NC")
    ofi_per_clausule = Counter(b["clausule"] for b in bevindingen if b["classificatie"] == "OFI")
    pos_per_clausule = Counter(b["clausule"] for b in bevindingen if b["classificatie"] == "positief")

    def _format_top(teller, n=8):
        regels = []
        for clausule, aantal in teller.most_common(n):
            # Voorbeeld-beschrijving (eerste NC/OFI van die clausule) als context
            voorbeeld = next(
                (b["beschrijving"][:150] for b in bevindingen
                 if b["clausule"] == clausule and b["classificatie"] in ("NC", "OFI")),
                "",
            )
            regels.append(f"- {clausule} ({aantal}×): {voorbeeld}")
        return "\n".join(regels) if regels else "(geen)"

    top_nc_tekst = _format_top(nc_per_clausule, n=8)
    top_ofi_tekst = _format_top(ofi_per_clausule, n=5)
    top_pos_tekst = _format_top(pos_per_clausule, n=5)

    return (
        f"Schrijf een Nederlandstalige management summary (max 350 woorden) "
        f"voor een ISO 9001/27001 auditrapport. Blijf feitelijk en gebruik "
        f"UITSLUITEND de onderstaande data — verzin geen aantallen of clusters.\n\n"
        f"{_MANAGEMENT_CONTEXT}\n"
        f"Resultaatoverzicht:\n"
        f"- Non-conformiteiten (NC): {nc_count}\n"
        f"- Kansen voor verbetering (OFI): {ofi_count}\n"
        f"- Positieve bevindingen: {pos_count}\n\n"
        f"NC-clusters per clausule (aantal bevindingen met voorbeeld):\n{top_nc_tekst}\n\n"
        f"OFI-clusters per clausule (top 5):\n{top_ofi_tekst}\n\n"
        f"Positieve clusters per clausule (top 5):\n{top_pos_tekst}\n\n"
        f"Structuur van de summary:\n"
        f"1. Intro met totaalcijfers (1 alinea)\n"
        f"2. NC-bevindingen: groepeer per thema OP BASIS VAN DE CLUSTERS HIERBOVEN. "
        f"   Benoem expliciet hoeveel NCs er per clausule zijn. "
        f"   Gebruik Conduction-context (bv. 5.11 BYOD, 5.12 intern vs extern). "
        f"   Geen claims over 'drie kritieke gebieden' tenzij er exact 3 prominente "
        f"   clusters zijn — anders benoem het werkelijke aantal.\n"
        f"3. OFI-bevindingen: kort, top 2-3 thema's.\n"
        f"4. Positieve bevindingen: korte erkenning.\n"
        f"5. Overall oordeel (voldoende / onvoldoende) + concrete prioritering.\n\n"
        f"Geef uitsluitend de tekst, geen opmaaktags."
    )


def _genereer_management_summary(bevindingen: list[dict]) -> str:
    """Taak 7.4: Genereer Nederlandse management summary via Claude."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1200,  # 350 woorden × ~2.5 tok/woord + structuurruimte
        messages=[{"role": "user", "content": _management_summary_prompt(bevindingen)}],
    )
    return message.content[0].text.strip()


def _groepeer_bevindingen(bevindingen: list[dict], norm_filter: str | None = None) -> str:
    per_clausule: dict[str, list[dict]] = defaultdict(list)
    for bev in bevindingen:
        clausule = bev["clausule"]
        if norm_filter == "9001" and not any(
            clausule.startswith(str(c)) for c in range(4, 11)
        ):
            continue
        if norm_filter == "27001" and any(
            clausule.startswith(str(c)) for c in range(4, 11)
        ):
            continue
        per_clausule[clausule].append(bev)

    regels = []
    for clausule_id in sorted(per_clausule.keys()):
        items = sorted(per_clausule[clausule_id], key=lambda b: VOLGORDE.get(b["classificatie"], 9))
        regels.append(f"\nClausule {clausule_id}: {items[0]['clausule_titel']}\n")
        for bev in items:
            regels.append(
                f"  [{bev['classificatie']}] {bev['herkomst']} — "
                f"{bev['document_naam']}\n"
                f"  {bev['beschrijving']}\n"
            )
    return "".join(regels) if regels else "(Geen bevindingen voor deze norm)"


def _overall_oordeel(bevindingen: list[dict]) -> str:
    return "onvoldoende" if any(b["classificatie"] == "NC" for b in bevindingen) else "voldoende"


def _top3_aanbevelingen(bevindingen: list[dict]) -> str:
    nc_items = [b for b in bevindingen if b["classificatie"] == "NC"]
    ofi_items = [b for b in bevindingen if b["classificatie"] == "OFI"]
    top3 = (nc_items + ofi_items)[:3]
    if not top3:
        return "Geen openstaande aanbevelingen."
    return "\n".join(
        f"{i+1}. Clausule {b['clausule']}: {b['beschrijving'][:120]}"
        for i, b in enumerate(top3)
    )


def _bouw_placeholders(
    bevindingen: list[dict],
    ontbrekende_clausules: list[dict],
    handmatige_review: list[dict],
    norm: str,
    management_summary: str,
) -> dict[str, str]:
    nc_count = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi_count = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    pos_count = sum(1 for b in bevindingen if b["classificatie"] == "positief")
    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)
    ontbrekend_tekst = (
        "\n".join(f"- Clausule {o['clausule']}: {o['titel']}" for o in ontbrekende_clausules)
        or "Geen ontbrekende clausules gedetecteerd."
    )
    handmatige_tekst = (
        "\n".join(f"- {h['naam']}: {h['reden']}" for h in handmatige_review)
        or "Geen items voor handmatige review."
    )
    return {
        "rapport_titel": f"Auditrapport {norm_label} — {date.today()}",
        "norm": norm_label,
        "template_versie": "v1.0",
        "aanmaakdatum": str(date.today()),
        "auditdoel": f"Interne audit conform {norm_label}",
        "auditscope": "(in te vullen door auditor)",
        "uitvoeringsperiode": str(date.today()),
        "auditteam": "(in te vullen door auditor)",
        "referentienorm": norm_label,
        "vorige_audit_datum": "(onbekend)",
        "management_summary": management_summary,
        "totaal_nc": str(nc_count),
        "totaal_ofi": str(ofi_count),
        "totaal_positief": str(pos_count),
        "overall_oordeel": _overall_oordeel(bevindingen),
        "bevindingen_9001": _groepeer_bevindingen(bevindingen, "9001"),
        "bevindingen_27001": _groepeer_bevindingen(bevindingen, "27001"),
        "ontbrekende_clausules": ontbrekend_tekst,
        "handmatige_review_items": handmatige_tekst,
        "conclusie": management_summary[:300],
        "top3_aanbevelingen": _top3_aanbevelingen(bevindingen),
        "auditor_naam": "(in te vullen)",
        "auditor_handtekening_datum": str(date.today()),
        "management_naam": "(in te vullen)",
        "management_handtekening_datum": "",
    }


def genereer_rapport(
    bevindingen: list[dict],
    ontbrekende_clausules: list[dict],
    handmatige_review: list[dict],
    norm: str,
    template_doc_id: str | None = None,
    folder_id: str | None = None,
) -> str:
    """
    Taken 7.1–7.7: Kopieer template en vul alle placeholders via gws CLI.
    Retourneert het Doc-ID van het gegenereerde rapport.
    """
    template_doc_id = template_doc_id or os.environ.get("AUDIT_TEMPLATE_DOC_ID")
    folder_id = folder_id or os.environ.get("AUDIT_DRIVE_FOLDER_ID")

    if not template_doc_id:
        raise EnvironmentError(
            "AUDIT_TEMPLATE_DOC_ID niet ingesteld. "
            "Voer eerst `python -m audit.pipeline --setup-template` uit."
        )

    norm_labels = {"9001": "ISO9001", "27001": "ISO27001", "beide": "ISO9001-27001"}
    bestandsnaam = f"Auditrapport_{norm_labels.get(norm, norm)}_{date.today()}"

    # Template kopiëren
    kopie = _gws(
        "drive", "files", "copy",
        params={"fileId": template_doc_id},
        body={"name": bestandsnaam},
    )
    doc_id = kopie["id"]

    # Verplaats naar audit-map
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

    # Management summary genereren
    logger.info("Management summary genereren via Claude...")
    management_summary = _genereer_management_summary(bevindingen)

    # Placeholders vullen
    placeholders = _bouw_placeholders(
        bevindingen, ontbrekende_clausules, handmatige_review, norm, management_summary
    )
    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": f"{{{{{naam}}}}}", "matchCase": True},
                "replaceText": waarde,
            }
        }
        for naam, waarde in placeholders.items()
    ]
    _gws(
        "docs", "documents", "batchUpdate",
        params={"documentId": doc_id},
        body={"requests": requests},
    )

    # Controleer resterende lege placeholders
    doc_inhoud = _gws("docs", "documents", "get", params={"documentId": doc_id})
    volledige_tekst = ""
    for elem in doc_inhoud.get("body", {}).get("content", []):
        for item in elem.get("paragraph", {}).get("elements", []):
            volledige_tekst += item.get("textRun", {}).get("content", "")

    resterende = re.findall(r"\{\{([^}]+)\}\}", volledige_tekst)
    if resterende:
        logger.warning(
            "%d placeholder(s) niet ingevuld: %s", len(resterende), resterende
        )

    logger.info("Rapport aangemaakt: %s (ID: %s)", bestandsnaam, doc_id)
    return doc_id
