#!/usr/bin/env python3
"""Gestión automática de resources*.mdx: añade herramientas, paginación automática, limpieza, dedup, traducción."""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from google import genai

from scripts.utils.constants_downloadfile import CONFIG, BLOG_PATH_DEFAULT, HERRAMIENTAS_PATH_DEFAULT

RESOURCES_PER_FILE = 500
SECTION_ID = "nuevas-herramientas"
SECTION_TITLE = "\U0001f1f9 Nuevas Herramientas Descubiertas"

IMPORT_BLOCK = (
    "import ResourceCard from '@components/ResourceCard.astro';\n"
    "import ResourceCategory from '@components/ResourceCategory.astro';\n"
)

# ── Component Templates ───────────────────────────────────────────────────────

CARD_TEMPLATE = """\
<ResourceCard
  href="{url}"
  title="{name}"
  description="{desc}"
/>"""

SECTION_TEMPLATE = """\
<ResourceCategory id="{section_id}" title="{section_title}">

{cards}

</ResourceCategory>"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def domain_from(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def escape_component(text: str) -> str:
    return text.replace('"', "&quot;")


def format_card(name: str, url: str, description: str) -> str:
    name_esc = name.replace('"', "&quot;")
    desc_esc = description.replace('"', "&quot;")
    return CARD_TEMPLATE.format(url=url, name=name_esc, desc=desc_esc)


def extract_existing_urls(text: str) -> set:
    seen = set()
    for u in re.findall(r"https?://[^\s\n<>\"\'\)]+", text):
        u = u.rstrip(".,;:)!?")
        if "google.com/s2/favicons" in u or "googleusercontent.com" in u:
            continue
        seen.add(u)
    return seen


def count_cards(text: str) -> int:
    return len(re.findall(r'<ResourceCard\n', text))


# ── Section Parsing (new component format) ────────────────────────────────────

SECTION_OPEN_RE = re.compile(
    r'<ResourceCategory id="([^"]*)" title="([^"]*)">'
)

def find_section_bounds(content: str, section_start: int) -> tuple[int, int]:
    """Find matching </ResourceCategory> with depth counting."""
    depth = 0
    i = section_start
    open_tag = '<ResourceCategory'
    close_tag = '</ResourceCategory>'
    open_len = len(open_tag)
    close_len = len(close_tag)
    while i < len(content):
        if content[i:i + close_len] == close_tag:
            depth -= 1
            if depth == 0:
                return section_start, i + close_len
            i += close_len
            continue
        if content[i:i + open_len] == open_tag:
            depth += 1
            i += open_len
            continue
        i += 1
    return section_start, len(content)


def extract_sections(content: str) -> list[tuple[str, str]]:
    """Extract (type, content) pairs: 'preamble' or 'section'."""
    sections = []
    pos = 0
    last_end = 0

    while True:
        m = SECTION_OPEN_RE.search(content, pos)
        if not m:
            break

        _, section_end = find_section_bounds(content, m.start())
        section_text = content[m.start():section_end]

        if m.start() > last_end:
            sections.append(("preamble", content[last_end:m.start()]))
        sections.append(("section", section_text))
        last_end = section_end
        pos = section_end

    if last_end < len(content):
        sections.append(("preamble", content[last_end:]))
    return sections


def extract_category_name(section_text: str) -> str:
    m = SECTION_OPEN_RE.search(section_text)
    if not m:
        return ""
    title = m.group(2).strip()
    parts = title.split(None, 1)
    if parts and len(parts) > 1 and not re.search(r'[a-zA-Z0-9]', parts[0]):
        return parts[1].strip().lower()
    return title.lower()


# ── File Management ──────────────────────────────────────────────────────────

def has_imports(text: str) -> bool:
    return "import ResourceCard from" in text


def ensure_imports(text: str) -> str:
    if has_imports(text):
        return text
    fm_end = text.find("---", 3)
    if fm_end == -1:
        return text
    fm_end += 3
    return text[:fm_end] + "\n" + IMPORT_BLOCK + "\n" + text[fm_end:]


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

CARD_URL_RE = re.compile(r'href="(https?://[^"]+)"')


def extract_card_urls(section_text: str) -> list[str]:
    return CARD_URL_RE.findall(section_text)


def merge_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Merge sections with the same category name, deduplicating cards by URL."""
    merged: dict[str, list[str]] = {}
    section_titles: dict[str, str] = {}

    for cat, text in sections:
        m = SECTION_OPEN_RE.search(text)
        if m:
            section_titles[cat] = m.group(2)
        if cat not in merged:
            merged[cat] = []
            section_titles.setdefault(cat, "")

        card_pattern = re.compile(
            r'<ResourceCard\n  href="[^"]+"\n  title="[^"]+"\n  description="[^"]*"\n/>',
            re.DOTALL,
        )
        seen_urls = set(extract_card_urls("\n".join(merged.get(cat, []))))
        for card in card_pattern.findall(text):
            url_match = re.search(r'href="(https?://[^"]+)"', card)
            if url_match and url_match.group(1) not in seen_urls:
                merged[cat].append(card)
                seen_urls.add(url_match.group(1))

    result = []
    for cat in merged:
        title = section_titles.get(cat, cat)
        cards_block = "\n\n".join(merged[cat])
        result.append((
            cat,
            SECTION_TEMPLATE.format(section_id=cat, section_title=title, cards=cards_block),
        ))
    return result


def _extract_all_sections(existing: list[Path]) -> tuple[str, list[tuple[str, str]], int]:
    """Extract all sections from all files, returning (preamble, sections, total_cards)."""
    first_content = existing[0].read_text(encoding="utf-8")
    parts = extract_sections(first_content)
    preamble_text = ""
    for t, content in parts:
        if t == "preamble":
            preamble_text = content
            break

    all_sections = []
    total_card_count = 0
    for f in existing:
        c = f.read_text(encoding="utf-8")
        sp = extract_sections(c)
        for t, content in sp:
            if t == "section":
                cat = extract_category_name(content)
                cards = re.findall(r'<ResourceCard\n', content)
                if cards:
                    total_card_count += len(cards)
                    all_sections.append((cat, content))

    return preamble_text, all_sections, total_card_count


def deduplicate_all_files(posts_dir: Path) -> int:
    """Deduplicate cards by URL across all resources*.mdx files. Keeps all files intact."""
    existing = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing:
        print("⚠️  No hay resources*.mdx para deduplicar.")
        return 0

    print(f"📂 Procesando {len(existing)} archivos...")

    total_removed = 0
    global_seen_urls = set()
    
    for f in existing:
        content = f.read_text(encoding="utf-8")
        original_len = len(content)

        # Extract sections
        parts = extract_sections(content)
        new_parts = []
        removed_in_file = 0

        for part_type, part_content in parts:
            if part_type == "preamble":
                new_parts.append(part_content)
            else:
                # Deduplicate cards across all files
                card_pattern = re.compile(
                    r'<ResourceCard\n  href="([^"]+)"\n  title="[^"]+"\n  description="[^"]*"\n/>',
                    re.DOTALL,
                )
                cards = card_pattern.findall(part_content)
                unique_cards = []
                for card_match in card_pattern.finditer(part_content):
                    url = card_match.group(1)
                    if url not in global_seen_urls:
                        global_seen_urls.add(url)
                        unique_cards.append(card_match.group(0))
                    else:
                        removed_in_file += 1

                # Rebuild section with only unique cards
                if unique_cards:
                    section_open = SECTION_OPEN_RE.search(part_content)
                    if section_open:
                        section_id = section_open.group(1)
                        section_title = section_open.group(2)
                        new_section = SECTION_TEMPLATE.format(
                            section_id=section_id,
                            section_title=section_title,
                            cards="\n\n".join(unique_cards),
                        )
                        new_parts.append(new_section)

        if removed_in_file > 0:
            new_content = "\n\n".join(new_parts) + "\n"
            new_content = ensure_imports(new_content)
            f.write_text(new_content, encoding="utf-8")
            print(f"   {f.name}: {removed_in_file} tarjetas duplicadas eliminadas")
            total_removed += removed_in_file
        else:
            print(f"   {f.name}: sin duplicados")

    print(f"\n✅ Deduplicación completa: {total_removed} tarjetas duplicadas eliminadas en {len(existing)} archivos")
    return total_removed


def translate_descriptions(posts_dir: Path):
    """Translate English card descriptions to Spanish using Gemini."""
    existing = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing:
        print("⚠️  No hay resources*.mdx para traducir.")
        return

    api_key = CONFIG.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  No se encontró GEMINI_KEY en CONFIG ni GEMINI_API_KEY en entorno.")
        return
    client = genai.Client(api_key=api_key)

    card_pattern = re.compile(
        r'<ResourceCard\n  href="[^"]+"\n  title="[^"]+"\n  description="([^"]*)"\n/>',
        re.DOTALL,
    )

    # Heuristic: descriptions with >=60% ASCII letters likely need translation
    def needs_translation(desc: str) -> bool:
        if not desc.strip():
            return False
        letters = [c for c in desc if c.isalpha()]
        if not letters:
            return False
        ascii_letters = sum(1 for c in letters if c.isascii())
        return (ascii_letters / len(letters)) >= 0.6

    total_translated = 0

    for f in existing:
        content = f.read_text(encoding="utf-8")
        matches = list(card_pattern.finditer(content))
        to_translate = [(m.start(1), m.end(1), m.group(1)) for m in matches if needs_translation(m.group(1))]

        if not to_translate:
            continue

        # Build batch prompt
        lines = [f"{i}: {desc}" for i, (_, _, desc) in enumerate(to_translate)]
        batch_text = "\n".join(lines)
        prompt = (
            "Traduce al español las siguientes descripciones de herramientas/recursos tecnológicos. "
            "Mantén el tono profesional y técnico. Conserva nombres propios, marcas, y URLs sin traducir.\n\n"
            "Devuelve SOLO un JSON array con objetos: {\"id\": número, \"tr\": \"traducción\"}\n\n"
            f"{batch_text}"
        )

        modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
        translated = {}
        for modelo in modelos:
            try:
                print(f"   🤖 Traduciendo {len(to_translate)} descripciones con {modelo}...")
                response = client.models.generate_content(model=modelo, contents=prompt)
                raw_text = response.text if response.text else "[]"
                clean = re.sub(r'```(?:json)?\s*|\s*```', '', raw_text.strip())
                data = json.loads(clean)
                translated = {item["id"]: item["tr"] for item in data if "tr" in item}
                break
            except Exception as e:
                print(f"   ⚠️  Error con {modelo}: {e}")
                continue

        if not translated:
            print(f"   ⚠️  No se pudieron traducir descripciones en {f.name}")
            continue

        # Apply translations
        modified = list(content)
        for idx, (start, end, original) in enumerate(to_translate):
            if idx in translated and translated[idx].strip():
                new_desc = translated[idx].strip().replace('"', '&quot;')
                modified[start:end] = new_desc
                total_translated += 1
                if total_translated <= 5:
                    print(f"   🌍 '{original[:50]}...' → '{new_desc[:50]}...'")

        f.write_text("".join(modified), encoding="utf-8")
        print(f"   ✅ {f.name}: {len(translated)} descripciones traducidas")

    print(f"\n✅ Traducción completa: {total_translated} descripciones" if total_translated else "   ℹ️  No había descripciones que traducir")


def reorder_resources(posts_dir: Path, max_cards: int):
    """Merge all resources*.mdx, sort sections alphabetically, redistribute."""
    existing = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing:
        print("⚠️  No hay resources*.mdx para reordenar.")
        return

    preamble_text, raw_sections, total_card_count = _extract_all_sections(existing)

    # Merge sections with same category
    merged_sections = merge_sections(raw_sections)
    merged_sections.sort(key=lambda x: x[0])
    print(f"📊 {len(merged_sections)} secciones ({total_card_count} tarjetas) ordenadas alfabéticamente (duplicados fusionados)")

    file_index = 0
    written_files = []
    section_ptr = 0

    while section_ptr < len(merged_sections):
        is_first = file_index == 0
        file_cards = 0
        file_sections = []

        while section_ptr < len(merged_sections):
            _, sec_text = merged_sections[section_ptr]
            sec_count = sec_text.count('<ResourceCard\n')
            if file_cards + sec_count <= max_cards:
                file_sections.append(sec_text)
                file_cards += sec_count
                section_ptr += 1
            else:
                if not file_sections:
                    file_sections.append(sec_text)
                    file_cards += sec_count
                    section_ptr += 1
                break

        body = "\n\n".join(file_sections) + "\n"

        if is_first:
            preamble_clean = preamble_text.strip()
            content = preamble_clean + "\n\n" + body if preamble_clean else body
            path = existing[0] if existing else posts_dir / "resources.mdx"
        else:
            fm = generate_frontmatter(file_index, file_cards)
            content = fm + "\n" + body

            if file_index < len(existing):
                path = existing[file_index]
            else:
                path, _ = get_next_filename(posts_dir, "resources.mdx")

        content = ensure_imports(content)

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
    """Ensure blank line between </ResourceCategory> and next section."""
    return re.sub(
        r'(</ResourceCategory>)\s*\n(<ResourceCategory)',
        r'\1\n\n\2',
        content,
    )


def fix_malformed_cards(content: str) -> str:
    """Fix ResourceCard tags that are missing the closing > (e.g., / instead of />)."""
    return re.sub(
        r'<ResourceCard\n  href="[^"]+"\n  title="[^"]+"\n  description="[^"]*"\n/\s*\n',
        lambda m: m.group(0).rstrip() + '/>\n' if not m.group(0).rstrip().endswith('/>') else m.group(0),
        content,
    )


def fix_all_files(posts_dir: Path):
    """Fix spacing issues in all resources*.mdx files."""
    fixed_count = 0
    for rf in sorted(posts_dir.glob("resources*.mdx")):
        content = rf.read_text(encoding="utf-8")
        fixed = fix_card_spacing(content)
        fixed = fix_malformed_cards(fixed)
        if not fixed.endswith("\n"):
            fixed += "\n"
        if fixed != content:
            rf.write_text(fixed, encoding="utf-8")
            print(f"   🔧 Fixed spacing in {rf.name}")
            fixed_count += 1
    return fixed_count


def _legacy_find_grid_bounds(content: str, grid_start: int) -> tuple[int, int]:
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
        if content[i:i + 4] == '<div' and (i + 4 >= len(content) or content[i + 4] in (' ', '>')):
            depth += 1
            i += 4
            continue
        i += 1
    return grid_start, len(content)


def convert_legacy_section(section_html: str) -> str:
    """Convert a legacy HTML section to new component format."""
    m = re.search(r'<h2[^>]* id="([^"]*)">([^<]+)</h2>', section_html)
    if not m:
        return section_html
    section_id = m.group(1)
    title = m.group(2)

    cards_text = section_html[m.end():]
    grid_start = cards_text.find('<div class="not-prose grid')
    if grid_start == -1:
        return section_html

    _, grid_end = _legacy_find_grid_bounds(cards_text, grid_start)
    grid_inner_start = cards_text.index('>', grid_start) + 1
    inner = cards_text[grid_inner_start:grid_end - 6]

    card_pattern = re.compile(
        r'<a href="([^"]+)" class="flex items-start gap-4[^"]*">'
        r'\s*<img[^>]*/>'
        r'\s*<div>'
        r'\s*<span[^>]*>([^<]+)</span>'
        r'\s*<p[^>]*>(.*?)</p>'
        r'\s*</div>'
        r'\s*</a>',
        re.DOTALL
    )

    cards = []
    for cm in card_pattern.finditer(inner):
        href = cm.group(1)
        name = cm.group(2)
        desc = cm.group(3)
        desc = desc.replace('&amp;', '&')
        cards.append(format_card(name, href, desc))

    if not cards:
        return section_html

    return SECTION_TEMPLATE.format(
        section_id=section_id,
        section_title=title,
        cards="\n\n".join(cards),
    )


def convert_all_legacy_files(posts_dir: Path):
    """Convert all resources*.mdx from legacy HTML to component format."""
    converted = 0
    for rf in sorted(posts_dir.glob("resources*.mdx")):
        content = rf.read_text(encoding="utf-8")
        if has_imports(content):
            continue

        print(f"   🔄 Converting {rf.name} from legacy HTML to components...")

        parts = extract_sections(content)
        new_parts = []
        for t, text in parts:
            if t == "section":
                text = convert_legacy_section(text)
            new_parts.append(text)

        new_content = "".join(new_parts)
        new_content = ensure_imports(new_content)

        rf.write_text(new_content, encoding="utf-8")
        converted += 1
        print(f"      Done ({count_cards(new_content)} cards)")

    return converted


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Manage blog resources files with auto-pagination")
    parser.add_argument("--blog-path", default=BLOG_PATH_DEFAULT, help="Path to the blog checkout directory")
    parser.add_argument("--tools-file", default=HERRAMIENTAS_PATH_DEFAULT, help="Path to herramientas.json")
    parser.add_argument("--max-cards", type=int, default=RESOURCES_PER_FILE, help="Max cards per file")
    parser.add_argument("--clean", action="store_true", help="Check URLs and remove dead resources")
    parser.add_argument("--reorder", action="store_true", help="Reorder all categories alphabetically")
    parser.add_argument("--fix-spacing", action="store_true", help="Fix missing blank lines between sections")
    parser.add_argument("--convert", action="store_true", help="Convert legacy HTML files to component format")
    parser.add_argument("--dedup", action="store_true", help="Deduplicate sections and cards across all resources files")
    parser.add_argument("--translate", action="store_true", help="Translate English descriptions to Spanish using Gemini")
    args = parser.parse_args()

    blog_path = Path(args.blog_path).resolve()
    tools_file = Path(args.tools_file)
    if not tools_file.exists():
        tools_file = blog_path.parent / args.tools_file

    posts_dir = blog_path / "src" / "content" / "posts"

    existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    if not existing_files:
        print(f"No se encuentra ningún resources*.mdx en {posts_dir}")
        sys.exit(1)

    print(f"📂 Archivos de recursos encontrados: {len(existing_files)}")
    total_cards = 0
    for f in existing_files:
        c = count_cards(f.read_text(encoding="utf-8"))
        total_cards += c
        print(f"   {f.name}: {c} tarjetas")
    print(f"   Total: {total_cards} tarjetas")

    # Convert legacy files
    if args.convert:
        print("\n🔄 Convirtiendo archivos legacy al formato de componentes...")
        converted = convert_all_legacy_files(posts_dir)
        if converted:
            existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
            print(f"   {converted} archivo(s) convertido(s)")
        else:
            print("   No hay archivos legacy que convertir")

    # Fix spacing issues
    if args.fix_spacing:
        print("\n🔧 Corrigiendo espaciado entre secciones...")
        fixed = fix_all_files(posts_dir)
        if fixed:
            existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # Ensure imports in all files
    for rf in existing_files:
        content = rf.read_text(encoding="utf-8")
        updated = ensure_imports(content)
        if updated != content:
            rf.write_text(updated, encoding="utf-8")
            print(f"   📥 Añadidos imports a {rf.name}")

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

    # Deduplicate
    if args.dedup:
        print("\n🔁 Deduplicando secciones y tarjetas...")
        deduplicate_all_files(posts_dir)
        existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # Translate descriptions to Spanish
    if args.translate:
        print("\n🌐 Traduciendo descripciones al español...")
        translate_descriptions(posts_dir)
        existing_files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
        print()

    # Clean dead links
    if args.clean:
        print("\n🔍 Verificando enlaces de recursos...")
        for rf in existing_files:
            content = rf.read_text(encoding="utf-8")
            card_pattern = re.compile(r'(<ResourceCard\n  href="[^"]+"\n  title="[^"]+"\n  description="[^"]*"\n/>)', re.DOTALL)
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

        cards = [format_card(
            t.get("titulo", domain_from(t.get("enlace", ""))),
            t.get("enlace", ""),
            t.get("descripcion", ""),
        ) for t in new_tools]
        cards_block = "\n\n".join(cards)

        section_text = SECTION_TEMPLATE.format(
            section_id=SECTION_ID,
            section_title=SECTION_TITLE,
            cards=cards_block,
        )

        if SECTION_ID in active_content:
            # Find existing "Nuevas Herramientas" section and append cards
            m = SECTION_OPEN_RE.search(active_content)
            while m:
                if m.group(1) == SECTION_ID:
                    _, sec_end = find_section_bounds(active_content, m.start())
                    before = active_content[:sec_end - 22].rstrip('\n')
                    after = active_content[sec_end:]
                    active_content = before + "\n\n" + cards_block + "\n\n</ResourceCategory>" + after
                    break
                m = SECTION_OPEN_RE.search(active_content, m.end())
            else:
                active_content = active_content.rstrip() + "\n\n" + section_text + "\n"
        else:
            active_content = active_content.rstrip() + "\n\n" + section_text + "\n"

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

        preamble_text = preambles[0] if preambles else ""

        kept_sections = []
        overflow_sections = []
        kept_count = 0

        for s in sections:
            s_cards = s.count('<ResourceCard\n')
            if kept_count + s_cards <= args.max_cards:
                kept_sections.append(s)
                kept_count += s_cards
            else:
                overflow_sections.append(s)

        if overflow_sections:
            new_index = active_index + 1
            new_path, _ = get_next_filename(posts_dir, "resources.mdx")

            overflow_card_count = sum(s.count('<ResourceCard\n') for s in overflow_sections)

            new_frontmatter = generate_frontmatter(new_index, overflow_card_count)
            new_body = "\n\n".join(overflow_sections) + "\n"
            new_content = new_frontmatter.strip() + "\n\n" + new_body
            new_content = ensure_imports(new_content)
            new_path.write_text(new_content, encoding="utf-8")
            print(f"   ✅ Creado {new_path.name} con {overflow_card_count} tarjetas ({len(overflow_sections)} secciones)")

            kept_body = preamble_text + "\n\n" + "\n\n".join(kept_sections) + "\n" if preamble_text else "\n\n".join(kept_sections) + "\n"
            kept_body = ensure_imports(kept_body)
            active_file.write_text(kept_body, encoding="utf-8")
            print(f"   ✅ {active_file.name} ahora tiene {kept_count} tarjetas ({len(kept_sections)} secciones)")
        else:
            print("   ⚠️  No se pudo dividir - tarjetas concentradas en pocas secciones grandes.")
    else:
        print(f"\n✅ {active_file.name} tiene {active_card_count}/{args.max_cards} tarjetas - no necesita paginación.")


if __name__ == "__main__":
    main()
