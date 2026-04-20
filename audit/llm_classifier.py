"""
LLM-gebaseerde clausule-classifier voor ISO 9001 documenten.

Gebruikt Claude Haiku om documenten semantisch te koppelen aan ISO 9001:2015
sub-clausules. Vervangt de keyword-gebaseerde clause_matches voor norm='9001'.

Gebruik:
  python3 -m audit.llm_classifier              # volledige run
  python3 -m audit.llm_classifier --droog      # dry-run, geen DB-wijzigingen
  python3 -m audit.llm_classifier --batch 10   # batch-grootte aanpassen
"""

import argparse
import json
import logging
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"
NORM = "9001"
MAX_TEKST = 500   # chars documenttekst mee te sturen
DEFAULT_BATCH = 8


def _bouw_sub_overzicht() -> str:
    from audit.normteksten import NORMTEKSTEN_9001
    regels = []
    for cid, data in NORMTEKSTEN_9001.items():
        for sp in data.get("sub_punten", []):
            regels.append(f"{cid}{sp['id']}: {sp['eis']}")
    return "\n".join(regels)


SUB_OVERZICHT = _bouw_sub_overzicht()

SYSTEM_PROMPT = f"""Je bent een ISO 9001:2015 interne auditor bij Conduction, een Nederlands softwarebedrijf dat open-source software maakt voor de publieke sector.

Jouw taak: bepaal voor elk aangeboden document welke ISO 9001:2015 sub-clausules het als BEWIJSLAST dekt. Een document is alleen bewijs als het aantoonbaar maakt dat de organisatie aan de eis voldoet — niet als het de eis slechts vermeldt of bespreekt.

Beschikbare sub-clausules:
{SUB_OVERZICHT}

Regels:
- Wees strikt en conservatief: liever te weinig dan te veel matches.
- Een document mag meerdere sub-clausules dekken.
- Geef een lege matches-lijst als het document geen relevante bewijslast is.
- Geef ook de clausule op hoofdniveau (bijv. "4.1" zonder sub_punt) alleen als het document de volledige clausule dekt.

Retourneer uitsluitend geldig JSON in dit formaat:
{{"resultaten": [{{"doc_id": "<id>", "matches": [{{"clausule": "4.1", "sub_punt": "b"}}]}}]}}

Gebruik exact dezelfde doc_id als aangeleverd. Geen uitleg buiten de JSON.
"""


def _classificeer_batch(
    docs: list[dict], client: anthropic.Anthropic
) -> list[dict]:
    invoer = "\n\n".join(
        f"DOC_ID: {d['id']}\nNAAM: {d['naam']}\nINHOUD: {d['tekst'][:MAX_TEKST]}"
        for d in docs
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": invoer}],
        )
        tekst = resp.content[0].text
        start = tekst.find("{")
        eind = tekst.rfind("}") + 1
        if start == -1:
            logger.warning("Geen JSON in response: %s", tekst[:100])
            return []
        return json.loads(tekst[start:eind]).get("resultaten", [])
    except (json.JSONDecodeError, anthropic.APIError) as e:
        logger.error("Fout bij batch: %s", e)
        return []


def run(batch_grootte: int = DEFAULT_BATCH, droog: bool = False) -> None:
    from audit.store import verbinding, upsert_clause_match

    conn = verbinding()
    docs = [
        dict(r)
        for r in conn.execute(
            "SELECT id, naam, tekst FROM documents WHERE herkomst='Drive' ORDER BY naam"
        ).fetchall()
    ]
    logger.info("%d documenten te classificeren (batch=%d)", len(docs), batch_grootte)

    client = anthropic.Anthropic()
    totaal_batches = (len(docs) + batch_grootte - 1) // batch_grootte
    totaal_matches = 0

    # Verifieer API-connectiviteit vóór we bestaande matches verwijderen
    if not droog:
        logger.info("API-connectiviteitscheck...")
        try:
            client.messages.create(
                model=MODEL, max_tokens=16,
                messages=[{"role": "user", "content": "ping"}],
            )
        except anthropic.APIError as e:
            logger.error("API niet beschikbaar (%s) — stop zonder DB-wijzigingen", e)
            conn.close()
            return
        logger.info("API OK — verwijder bestaande keyword-matches voor norm=%s", NORM)
        conn.execute(
            "DELETE FROM clause_matches WHERE norm=? AND herkomst='Drive'", (NORM,)
        )
        conn.commit()

    for batch_nr, i in enumerate(range(0, len(docs), batch_grootte), 1):
        batch = docs[i : i + batch_grootte]
        logger.info(
            "Batch %d/%d — %s t/m %s",
            batch_nr, totaal_batches,
            batch[0]["naam"][:40], batch[-1]["naam"][:40],
        )

        resultaten = _classificeer_batch(batch, client)
        doc_map = {d["id"]: d for d in batch}

        for res in resultaten:
            doc_id = res.get("doc_id", "")
            if doc_id not in doc_map:
                logger.warning("Onbekend doc_id in response: %s", doc_id)
                continue
            matches = res.get("matches", [])
            if not matches:
                continue

            if droog:
                logger.info(
                    "  [DROOG] %s → %s",
                    doc_map[doc_id]["naam"][:50],
                    [(m["clausule"], m.get("sub_punt", "")) for m in matches],
                )
                totaal_matches += len(matches)
                continue

            for m in matches:
                cid = m.get("clausule", "")
                sp = m.get("sub_punt", "")
                if not cid:
                    continue
                upsert_clause_match(conn, doc_id, "Drive", cid, NORM, sp)
                # Zorg ook voor clausule-niveau record
                upsert_clause_match(conn, doc_id, "Drive", cid, NORM, "")
                totaal_matches += 1

        if not droog:
            conn.commit()

    conn.close()
    logger.info(
        "Klaar: %d matches voor %d documenten (%s)",
        totaal_matches, len(docs), "DRY-RUN" if droog else "opgeslagen",
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="LLM-classifier voor ISO 9001 clausule-matching")
    parser.add_argument("--droog", action="store_true", help="Dry-run, geen DB-wijzigingen")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="Batch-grootte (default: 8)")
    args = parser.parse_args()
    run(batch_grootte=args.batch, droog=args.droog)


if __name__ == "__main__":
    main()
