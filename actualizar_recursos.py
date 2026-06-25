#!/usr/bin/env python3
"""Merge newly discovered tools into blog's resources.mdx and re-categorize.

Usage:
    python actualizar_recursos.py --blog-path ./blog

Reads files/herramientas.json (accumulated tool discoveries), appends new
tools to resources.mdx in a "🆕 Nuevas herramientas" section, then runs
scripts/generate_resources.py from the blog checkout to re-categorize all
entries with proper names and descriptions.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def domain_from(url: str) -> str:
    return urlparse(url).netloc.replace('www.', '')


def extract_existing_urls(text: str) -> set:
    seen = set()
    for u in re.findall(r'https?://[^\s\n<>"\'\)]+', text):
        u = u.rstrip('.,;:)!?')
        if 'google.com/s2/favicons' in u or 'googleusercontent.com' in u:
            continue
        seen.add(u)
    return seen


def main():
    parser = argparse.ArgumentParser(description="Merge tools into blog's resources.mdx")
    parser.add_argument('--blog-path', default='./blog', help='Path to the blog checkout directory')
    args = parser.parse_args()

    blog_path = Path(args.blog_path).resolve()
    resources_file = blog_path / 'src' / 'content' / 'posts' / 'resources.mdx'
    herramientas_file = Path('files/herramientas.json')

    if not herramientas_file.exists():
        print("ℹ️  No se encuentra files/herramientas.json. Sin herramientas nuevas.")
        sys.exit(2)

    with open(herramientas_file, 'r', encoding='utf-8') as f:
        herramientas = json.load(f)

    if not herramientas:
        print("ℹ️  No hay herramientas nuevas para añadir.")
        sys.exit(2)

    if not resources_file.exists():
        print(f"❌ No se encuentra {resources_file}")
        sys.exit(1)

    current_content = resources_file.read_text(encoding='utf-8')
    existing_urls = extract_existing_urls(current_content)

    new_tools = []
    for h in herramientas:
        url = h.get('enlace', '')
        if url and url not in existing_urls:
            new_tools.append(h)
            existing_urls.add(url)

    if not new_tools:
        print("ℹ️  Todas las herramientas descubiertas ya están en resources.mdx.")
        sys.exit(2)

    new_lines = []
    for t in new_tools:
        name = t.get('titulo', domain_from(t.get('enlace', '')))
        desc = t.get('descripcion', '')
        url = t.get('enlace', '')
        dom = domain_from(url)
        fv = f"https://www.google.com/s2/favicons?domain={dom}&sz=32"
        new_lines.append(
            f'- <img src="{fv}" width="16" height="16" '
            f'style="vertical-align:middle;margin-right:6px" alt="{name}" /> '
            f'**[{name}]({url})** — {desc}'
        )

    header = '## 🆕 Nuevas herramientas descubiertas\n'
    block = header + '\n'.join(new_lines) + '\n\n'

    if header.strip() in current_content:
        updated = current_content.rstrip('\n') + '\n' + '\n'.join(new_lines) + '\n'
    else:
        updated = current_content.rstrip('\n') + '\n\n' + block

    resources_file.write_text(updated, encoding='utf-8')
    print(f"✅ {len(new_tools)} herramientas añadidas a {resources_file.relative_to(blog_path) if resources_file.is_relative_to(blog_path) else resources_file}")

    recipe_script = blog_path / 'scripts' / 'generate_resources.py'
    if recipe_script.exists():
        print("🔄  Re-categorizando con generate_resources.py...")
        result = subprocess.run(
            [sys.executable, str(recipe_script)],
            cwd=str(blog_path),
            capture_output=True, text=True
        )
        print(result.stdout.strip())
        if result.returncode != 0:
            print(f"⚠️  generate_resources.py terminó con código {result.returncode}")
            if result.stderr:
                print(result.stderr[:500])
    else:
        print(f"ℹ️  generate_resources.py no encontrado en {recipe_script}. Se mantiene sección 'Nuevas herramientas'.")


if __name__ == '__main__':
    main()
