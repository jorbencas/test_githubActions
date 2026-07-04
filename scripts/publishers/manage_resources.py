#!/usr/bin/env python3
"""Gestión automática de resources.mdx: añade herramientas, paginación automática, limpieza."""

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

RESOURCES_PER_FILE = 500
SECTION_ID = "nuevas-herramientas"
SECTION_TITLE = "\U0001f1f9 Nuevas Herramientas Descubiertas"

# ── HTML Templates ──────────────────────────────────────────────────────────

SECTION_HEADER_TEMPLATE = (
    '<div class="not-prose mt-12 mb-6">'
    '<h2 class="inline-flex items-center gap-2 bg-gradient-to-r from-sky-800 to-cyan-500 '
    'dark:from-sky-600 dark:to-cyan-400 px-5 py-2.5 text-xs sm:text-sm font-black '
    'uppercase tracking-[0.25em] text-white dark:text-slate-900 '
    'shadow-[4px_4px_0px_0px_rgba(6,182,212,0.3)]" id="{section_id}">'
    '{title}</h2></div>'
)

GRID_TEMPLATE = '<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">'

CARD_TEMPLATE = """\
<a href="{url}" class="flex items-start gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-cyan-400 dark:hover:border-cyan-400 hover:shadow-xl hover:-translate-y-1 transition-all no-underline group">
  <img src="{favicon}" width="20" height="20" class="mt-1 shrink-0 rounded bg-slate-100 dark:bg-slate-800 p-0.5" alt="{name}" loading="lazy" />
  <div>
    <span class="font-bold text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">{name}</span>{desc_html}
  </div>
</a>"""

CARD_DESC_TEMPLATE = '\n    <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5 leading-snug">{desc}</p>'

# ── Helpers ──────────────────────────────────────────────────────────────────

def domain_from(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def format_card(name: str, url: str, description: str) -> str:
    dom = domain_from(url)
    favicon = f"https://www.google.com/s2/favicons?domain={dom}&sz=32"
    name_esc = escape_html(name)
    desc_esc = escape_html(description)
    desc_html = CARD_DESC_TEMPLATE.format(desc=desc_esc) if desc_esc else ""
    return CARD_TEMPLATE.format(url=url, favicon=favicon, name=name_esc, desc_html=desc_html)


def extract_existing_urls(text: str) -> set:
    seen = set()
    for u in re.findall(r"https?://[^\s\n<>\"\'\)]+", text):
        u = u.rstrip(".,;:)!?")
        if "google.com/s2/favicons" in u or "googleusercontent.com" in u:
            continue
        seen.add(u)
    return seen


def count_cards(text: str) -> int:
    return len(re.findall(r'<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>', text, re.DOTALL))


# ── Section Parsing ──────────────────────────────────────────────────────────

def find_grid_bounds(content: str, grid_start: int) -> tuple[int, int]:
    """Find matching </div> for grid with depth counting."""
    depth = 0
    i = grid_start
    while i < len(content):
        if content[i:i + 6] == '</div>':
            depth -= 1
            if depth == 0:
                return grid_start, i + 6
            i += 6
            continue
        if content[i:i + 4] == '<div' and content[i + 4] in (' ', '>'):
            depth += 1
            i += 4
            continue
        i += 1
    return grid_start, len(content)


def extract_sections(content: str) -> list[tuple[str, str]]:
    """Extract (type, content) pairs: 'preamble' or 'section'."""
    sections = []
    pos = 0
    last_end = 0

    while True:
        header_start = content.find('<div class="not-prose mt-12 mb-6">', pos)
        if header_start == -1:
            break
        header_end = content.find('</h2></div>', header_start)
        if header_end == -1:
            break
        header_end += len('</h2></div>')

        grid_start = content.find('<div class="not-prose grid grid-cols-1', header_end)
        if grid_start == -1:
            break

        _, grid_end = find_grid_bounds(content, grid_start)
        section = content[header_start:grid_end]

        if header_start > last_end:
            sections.append(("preamble", content[last_end:header_start]))
        sections.append(("section", section))
        last_end = grid_end
        pos = grid_end

    if last_end < len(content):
        sections.append(("preamble", content[last_end:]))
    return sections


def extract_category_name(section_html: str) -> str:
    m = re.search(r'<h2[^>]*>([^<]+)</h2>', section_html)
    if not m:
        return ""
    text = m.group(1).strip()
    parts = text.split(None, 1)
    if parts and len(parts) > 1 and not re.search(r'[a-zA-Z0-9]', parts[0]):
        return parts[1].strip().lower()
    return text.lower()


# ── File Management ──────────────────────────────────────────────────────────

def get_next_filename(posts_dir: Path, base_name: str) -> tuple[Path, int]:
    for i in range(100):
        name = base_name if i == 0 else f"{base_name.rstrip('.mdx')}{i + 1}.mdx"
        path = posts_dir / name
        if not path.exists():
            return path, i
    raise RuntimeError("Too many resources files (>100)")


def generate_frontmatter(index: int, card_count: int) -> str:
    title = "Recursos para desarrolladores" if index == 0 else f"Recursos para desarrolladores (Página {index + 1})"
    description = f"Más de {card_count} recursos adicionales - continuación de la guía de recursos para developers."
    tags = '["recursos", "herramientas", "desarrollo-web", "api", "ia", "github", "referencias"]'
    return f"""---
draft: false
title: "{title}"
description: "{description}"
pubDate: "2025-04-01"
tags: {tags}
image: "img/resources/resources_cover-1200.webp"
author: "Jorge Beneyto Castelló"
---
"""


# ── Reorder ──────────────────────────────────────────────────────────────────

def reorder_resources(posts_dir: Path, max_cards: int):
    """Merge all resources*.mdx, sort sections alphabetically, redistribute."""
    existing = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing:
        print("⚠️  No hay resources*.mdx para reordenar.")
        return

    first_content = existing[0].read_text(encoding="utf-8")
    parts = extract_sections(first_content)
    preamble_text = ""
    for t, content in parts:
        if t == "preamble":
            preamble_text = content
            break

    fm_end = first_content.find("---", 3)
    frontmatter = first_content[:fm_end + 3] if fm_end != -1 else first_content

    while preamble_text.startswith("---"):
        fm_close = preamble_text.find("---", 3)
        if fm_close == -1:
            break
        preamble_text = preamble_text[fm_close + 3:].lstrip("\n")

    all_sections = []
    total_card_count = 0
    for f in existing:
        c = f.read_text(encoding="utf-8")
        sp = extract_sections(c)
        for t, content in sp:
            if t == "section":
                cat = extract_category_name(content)
                cards = re.findall(r'<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>', content, re.DOTALL)
                if cards:
                    total_card_count += len(cards)
                    all_sections.append((cat, content))

    all_sections.sort(key=lambda x: x[0])
    print(f"📊 {len(all_sections)} secciones ({total_card_count} tarjetas) ordenadas alfabéticamente")

    file_index = 0
    written_files = []
    section_ptr = 0

    while section_ptr < len(all_sections):
        is_first = file_index == 0
        file_cards = 0
        file_sections = []

        while section_ptr < len(all_sections):
            _, sec_html = all_sections[section_ptr]
            sec_count = len(re.findall(r'<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>', sec_html, re.DOTALL))
            if file_cards + sec_count <= max_cards:
                file_sections.append(sec_html)
                file_cards += sec_count
                section_ptr += 1
            else:
                if not file_sections:
                    file_sections.append(sec_html)
                    file_cards += sec_count
                    section_ptr += 1
                break

        if is_first:
            body = preamble_text + "\n\n" + "\n\n".join(file_sections) + "\n"
            content = frontmatter + "\n" + body
            path = posts_dir / "resources.mdx"
        else:
            body = "\n\n".join(file_sections) + "\n"
            fm = generate_frontmatter(file_index, file_cards)
            content = fm + "\n" + body
            if file_index <= len(existing) - 1:
                path = existing[file_index]
            else:
                path, _ = get_next_filename(posts_dir, "resources.mdx")

        path.write_text(content, encoding="utf-8")
        written_files.append(path)
        print(f"   {path.name}: {file_cards} tarjetas ({len(file_sections)} secciones)")
        file_index += 1

    for f in existing:
        if f not in written_files:
            f.unlink()
            print(f"   🗑️  Eliminado {f.name} (sobrante)")

    print(f"\n✅ Reordenación completa: {len(written_files)} archivo(s)")


# ── Fix Spacing ──────────────────────────────────────────────────────────────

def fix_card_spacing(content: str) -> str:
    """Ensure blank line between </a> and next <a> card."""
    return re.sub(
        r'(</a>)\s*\n(<a href="https?://[^"]+" class="flex items-start gap-4)',
        r'\1\n\n\2',
        content,
    )


def fix_all_files(posts_dir: Path):
    """Fix spacing issues in all resources*.mdx files."""
    fixed_count = 0
    for rf in sorted(posts_dir.glob("resources*.mdx")):
        content = rf.read_text(encoding="utf-8")
        fixed = fix_card_spacing(content)
        # Also ensure file ends with newline
        if not fixed.endswith("\n"):
            fixed += "\n"
        if fixed != content:
            rf.write_text(fixed, encoding="utf-8")
            print(f"   🔧 Fixed spacing in {rf.name}")
            fixed_count += 1
    return fixed_count


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Manage blog resources files with auto-pagination")
    parser.add_argument("--blog-path", default="blog", help="Path to the blog checkout directory")
    parser.add_argument("--tools-file", default="files/herramientas.json", help="Path to herramientas.json")
    parser.add_argument("--max-cards", type=int, default=RESOURCES_PER_FILE, help="Max cards per file")
    parser.add_argument("--clean", action="store_true", help="Check URLs and remove dead resources")
    parser.add_argument("--reorder", action="store_true", help="Reorder all categories alphabetically")
    parser.add_argument("--fix-spacing", action="store_true", help="Fix missing blank lines between cards")
    args = parser.parse_args()

    blog_path = Path(args.blog_path).resolve()
    tools_file = Path(args.tools_file)
    if not tools_file.exists():
        tools_file = blog_path.parent / args.tools_file

    posts_dir = blog_path / "src" / "content" / "posts"

    existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing_files:
        print(f"No se encuentra resources.mdx en {posts_dir}")
        sys.exit(1)

    print(f"📂 Archivos de recursos encontrados: {len(existing_files)}")
    total_cards = 0
    for f in existing_files:
        c = count_cards(f.read_text(encoding="utf-8"))
        total_cards += c
        print(f"   {f.name}: {c} tarjetas")
    print(f"   Total: {total_cards} tarjetas")

    # Fix spacing issues
    if args.fix_spacing:
        print("\n🔧 Corrigiendo espaciado entre cards...")
        fixed = fix_all_files(posts_dir)
        if fixed:
            existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # Fix broken </a> tags
    for rf in existing_files:
        content = rf.read_text(encoding="utf-8")
        fixed = re.sub(
            r'(?<!</a>\n)(</div>)\s*\n\s*(<a href="https?://[^"]+" class="flex items-start gap-4)',
            r'\1\n</a>\n\2',
            content,
        )
        if fixed != content:
            rf.write_text(fixed, encoding="utf-8")
            print(f"   🔧 Reparados cards sin </a> en {rf.name}")

    # Ensure "recursos" tag
    for rf in existing_files:
        content = rf.read_text(encoding="utf-8")
        fm_end = content.find('---', 3)
        if fm_end != -1 and '"recursos"' not in content[3:fm_end]:
            content = re.sub(
                r'(tags:\s*\[[^\]]*)(\])',
                r'\1, "recursos"\2',
                content,
                count=1,
            )
            rf.write_text(content, encoding="utf-8")
            print(f"   🏷️  Añadido tag 'recursos' a {rf.name}")

    # Reorder
    if args.reorder:
        reorder_resources(posts_dir, args.max_cards)
        existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # Clean dead links
    if args.clean:
        print("\n🔍 Verificando enlaces de recursos...")
        for rf in existing_files:
            content = rf.read_text(encoding="utf-8")
            card_pattern = re.compile(r'(<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>)', re.DOTALL)
            cards = card_pattern.findall(content)
            removed = 0
            checked = 0
            for card in cards:
                url_match = re.search(r'href="(https?://[^"]+)"', card)
                if not url_match:
                    continue
                url = url_match.group(1)
                checked += 1
                if checked > 30:
                    break
                try:
                    req = urllib.request.Request(url, method="HEAD")
                    req.add_header("User-Agent", "Mozilla/5.0")
                    resp = urllib.request.urlopen(req, timeout=10)
                    if resp.status >= 400:
                        content = content.replace(card, "")
                        removed += 1
                        print(f"   ❌ {resp.status} {url[:60]}")
                except Exception:
                    content = content.replace(card, "")
                    removed += 1
                    print(f"   ❌ Error al conectar: {url[:60]}")
                time.sleep(0.5)
            if removed:
                rf.write_text(content, encoding="utf-8")
                print(f"   🗑️  {rf.name}: {removed} recursos eliminados")
            else:
                print(f"   ✅ {rf.name}: sin recursos obsoletos")
        print()

    # Load new tools
    new_tools = []
    if tools_file.exists():
        with open(tools_file, "r", encoding="utf-8") as f:
            herramientas = json.load(f)

        all_existing_urls = set()
        for rf in existing_files:
            all_existing_urls |= extract_existing_urls(rf.read_text(encoding="utf-8"))

        for h in herramientas:
            url = h.get("enlace", "")
            if url and url not in all_existing_urls:
                new_tools.append(h)
                all_existing_urls.add(url)
    else:
        print(f"⚠️  No se encuentra {tools_file}. Solo se hará paginación.")

    # Find active file
    active_file = existing_files[-1]
    active_content = active_file.read_text(encoding="utf-8")
    active_card_count = count_cards(active_content)
    active_index = len(existing_files) - 1

    print(f"\n📄 Archivo activo: {active_file.name} ({active_card_count}/{args.max_cards} tarjetas)")

    # Add new tools
    if new_tools:
        print(f"\n➕ Añadiendo {len(new_tools)} nuevas herramientas...")

        cards = [format_card(t.get("titulo", domain_from(t.get("enlace", ""))), t.get("enlace", ""), t.get("descripcion", "")) for t in new_tools]
        cards_block = "\n\n".join(cards)

        # Find "Nuevas Herramientas" section or create it
        section_header = SECTION_HEADER_TEMPLATE.format(section_id=SECTION_ID, title=SECTION_TITLE)
        grid_open = GRID_TEMPLATE

        if SECTION_ID in active_content:
            # Find end of grid in existing section
            header_idx = active_content.find(f'id="{SECTION_ID}"')
            if header_idx != -1:
                grid_start = active_content.find(grid_open, header_idx)
                if grid_start != -1:
                    _, grid_end = find_grid_bounds(active_content, grid_start)
                    before = active_content[:grid_end]
                    after = active_content[grid_end:]
                    active_content = before + "\n\n" + cards_block + "\n" + after
        else:
            separator = "\n\n---\n\n" if active_content.rstrip().endswith("</div>") else "\n\n"
            block = (
                separator
                + section_header
                + "\n"
                + grid_open
                + "\n\n"
                + cards_block
                + "\n\n</div>\n"
            )
            active_content = active_content.rstrip() + block

        active_file.write_text(active_content, encoding="utf-8")
        active_card_count = count_cards(active_content)
        print(f"   {active_file.name} ahora tiene {active_card_count} tarjetas")
    else:
        print("✅ No hay herramientas nuevas que añadir.")

    # Paginate if needed
    if active_card_count > args.max_cards:
        print(f"\n📄 {active_file.name} excede {args.max_cards} tarjetas. Paginando...")

        parts = extract_sections(active_content)
        sections = [p[1] for p in parts if p[0] == "section"]
        preambles = [p[1] for p in parts if p[0] == "preamble"]

        if not sections:
            print("⚠️  No se pudieron identificar secciones para paginar.")
            sys.exit(0)

        preamble_text = preambles[0] if preambles else active_content

        kept_sections = []
        overflow_sections = []
        kept_count = 0

        for s in sections:
            s_cards = count_cards(s)
            if kept_count + s_cards <= args.max_cards:
                kept_sections.append(s)
                kept_count += s_cards
            else:
                overflow_sections.append(s)

        if overflow_sections:
            new_index = active_index + 1
            new_path, _ = get_next_filename(posts_dir, "resources.mdx")

            overflow_card_count = sum(count_cards(s) for s in overflow_sections)

            new_frontmatter = generate_frontmatter(new_index, overflow_card_count)
            new_content = new_frontmatter.strip() + "\n\n" + "\n\n".join(overflow_sections) + "\n"
            new_path.write_text(new_content, encoding="utf-8")
            print(f"   ✅ Creado {new_path.name} con {overflow_card_count} tarjetas ({len(overflow_sections)} secciones)")

            kept_content = preamble_text + "\n" + "\n\n".join(kept_sections) + "\n"
            active_file.write_text(kept_content, encoding="utf-8")
            print(f"   ✅ {active_file.name} ahora tiene {kept_count} tarjetas ({len(kept_sections)} secciones)")
        else:
            print("   ⚠️  No se pudo dividir - tarjetas concentradas en pocas secciones grandes.")
    else:
        print(f"\n✅ {active_file.name} tiene {active_card_count}/{args.max_cards} tarjetas - no necesita paginación.")


if __name__ == "__main__":
    main()
