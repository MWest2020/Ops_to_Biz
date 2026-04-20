"""
HTML → DOCX converter voor auditrapporten via htmldocx.

htmldocx wrapt python-docx en mapt HTML-elementen (h1-h4, tables, links,
strong, em, blockquote) naar Word-stijlen. CSS styling (kleur, grid layout,
sticky TOC) gaat verloren — blijft over: gestructureerde Word-document met
werkende koppen, tabellen en hyperlinks.

Gebruik:
  python3 -m audit.html_to_docx output/audit_reports/Auditrapport_beide_2026-04-20_s05.html
"""

import argparse
import os
import sys

from docx import Document
from htmldocx import HtmlToDocx


def converteer(html_pad: str, docx_pad: str | None = None) -> str:
    if not os.path.exists(html_pad):
        raise FileNotFoundError(html_pad)
    if docx_pad is None:
        docx_pad = html_pad.rsplit(".", 1)[0] + ".docx"

    with open(html_pad, encoding="utf-8") as f:
        html = f.read()

    doc = Document()
    HtmlToDocx().add_html_to_document(html, doc)
    doc.save(docx_pad)
    return docx_pad


def main():
    parser = argparse.ArgumentParser(description="HTML → DOCX via htmldocx")
    parser.add_argument("html_pad")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    pad = converteer(args.html_pad, args.output)
    print(f"DOCX geschreven: {pad} ({os.path.getsize(pad) / 1024:.0f} KB)")


if __name__ == "__main__":
    sys.exit(main() or 0)
