"""
Orchestrator: ISO audit pipeline.

Gebruik:
  python -m audit.pipeline --norm 9001
  python -m audit.pipeline --norm 27001
  python -m audit.pipeline --norm beide

  # Eén hoofdstuk uitvoeren (minder API-calls, sneller):
  python -m audit.pipeline --norm 9001 --chapter 4
  python -m audit.pipeline --norm beide --chapter 8

  # Dry-run zonder externe verbindingen (test + lokale output):
  python -m audit.pipeline --local-only --norm 9001

  # Alleen template aanmaken (eerste keer):
  python -m audit.pipeline --setup-template

Omgevingsvariabelen: zie .env.example
"""

import argparse
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _valideer_env():
    """Controleer dat gws beschikbaar en ingelogd is."""
    import shutil
    import subprocess
    if not shutil.which("gws"):
        logger.error("gws CLI niet gevonden in PATH.")
        sys.exit(1)
    # Controleer auth-status (non-fatal waarschuwing)
    try:
        result = subprocess.run(
            ["gws", "auth", "status"], capture_output=True, text=True, timeout=10
        )
        import json as _json
        status = _json.loads(result.stdout) if result.stdout.strip() else {}
        if not status.get("token_valid", False):
            logger.warning(
                "gws auth token niet geldig (%s). Voer `gws auth login` uit als API-calls falen.",
                status.get("token_error", "onbekend"),
            )
    except Exception:
        pass  # auth status check is best-effort


_LOKALE_TEST_BEVINDINGEN = [
    {
        "clausule": "4.1",
        "clausule_titel": "Inzicht in de organisatie en haar context",
        "document_naam": "[TESTDATA] Contextanalyse_2025.docx",
        "herkomst": "Drive",
        "classificatie": "positief",
        "beschrijving": "De organisatie heeft een gedocumenteerde contextanalyse uitgevoerd. Interne en externe factoren zijn beschreven.",
        "onderbouwing": "ISO 9001:2015 §4.1 vereist begrip van interne en externe context.",
        "pre_classificatie": None,
    },
    {
        "clausule": "5.2",
        "clausule_titel": "Beleid",
        "document_naam": "[TESTDATA] Kwaliteitsbeleid_v2.docx",
        "herkomst": "Drive",
        "classificatie": "OFI",
        "beschrijving": "Het kwaliteitsbeleid is aanwezig maar wordt niet actief gecommuniceerd naar alle medewerkers.",
        "onderbouwing": "ISO 9001:2015 §5.2.2 vereist dat het beleid beschikbaar is als gedocumenteerde informatie.",
        "pre_classificatie": None,
    },
    {
        "clausule": "8.1",
        "clausule_titel": "Operationele planning en beheersing",
        "document_naam": "[TESTDATA] Miro sticky: geen gedocumenteerd proces",
        "herkomst": "Miro",
        "classificatie": "NC",
        "beschrijving": "Er is geen gedocumenteerde operationele planning voor het primaire proces aangetroffen.",
        "onderbouwing": "ISO 9001:2015 §8.1 vereist planning, implementatie en beheersing van operationele processen.",
        "pre_classificatie": "rood",
    },
]

_LOKALE_TEST_ONTBREKEND = [
    {
        "clausule": "9.3",
        "titel": "Directiebeoordeling",
        "reden": "[TESTDATA] Geen bewijs van directiebeoordeling gevonden",
    },
]


def run_local_only(norm: str):
    """
    Dry-run zonder externe verbindingen: synthetische testdata → lokale Markdown + CSV + Excel.
    Nuttig voor het testen van de rapportage-logica zonder GWS-credentials.
    """
    from audit.local_report import schrijf_rapport
    from audit.tabular_report import schrijf_csv, schrijf_excel, bepaal_thema

    logger.info("=== ISO Audit Pipeline — LOCAL ONLY (testdata) ===")
    logger.info("Norm: %s | Geen Drive/Claude/Sheets-verbinding", norm)

    management_summary = (
        "**[TESTDATA]** Dit rapport is gegenereerd met synthetische testbevindingen "
        "zonder verbinding met Google Drive of de Claude API. "
        "Gebruik `--local-only` uitsluitend voor het testen van de rapportage-logica."
    )

    # Heuristisch thema toevoegen zodat markdown ook de thema-bundeling toont
    for bev in _LOKALE_TEST_BEVINDINGEN:
        bev.setdefault("thema", bepaal_thema(bev))

    lokaal_pad = schrijf_rapport(
        _LOKALE_TEST_BEVINDINGEN,
        _LOKALE_TEST_ONTBREKEND,
        [],
        management_summary,
        norm,
    )
    logger.info("Lokaal testrapport: %s", lokaal_pad)

    csv_pad = schrijf_csv(_LOKALE_TEST_BEVINDINGEN, norm)
    xlsx_pad = schrijf_excel(_LOKALE_TEST_BEVINDINGEN, norm)
    logger.info("Tabulair: %s  |  %s", csv_pad, xlsx_pad)

    return lokaal_pad


def run_setup_template():
    """Éénmalige setup: template aanmaken in Drive."""
    from audit.template_setup import create_template, verify_placeholders

    folder_id = os.environ.get("AUDIT_DRIVE_FOLDER_ID", "")
    logger.info("Template aanmaken...")
    doc_id = create_template(folder_id)
    ontbrekend = verify_placeholders(doc_id)
    if ontbrekend:
        logger.warning("Voeg AUDIT_TEMPLATE_DOC_ID=%s toe aan .env", doc_id)
    else:
        logger.info("Template klaar. Voeg toe aan .env: AUDIT_TEMPLATE_DOC_ID=%s", doc_id)


def run_audit(
    norm: str,
    no_review: bool = False,
    write_sheets: bool = False,
    chapter: str | None = None,
    scherpte: float = 1.0,
    thema_llm: bool = False,
    rehash: bool = False,
    dry_run_cost: bool = False,
):
    """Volledige auditpipeline uitvoeren."""
    from audit.clause_mapping import laad_clause_map, filter_clause_map, koppel_documenten, ontbrekende_dekking
    from audit.drive_ingest import haal_documenten_op
    from audit.miro_ingest import haal_notities_op, koppel_aan_clausules, merge_met_drive_bevindingen
    # v2 classifier: system prompt caching, per-call usage tracking, rehash-support
    from audit.finding_classification_20260420 import (
        classificeer_alle_bevindingen, review_en_bevestig, sla_op_in_sheets,
        schat_kosten,
    )
    from audit.report_generation import genereer_rapport
    from audit.slide_summary import genereer_slides
    from audit.notification import stuur_calendar_uitnodiging, stuur_gmail_notificatie
    from audit.local_report import schrijf_rapport
    from audit.tabular_report import schrijf_csv, schrijf_excel

    logger.info("=== ISO Audit Pipeline gestart (norm: %s, rehash: %s, dry-run-cost: %s) ===",
                norm, rehash, dry_run_cost)

    # Stap 1: Clausule-map laden
    logger.info("Stap 1/7: Clausule-map laden...")
    clause_map = laad_clause_map(norm)
    if chapter:
        clause_map = filter_clause_map(clause_map, chapter)
        logger.info("Hoofdstuk-filter actief: alleen clausule %s.*", chapter)

    # Stap 2: Drive-documenten inlezen
    logger.info("Stap 2/7: Drive-documenten inlezen...")
    documenten, handmatige_review = haal_documenten_op()
    if handmatige_review:
        logger.warning(
            "%d bestand(en) vereisen handmatige review: %s",
            len(handmatige_review),
            [h["naam"] for h in handmatige_review],
        )

    # Stap 3: Miro-notities inlezen (best-effort)
    logger.info("Stap 3/7: Miro-notities inlezen...")
    miro_notities = []
    try:
        miro_notities_raw = haal_notities_op()
        miro_notities = koppel_aan_clausules(miro_notities_raw, clause_map)
        logger.info("%d Miro-notities ingelezen", len(miro_notities))
    except EnvironmentError as e:
        logger.warning("Miro overgeslagen: %s", e)
    except Exception as e:
        logger.warning("Miro-ingest mislukt (niet kritiek): %s", e)

    # Stap 4: Clausule-koppeling + leeftijdsfilter
    logger.info("Stap 4/7: Documenten koppelen aan clausules...")
    from datetime import date, timedelta
    cutoff = (date.today() - timedelta(days=2*365)).isoformat()

    gekoppeld_alle, niet_geclassificeerd = koppel_documenten(documenten, clause_map)

    gearchiveerd = [d for d in gekoppeld_alle if (d.get("modified_at") or "") < cutoff]
    gekoppeld = [d for d in gekoppeld_alle if (d.get("modified_at") or "") >= cutoff]
    logger.info(
        "Leeftijdsfilter (%s): %d actief, %d gearchiveerd (>2 jaar oud)",
        cutoff, len(gekoppeld), len(gearchiveerd),
    )

    alle_input = merge_met_drive_bevindingen(miro_notities, [
        {**doc, "herkomst": "Drive"} for doc in gekoppeld
    ])
    ontbrekend = ontbrekende_dekking(gekoppeld, miro_notities, clause_map)

    if niet_geclassificeerd:
        logger.warning(
            "%d document(en) zonder clausule-match: %s",
            len(niet_geclassificeerd),
            [d["naam"] for d in niet_geclassificeerd],
        )

    # Stap 5: Classificatie via Claude (of alleen kostenschatting bij dry-run-cost)
    if dry_run_cost:
        logger.info("Stap 5/7: Kostenschatting (dry-run, GEEN API-calls)...")
        schatting = schat_kosten(
            gekoppeld, miro_notities, clause_map,
            norm=norm, scherpte=scherpte, rehash=rehash,
        )
        logger.info("=== Kostenschatting ===")
        for k, v in schatting.items():
            logger.info("  %-25s %s", k + ":", v)
        logger.info("=== Einde dry-run-cost (stoppen vóór API-calls) ===")
        return

    logger.info("Stap 5/7: Bevindingen classificeren via Claude... (scherpte=%.1f, rehash=%s)",
                scherpte, rehash)
    bevindingen = classificeer_alle_bevindingen(
        gekoppeld, miro_notities, clause_map,
        norm=norm, scherpte=scherpte, rehash=rehash,
    )

    # Stap 6: Menselijke review
    logger.info("Stap 6/7: Menselijke review...")
    bevestigde_bevindingen = review_en_bevestig(bevindingen, auto_accept=no_review)

    # Sheets opslaan (alleen als expliciet geconfigureerd of gevraagd)
    if write_sheets or os.environ.get("AUDIT_SHEETS_ID"):
        sheets_id = sla_op_in_sheets(bevestigde_bevindingen, ontbrekend)
        logger.info("Bevindingen opgeslagen in Sheets: %s", sheets_id)
    else:
        logger.info("Sheets-schrijven overgeslagen (geen AUDIT_SHEETS_ID of --write-sheets).")

    # Stap 7: Rapport en slides genereren
    logger.info("Stap 7/7: Rapport en presentatie genereren...")

    # Altijd lokaal naar disk schrijven
    from audit.report_generation import _genereer_management_summary
    try:
        management_summary = _genereer_management_summary(bevestigde_bevindingen)
    except Exception as e:
        logger.warning("Management summary genereren mislukt (%s) — placeholder gebruikt.", e)
        nc = sum(1 for b in bevestigde_bevindingen if b["classificatie"] == "NC")
        ofi = sum(1 for b in bevestigde_bevindingen if b["classificatie"] == "OFI")
        management_summary = (
            f"_(Automatische samenvatting niet beschikbaar: {e})_\n\n"
            f"Bevindingen: {len(bevestigde_bevindingen)} totaal — {nc} NC, {ofi} OFI."
        )
    # Thema-toekenning: heuristisch, optioneel verfijnd via LLM (route B)
    from audit.tabular_report import bepaal_thema
    llm_themas: dict[str, str] = {}
    if thema_llm:
        try:
            from audit.thema_classifier import verfijn_overig
            llm_themas = verfijn_overig(bevestigde_bevindingen)
        except Exception as e:
            logger.warning("LLM thema-verfijning mislukt (niet kritiek): %s", e)

    # Hang thema aan elke bevinding voor het markdown-rapport
    for i, bev in enumerate(bevestigde_bevindingen):
        bev_id = str(bev.get("id") or bev.get("_bev_id") or i)
        bev["_bev_id"] = bev_id
        bev["thema"] = llm_themas.get(bev_id) or bepaal_thema(bev)

    lokaal_pad = schrijf_rapport(
        bevestigde_bevindingen, ontbrekend, handmatige_review, management_summary, norm,
        gearchiveerd=gearchiveerd,
        scherpte=scherpte,
    )
    logger.info("Lokaal rapport: %s", lokaal_pad)

    # Tabulaire output naast markdown
    try:
        csv_pad = schrijf_csv(
            bevestigde_bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas
        )
        xlsx_pad = schrijf_excel(
            bevestigde_bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas
        )
        logger.info("Tabulair: %s  |  %s", csv_pad, xlsx_pad)
    except Exception as e:
        logger.warning("Tabulaire export mislukt (niet kritiek): %s", e)

    # Google Docs + Slides (optioneel als template geconfigureerd is)
    rapport_doc_id = None
    slides_id = None
    if os.environ.get("AUDIT_TEMPLATE_DOC_ID"):
        rapport_doc_id = genereer_rapport(
            bevestigde_bevindingen, ontbrekend, handmatige_review, norm
        )
        slides_id = genereer_slides(bevestigde_bevindingen, norm)
        logger.info("Rapport:     https://docs.google.com/document/d/%s", rapport_doc_id)
        logger.info("Presentatie: https://docs.google.com/presentation/d/%s", slides_id)
    else:
        logger.info("AUDIT_TEMPLATE_DOC_ID niet ingesteld — Google Docs/Slides overgeslagen.")

    # Optioneel: Calendar + Gmail (alleen als Drive-output aangemaakt is)
    if rapport_doc_id and slides_id:
        stuur_calendar_uitnodiging(rapport_doc_id, slides_id, norm)
        stuur_gmail_notificatie(rapport_doc_id, slides_id, norm, bevestigde_bevindingen)

    logger.info("=== Audit pipeline klaar ===")


def main():
    parser = argparse.ArgumentParser(description="ISO Audit Pipeline")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
        help="Toepasselijke norm (default: waarde van AUDIT_NORM in .env)",
    )
    parser.add_argument(
        "--setup-template",
        action="store_true",
        help="Maak het rapporttemplate aan in Drive (éénmalig)",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Dry-run met synthetische testdata; geen Drive/Claude/Sheets-verbinding vereist",
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Sla interactieve review over en accepteer alle Claude-classificaties",
    )
    parser.add_argument(
        "--write-sheets",
        action="store_true",
        help="Schrijf bevindingen naar Google Sheets (vereist gws auth login)",
    )
    parser.add_argument(
        "--scherpte",
        type=float,
        default=float(os.environ.get("AUDIT_SCHERPTE", "1.0")),
        metavar="0.0-1.0",
        help="Classificatie-scherpte: 1.0=strikt (default), 0.5=genuanceerd (PDCA)",
    )
    parser.add_argument(
        "--chapter",
        default=None,
        metavar="N",
        help="Beperk tot één hoofdstuk (bv. 4, 8, 5.1). Vermindert API-calls sterk.",
    )
    parser.add_argument(
        "--thema-llm",
        action="store_true",
        help="Verfijn thema-toekenning via LLM voor 'Overig'-findings (route B, enkele Haiku-calls)",
    )
    parser.add_argument(
        "--rehash",
        action="store_true",
        help="Ignoreer checkpoint en herclassificeer alle (doc, clausule, norm) combinaties (UPSERT)",
    )
    parser.add_argument(
        "--dry-run-cost",
        action="store_true",
        help="Toon alleen kostenschatting van de classificatie-stap — géén API-calls voor LLM",
    )
    args = parser.parse_args()

    if args.local_only:
        run_local_only(args.norm)
    elif args.setup_template:
        _valideer_env()
        run_setup_template()
    else:
        _valideer_env()
        run_audit(args.norm, no_review=args.no_review, write_sheets=args.write_sheets,
                  chapter=args.chapter, scherpte=args.scherpte, thema_llm=args.thema_llm,
                  rehash=args.rehash, dry_run_cost=args.dry_run_cost)


if __name__ == "__main__":
    main()
