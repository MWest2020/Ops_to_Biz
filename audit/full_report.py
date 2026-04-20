"""
Volledig auditrapport — alle clausules met normtekst, bewijs en bevindingen.

Genereert een Markdown-rapport per norm met voor elke clausule:
  - Normtekst
  - Interpretatie
  - Bewijslast (wat zou aanwezig moeten zijn)
  - Gevonden bewijs (Drive-documenten + Miro-notities, met links)
  - Interview-bevinding (NC / OFI / positief)
  - Planning 2025 (geplande maanden)

Gebruik:
  python -m audit.full_report --norm 27001
  python -m audit.full_report --norm 9001
  python -m audit.full_report --norm beide
"""

import argparse
import logging
import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "output", "audit_reports"
)

BEVINDING_LABEL = {
    "NC":          "🔴 Non-conformiteit",
    "OFI":         "🟡 Verbeterpunt (OFI)",
    "positief":    "🟢 Positief",
    "overgeslagen": "⚪ Overgeslagen",
}


def _drive_link(doc_id: str, mime: str | None) -> str:
    if mime == "application/vnd.google-apps.document":
        return f"https://docs.google.com/document/d/{doc_id}"
    if mime == "application/vnd.google-apps.spreadsheet":
        return f"https://docs.google.com/spreadsheets/d/{doc_id}"
    return f"https://drive.google.com/file/d/{doc_id}"


def genereer_rapport(norm: str) -> str:
    from audit.store import verbinding
    from audit.clause_mapping import laad_clause_map

    conn = verbinding()

    # Laad alle benodigde data in één keer
    clause_map = laad_clause_map(norm)
    clausules = clause_map.get("clausules", {})

    # clause_id → lijst van {naam, doc_id, herkomst, mime_type}
    bewijzen: dict[str, list[dict]] = {k: [] for k in clausules}
    for row in conn.execute("""
        SELECT cm.clausule_id, cm.doc_id, cm.herkomst,
               COALESCE(d.naam, m.tekst) AS naam,
               d.mime_type
        FROM clause_matches cm
        LEFT JOIN documents d  ON d.id  = cm.doc_id AND cm.herkomst = 'Drive'
        LEFT JOIN miro_notes m ON m.id  = cm.doc_id AND cm.herkomst = 'Miro'
        WHERE cm.norm IN (?, 'beide')
          AND (cm.herkomst != 'Drive' OR d.scope = 'in')
          AND cm.sub_punt = ''
        ORDER BY cm.clausule_id, naam
    """, (norm,)).fetchall():
        if row["clausule_id"] in bewijzen:
            bewijzen[row["clausule_id"]].append(dict(row))

    # Interview-bevindingen
    interviews: dict[str, dict] = {}
    for row in conn.execute(
        "SELECT * FROM interviews WHERE norm IN (?, 'beide')", (norm,)
    ).fetchall():
        interviews[row["clausule_id"]] = dict(row)

    # Planning 2025
    planning: dict[str, str] = {}
    for row in conn.execute(
        "SELECT clausule_id, kwartaal FROM audit_planning WHERE norm=? AND jaar=2025",
        (norm,)
    ).fetchall():
        if row["kwartaal"]:
            planning[row["clausule_id"]] = row["kwartaal"]

    # Statistieken
    gedekt = sum(1 for v in bewijzen.values() if v)
    total = len(clausules)
    interviews_gedaan = len(interviews)

    conn.close()

    # Normteksten laden
    normteksten = _laad_normteksten(norm)

    # ── Rapport opbouwen ──────────────────────────────────────────────────────
    norm_label = clause_map.get("norm", norm)
    regels = [
        f"# Volledig Auditrapport — {norm_label}",
        f"",
        f"**Datum**: {date.today()}  ",
        f"**Clausule-dekking**: {gedekt}/{total} ({round(gedekt/total*100) if total else 0}%)  ",
        f"**Interviews gedaan**: {interviews_gedaan}  ",
        f"",
        f"---",
        f"",
    ]

    for clausule_id in sorted(clausules.keys(), key=_sorteersleutel):
        titel = clausules[clausule_id].get("titel", "")
        nt = normteksten.get(clausule_id, {})
        items = bewijzen.get(clausule_id, [])
        iv = interviews.get(clausule_id)
        plan = planning.get(clausule_id)

        drive_items = [i for i in items if i["herkomst"] == "Drive"]
        miro_items  = [i for i in items if i["herkomst"] == "Miro"]

        regels.append(f"## {clausule_id} — {titel}")
        regels.append("")

        # Normtekst
        if nt.get("normtekst"):
            regels.append(f"**Normtekst**")
            regels.append(f"> {nt['normtekst']}")
            regels.append("")

        # Interpretatie
        if nt.get("interpretatie"):
            regels.append(f"**Interpretatie**")
            regels.append(nt["interpretatie"])
            regels.append("")

        # Bewijslast
        if nt.get("bewijslast"):
            regels.append(f"**Bewijslast** — wat moet aanwezig zijn:")
            for b in nt["bewijslast"]:
                regels.append(f"- {b}")
            regels.append("")

        # Gevonden bewijs
        if drive_items or miro_items:
            totaal_bewijs = len(drive_items) + len(miro_items)
            regels.append(f"**Gevonden bewijs** ({totaal_bewijs})")
            for item in drive_items[:15]:
                link = _drive_link(item["doc_id"], item.get("mime_type"))
                regels.append(f"- [{item['naam']}]({link})")
            if len(drive_items) > 15:
                regels.append(f"- _...en {len(drive_items) - 15} meer Drive-documenten_")
            for item in miro_items[:5]:
                tekst = (item["naam"] or "")[:80]
                regels.append(f"- _(Miro)_ {tekst}")
            regels.append("")
        else:
            regels.append(f"**Gevonden bewijs**: _(geen)_")
            regels.append("")

        # Interview-bevinding
        if iv:
            label = BEVINDING_LABEL.get(iv["bevinding"], iv["bevinding"])
            regels.append(f"**Bevinding**: {label}")
            if iv.get("notitie"):
                regels.append(f"> {iv['notitie']}")
            regels.append("")
        else:
            regels.append(f"**Bevinding**: _(nog niet geïnterviewd)_")
            regels.append("")

        # Planning
        if plan:
            regels.append(f"**Planning 2025**: {plan}")
        else:
            regels.append(f"**Planning 2025**: _(niet in auditplanning)_")
        regels.append("")
        regels.append("---")
        regels.append("")

    regels.append(f"_Gegenereerd op {date.today()} uit lokale audit DB_")
    return "\n".join(regels)


def _laad_normteksten(norm: str) -> dict:
    """Geeft {clausule_id: {normtekst, interpretatie, bewijslast}} voor de norm."""
    from audit.normteksten import NORMTEKSTEN_9001, NORMTEKSTEN_27001
    if norm == "9001":
        return NORMTEKSTEN_9001
    if norm == "27001":
        return NORMTEKSTEN_27001
    # beide: combineer
    return {**NORMTEKSTEN_9001, **NORMTEKSTEN_27001}


def _sorteersleutel(clausule_id: str):
    """Sorteert "5.12" correct na "5.9" (numeriek, niet lexicografisch)."""
    parts = clausule_id.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0,)


def schrijf_rapport(norm: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bestandsnaam = f"Auditrapport_volledig_{norm}_{date.today()}.md"
    pad = os.path.join(OUTPUT_DIR, bestandsnaam)
    inhoud = genereer_rapport(norm)
    with open(pad, "w", encoding="utf-8") as f:
        f.write(inhoud)
    logger.info("Rapport geschreven: %s", pad)
    return pad


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Volledig auditrapport genereren")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default="beide",
    )
    args = parser.parse_args()

    if args.norm == "beide":
        for n in ["9001", "27001"]:
            pad = schrijf_rapport(n)
            print(f"Rapport: {pad}")
    else:
        pad = schrijf_rapport(args.norm)
        print(f"Rapport: {pad}")


if __name__ == "__main__":
    main()
