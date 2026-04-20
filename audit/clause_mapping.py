"""
Taak 5: Clausule-mapping — documenten koppelen aan norm-clausules.

Laadt clause_map_<norm>.yaml en matcht documenten op zoektermen.
Rapporteert ontbrekende clausule-dekking.
"""

import logging
import os
import re
import yaml

logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def filter_clause_map(clause_map: dict, chapter: str) -> dict:
    """
    Beperk clause_map tot clausules die beginnen met het opgegeven hoofdstuk-prefix.

    Voorbeelden:
      filter_clause_map(m, "4")   → alleen 4.1, 4.2, ...
      filter_clause_map(m, "8")   → alleen 8.x (9001 én 27001)
      filter_clause_map(m, "5.1") → alleen 5.1x sub-clausules
    """
    prefix = chapter.rstrip(".") + "."
    gefilterd = {
        k: v for k, v in clause_map.get("clausules", {}).items()
        if k.startswith(prefix) or k == chapter
    }
    if not gefilterd:
        beschikbaar = sorted(
            {k.split(".")[0] for k in clause_map.get("clausules", {}).keys()}
        )
        raise ValueError(
            f"Geen clausules gevonden voor hoofdstuk '{chapter}'. "
            f"Beschikbare hoofdstukken: {', '.join(beschikbaar)}"
        )
    result = dict(clause_map)
    result["clausules"] = gefilterd
    logger.info(
        "Hoofdstuk-filter '%s': %d clausules geselecteerd", chapter, len(gefilterd)
    )
    return result


def laad_clause_map(norm: str) -> dict:
    """
    Taak 5.1: Laad de clause_map voor de gegeven norm ('9001', '27001' of 'beide').
    Bij 'beide' worden de twee maps samengevoegd.
    """
    if norm == "beide":
        map_9001 = _laad_bestand("clause_map_9001.yaml")
        map_27001 = _laad_bestand("clause_map_27001.yaml")
        samengevoegd = dict(map_9001)
        samengevoegd["clausules"] = {
            **map_9001.get("clausules", {}),
            **map_27001.get("clausules", {}),
        }
        samengevoegd["norm"] = "ISO 9001:2015 + ISO 27001:2022"
        return samengevoegd

    bestandsnaam = f"clause_map_{norm}.yaml"
    return _laad_bestand(bestandsnaam)


def _laad_bestand(bestandsnaam: str) -> dict:
    pad = os.path.join(CONFIG_DIR, bestandsnaam)
    if not os.path.exists(pad):
        raise FileNotFoundError(f"Clause-map niet gevonden: {pad}")
    with open(pad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def koppel_documenten(
    documenten: list[dict], clause_map: dict
) -> tuple[list[dict], list[dict]]:
    """
    Taken 5.2–5.3: Koppel elk document aan één of meer clausules én sub-punten via zoektermen.

    Retourneert:
      (gekoppeld, niet_geclassificeerd)
      - gekoppeld: documenten met:
          'clausules': [clausule-IDs]
          'sub_punt_matches': [(clausule_id, sub_punt_id), ...]
      - niet_geclassificeerd: documenten zonder enige match
    """
    clausules = clause_map.get("clausules", {})
    gekoppeld = []
    niet_geclassificeerd = []

    for doc in documenten:
        tekst_lower = doc.get("tekst", "").lower()
        naam_lower = doc.get("naam", "").lower()
        gecombineerd = tekst_lower + " " + naam_lower

        gevonden_clausules = []
        sub_punt_matches = []  # [(clausule_id, sub_punt_id), ...]

        for clausule_id, data in clausules.items():
            # Clausule-niveau match — hele-woord matching om valse positieven te voorkomen
            zoektermen = data.get("zoektermen", [])
            clausule_match = any(
                re.search(r'\b' + re.escape(term.lower()) + r'\b', gecombineerd)
                for term in zoektermen
            )
            if clausule_match:
                gevonden_clausules.append(clausule_id)

            # Sub-punt niveau match
            for sp in data.get("sub_punten", []):
                sp_termen = sp.get("zoektermen", [])
                if any(
                    re.search(r'\b' + re.escape(term.lower()) + r'\b', gecombineerd)
                    for term in sp_termen
                ):
                    sub_punt_matches.append((clausule_id, sp["id"]))
                    # Zorg dat clausule ook in gevonden_clausules zit
                    if clausule_id not in gevonden_clausules:
                        gevonden_clausules.append(clausule_id)

        doc_met_koppeling = {
            **doc,
            "clausules": gevonden_clausules,
            "sub_punt_matches": sub_punt_matches,
        }

        if gevonden_clausules:
            gekoppeld.append(doc_met_koppeling)
            logger.debug(
                "Document '%s' → clausules: %s, sub-punten: %s",
                doc["naam"], gevonden_clausules, sub_punt_matches,
            )
        else:
            niet_geclassificeerd.append(doc_met_koppeling)
            logger.info("Geen clausule-match voor: %s", doc["naam"])

    return gekoppeld, niet_geclassificeerd


def ontbrekende_dekking(
    gekoppelde_docs: list[dict],
    miro_notities: list[dict],
    clause_map: dict,
) -> list[dict]:
    """
    Taak 5.4: Bepaal welke clausules geen enkel document of notitie hebben.

    Retourneert lijst van dicts met clausule-info voor het validatierapport.
    """
    clausules = clause_map.get("clausules", {})

    # Verzamel alle gedekte clausule-IDs
    gedekte_ids: set[str] = set()
    for doc in gekoppelde_docs:
        gedekte_ids.update(doc.get("clausules", []))
    for notitie in miro_notities:
        if notitie.get("clausule"):
            gedekte_ids.add(notitie["clausule"])

    ontbrekend = []
    for clausule_id, data in clausules.items():
        if clausule_id not in gedekte_ids:
            ontbrekend.append({
                "clausule": clausule_id,
                "titel": data.get("titel", ""),
                "reden": "Geen gedocumenteerd bewijs gevonden",
            })
            logger.warning("Ontbrekende dekking voor clausule %s: %s",
                           clausule_id, data.get("titel", ""))

    logger.info(
        "Clausule-dekking: %d gedekt, %d ontbrekend",
        len(clausules) - len(ontbrekend),
        len(ontbrekend),
    )
    return ontbrekend
