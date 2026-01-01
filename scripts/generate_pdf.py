#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List

# Ensure print dependencies are discoverable on macOS/Homebrew setups.
os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")
os.environ.setdefault("PKG_CONFIG_PATH", "/opt/homebrew/lib/pkgconfig")

import markdown
from weasyprint import CSS, HTML

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "livro" / "master.md"
OUTPUT = ROOT / "Ethics_of_Coauthorship_Living_Draft_v1_2026.pdf"
FONT_DIR = ROOT / "assets" / "fonts"

COVER_HTML = """
<div class="cover">
  <div class="cover-vfill"></div>
  <div class="cover-content">
    <div class="cover-title">Ethics of Coauthorship — Human–AI Responsibility in the Age of Systems</div>
    <div class="cover-subtitle">Living Draft v1.0 – 2026</div>
    <div class="cover-author">Débora Mariane da Silva Lutz</div>
    <div class="cover-institution">Lichtara Institute</div>
    <div class="cover-doi">DOI: 10.5281/zenodo.18116717</div>
  </div>
  <div class="cover-vfill"></div>
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
  @bottom-center {{
    content: counter(page);
    font-size: 10pt;
    color: #555;
    font-family: 'Inter', sans-serif;
  }}
}}
@page:first {{
  @bottom-center {{ content: none; }}
}}
html {{
  font-size: 12pt;
}}
body {{
  font-family: 'Inter', sans-serif;
  line-height: 1.5;
  text-align: justify;
  margin: 0;
  padding: 0;
  hyphens: none;
  -webkit-hyphens: none;
  -ms-hyphens: none;
  word-break: keep-all;
  overflow-wrap: normal;
  white-space: normal;
}}
body * {{
  hyphens: none !important;
  -webkit-hyphens: none !important;
  -ms-hyphens: none !important;
  word-break: keep-all !important;
  overflow-wrap: normal !important;
}}
.cover {{
  display: flex;
  flex-direction: column;
  height: calc(297mm - 5cm);
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  text-align: center;
}}
.cover-content {{
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.cover-vfill {{
  flex: 1;
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
  break-before: page;
}}
.part-page {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: calc(297mm - 5cm);
  min-height: 100vh;
  text-align: center;
}}
.part-title {{
  font-size: 18pt;
  font-weight: 600;
  letter-spacing: 0.5pt;
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


def remove_leading_newpage(text: str) -> str:
    return re.sub(r"^\\s*\\\\newpage\\s*", "", text, count=1)


def remove_main_title(text: str) -> str:
    title_pattern = re.compile(r"^#\s+Ethics of Coauthorship — Human–AI Responsibility in the Age of Systems\s*$\n", re.MULTILINE)
    return title_pattern.sub("", text, count=1)


def remove_invisible_breaks(text: str) -> str:
    # Strip soft hyphens, zero-width spaces and stray BOM-like markers.
    unwanted = {"\u00ad", "\ufeff", "\ufffe", "\u2060", "\u200b", "\u200c", "\u200d"}
    return "".join(ch for ch in text if ch not in unwanted)


PART_PATTERN = re.compile(r"^#{1,6}\s*(PARTE\s+[IVX]+(?:\s+—\s+.*)?)\s*$", re.IGNORECASE)


def transform_part_pages(text: str) -> str:
    lines: List[str] = text.splitlines()
    result: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        # Skip a \newpage immediately before a PART heading to avoid blank pages.
        if stripped == "\\newpage" and PART_PATTERN.match(next_line):
            i += 1
            continue

        match = PART_PATTERN.match(stripped)
        if match:
            title = match.group(1)
            result.append(f'<div class="part-page"><div class="part-title">{title}</div></div>')
            result.append('<div class="page-break"></div>')
        else:
            result.append(line)

        i += 1

    return "\n".join(result)


def convert_newpages(text: str) -> str:
    return text.replace("\\newpage", "<div class=\"page-break\"></div>")


def main() -> None:
    content = SOURCE.read_text(encoding="utf-8")
    content = strip_front_matter(content)
    content = remove_leading_newpage(content)
    content = remove_main_title(content)
    content = remove_invisible_breaks(content)
    content = transform_part_pages(content)
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
