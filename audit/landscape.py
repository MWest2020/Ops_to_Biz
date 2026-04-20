"""
Audit landschap — clausure-dekking rapport uit lokale DB.

Geen LLM nodig. Toont per clausule:
  - Gedekt: welke documenten matchen
  - Niet gedekt: clausules zonder enig bewijs
  - Miro-notities per clausule

Gebruik:
  python -m audit.landscape              # beide normen
  python -m audit.landscape --norm 9001
  python -m audit.landscape --chapter 8  # één hoofdstuk
  python -m audit.landscape --zoek "incident management"
"""

import argparse
import logging
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "landscape")


def genereer_landschap(norm: str, chapter: str | None = None) -> str:
    from audit.store import verbinding
    from audit.clause_mapping import laad_clause_map, filter_clause_map

    conn = verbinding()
    clause_map = laad_clause_map(norm)
    if chapter:
        clause_map = filter_clause_map(clause_map, chapter)

    clausules = clause_map.get("clausules", {})
    norm_label = clause_map.get("norm", norm)

    # Haal alle matches op uit DB
    rows = conn.execute("""
        SELECT cm.clausule_id, cm.herkomst, cm.doc_id,
               COALESCE(d.naam, m.tekst) AS naam
        FROM clause_matches cm
        LEFT JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
        LEFT JOIN miro_notes m ON m.id = cm.doc_id AND cm.herkomst = 'Miro'
        WHERE cm.norm IN (?, 'beide')
          AND (cm.herkomst != 'Drive' OR d.scope = 'in')
          AND cm.sub_punt = ''
        ORDER BY cm.clausule_id, cm.herkomst, naam
    """, (norm,)).fetchall()

    # Interview-bevindingen ophalen
    interview_rows = conn.execute(
        "SELECT clausule_id, bevinding, notitie, interviewed_at FROM interviews WHERE norm IN (?, 'beide') ORDER BY clausule_id",
        (norm,)
    ).fetchall()
    interviews: dict[str, dict] = {r["clausule_id"]: dict(r) for r in interview_rows}

    # Ingest log
    log = conn.execute("SELECT * FROM ingest_log").fetchall()
    ingest_info = {r["bron"]: r for r in log}

    # Statistieken
    total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    total_miro = conn.execute("SELECT COUNT(*) FROM miro_notes").fetchone()[0]
    total_interviews = conn.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
    conn.close()

    # Groepeer per clausule
    matches: dict[str, list[dict]] = {k: [] for k in clausules}
    for row in rows:
        if row["clausule_id"] in matches:
            matches[row["clausule_id"]].append({"naam": row["naam"], "herkomst": row["herkomst"]})

    gedekt = [k for k, v in matches.items() if v]
    niet_gedekt = [k for k, v in matches.items() if not v]
    dekking_pct = round(len(gedekt) / len(clausules) * 100) if clausules else 0

    regels = [
        f"# Audit Landschap — {norm_label}",
        f"",
        f"| | |",
        f"|---|---|",
        f"| Datum | {date.today()} |",
        f"| Norm | {norm_label} |",
        f"| Drive-documenten in DB | {total_docs} |",
        f"| Miro-notities in DB | {total_miro} |",
        f"| Interview-bevindingen | {total_interviews} |",
    ]
    if "drive" in ingest_info:
        regels.append(f"| Drive laatste sync | {ingest_info['drive']['last_run'][:19]} |")
    if "miro" in ingest_info:
        regels.append(f"| Miro laatste sync | {ingest_info['miro']['last_run'][:19]} |")
    regels += [
        f"",
        f"**Clausule-dekking: {len(gedekt)}/{len(clausules)} ({dekking_pct}%)**",
        f"",
        f"---",
        f"",
        f"## Gedekte clausules ({len(gedekt)})",
        f"",
    ]

    for clausule_id in sorted(gedekt):
        titel = clausules[clausule_id].get("titel", "")
        items = matches[clausule_id]
        drive_items = [i for i in items if i["herkomst"] == "Drive"]
        miro_items = [i for i in items if i["herkomst"] == "Miro"]
        regels.append(f"### {clausule_id} — {titel}")
        regels.append("")
        if drive_items:
            regels.append(f"**Drive** ({len(drive_items)} document(en)):")
            for item in drive_items[:10]:
                regels.append(f"- {item['naam']}")
            if len(drive_items) > 10:
                regels.append(f"- _...en {len(drive_items) - 10} meer_")
        if miro_items:
            regels.append(f"")
            regels.append(f"**Miro** ({len(miro_items)} notitie(s)):")
            for item in miro_items[:5]:
                tekst = (item['naam'] or '')[:80]
                regels.append(f"- _{tekst}_")
        regels.append("")

    # Splits niet-gedekte clausules op basis van interview-bevinding
    nc_list = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "NC"]
    ofi_list = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "OFI"]
    positief_via_interview = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "positief"]
    niet_beantwoord = [k for k in niet_gedekt if k not in interviews]
    overgeslagen = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "overgeslagen"]

    regels += [
        f"---",
        f"",
        f"## Niet gedekte clausules ({len(niet_gedekt)}) ⚠️",
        f"",
        f"Deze clausules hebben geen gedocumenteerd bewijs in Drive of Miro.",
        f"",
    ]

    if nc_list:
        regels += [f"### Non-conformiteiten ({len(nc_list)}) 🔴", ""]
        for cid in sorted(nc_list):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(f"- **{cid}** — {titel}{notitie}")
        regels.append("")

    if ofi_list:
        regels += [f"### Verbeterpunten / OFI ({len(ofi_list)}) 🟡", ""]
        for cid in sorted(ofi_list):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(f"- **{cid}** — {titel}{notitie} _(praktijk bestaat, documentatie ontbreekt)_")
        regels.append("")

    if positief_via_interview:
        regels += [f"### Positief bevonden via interview ({len(positief_via_interview)}) 🟢", ""]
        for cid in sorted(positief_via_interview):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(f"- **{cid}** — {titel}{notitie}")
        regels.append("")

    if niet_beantwoord:
        regels += [f"### Nog niet geïnterviewd ({len(niet_beantwoord)}) — prioriteit voor interview", ""]
        for cid in sorted(niet_beantwoord):
            titel = clausules[cid].get("titel", "")
            regels.append(f"- **{cid}** — {titel}")
        regels.append("")

    if overgeslagen:
        regels += [f"### Overgeslagen ({len(overgeslagen)})", ""]
        for cid in sorted(overgeslagen):
            titel = clausules[cid].get("titel", "")
            regels.append(f"- **{cid}** — {titel}")
        regels.append("")

    regels += ["", "---", f"_Gegenereerd op {date.today()} uit lokale audit DB_"]

    return "\n".join(regels)


def schrijf_landschap(norm: str, chapter: str | None = None) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    suffix = f"_h{chapter}" if chapter else ""
    bestandsnaam = f"Landschap_{norm}{suffix}_{date.today()}.md"
    pad = os.path.join(OUTPUT_DIR, bestandsnaam)
    inhoud = genereer_landschap(norm, chapter)
    with open(pad, "w", encoding="utf-8") as f:
        f.write(inhoud)
    logger.info("Landschap geschreven: %s", pad)
    return pad


def zoek_in_db(query: str) -> None:
    from audit.store import verbinding, zoek
    conn = verbinding()
    resultaten = zoek(conn, query)
    conn.close()
    if not resultaten:
        print(f"Geen resultaten voor '{query}'")
        return
    print(f"\nZoekresultaten voor '{query}' ({len(resultaten)} gevonden):\n")
    for r in resultaten:
        print(f"  [{r['herkomst']}] {r['naam']}")
        print(f"    ...{r['fragment']}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="Audit landschap rapport")
    parser.add_argument("--norm", choices=["9001", "27001", "beide"], default=os.environ.get("AUDIT_NORM", "beide"))
    parser.add_argument("--chapter", default=None, metavar="N")
    parser.add_argument("--zoek", default=None, metavar="QUERY", help="Zoek in DB i.p.v. rapport genereren")
    args = parser.parse_args()

    if args.zoek:
        zoek_in_db(args.zoek)
    else:
        pad = schrijf_landschap(args.norm, args.chapter)
        print(f"Landschap: {pad}")


if __name__ == "__main__":
    main()
