"""
Drive-document verificatie — ruimt de DB op na verwijderde of verouderde bestanden.

Controleert elk Drive-document in de DB:
  1. Bestaat het bestand nog op Drive?  → zo niet: verwijder uit DB
  2. Is het ouder dan --voor jaar?       → rapporteer voor handmatige review

Gebruik:
  python3 -m audit.verify_docs               # droog-run, rapport tonen
  python3 -m audit.verify_docs --opruimen    # ook echt verwijderen
  python3 -m audit.verify_docs --voor 2023   # verouderd = voor 2023 (standaard)
"""

import argparse
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _metadata_via_sa(svc, file_id: str) -> dict | None:
    """Haalt bestandsmetadata op via de Drive API. Geeft None bij 404/403."""
    try:
        return svc.files().get(
            fileId=file_id,
            supportsAllDrives=True,
            fields="id,name,trashed,createdTime,modifiedTime",
        ).execute()
    except Exception as e:
        msg = str(e)
        if "404" in msg or "notFound" in msg or "403" in msg:
            return None
        logger.warning("Onverwachte Drive-fout voor %s: %s", file_id, msg)
        return {}   # leeg dict = onbekend, geen actie


def _metadata_via_gws(file_id: str) -> dict | None:
    """Haalt bestandsmetadata op via gws CLI. Geeft None bij niet gevonden."""
    import json
    import subprocess
    try:
        result = subprocess.run(
            ["gws", "drive", "files", "get",
             "--params", json.dumps({
                 "fileId": file_id,
                 "supportsAllDrives": True,
                 "fields": "id,name,trashed,createdTime,modifiedTime",
             })],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        if "error" in data:
            code = data["error"].get("code", 0)
            if code in (404, 403):
                return None
            logger.warning("gws fout voor %s: %s", file_id, data["error"])
            return {}
        return data
    except Exception as e:
        logger.warning("gws aanroep mislukt voor %s: %s", file_id, e)
        return {}


def _parse_drive_datum(iso_str: str | None) -> datetime | None:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def run(opruimen: bool = False, voor_jaar: int = 2023) -> None:
    from audit.gsa_client import _sa_beschikbaar
    from audit.store import verbinding

    conn = verbinding()

    docs = conn.execute(
        "SELECT id, naam FROM documents WHERE herkomst = 'Drive' ORDER BY naam"
    ).fetchall()

    if not docs:
        logger.info("Geen Drive-documenten in DB.")
        conn.close()
        return

    logger.info("Verificatie van %d Drive-documenten...", len(docs))

    gebruik_sa = False
    svc = None
    if _sa_beschikbaar():
        # Test of SA ook echt werkt (DWD moet geautoriseerd zijn)
        try:
            from audit.gsa_client import drive_service
            _svc = drive_service()
            _svc.files().get(fileId="root", fields="id").execute()
            svc = _svc
            gebruik_sa = True
            logger.info("Drive-check via service account.")
        except Exception as e:
            if "unauthorized_client" in str(e) or "invalid_grant" in str(e):
                logger.info("Service account niet geautoriseerd — fallback naar gws CLI.")
            else:
                logger.warning("SA-test mislukt: %s — fallback naar gws CLI.", e)
    if not gebruik_sa:
        logger.info("Drive-check via gws CLI.")

    niet_gevonden = []
    verouderd = []
    drempel = datetime(voor_jaar, 1, 1, tzinfo=timezone.utc)

    for i, doc in enumerate(docs, 1):
        doc_id = doc["id"]
        naam = doc["naam"]

        if gebruik_sa:
            meta = _metadata_via_sa(svc, doc_id)
        else:
            meta = _metadata_via_gws(doc_id)

        if meta is None:
            # Definitief niet gevonden
            niet_gevonden.append({"id": doc_id, "naam": naam})
            logger.info("Niet gevonden op Drive: %s", naam)
            continue

        if meta and meta.get("trashed"):
            niet_gevonden.append({"id": doc_id, "naam": naam, "reden": "verplaatst naar prullenbak"})
            logger.info("In prullenbak op Drive: %s", naam)
            continue

        # Datum-check op werkelijke Drive-datum
        drive_datum = _parse_drive_datum(meta.get("modifiedTime") or meta.get("createdTime"))
        if drive_datum and drive_datum < drempel:
            verouderd.append({
                "id": doc_id,
                "naam": naam,
                "datum": drive_datum.strftime("%Y-%m-%d"),
            })

        if i % 50 == 0:
            logger.info("  %d/%d gecontroleerd...", i, len(docs))

    # ── Rapport ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Drive-verificatie: {len(docs)} documenten gecontroleerd")
    print(f"{'='*60}\n")

    if niet_gevonden:
        print(f"❌ Niet meer beschikbaar op Drive ({len(niet_gevonden)}):")
        for d in niet_gevonden:
            status = "→ verwijderd uit DB" if opruimen else "→ gebruik --opruimen om te verwijderen"
            print(f"  [{d['id'][:20]}...] {d['naam']}  {status}")
        print()
    else:
        print("✅ Alle Drive-documenten nog bereikbaar.\n")

    if verouderd:
        print(f"⏰ Verouderd (gewijzigd vóór {voor_jaar}): {len(verouderd)} documenten — handmatige review:")
        for d in verouderd:
            print(f"  {d['datum']}  {d['naam']}")
        # Schrijf ook naar bestand voor makkelijke review
        import os
        from datetime import date as _date
        out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)
        rapport_pad = os.path.join(out_dir, f"verouderde_documenten_{_date.today()}.md")
        with open(rapport_pad, "w", encoding="utf-8") as f:
            f.write(f"# Verouderde Drive-documenten (gewijzigd vóór {voor_jaar})\n\n")
            f.write(f"Gegenereerd: {_date.today()}  \n")
            f.write(f"Totaal: {len(verouderd)} van {len(docs)} documenten\n\n")
            f.write("| Datum gewijzigd | Naam | Drive-link |\n")
            f.write("|---|---|---|\n")
            for d in sorted(verouderd, key=lambda x: x["datum"]):
                link = f"https://drive.google.com/file/d/{d['id']}"
                f.write(f"| {d['datum']} | {d['naam']} | [open]({link}) |\n")
        print(f"\nLijst opgeslagen: {rapport_pad}")
        print()

    # ── Opruimen ─────────────────────────────────────────────────────────────
    if opruimen and niet_gevonden:
        ids = [d["id"] for d in niet_gevonden]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM clause_matches WHERE doc_id IN ({placeholders})", ids)
        conn.execute(f"DELETE FROM documents WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"🗑️  {len(ids)} document(en) verwijderd uit DB (documents + clause_matches).")
    elif niet_gevonden:
        print("ℹ️  Droog-run — geen wijzigingen. Gebruik --opruimen om te verwijderen.")

    conn.close()

    totaal_verwijderd = len(niet_gevonden) if opruimen else 0
    logger.info(
        "Klaar: %d niet gevonden, %d verouderd, %d verwijderd",
        len(niet_gevonden), len(verouderd), totaal_verwijderd,
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Drive-documenten verifiëren en DB opruimen")
    parser.add_argument(
        "--opruimen",
        action="store_true",
        help="Verwijder niet-bestaande documenten uit de DB (standaard: droog-run)",
    )
    parser.add_argument(
        "--voor",
        type=int,
        default=2023,
        metavar="JAAR",
        help="Verouderd = ingested vóór dit jaar (standaard: 2023)",
    )
    args = parser.parse_args()
    run(opruimen=args.opruimen, voor_jaar=args.voor)


if __name__ == "__main__":
    main()
