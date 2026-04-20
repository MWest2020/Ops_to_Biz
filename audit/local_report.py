"""
Lokale rapportage — schrijft het auditrapport als Markdown naar disk.

Wordt altijd uitgevoerd naast de Google Docs output.
Configureer LOCAL_REPORT_DIR in .env (default: ./output/audit_reports/).
"""

import logging
import os
from collections import defaultdict
from datetime import date
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "output", "audit_reports"
)

VOLGORDE = {"NC": 0, "OFI": 1, "positief": 2}

BADGES = {"NC": "🔴 NC", "OFI": "🟠 OFI", "positief": "🟢 Positief"}


def _norm_label(norm: str) -> str:
    return {"9001": "ISO 9001:2015", "27001": "ISO 27001:2022", "beide": "ISO 9001:2015 + ISO 27001:2022"}.get(norm, norm)


def _groepeer_per_clausule(bevindingen: list[dict]) -> dict[str, list[dict]]:
    per_clausule: dict[str, list[dict]] = defaultdict(list)
    for bev in bevindingen:
        per_clausule[bev["clausule"]].append(bev)
    return {
        k: sorted(v, key=lambda b: VOLGORDE.get(b["classificatie"], 9))
        for k, v in sorted(per_clausule.items())
    }


def _render_clausules_met_themas(regels: list[str], bevindingen: list[dict]) -> None:
    """
    Render per clausule → thema-subsectie → bevindingen.

    Thema's binnen een clausule worden gesorteerd op aantal (afnemend), Overig laatst.
    Als een clausule maar één thema heeft, wordt de thema-kop weggelaten (geen ruis).
    """
    from audit.tabular_report import bepaal_thema  # vermijd circulaire import bij setup
    from collections import Counter

    per_clausule = _groepeer_per_clausule(bevindingen)
    for clausule_id, items in per_clausule.items():
        titel = items[0].get("clausule_titel", "")
        regels.append(f"### Clausule {clausule_id}: {titel}")
        regels.append("")

        # Verdeel in thema's (overschrijfbaar via bev["thema"] indien al toegekend)
        thema_groepen: dict[str, list[dict]] = {}
        for bev in items:
            thema = bev.get("thema") or bepaal_thema(bev)
            thema_groepen.setdefault(thema, []).append(bev)

        # Sorteer thema's: grootste groep eerst, "Overig" altijd laatst
        def thema_key(kv):
            thema, lijst = kv
            return (thema == "Overig", -len(lijst), thema)

        geordende_themas = sorted(thema_groepen.items(), key=thema_key)
        toon_thema_kop = len(geordende_themas) > 1

        for thema, groep in geordende_themas:
            if toon_thema_kop:
                tellers = Counter(b["classificatie"] for b in groep)
                kop_meta = " · ".join(
                    f"{tellers[c]} {c}" for c in ("NC", "OFI", "positief") if tellers.get(c)
                )
                regels.append(f"#### Thema: {thema} _({kop_meta})_")
                regels.append("")

            for bev in sorted(groep, key=lambda b: VOLGORDE.get(b["classificatie"], 9)):
                badge = BADGES.get(bev["classificatie"], bev["classificatie"])
                doc_link = _doc_link(bev)
                regels.append(f"**{badge}** — {bev['herkomst']}: {doc_link}")
                regels.append("")
                beschrijving = bev.get("beschrijving") or "_(geen beschrijving)_"
                regels.append(f"> {beschrijving}")
                regels.append("")
                if bev.get("onderbouwing"):
                    regels.append(f"_Onderbouwing: {bev['onderbouwing']}_")
                    regels.append("")


def _doc_link(bev: dict) -> str:
    """Bouw een klikbare Markdown-link naar het brondocument."""
    doc_id = bev.get("doc_id", "")
    naam = bev.get("document_naam", "onbekend")
    if not doc_id:
        return f"_{naam}_"
    if bev.get("herkomst") == "Miro":
        board_id = os.environ.get("MIRO_BOARD_ID", "")
        if board_id:
            url = f"https://miro.com/app/board/{board_id}/?moveToWidget={doc_id}"
            return f"[{naam}]({url})"
        return f"_{naam}_"
    url = f"https://drive.google.com/file/d/{doc_id}/view"
    return f"[{naam}]({url})"


def schrijf_rapport(
    bevindingen: list[dict],
    ontbrekende_clausules: list[dict],
    handmatige_review: list[dict],
    management_summary: str,
    norm: str,
    output_dir: str | None = None,
    gearchiveerd: list[dict] | None = None,
    scherpte: float = 1.0,
) -> str:
    """
    Schrijf het volledige auditrapport als Markdown naar disk.
    Retourneert het pad van het aangemaakte bestand.
    """
    output_dir = output_dir or os.environ.get("LOCAL_REPORT_DIR", DEFAULT_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    norm_bestand = norm.replace(" ", "").replace("+", "-")
    scherpte_label = f"_s{str(scherpte).replace('.', '')}" if scherpte != 1.0 else ""
    bestandsnaam = f"Auditrapport_{norm_bestand}_{date.today()}{scherpte_label}.md"
    pad = os.path.join(output_dir, bestandsnaam)

    nc_count = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi_count = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    pos_count = sum(1 for b in bevindingen if b["classificatie"] == "positief")
    oordeel = "**onvoldoende**" if nc_count > 0 else "**voldoende**"

    regels = [
        f"# Auditrapport {_norm_label(norm)}",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Datum | {date.today()} |",
        f"| Norm | {_norm_label(norm)} |",
        f"| Template versie | v1.0 |",
        f"| Overall oordeel | {oordeel} |",
        f"",
        f"---",
        f"",
        f"## 1. Management Summary",
        f"",
        management_summary,
        f"",
        f"---",
        f"",
        f"## 2. Resultaatoverzicht",
        f"",
        f"| Classificatie | Aantal |",
        f"|---|---|",
        f"| Non-conformiteiten (NC) | {nc_count} |",
        f"| Kansen voor verbetering (OFI) | {ofi_count} |",
        f"| Positieve bevindingen | {pos_count} |",
        f"| **Totaal** | **{len(bevindingen)}** |",
        f"",
        f"---",
        f"",
    ]

    # Bevindingen per norm
    normen_secties = []
    if norm in ("9001", "beide"):
        normen_secties.append(("3. Bevindingen ISO 9001:2015", "9001"))
    if norm in ("27001", "beide"):
        normen_secties.append((
            "4. Bevindingen ISO 27001:2022 (Addendum)" if norm == "beide"
            else "3. Bevindingen ISO 27001:2022",
            "27001",
        ))

    for sectie_titel, norm_filter in normen_secties:
        regels.append(f"## {sectie_titel}")
        regels.append("")

        gefilterd = [
            b for b in bevindingen
            if norm_filter == "9001" and any(b["clausule"].startswith(str(c)) for c in range(4, 11))
            or norm_filter == "27001" and not any(b["clausule"].startswith(str(c)) for c in range(4, 11))
        ]

        if not gefilterd:
            regels.append("_(geen bevindingen)_")
            regels.append("")
        else:
            _render_clausules_met_themas(regels, gefilterd)

        regels.append("---")
        regels.append("")

    # Ontbrekende bewijsstukken
    regels.append("## 5. Ontbrekende bewijsstukken")
    regels.append("")
    if ontbrekende_clausules:
        for o in ontbrekende_clausules:
            regels.append(f"- Clausule {o['clausule']}: {o['titel']}")
    else:
        regels.append("_Geen ontbrekende clausules gedetecteerd._")
    regels.append("")

    if handmatige_review:
        regels.append("### Items voor handmatige review")
        regels.append("")
        for h in handmatige_review:
            regels.append(f"- {h['naam']}: {h['reden']}")
        regels.append("")

    if gearchiveerd:
        regels.append("## 6. Gearchiveerde documenten (>2 jaar oud)")
        regels.append("")
        regels.append("_Onderstaande documenten zijn ouder dan 2 jaar en zijn niet meegenomen in de classificatie. Ze worden als OFI beschouwd: de organisatie is sindsdien dermate gewijzigd dat deze documenten dienen te worden herzien of ingetrokken._")
        regels.append("")
        for doc in sorted(gearchiveerd, key=lambda d: d.get("modified_at", "")):
            datum = (doc.get("modified_at") or "")[:10]
            url = f"https://drive.google.com/file/d/{doc['id']}/view"
            regels.append(f"- [{doc['naam']}]({url}) _(laatst gewijzigd: {datum})_")
        regels.append("")

    regels.append("---")
    regels.append("")
    regels.append("## 7. Handtekeningblok")
    regels.append("")
    regels.append(f"| Rol | Naam | Datum |")
    regels.append(f"|---|---|---|")
    regels.append(f"| Lead-auditor | | {date.today()} |")
    regels.append(f"| Verantwoordelijk manager | | |")
    regels.append("")
    regels.append("---")
    regels.append(f"_Gegenereerd door geautomatiseerd audit-systeem op {date.today()}_")

    with open(pad, "w", encoding="utf-8") as f:
        f.write("\n".join(regels))

    logger.info("Lokaal rapport geschreven: %s", pad)
    return pad
