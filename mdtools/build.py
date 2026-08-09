#!/usr/bin/env python3
"""Genera las páginas HTML de mdtools en public/mdtools/."""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.constants_mdtools import (
    MDTOOLS_BASE_TEMPLATE, MDTOOLS_NAV_HTML,
    MDTOOLS_HOME_CONTENT, MDTOOLS_PDF_CONTENT, MDTOOLS_SLIDES_CONTENT,
    MDTOOLS_TABLE_CONTENT, MDTOOLS_SNIPPETS_CONTENT, MDTOOLS_CHEATSHEET_CONTENT,
    MDTOOLS_JS_CONFIG,
)

OUTPUT_DIR = os.path.join("public", "mdtools")
CSS_DIR = os.path.join(OUTPUT_DIR, "css")
JS_DIR = os.path.join(OUTPUT_DIR, "js")

os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(JS_DIR, exist_ok=True)

def render_nav(active: str) -> str:
    keys = ["home", "pdf", "slides", "table", "snippets", "cheatsheet"]
    return MDTOOLS_NAV_HTML.format(**{f"active_{k}": "active" if k == active else "" for k in keys})

def render_page(title: str, description: str, active_nav: str, content: str,
                extra_head: str = "", extra_scripts: str = "") -> str:
    return MDTOOLS_BASE_TEMPLATE.format(
        title=title,
        description=description,
        nav=render_nav(active_nav),
        content=content,
        extra_head=extra_head,
        extra_scripts=extra_scripts,
    )

def write_page(filename: str, html: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {path}")

print("Generando mdtools...")

# ── Página principal ──
write_page("index.html", render_page(
    title="Inicio",
    description="Herramientas offline para convertir y transformar Markdown",
    active_nav="home",
    content=MDTOOLS_HOME_CONTENT,
    extra_scripts=f"<script>{MDTOOLS_JS_CONFIG}</script>",
))

# ── PDF ──
write_page("pdf.html", render_page(
    title="Markdown a PDF",
    description="Convierte Markdown a PDF con tablas, listas y código",
    active_nav="pdf",
    content=MDTOOLS_PDF_CONTENT,
    extra_head="<script src=\"https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/pdfmake.min.js\"></script>"
               "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/vfs_fonts.js\"></script>"
               "<script src=\"https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js\"></script>",
    extra_scripts="<script src=\"/mdtools/js/pdf.js\"></script>",
))

# ── Slides ──
write_page("slides.html", render_page(
    title="Diapositivas",
    description="Crea presentaciones estilo Reveal.js desde Markdown",
    active_nav="slides",
    content=MDTOOLS_SLIDES_CONTENT,
    extra_head="<script src=\"https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js\"></script>",
    extra_scripts="<script src=\"/mdtools/js/slides.js\"></script>",
))

# ── Table ──
write_page("table.html", render_page(
    title="Tabla Markdown",
    description="Genera tablas Markdown a partir de datos tabulares",
    active_nav="table",
    content=MDTOOLS_TABLE_CONTENT,
    extra_scripts="<script src=\"/mdtools/js/table.js\"></script>",
))

# ── Snippets ──
write_page("snippets.html", render_page(
    title="Snippets de Código",
    description="Extrae y formatea fragmentos de código Markdown",
    active_nav="snippets",
    content=MDTOOLS_SNIPPETS_CONTENT,
    extra_head="<script src=\"https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js\"></script>",
    extra_scripts="<script src=\"/mdtools/js/snippets.js\"></script>",
))

# ── Cheatsheet ──
write_page("cheatsheet.html", render_page(
    title="Cheatsheet",
    description="Referencia completa de Markdown y MDX con preview en vivo.",
    active_nav="cheatsheet",
    content=MDTOOLS_CHEATSHEET_CONTENT,
    extra_head="<script src=\"https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js\"></script>",
    extra_scripts="<script src=\"/mdtools/js/cheatsheet.js\"></script>",
))

print("Listo ✅")
