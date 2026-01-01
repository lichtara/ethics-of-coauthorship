#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import markdown
from weasyprint import CSS, HTML

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "livro" / "master.md"
OUTPUT = ROOT / "Ethics_of_Coauthorship_Living_Draft_v1_2026.pdf"
FONT_DIR = ROOT / "assets" / "fonts"

COVER_HTML = """
<div class="cover">
  <div class="cover-content">
    <div class="cover-title">Ethics of Coauthorship — Human–AI Responsibility in the Age of Systems</div>
    <div class="cover-subtitle">Living Draft v1.0 – 2026</div>
    <div class="cover-author">Débora Mariane da Silva Lutz</div>
    <div class="cover-institution">Lichtara Institute</div>
    <div class="cover-doi">DOI: 10.5281/zenodo.18116717</div>
  </div>
</div>
<div class="page-break"></div>
"""

CSS_STYLE = f"""
@font-face {{
  font-family: 'Inter';
  src: url('{(FONT_DIR / "Inter-VariableFont_slnt,wght.ttf").as_posix()}') format('truetype');
  font-weight: 100 900;
  font-style: normal;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{(FONT_DIR / "Inter-Italic-VariableFont_slnt,wght.ttf").as_posix()}') format('truetype');
  font-weight: 100 900;
  font-style: italic;
}}
@page {{
  size: A4;
  margin: 2.5cm;
}}
html {{
  font-size: 12pt;
}}
body {{
  font-family: 'Inter', sans-serif;
  line-height: 1.5;
  text-align: justify;
  hyphens: none;
  word-break: normal;
  overflow-wrap: normal;
  white-space: normal;
}}
.cover {{
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100vh;
}}
.cover-title {{
  font-size: 22pt;
  font-weight: 600;
  margin-bottom: 12pt;
}}
.cover-subtitle {{
  font-size: 14pt;
  margin-bottom: 18pt;
}}
.cover-author {{
  font-size: 12pt;
  margin-bottom: 4pt;
}}
.cover-institution {{
  font-size: 12pt;
  margin-bottom: 16pt;
}}
.cover-doi {{
  font-size: 11pt;
}}
.page-break {{
  page-break-before: always;
}}
h1, h2, h3 {{
  page-break-after: avoid;
}}
"""


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        _, _, remainder = text.partition("---")
        _, _, remainder = remainder.partition("---")
        return remainder.lstrip()
    return text


def remove_main_title(text: str) -> str:
    title_pattern = re.compile(r"^#\s+Ethics of Coauthorship — Human–AI Responsibility in the Age of Systems\s*$\n", re.MULTILINE)
    return title_pattern.sub("", text, count=1)


def convert_newpages(text: str) -> str:
    return text.replace("\\newpage", "<div class=\"page-break\"></div>")


def main() -> None:
    content = SOURCE.read_text(encoding="utf-8")
    content = strip_front_matter(content)
    content = remove_main_title(content)
    content = convert_newpages(content)

    md = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])
    body_html = md.convert(content)

    html = f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Ethics of Coauthorship — Human–AI Responsibility in the Age of Systems</title>
</head>
<body>
  {COVER_HTML}
  {body_html}
</body>
</html>
"""

    HTML(string=html, base_url=str(ROOT)).write_pdf(
        OUTPUT,
        stylesheets=[CSS(string=CSS_STYLE)],
    )


if __name__ == "__main__":
    main()
