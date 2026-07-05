#!/usr/bin/env python3
"""Merge free-for.dev resources into resources.mdx (card format) without duplicating."""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Categories to skip entirely (too many/low-value/well-covered)
SKIP_FF_CATEGORIES = {
    "major cloud providers", "analytics, events, and statistics",
    "email", "domain", "dns", "forms", "iaas", "paas",
    "log management", "mobile app distribution and feedback",
    "package build system", "payment and billing integration",
    "privacy management", "storage and media processing",
    "tunneling, webrtc, web socket servers and other routers",
    "translation management", "visitor session recording",
    "web hosting", "commenting platforms",
    "browser based hardware emulation", "remote desktop tools",
    "other free resources", "miscellaneous",
    "international mobile number verification api and sdk",
    "feature toggles management platforms",
    "flutter related and building ios apps without mac",
    "messaging and streaming",
}

# Map free-for.dev categories to blog categories (or None to create new)
CAT_MAP = {
    "major cloud providers": "☁️ Hosting / Nube",
    "cloud management solutions": "☁️ Hosting / Nube",
    "analytics, events, and statistics": "Analytics",
    "apis, data and ml": "🔌 APIs",
    "artifact repos": "Utilidades Dev",
    "baas": "Backend as a Service",
    "low-code platform": "Herramientas Dev",
    "cdn and protection": "☁️ Hosting / Nube",
    "ci and cd": "CI/CD",
    "cms": "📝 CMS",
    "code generation": "🤖 AI",
    "code quality": "🧪 Testing",
    "code search and browsing": "Herramientas Dev",
    "crash and exception handling": "Monitoring",
    "data visualization on maps": "🔌 APIs",
    "managed data services": "Datos",
    "design and ui": "✨ Diseño",
    "dev blogging sites": "📝 Blogs / Referencias",
    "dns": "🌐 Redes / DNS",
    "docker related": "🐳 Docker",
    "domain": "🌐 Redes / DNS",
    "education and career development": "📚 Aprendizaje",
    "email": "📧 Email",
    "feature toggles management platforms": "Herramientas Dev",
    "font": "🎨 Iconos",
    "forms": "Herramientas Dev",
    "generative ai": "🤖 AI",
    "iaas": "☁️ Hosting / Nube",
    "ide and code editing": "💻 Herramientas Terminal",
    "international mobile number verification api and sdk": "🔌 APIs",
    "issue tracking and project management": "Productividad",
    "log management": "Monitoring",
    "mobile app distribution and feedback": "Herramientas Dev",
    "management system": "Productividad",
    "messaging and streaming": "🔌 APIs",
    "miscellaneous": "Utilidades Dev",
    "monitoring": "Monitoring",
    "paas": "☁️ Hosting / Nube",
    "package build system": "Utilidades Dev",
    "payment and billing integration": "🔌 APIs",
    "privacy management": "Seguridad",
    "screenshot apis": "🔌 APIs",
    "flutter related and building ios apps without mac": "Frameworks",
    "search": "🔌 APIs",
    "security and pki": "🔒 Hacking / Seguridad",
    "authentication, authorization, and user management": "🔌 APIs",
    "source code repos": "Source Code",
    "storage and media processing": "☁️ Hosting / Nube",
    "tunneling, webrtc, web socket servers and other routers": "🌐 Redes / DNS",
    "testing": "🧪 Testing",
    "tools for teams and collaboration": "Productividad",
    "translation management": "Herramientas Dev",
    "visitor session recording": "Analytics",
    "web hosting": "☁️ Hosting / Nube",
    "commenting platforms": "CMS",
    "browser based hardware emulation": "Herramientas Dev",
    "remote desktop tools": "Herramientas Dev",
    "other free resources": "Utilidades Dev",
}

CAT_EMOJI = {
    "☁️ Hosting / Nube": "☁️",
    "🔌 APIs": "🔌",
    "🧪 Testing": "🧪",
    "📝 CMS": "📝",
    "🤖 AI": "🤖",
    "✨ Diseño": "✨",
    "📚 Aprendizaje": "📚",
    "🎨 Iconos": "🎨",
    "💻 Herramientas Terminal": "💻",
    "Productividad": "⏱️",
    "Herramientas Dev": "🔧",
    "Utilidades Dev": "🛠️",
    "🌐 Redes / DNS": "🌐",
    "📧 Email": "📧",
    "🔒 Hacking / Seguridad": "🔒",
    "Frameworks": "⚙️",
    "🐳 Docker": "🐳",
    "Analytics": "📊",
    "Monitoring": "📈",
    "Datos": "🗄️",
    "Source Code": "📦",
    "Backend as a Service": "⚡",
    "CI/CD": "🔄",
}

ICON_CATS = {}
for k in CAT_EMOJI:
    ICON_CATS[k] = CAT_EMOJI[k]


def domain_from(url):
    return urlparse(url).netloc.replace("www.", "")


def extract_existing_urls(text):
    seen = set()
    for m in re.finditer(r'href="(https?://[^"]+)"', text):
        u = m.group(1).rstrip(".,;:)!?/")
        if "google.com/s2/favicons" not in u:
            seen.add(u)
    return seen


def extract_existing_sections(text):
    """Return dict of section_name -> (start_line_of_grid_close_or_end)."""
    sections = {}
    lines = text.split("\n")
    current_h2 = None
    for i, line in enumerate(lines):
        m = re.search(r'<h2[^>]*>(.*?)</h2>', line)
        if m:
            current_h2 = m.group(1)
            sections[current_h2] = i
    return sections


def parse_freefordev(text):
    """Parse free-for.dev markdown, return list of (section, name, url, description)."""
    resources = []
    current_section = None

    for line in text.split("\n"):
        # Section heading: ## Section Name
        m = re.match(r'^##\s+(.+)', line)
        if m:
            current_section = m.group(1).strip()
            continue

        # Resource:   * [Name](url) - description
        # Or:   * [Name](url) — description  
        # Or sub-items with indentation
        m = re.match(r'\s*\*\s+\[([^\]]+)\]\(([^)]+)\)\s*[—–-]\s*(.*)', line)
        if m and current_section:
            name = m.group(1).strip()
            url = m.group(2).strip()
            desc = m.group(3).strip()
            if url and name:
                resources.append((current_section, name, url, desc))
            continue

        # Sub-bullet:     * Sub item - description (no link)
        m = re.match(r'\s+\*\s+(.+?)\s*[—–-]\s*(.*)', line)
        if m and current_section:
            # These are sub-items of a parent, skip (they're details of the main item)
            continue

        # Just a URL:   * https://example.com
        m = re.match(r'\s*\*\s+(https?://[^\s]+)', line)
        if m and current_section:
            url = m.group(1).rstrip(".,;:)")
            name = domain_from(url).split(".")[0].capitalize()
            resources.append((current_section, name, url, ""))

    return resources


from scripts.publishers.manage_resources import format_card as make_card


def make_section_header(name):
    emoji = name.split()[0] if name.split()[0] else ""
    rest = name[len(emoji):].strip() if emoji else name
    sec_id = rest.lower().replace("/", "").replace(" ", "-").replace("--", "-")
    return (
        f'<div class="not-prose mt-12 mb-6"><h2 '
        f'class="inline-flex items-center gap-2 bg-gradient-to-r from-sky-800 to-cyan-500 '
        f'dark:from-sky-600 dark:to-cyan-400 px-5 py-2.5 text-xs sm:text-sm font-black '
        f'uppercase tracking-[0.25em] text-white dark:text-slate-900 '
        f'shadow-[4px_4px_0px_0px_rgba(6,182,212,0.3)]" '
        f'id="{sec_id}">{name}</h2></div>'
    )


def find_grid_end(content, grid_start):
    close_tag = '</div>'
    grid_open = content[grid_start:grid_start + 100]
    # Count depth - find the matching close
    depth = 0
    i = grid_start
    while i < len(content):
        if content[i:i+len('<div class="not-prose')] == '<div class="not-prose':
            depth += 1
            i += 5
        elif content[i:i+len(close_tag)] == close_tag:
            depth -= 1
            if depth == 0:
                return i + len(close_tag)
            i += len(close_tag)
        else:
            i += 1
    return len(content)


def add_section_after_nav(content, section_header, cards_html):
    """Add a new section after the navigation grid."""
    nav_end = content.find('</div>\n<div class="not-prose mt-12 mb-6">')
    if nav_end == -1:
        # Fallback: find first h2
        nav_end = content.find('<div class="not-prose mt-12 mb-6">')
    insert_point = nav_end
    block = f'\n{section_header}\n<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">\n{cards_html}\n</div>\n'
    return content[:insert_point] + block + content[insert_point:]


def add_cards_to_section(content, grid_start, cards_html):
    """Add cards to an existing section's grid (inside, before closing)."""
    close_idx = content.find("</div>", grid_start)
    depth = 1
    i = grid_start + len('<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">')
    while i < len(content) and depth > 0:
        if content[i:i+4] == '<div' and content[i+4] in (' ', '>'):
            depth += 1
            i += 4
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                close_idx = i
                break
            i += 6
        else:
            i += 1
    before = content[:close_idx]
    after = content[close_idx:]
    return before + "\n" + cards_html + "\n" + after


def main():
    parser = argparse.ArgumentParser(description="Merge free-for.dev resources into blog resources.mdx")
    parser.add_argument("--blog-path", default=".", help="Path to blog repo root (default: current dir)")
    parser.add_argument("--free-dev-file", default="/tmp/free-for-dev.md", help="Path to free-for-dev README.md")
    args = parser.parse_args()

    blog_path = Path(args.blog_path).resolve()
    resources_path = blog_path / "src" / "content" / "posts" / "resources.mdx"
    free_dev_path = Path(args.free_dev_file)

    content = resources_path.read_text(encoding="utf-8")
    existing_urls = extract_existing_urls(content)
    existing_sections = extract_existing_sections(content)
    
    f_text = free_dev_path.read_text(encoding="utf-8")
    ff_resources = parse_freefordev(f_text)
    
    # Group new resources by blog category
    new_by_cat = {}
    total_new = 0
    
    MAX_PER_CATEGORY = 3
    
    for section, name, url, desc in ff_resources:
        section_lower = section.lower().strip()
        
        # Skip low-value categories
        if section_lower in SKIP_FF_CATEGORIES:
            continue
        
        url_clean = url.rstrip("/")
        if url_clean in existing_urls or url_clean + "/" in existing_urls:
            continue
        if any(u.rstrip("/") == url_clean for u in existing_urls):
            continue
        existing_urls.add(url_clean)
        
        # Map category
        blog_cat = CAT_MAP.get(section_lower, section)
        for cat_key, emoji in CAT_EMOJI.items():
            if cat_key.lower() == blog_cat.lower() or blog_cat.lower() == section_lower:
                blog_cat = cat_key
                break
        
        has_emoji = any(blog_cat.startswith(e) for e in set(CAT_EMOJI.values()) if e)
        if not has_emoji:
            emoji = CAT_EMOJI.get(blog_cat, "📌")
            blog_cat = f"{emoji} {blog_cat}"
        
        # Check per-category limit
        if blog_cat not in new_by_cat:
            new_by_cat[blog_cat] = []
        if len(new_by_cat[blog_cat]) >= MAX_PER_CATEGORY:
            continue
        
        new_by_cat[blog_cat].append((name, url, desc))
        total_new += 1
    
    if total_new == 0:
        print("No hay recursos nuevos de free-for.dev para añadir.")
        return
    
    print(f"📦 {total_new} recursos nuevos de free-for.dev para añadir en {len(new_by_cat)} categorías:")
    for cat, items in sorted(new_by_cat.items()):
        print(f"   {cat}: {len(items)}")
    
    # Build the modified content
    modified = content
    for cat, items in sorted(new_by_cat.items()):
        cards_html = "\n".join(make_card(n, u, d) for n, u, d in items)
        sec_header = make_section_header(cat)
        
        # Check if section already exists in content
        # Find by id
        emoji = cat.split()[0] if cat.split()[0] else ""
        rest = cat[len(emoji):].strip() if emoji else cat
        sec_id = rest.lower().replace("/", "").replace(" ", "-").replace("--", "-")
        pattern = f'id="{sec_id}"'
        idx = modified.find(pattern)
        
        if idx != -1:
            grid_start = modified.find('<div class="not-prose grid grid-cols-1', idx)
            if grid_start != -1:
                modified = add_cards_to_section(modified, grid_start, cards_html)
                print(f"   ➕ Añadidos {len(items)} a categoría existente: {cat}")
                continue
        
        # New section - add after navigation or at end
        modified = add_section_after_nav(modified, sec_header, cards_html)
        print(f"   🆕 Creada nueva categoría: {cat} con {len(items)} recursos")
    
    resources_path.write_text(modified, encoding="utf-8")
    print(f"\n✅ {resources_path.name} actualizado con {total_new} nuevos recursos de free-for.dev")


if __name__ == "__main__":
    main()
