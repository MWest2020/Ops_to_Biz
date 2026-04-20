"""
Audit interview — interactieve doorloop van ongedekte clausules.

Geen LLM nodig. Vraagt per ongedekte clausule of de praktijk bestaat in de org,
ook als die niet gedocumenteerd is. Antwoorden worden opgeslagen als bevindingen.

Bevindingen:
  positief   — praktijk bestaat én is (voldoende) gedocumenteerd/geborgd
  OFI        — praktijk bestaat maar is niet/onvoldoende gedocumenteerd
  NC         — praktijk bestaat niet of niet aantoonbaar
  overgeslagen — niet beantwoord (uitgesteld)

Gebruik:
  python -m audit.interview                  # beide normen, alleen gaps
  python -m audit.interview --norm 9001
  python -m audit.interview --alle           # ook al gedekte clausules
  python -m audit.interview --herinterviewen # herinterviewen van eerder beantwoorde gaps
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

_BEVINDING_KEUZES = {
    "j": "positief",
    "ja": "positief",
    "y": "positief",
    "yes": "positief",
    "d": "OFI",
    "deels": "OFI",
    "ofi": "OFI",
    "n": "NC",
    "nee": "NC",
    "no": "NC",
    "nc": "NC",
    "s": "overgeslagen",
    "skip": "overgeslagen",
    "sl": "overgeslagen",
}

_UITLEG = {
    "positief": "Praktijk bestaat en is geborgd",
    "OFI":      "Praktijk bestaat maar niet/onvoldoende gedocumenteerd (OFI)",
    "NC":       "Praktijk bestaat niet of niet aantoonbaar (NC)",
    "overgeslagen": "Uitgesteld — kom later terug",
}


def _kleur(tekst: str, code: str) -> str:
    """ANSI kleur als terminal het ondersteunt."""
    if not sys.stdout.isatty():
        return tekst
    return f"\033[{code}m{tekst}\033[0m"


def _rood(t: str) -> str:    return _kleur(t, "31")
def _groen(t: str) -> str:   return _kleur(t, "32")
def _geel(t: str) -> str:    return _kleur(t, "33")
def _blauw(t: str) -> str:   return _kleur(t, "34")
def _vet(t: str) -> str:     return _kleur(t, "1")


def _vraag_bevinding(clausule_id: str, titel: str, norm: str, bestaand: str | None) -> tuple[str, str | None, str | None]:
    """
    Stel de auditor vragen over één clausule.
    Geeft (bevinding, antwoord_samenvatting, notitie) terug.
    Gooit KeyboardInterrupt als de gebruiker wil stoppen.
    """
    print()
    print(_vet(f"━━━ {clausule_id} — {titel} ") + _blauw(f"[{norm}]"))
    if bestaand:
        print(_geel(f"  Eerder beantwoord: {bestaand}"))
    print()
    print("  Bestaat deze praktijk / dit beleid in de organisatie, ook al is het niet gedocumenteerd?")
    print()
    print(f"  {_groen('j')}a  — ja, bestaat en is geborgd  → positief")
    print(f"  {_geel('d')}eels — bestaat maar niet gedocumenteerd → OFI")
    print(f"  {_rood('n')}ee  — bestaat niet of niet aantoonbaar → NC")
    print(f"  {_blauw('s')}kip — nu overslaan")
    print(f"  q(uit) — stoppen en opslaan wat er is")
    print()

    while True:
        try:
            keuze = input("  Keuze [j/d/n/s/q]: ").strip().lower()
        except EOFError:
            raise KeyboardInterrupt

        if keuze in ("q", "quit", "exit"):
            raise KeyboardInterrupt

        bevinding = _BEVINDING_KEUZES.get(keuze)
        if not bevinding:
            print(f"  {_rood('Onbekende keuze.')} Typ j, d, n, s of q.")
            continue

        # Korte toelichting vragen (optioneel)
        notitie = None
        if bevinding != "overgeslagen":
            try:
                notitie_raw = input("  Toelichting (Enter om over te slaan): ").strip()
                notitie = notitie_raw if notitie_raw else None
            except EOFError:
                pass

        antwoord = keuze
        return bevinding, antwoord, notitie


def _haal_gaps_op(conn, norm: str) -> list[dict]:
    """
    Clausules zonder enige clause_match in de DB, voor de gegeven norm.
    """
    from audit.clause_mapping import laad_clause_map
    clause_map = laad_clause_map(norm)
    clausules = clause_map.get("clausules", {})
    norm_label = clause_map.get("norm", norm)

    matched_ids = set(
        row[0] for row in conn.execute(
            "SELECT DISTINCT clausule_id FROM clause_matches WHERE norm IN (?, 'beide')",
            (norm,)
        ).fetchall()
    )

    gaps = []
    for clausule_id, data in sorted(clausules.items()):
        if clausule_id not in matched_ids:
            gaps.append({
                "clausule_id": clausule_id,
                "titel": data.get("titel", ""),
                "norm": norm_label,
                "norm_key": norm,
            })
    return gaps


def _haal_alle_clausules_op(conn, norm: str) -> list[dict]:
    from audit.clause_mapping import laad_clause_map
    clause_map = laad_clause_map(norm)
    clausules = clause_map.get("clausules", {})
    norm_label = clause_map.get("norm", norm)
    return [
        {"clausule_id": k, "titel": v.get("titel", ""), "norm": norm_label, "norm_key": norm}
        for k, v in sorted(clausules.items())
    ]


def run_interview(norm: str, alle: bool = False, herinterviewen: bool = False) -> None:
    from audit.store import verbinding, initialiseer, upsert_interview, laad_interviews

    conn = verbinding()
    initialiseer(conn)

    # Bepaal welke clausules we behandelen
    norms = ["9001", "27001"] if norm == "beide" else [norm]
    te_behandelen: list[dict] = []

    for n in norms:
        if alle:
            te_behandelen.extend(_haal_alle_clausules_op(conn, n))
        else:
            te_behandelen.extend(_haal_gaps_op(conn, n))

    if not te_behandelen:
        print("Geen gaps gevonden. Gebruik --alle om alle clausules te behandelen.")
        conn.close()
        return

    # Bestaande interviews ophalen
    bestaande = {
        (r["clausule_id"], r["norm"]): r["bevinding"]
        for r in laad_interviews(conn)
    }

    # Filter: als herinterviewen=False, sla al beantwoorde over (tenzij --alle)
    if not herinterviewen:
        te_behandelen = [
            c for c in te_behandelen
            if (c["clausule_id"], c["norm_key"]) not in bestaande
            and (c["clausule_id"], "beide") not in bestaande
        ]

    if not te_behandelen:
        print("Alle gaps zijn al beantwoord. Gebruik --herinterviewen om opnieuw te doen.")
        conn.close()
        return

    totaal = len(te_behandelen)
    print()
    print(_vet(f"Audit interview — {totaal} clausule(s) te behandelen"))
    print("Typ q om te stoppen. Antwoorden worden direct opgeslagen.")

    gedaan = 0
    resultaten: dict[str, int] = {"positief": 0, "OFI": 0, "NC": 0, "overgeslagen": 0}

    for i, clausule in enumerate(te_behandelen, 1):
        cid = clausule["clausule_id"]
        bestaand_antwoord = bestaande.get((cid, clausule["norm_key"]))

        print()
        print(_blauw(f"  [{i}/{totaal}]"), end="")

        try:
            bevinding, antwoord, notitie = _vraag_bevinding(
                cid, clausule["titel"], clausule["norm"], bestaand_antwoord
            )
        except KeyboardInterrupt:
            print()
            print(_geel("  Gestopt. Opgeslagen antwoorden blijven bewaard."))
            break

        upsert_interview(conn, cid, clausule["norm_key"], bevinding, antwoord, notitie)
        conn.commit()
        gedaan += 1
        resultaten[bevinding] += 1

        label = _UITLEG[bevinding]
        if bevinding == "NC":
            print(f"  {_rood('→ ' + label)}")
        elif bevinding == "OFI":
            print(f"  {_geel('→ ' + label)}")
        elif bevinding == "positief":
            print(f"  {_groen('→ ' + label)}")
        else:
            print(f"  → {label}")

    conn.close()

    print()
    print(_vet("━━━ Samenvatting ━━━"))
    print(f"  Behandeld:    {gedaan}/{totaal}")
    print(f"  {_groen('Positief')}:    {resultaten['positief']}")
    print(f"  {_geel('OFI')}:         {resultaten['OFI']}")
    print(f"  {_rood('NC')}:          {resultaten['NC']}")
    print(f"  Overgeslagen: {resultaten['overgeslagen']}")
    print()
    print("Voer daarna uit:")
    print(f"  /usr/bin/python3 -m audit.landscape --norm {norm}")
    print("om het landschap opnieuw te genereren met interview-bevindingen.")


def main():
    parser = argparse.ArgumentParser(description="Audit interview — doorloop ongedekte clausules")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
    )
    parser.add_argument(
        "--alle",
        action="store_true",
        help="Behandel ook al gedekte clausules (default: alleen gaps)",
    )
    parser.add_argument(
        "--herinterviewen",
        action="store_true",
        help="Herinterviewen van al eerder beantwoorde clausules",
    )
    args = parser.parse_args()
    run_interview(args.norm, alle=args.alle, herinterviewen=args.herinterviewen)


if __name__ == "__main__":
    main()
