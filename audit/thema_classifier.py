"""
LLM-gebaseerde thema-toekenning voor audit-bevindingen (route B).

Verfijnt de heuristische thema-toekenning uit tabular_report.py: voor bevindingen
waar de heuristiek 'Overig' teruggeeft wordt een LLM-batch-call gedaan om een
specifieker thema toe te kennen uit de vaste taxonomie (THEMA_LIJST).

Ontwerp-keuzes:
  - Eén batch per ~50 findings → enkele API-calls per run (vs. per-finding).
  - System prompt is statisch en gecached (ephemeral cache_control).
  - Bij fout/parse-probleem: lege dict, zodat caller heuristiek behoudt.
  - Keuze voor Haiku 4.5 voor batch-classificatie (kostenefficiënt).

Gebruik:
  from audit.thema_classifier import verfijn_overig
  llm_themas = verfijn_overig(bevindingen)
  # llm_themas: {bev_id: thema} — alleen voor findings die heuristisch 'Overig' waren
"""

import json
import logging
import os

import anthropic
from dotenv import load_dotenv

from audit.tabular_report import THEMA_LIJST, bepaal_thema

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"
BATCH_GROOTTE = 50
MAX_BESCHRIJVING_CHARS = 500
MAX_ONDERBOUWING_CHARS = 250

SYSTEM_PROMPT = (
    "Je bent een ISO 9001:2015 + ISO 27001:2022 auditor bij Conduction, een "
    "Nederlands softwarebedrijf (open-source, publieke sector).\n\n"
    "Jouw taak: wijs elke aangeboden audit-bevinding toe aan precies één thema "
    "uit de onderstaande vaste taxonomie. Kies het thema dat het KERNPROBLEEM "
    "van de bevinding beschrijft, niet een bijkomstig detail.\n\n"
    "Taxonomie (kies één):\n"
    + "\n".join(f"- {t}" for t in THEMA_LIJST)
    + "\n\nRegels:\n"
    "- Gebruik exact de thema-naam zoals hierboven geschreven.\n"
    "- Gebruik 'Overig' uitsluitend als geen ander thema passend is.\n"
    "- Baseer je keuze op de bevindingsbeschrijving + onderbouwing.\n"
    "- Retourneer uitsluitend geldig JSON:\n"
    '  {"toewijzingen": [{"id": "<id>", "thema": "<thema>"}]}\n'
    "Geen uitleg buiten de JSON."
)


def _bouw_batch_input(batch: list[dict]) -> str:
    regels = []
    for b in batch:
        bid = str(b["_bev_id"])
        cl = b.get("clausule") or b.get("clausule_id", "")
        cls = b.get("classificatie", "")
        besc = (b.get("beschrijving") or "")[:MAX_BESCHRIJVING_CHARS]
        ond = (b.get("onderbouwing") or "")[:MAX_ONDERBOUWING_CHARS]
        regels.append(
            f"ID: {bid}\nCLAUSULE: {cl} ({cls})\n"
            f"BESCHRIJVING: {besc}\nONDERBOUWING: {ond}"
        )
    return "\n\n---\n\n".join(regels)


def _verwerk_batch(
    client: anthropic.Anthropic, batch: list[dict]
) -> dict[str, str]:
    invoer = _bouw_batch_input(batch)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": invoer}],
    )
    tekst = resp.content[0].text
    start = tekst.find("{")
    eind = tekst.rfind("}") + 1
    if start == -1 or eind <= start:
        logger.warning("Geen JSON in respons — batch overgeslagen")
        return {}
    try:
        data = json.loads(tekst[start:eind])
        return {
            str(t["id"]): t["thema"]
            for t in data.get("toewijzingen", [])
            if "id" in t and "thema" in t
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("JSON parse fout: %s", e)
        return {}


def _valideer(toewijzingen: dict[str, str]) -> dict[str, str]:
    """Vervang thema's die niet in de taxonomie staan door 'Overig'."""
    geldig = set(THEMA_LIJST)
    resultaat = {}
    onbekend = 0
    for bid, thema in toewijzingen.items():
        if thema in geldig:
            resultaat[bid] = thema
        else:
            resultaat[bid] = "Overig"
            onbekend += 1
    if onbekend:
        logger.warning("%d toewijzingen met onbekend thema — vervangen door 'Overig'", onbekend)
    return resultaat


def classificeer_themas(bevindingen: list[dict]) -> dict[str, str]:
    """
    Wijs thema's toe aan alle meegegeven bevindingen via batch LLM-calls.

    Input: list[dict] — elke bev moet een `_bev_id` hebben (wordt intern gezet).
    Output: dict[str, str] — {bev_id: thema}. Lege dict bij volledige fout.
    """
    if not bevindingen:
        return {}
    try:
        client = anthropic.Anthropic()
    except Exception as e:
        logger.warning("Anthropic client init mislukt: %s — LLM-thema overgeslagen", e)
        return {}

    for i, b in enumerate(bevindingen):
        b["_bev_id"] = str(b.get("id") or b.get("_bev_id") or i)

    aantal_batches = (len(bevindingen) + BATCH_GROOTTE - 1) // BATCH_GROOTTE
    logger.info(
        "LLM thema-toekenning: %d bevindingen in %d batch(es) (model=%s)",
        len(bevindingen), aantal_batches, MODEL,
    )

    resultaat: dict[str, str] = {}
    for i in range(0, len(bevindingen), BATCH_GROOTTE):
        batch = bevindingen[i:i + BATCH_GROOTTE]
        batch_num = i // BATCH_GROOTTE + 1
        try:
            resultaat.update(_verwerk_batch(client, batch))
            logger.info("Batch %d/%d klaar (%d cumulatief)",
                        batch_num, aantal_batches, len(resultaat))
        except Exception as e:
            logger.warning("Batch %d mislukt: %s", batch_num, e)

    resultaat = _valideer(resultaat)
    logger.info("LLM thema-toekenning klaar: %d/%d toegewezen",
                len(resultaat), len(bevindingen))
    return resultaat


def verfijn_overig(bevindingen: list[dict]) -> dict[str, str]:
    """
    Hybride aanpak: alleen bevindingen die heuristisch 'Overig' krijgen
    worden via LLM opnieuw geclassificeerd.

    Gebruik deze variant om kosten/tijd laag te houden.
    """
    overig = [b for b in bevindingen if bepaal_thema(b) == "Overig"]
    if not overig:
        logger.info("Geen 'Overig'-bevindingen om via LLM te verfijnen")
        return {}
    logger.info("Verfijn %d/%d 'Overig'-bevindingen via LLM",
                len(overig), len(bevindingen))
    return classificeer_themas(overig)
