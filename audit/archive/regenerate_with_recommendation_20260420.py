"""
Eenmalige regenerate — management summary + aanvullende auditor-aanbeveling.

Na de update aan bevinding 7996 (5.14 delete): genereer LLM-summary, plak
daar een lead-auditor-gecureerde aanvullende aanbeveling achter over
softwarecatalogus en innovatiebeheer, schrijf markdown + CSV + Excel + HTML.
"""

import csv
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

from audit.tabular_report import lees_uit_db, schrijf_csv, schrijf_excel, bepaal_thema
from audit.local_report import schrijf_rapport
from audit.report_generation import _genereer_management_summary
from audit.md_to_html import converteer


AANVULLENDE_AANBEVELING = """

---

**AANVULLENDE AANBEVELING LEAD-AUDITOR — Softwarecatalogus en innovatiebeheer (ISO 9001 §8.2)**

Projectborging functioneert (geborgd door Remco Damhuis). Twee aandachtspunten die als sterke aanbeveling worden opgenomen:

1. **Softwarecatalogus** — de huidige registratie is onvolledig. ISO 9001 §8.2 vereist dat vastgestelde klant- en product-/dienst­eisen worden vastgelegd, overgedragen en gecontroleerd. Versterking van de softwarecatalogus (wat draait er, welke versie, welke klant, welke eisen) is nodig om aan deze eis aantoonbaar te voldoen.

2. **Innovatie- en AI-projecten** — opzet verdient scherpere structuur. Nu ontbreekt een heldere PDCA-cyclus op deze projecten. Risico: onvoldoende zicht op lopende activiteiten en drift weg van de vastgestelde doelstellingen. Aanbeveling: PDCA-ritme (plan → uitvoering → review → bijstellen) per innovatie-/AI-project; periodieke MT-rapportage.
"""


def main():
    bevs = lees_uit_db(norm="beide")
    with open("output/audit_reports/Bevindingen_beide_2026-04-20_s05.csv") as f:
        thema_map = {
            (r["doc_id"], r["clausule"], r["classificatie"]): r["thema"]
            for r in csv.DictReader(f)
        }
    for b in bevs:
        b["clausule_titel"] = ""
        k = (b.get("doc_id", ""), b["clausule"], b["classificatie"])
        b["thema"] = thema_map.get(k) or bepaal_thema(b)

    llm_summary = _genereer_management_summary(bevs)
    full_summary = llm_summary + AANVULLENDE_AANBEVELING

    md = schrijf_rapport(bevs, [], [], full_summary, norm="beide", scherpte=0.5)
    schrijf_csv(bevs, norm="beide", scherpte=0.5)
    schrijf_excel(bevs, norm="beide", scherpte=0.5)
    html = converteer(md)

    from collections import Counter
    cls = Counter(b["classificatie"] for b in bevs)
    print(f"DB totalen: NC={cls['NC']}, OFI={cls['OFI']}, positief={cls['positief']}, totaal={sum(cls.values())}")
    print(f"MD:   {md}")
    print(f"HTML: {html}")


if __name__ == "__main__":
    main()
