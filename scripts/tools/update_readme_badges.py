#!/usr/bin/env python3
"""Actualiza las badges dinámicas del README.md con datos actuales."""

import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
README_PATH = os.path.join(ROOT, "README.md")
NEWS_PATH = os.path.join(ROOT, "files", "noticias_historico.json")
TOOLS_PATH = os.path.join(ROOT, "files", "herramientas.json")

BADGE_STYLE = "for-the-badge"
BASE = "https://img.shields.io/badge"


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def count_sources(items):
    return len({item.get("fuente", "") for item in items})


def count_categories(items):
    cats = {}
    for item in items:
        c = item.get("categoria", "Sin categoría")
        cats[c] = cats.get(c, 0) + 1
    return cats


def last_updated(items):
    latest = ""
    for item in items:
        ts = item.get("ts", "")
        if ts > latest:
            latest = ts
    if latest:
        try:
            dt = datetime.fromisoformat(latest.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    return ""


def make_badge(label, value, color, style=BADGE_STYLE):
    label_enc = label.replace("-", "--").replace("_", "__").replace(" ", "_")
    value_enc = value.replace("-", "--").replace("_", "__").replace(" ", "_")
    return f"![{label}]({BASE}/{label_enc}-{value_enc}-{color}?style={style}&logo=newsblur&logoColor=white)"


def update_readme():
    news = load_json(NEWS_PATH)
    tools = load_json(TOOLS_PATH)

    total_news = len(news)
    total_sources = count_sources(news)
    total_tools = len(tools)
    updated = last_updated(news)

    new_badges = "\n".join([
        make_badge("Noticias", f"{total_news:,}".replace(",", "."), "3b82f6"),
        make_badge("Fuentes", str(total_sources), "8b5cf6"),
        make_badge("Herramientas", str(total_tools), "10b981"),
        make_badge("Actualizado", updated, "f59e0b"),
    ])

    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- DYNAMIC_BADGES_START -->.*?<!-- DYNAMIC_BADGES_END -->"
    replacement = f"<!-- DYNAMIC_BADGES_START -->\n{new_badges}\n<!-- DYNAMIC_BADGES_END -->"

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        marker = "![Tips]"
        if marker in content:
            new_content = content.replace(
                marker,
                f"{marker}\n{replacement}",
            )
        else:
            new_content = content + f"\n\n{replacement}\n"

    if new_content != content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"README actualizado: {total_news} noticias, {total_sources} fuentes, {total_tools} herramientas, {updated}")
    else:
        print("README sin cambios")


if __name__ == "__main__":
    update_readme()
