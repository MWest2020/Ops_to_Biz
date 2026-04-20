"""
HTML → PDF converter via Chrome headless.

Chrome rendert de volledige CSS (grid, sticky TOC, conditional formatting)
snel en betrouwbaar. WeasyPrint (Python-native alternatief) bleek traag op
lange rapporten met complex grid-layout — Chrome headless is boring &
auditable.

Vereist: google-chrome of chromium in PATH.

Gebruik:
  python3 -m audit.html_to_pdf output/audit_reports/Auditrapport_beide_2026-04-20_s05.html
  python3 -m audit.html_to_pdf <html_pad> [--output <pdf_pad>]
"""

import argparse
import os
import shutil
import subprocess
import sys


def _vind_chrome() -> str:
    for cmd in ("google-chrome", "chromium", "chrome"):
        pad = shutil.which(cmd)
        if pad:
            return pad
    raise FileNotFoundError(
        "Geen Chrome/Chromium gevonden. Installeer google-chrome of chromium."
    )


def converteer(html_pad: str, pdf_pad: str | None = None) -> str:
    if not os.path.exists(html_pad):
        raise FileNotFoundError(html_pad)
    if pdf_pad is None:
        pdf_pad = html_pad.rsplit(".", 1)[0] + ".pdf"

    chrome = _vind_chrome()
    abs_html = os.path.abspath(html_pad)
    abs_pdf = os.path.abspath(pdf_pad)

    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={abs_pdf}",
            f"file://{abs_html}",
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return pdf_pad


def main():
    parser = argparse.ArgumentParser(description="HTML → PDF via WeasyPrint")
    parser.add_argument("html_pad")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    pad = converteer(args.html_pad, args.output)
    print(f"PDF geschreven: {pad} ({os.path.getsize(pad) / 1024:.0f} KB)")


if __name__ == "__main__":
    sys.exit(main() or 0)
