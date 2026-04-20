"""
Taak 9: Notificatie — Google Calendar uitnodigingen en optionele Gmail-notificatie via gws CLI.

Alle verzendacties vereisen expliciete bevestiging van de auditor.
"""

import logging
import os
import subprocess
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


def _bevestig(actie: str, ontvangers: list[str]) -> bool:
    """Taak 9.1: Vraag expliciete bevestiging vóór elke verzendactie."""
    print(f"\n{'='*60}")
    print(f"BEVESTIGING VEREIST: {actie}")
    print("Ontvangers/deelnemers:")
    for o in ontvangers:
        print(f"  - {o}")
    invoer = input("Bevestig verzending? [ja/nee]: ").strip().lower()
    return invoer in ("ja", "j", "yes", "y")


def stuur_calendar_uitnodiging(
    rapport_doc_id: str,
    slides_id: str,
    norm: str,
    deelnemers: list[str] | None = None,
    audit_datum: str | None = None,
    calendar_id: str | None = None,
) -> str | None:
    """
    Taak 9.2: Maak een Google Calendar-uitnodiging aan via gws CLI.
    Retourneert het event-ID of None als overgeslagen.
    """
    calendar_id = calendar_id or os.environ.get("AUDIT_CALENDAR_ID", "primary")
    deelnemers = deelnemers or []
    if not deelnemers:
        logger.info("Calendar-uitnodiging overgeslagen: geen deelnemers geconfigureerd")
        return None

    if not _bevestig("Google Calendar uitnodiging versturen", deelnemers):
        logger.info("Calendar-uitnodiging geannuleerd door gebruiker.")
        return None

    if audit_datum:
        start_dt = datetime.fromisoformat(audit_datum)
    else:
        start_dt = datetime.combine(date.today(), datetime.min.time().replace(hour=9))
    eind_dt = start_dt + timedelta(hours=2)

    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)

    beschrijving = (
        f"Bespreking auditresultaten {norm_label}\n\n"
        f"Auditrapport: https://docs.google.com/document/d/{rapport_doc_id}\n"
        f"Presentatie: https://docs.google.com/presentation/d/{slides_id}\n\n"
        f"Aangemaakt door geautomatiseerd audit-systeem."
    )

    cmd = [
        "gws", "calendar", "+insert",
        "--calendar", calendar_id,
        "--summary", f"Interne audit {norm_label} — bevindingspresentatie",
        "--start", start_dt.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "--end", eind_dt.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "--description", beschrijving,
    ]
    for deelnemer in deelnemers:
        cmd += ["--attendee", deelnemer]

    import json
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    event = json.loads(result.stdout)
    event_id = event.get("id", "")
    logger.info("Calendar-uitnodiging aangemaakt: %s", event_id)
    return event_id


def stuur_gmail_notificatie(
    rapport_doc_id: str,
    slides_id: str,
    norm: str,
    bevindingen: list[dict],
    ontvangers: list[str] | None = None,
) -> bool:
    """
    Taak 9.3: Verstuur optionele Gmail-notificatie via gws CLI.
    Retourneert True als verstuurd, False als overgeslagen.
    """
    ontvangers_env = os.environ.get("AUDIT_NOTIFICATIE_ONTVANGERS", "")
    ontvangers = ontvangers or [o.strip() for o in ontvangers_env.split(",") if o.strip()]

    if not ontvangers:
        logger.info("Gmail-notificatie overgeslagen: geen ontvangers geconfigureerd")
        return False

    if not _bevestig("Gmail-notificatie versturen", ontvangers):
        logger.info("Gmail-notificatie geannuleerd door gebruiker.")
        return False

    nc_count = sum(1 for b in bevindingen if b["classificatie"] == "NC")
    ofi_count = sum(1 for b in bevindingen if b["classificatie"] == "OFI")
    norm_labels = {
        "9001": "ISO 9001:2015",
        "27001": "ISO 27001:2022",
        "beide": "ISO 9001:2015 + ISO 27001:2022",
    }
    norm_label = norm_labels.get(norm, norm)

    onderwerp = f"Auditrapport {norm_label} — {date.today()}"
    tekst = (
        f"Beste collega,\n\n"
        f"Het auditrapport voor {norm_label} is gereed.\n\n"
        f"Samenvatting resultaten:\n"
        f"  Non-conformiteiten (NC): {nc_count}\n"
        f"  Kansen voor verbetering (OFI): {ofi_count}\n\n"
        f"Documenten:\n"
        f"  Auditrapport: https://docs.google.com/document/d/{rapport_doc_id}\n"
        f"  Presentatie:  https://docs.google.com/presentation/d/{slides_id}\n\n"
        f"Met vriendelijke groet,\n"
        f"Geautomatiseerd Audit Systeem\n"
        f"Datum: {date.today()}"
    )

    for ontvanger in ontvangers:
        subprocess.run(
            [
                "gws", "gmail", "+send",
                "--to", ontvanger,
                "--subject", onderwerp,
                "--body", tekst,
            ],
            check=True,
            capture_output=True,
        )
        logger.info("E-mail verstuurd naar: %s", ontvanger)

    return True
