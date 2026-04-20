"""
Markdown → standalone HTML voor visuele preview van het auditrapport.

Gebruikt python-markdown met de standaard `tables`, `toc`, `fenced_code` en
`attr_list` extensies. Minimal CSS inline — geen externe dependencies bij render.

Gebruik:
  python3 -m audit.md_to_html output/audit_reports/Auditrapport_beide_2026-04-20_s05.md
  python3 -m audit.md_to_html <md_pad> [--output <html_pad>]
"""

import argparse
import os
import sys

import markdown


CSS = """
:root {
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #666;
  --border: #e1e4e8;
  --nc: #d73a49;
  --ofi: #e36209;
  --pos: #22863a;
  --accent: #0969da;
  --code-bg: #f6f8fa;
}
html, body {
  margin: 0;
  padding: 0;
  color: var(--fg);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.55;
}
.page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 2.5em;
  max-width: 1280px;
  margin: 0 auto;
  padding: 2em;
  align-items: start;
}
main { min-width: 0; }
h1 { border-bottom: 2px solid var(--border); padding-bottom: 0.3em; }
h2 { border-bottom: 1px solid var(--border); padding-bottom: 0.2em; margin-top: 2em; }
h3 { color: #111; margin-top: 1.6em; }
h4 {
  color: var(--accent);
  margin-top: 1em;
  padding: 0.3em 0.6em;
  background: #f0f6ff;
  border-left: 3px solid var(--accent);
  border-radius: 3px;
}
table { border-collapse: collapse; margin: 1em 0; width: 100%; }
th, td {
  border: 1px solid var(--border);
  padding: 0.4em 0.8em;
  text-align: left;
  vertical-align: top;
}
th { background: #f6f8fa; }
blockquote {
  margin: 0.5em 0;
  padding: 0.2em 1em;
  color: #333;
  border-left: 3px solid var(--border);
  background: #fafbfc;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
em { color: var(--muted); }
code { background: var(--code-bg); padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }

/* Sticky TOC in de tweede grid-kolom */
.toc {
  position: sticky;
  top: 1em;
  max-height: calc(100vh - 2em);
  overflow-y: auto;
  padding: 0.8em 1em;
  border: 1px solid var(--border);
  background: #fafbfc;
  font-size: 0.85em;
  border-radius: 4px;
}
.toc ul { padding-left: 1em; margin: 0.2em 0; }
.toc > ul { padding-left: 0; list-style: none; }
.toc li { margin: 0.15em 0; }

/* Responsive: TOC onder content op smalle schermen */
@media (max-width: 1100px) {
  .page { grid-template-columns: 1fr; gap: 1em; }
  .toc { position: static; max-height: none; order: -1; }
}
@media print {
  .toc { display: none; }
  .page { grid-template-columns: 1fr; max-width: none; padding: 0; }
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="page">
<main>
{body}
</main>
{toc}
</div>
</body>
</html>
"""


def converteer(md_pad: str, html_pad: str | None = None) -> str:
    if not os.path.exists(md_pad):
        raise FileNotFoundError(md_pad)

    with open(md_pad, encoding="utf-8") as f:
        tekst = f.read()

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "toc"],
        extension_configs={"toc": {"toc_depth": "2-4"}},
    )
    body = md.convert(tekst)
    toc = f'<nav class="toc"><strong>Inhoud</strong>{md.toc}</nav>' if md.toc else ""

    titel = os.path.basename(md_pad).rsplit(".", 1)[0]
    html = HTML_TEMPLATE.format(title=titel, css=CSS, toc=toc, body=body)

    if html_pad is None:
        html_pad = md_pad.rsplit(".", 1)[0] + ".html"

    with open(html_pad, "w", encoding="utf-8") as f:
        f.write(html)

    return html_pad


def main():
    parser = argparse.ArgumentParser(description="Markdown → standalone HTML preview")
    parser.add_argument("md_pad")
    parser.add_argument("--output", "-o", default=None, help="HTML-uitvoerpad (default: naast .md)")
    args = parser.parse_args()

    html_pad = converteer(args.md_pad, args.output)
    print(f"HTML geschreven: {html_pad}")
    print(f"Open in browser: file://{os.path.abspath(html_pad)}")


if __name__ == "__main__":
    sys.exit(main() or 0)
