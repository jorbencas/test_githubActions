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

SECTION_HEADER = (
    '<div class="not-prose mt-12 mb-6"><h2 '
    'class="inline-flex items-center gap-2 bg-gradient-to-r from-sky-800 to-cyan-500 '
    'dark:from-sky-600 dark:to-cyan-400 px-5 py-2.5 text-xs sm:text-sm font-black '
    'uppercase tracking-[0.25em] text-white dark:text-slate-900 '
    'shadow-[4px_4px_0px_0px_rgba(6,182,212,0.3)]"'
    f' id="{SECTION_ID}">{SECTION_TITLE}</h2></div>'
)

GRID_OPEN = '<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">'
GRID_CLOSE = "</div>"
CARD_PATTERN = re.compile(r'<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>', re.DOTALL)


def domain_from(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def format_card(name: str, url: str, description: str) -> str:
    dom = domain_from(url)
    favicon = f"https://www.google.com/s2/favicons?domain={dom}&sz=32"
    desc_escaped = description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    name_escaped = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    desc_html = f'\n    <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5 leading-snug">{desc_escaped}</p>' if desc_escaped else ""
    return (
        f'<a href="{url}" '
        'class="flex items-start gap-4 p-4 rounded-xl border border-slate-200 '
        'dark:border-slate-700 bg-white dark:bg-slate-900 '
        'hover:border-cyan-400 dark:hover:border-cyan-400 '
        'hover:shadow-xl hover:-translate-y-1 transition-all no-underline group">'
        f'\n  <img src="{favicon}" width="20" height="20" '
        'class="mt-1 shrink-0 rounded bg-slate-100 dark:bg-slate-800 p-0.5"'
        f' alt="{name_escaped}" loading="lazy" />'
        "\n  <div>"
        f'\n    <span class="font-bold text-slate-900 dark:text-white '
        "group-hover:text-cyan-600 dark:group-hover:text-cyan-400 "
        f'transition-colors">{name_escaped}</span>'
        f"{desc_html}"
        "\n  </div>"
        "\n</a>"
    )


def extract_existing_urls(text: str) -> set:
    seen = set()
    for u in re.findall(r"https?://[^\s\n<>\"\'\)]+", text):
        u = u.rstrip(".,;:)!?")
        if "google.com/s2/favicons" in u or "googleusercontent.com" in u:
            continue
        seen.add(u)
    return seen


def count_cards(text: str) -> int:
    return len(CARD_PATTERN.findall(text))





def card_count_from_html(text: str) -> int:
    """Count <a class=\"flex items-start gap-4...\" cards in text."""
    return len(re.findall(r'<a href="https?://[^"]+" class="flex items-start gap-4.*?</a>', text, re.DOTALL))


def find_grid_bounds(content: str, grid_start: int) -> tuple[int, int]:
    """Find matching grid close tag with depth counting for nested divs."""
    depth = 0
    i = grid_start
    while i < len(content):
        if content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return grid_start, i + 6
            i += 6
            continue
        if content[i:i+4] == '<div' and content[i+4] in (' ', '>'):
            depth += 1
            i += 4
            continue
        i += 1
    return grid_start, len(content)


def find_section_bounds(content: str, section_id: str):
    id_pattern = f'id="{section_id}"'
    idx = content.find(id_pattern)
    if idx == -1:
        return None
    grid_start = content.find(GRID_OPEN, idx)
    if grid_start == -1:
        return None
    return find_grid_bounds(content, grid_start)


def extract_sections_with_depth(content: str) -> list[tuple[str, str]]:
    """Extract (preamble_before_section, section_content) using depth-based matching."""
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


def get_next_filename(posts_dir: Path, base_name: str) -> tuple[Path, int]:
    """Return (path, index) for the next resources file. index=0 is resources.mdx."""
    for i in range(100):
        name = base_name if i == 0 else f"{base_name.rstrip('.mdx')}{i+1}.mdx"
        path = posts_dir / name
        if not path.exists():
            return path, i
    raise RuntimeError("Too many resources files (>100)")


def generate_frontmatter(index: int, total: int, card_count: int) -> str:
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


def extract_category_name(section_html: str) -> str:
    """Extract category name from section header, stripping emoji."""
    m = re.search(r'<h2[^>]*>([^<]+)</h2>', section_html)
    if not m:
        return ""
    text = m.group(1).strip()
    parts = text.split(None, 1)
    if parts and len(parts) > 1 and not re.search(r'[a-zA-Z0-9]', parts[0]):
        return parts[1].strip().lower()
    return text.lower()


def reorder_resources(posts_dir: Path, max_cards: int):
    """Merge all resources*.mdx, sort sections alphabetically, redistribute into ≤max_cards per file."""
    existing = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing:
        print("⚠️  No hay resources*.mdx para reordenar.")
        return

    # Extract frontmatter + intro preamble (before first section) from first file
    first_content = existing[0].read_text(encoding="utf-8")
    parts = extract_sections_with_depth(first_content)
    preamble_text = ""
    for t, content in parts:
        if t == "preamble":
            preamble_text = content
            break

    fm_end = first_content.find("---", 3)
    frontmatter = first_content[:fm_end + 3] if fm_end != -1 else first_content

    # Strip ALL frontmatter blocks from preamble_text to avoid duplication
    while preamble_text.startswith("---"):
        fm_close = preamble_text.find("---", 3)
        if fm_close == -1:
            break
        preamble_text = preamble_text[fm_close + 3:].lstrip("\n")

    # Collect all sections from all files
    all_sections = []
    total_card_count = 0
    for f in existing:
        c = f.read_text(encoding="utf-8")
        sp = extract_sections_with_depth(c)
        for t, content in sp:
            if t == "section":
                cat = extract_category_name(content)
                cards = CARD_PATTERN.findall(content)
                if cards:
                    total_card_count += len(cards)
                    all_sections.append((cat, content))

    all_sections.sort(key=lambda x: x[0])
    print(f"📊 {len(all_sections)} secciones ({total_card_count} tarjetas) ordenadas alfabéticamente")

    # Redistribute into files
    file_index = 0
    written_files = []
    section_ptr = 0

    while section_ptr < len(all_sections):
        is_first = file_index == 0
        file_cards = 0
        file_sections = []

        while section_ptr < len(all_sections):
            _, sec_html = all_sections[section_ptr]
            sec_count = len(CARD_PATTERN.findall(sec_html))
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
            fm = generate_frontmatter(file_index, 0, file_cards)
            content = fm + "\n" + body
            if file_index <= len(existing) - 1:
                path = existing[file_index]
            else:
                path, _ = get_next_filename(posts_dir, "resources.mdx")

        path.write_text(content, encoding="utf-8")
        written_files.append(path)
        print(f"   {path.name}: {file_cards} tarjetas ({len(file_sections)} secciones)")
        file_index += 1

    # Remove excess files
    for f in existing:
        if f not in written_files:
            f.unlink()
            print(f"   🗑️  Eliminado {f.name} (sobrante)")

    print(f"\n✅ Reordenación completa: {len(written_files)} archivo(s)")


def main():
    parser = argparse.ArgumentParser(description="Manage blog resources files with auto-pagination")
    parser.add_argument("--blog-path", default="blog", help="Path to the blog checkout directory")
    parser.add_argument("--tools-file", default="files/herramientas.json", help="Path to herramientas.json")
    parser.add_argument("--max-cards", type=int, default=RESOURCES_PER_FILE, help="Max cards per file")
    parser.add_argument("--clean", action="store_true", help="Check URLs and remove dead resources")
    parser.add_argument("--reorder", action="store_true", help="Reordenar todas las categorías alfabéticamente y redistribuir en ≤500 tarjetas")
    args = parser.parse_args()

    blog_path = Path(args.blog_path).resolve()
    tools_file = Path(args.tools_file)
    if not tools_file.exists():
        tools_file = blog_path.parent / args.tools_file

    posts_dir = blog_path / "src" / "content" / "posts"
    base_name = "resources.mdx"
    max_cards = args.max_cards

    # Find all existing resources files
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

    # Fix broken cards: añadir </a> si falta entre </div> y el siguiente card
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

    # Ensure all resources files have the "recursos" tag in frontmatter
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

    # ── Reorder: merge, sort alphabetically, redistribute ──
    if args.reorder:
        reorder_resources(posts_dir, max_cards)
        # Re-scan after reorder
        existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # ── Clean: check URLs and remove dead resources ──
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

    # Load tools from herramientas.json
    new_tools = []
    if tools_file.exists():
        with open(tools_file, "r", encoding="utf-8") as f:
            herramientas = json.load(f)

        # Find all existing URLs across all resources files
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

    # Find the active file (the last one that has room)
    active_file = existing_files[-1]
    active_content = active_file.read_text(encoding="utf-8")
    active_card_count = count_cards(active_content)
    active_index = len(existing_files) - 1

    print(f"\n📄 Archivo activo: {active_file.name} ({active_card_count}/{max_cards} tarjetas)")

    # Add new tools to the active file
    if new_tools:
        print(f"\n➕ Añadiendo {len(new_tools)} nuevas herramientas...")

        cards = []
        for t in new_tools:
            name = t.get("titulo", domain_from(t.get("enlace", "")))
            desc = t.get("descripcion", "")
            url = t.get("enlace", "")
            cards.append(format_card(name, url, desc))

        cards_block = "\n\n".join(cards)
        bounds = find_section_bounds(active_content, SECTION_ID)

        if bounds:
            grid_start, grid_end = bounds
            before = active_content[:grid_end]
            after = active_content[grid_end:]
            active_content = before + "\n\n" + cards_block + "\n" + after
        else:
            separator = "\n\n---\n\n" if active_content.rstrip().endswith("</div>") else "\n\n"
            block = (
                separator
                + SECTION_HEADER
                + "\n"
                + GRID_OPEN
                + "\n\n"
                + cards_block
                + "\n\n"
                + GRID_CLOSE
                + "\n"
            )
            active_content = active_content.rstrip() + block

        active_file.write_text(active_content, encoding="utf-8")
        active_card_count = count_cards(active_content)
        print(f"   {active_file.name} ahora tiene {active_card_count} tarjetas")
    else:
        print("✅ No hay herramientas nuevas que añadir.")

    # Check if we need to paginate (active file exceeds max)
    if active_card_count > max_cards:
        print(f"\n📄 {active_file.name} excede {max_cards} tarjetas. Paginando...")

        # Extract sections with depth-based parsing
        parts = extract_sections_with_depth(active_content)
        sections = [p[1] for p in parts if p[0] == "section"]
        preambles = [p[1] for p in parts if p[0] == "preamble"]

        if not sections:
            print("⚠️  No se pudieron identificar secciones para paginar.")
            sys.exit(0)

        # Frontmatter is the content before the first section
        preamble_text = preambles[0] if preambles else active_content

        # Determine split: move sections until the kept file has <= max_cards
        total_sections = len(sections)
        kept_sections = []
        overflow_sections = []
        kept_count = 0

        for s in sections:
            s_cards = len(CARD_PATTERN.findall(s))
            if kept_count + s_cards <= max_cards:
                kept_sections.append(s)
                kept_count += s_cards
            else:
                overflow_sections.append(s)

        if overflow_sections:
            new_index = active_index + 1
            new_path, _ = get_next_filename(posts_dir, "resources.mdx")
            new_name = new_path.name

            overflow_card_count = sum(len(CARD_PATTERN.findall(s)) for s in overflow_sections)

            # Write the new file
            new_frontmatter = generate_frontmatter(new_index, 0, overflow_card_count)
            new_content = new_frontmatter.strip() + "\n\n" + "\n\n".join(overflow_sections) + "\n"
            new_path.write_text(new_content, encoding="utf-8")
            print(f"   ✅ Creado {new_name} con {overflow_card_count} tarjetas ({len(overflow_sections)} secciones)")

            # Update the kept file
            kept_content = preamble_text + "\n" + "\n\n".join(kept_sections) + "\n"
            active_file.write_text(kept_content, encoding="utf-8")
            print(f"   ✅ {active_file.name} ahora tiene {kept_count} tarjetas ({len(kept_sections)} secciones)")

            total_cards = kept_count + overflow_card_count
        else:
            print("   ⚠️  No se pudo dividir - tarjetas concentradas en pocas secciones grandes.")
    else:
        print(f"\n✅ {active_file.name} tiene {active_card_count}/{max_cards} tarjetas - no necesita paginación.")


if __name__ == "__main__":
    main()
