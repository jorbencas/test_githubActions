#!/usr/bin/env python3
"""
scrape_publicapis.py — Extrae APIs de publicapis.io y las guarda en formato compatible con el pipeline de recursos.
Salida: files/publicapis_apis.json (formato igual a herramientas.json para manage_resources.py).
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("scrape_publicapis")

BASE_URL = "https://publicapis.io"
OUTPUT_FILE = Path("files/publicapis_apis.json")


def fetch_page(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def parse_resources(html: str) -> list[dict]:
    """Parse resources from publicapis.io HTML page.

    Structure per card:
        div.api-card
          a.logo[href]          → link to detail page (/slug)
          div.meta
            div.card-head > a   → title text + div.category
            div.meta > a        → description text
    """
    soup = BeautifulSoup(html, "html.parser")
    resources = []

    cards = soup.select("div.api-card")
    for card in cards:
        # Link
        a_logo = card.select_one("a.logo")
        if not a_logo:
            continue
        href = a_logo.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = BASE_URL + href

        # Title: text inside card-head > a, minus the category div text
        inner_a = card.select_one("div.card-head > a")
        if not inner_a:
            continue
        cat_div = inner_a.select_one("div")
        cat_text = cat_div.get_text(strip=True) if cat_div else ""
        full_text = inner_a.get_text(strip=True)
        title = full_text.replace(cat_text, "").strip()
        if not title:
            continue

        # Description
        desc_a = card.select_one("div.meta > a")
        description = desc_a.get_text(strip=True) if desc_a else ""

        resources.append({
            "titulo": title,
            "enlace": href,
            "fuente": "Public APIs",
            "tipo": "herramienta",
            "f": datetime.now().strftime("%d/%m"),
            "fecha_publicacion": "",
            "subtipo": "api",
            "descripcion": description[:200],
            "categoria": cat_text or "📊 APIs",
        })

    return resources


def scrape_all() -> list[dict]:
    """Scrape all resources from publicapis.io (paginated + categories)."""
    all_resources = []
    seen_urls = set()

    # 1) Paginated main listing
    page = 1
    max_pages = 30
    while page <= max_pages:
        url = f"{BASE_URL}?page={page}" if page > 1 else BASE_URL
        logger.info(f"Fetching page {page}: {url}")

        html = fetch_page(url)
        if not html:
            break

        resources = parse_resources(html)
        if not resources:
            logger.info(f"No more resources on page {page}. Stopping.")
            break

        new_count = 0
        for r in resources:
            if r["enlace"] not in seen_urls:
                seen_urls.add(r["enlace"])
                all_resources.append(r)
                new_count += 1

        logger.info(f"  Page {page}: {len(resources)} found, {new_count} new (total: {len(all_resources)})")

        if new_count == 0:
            break
        page += 1

    # 2) Category pages for extra coverage
    categories = [
        "development", "data-access", "finance", "cryptocurrency",
        "machine-learning", "geocoding", "transportation", "weather",
        "sports-and-fitness", "music", "social", "news", "security",
        "games-and-comics", "open-data", "environment", "health",
        "documents-and-productivity", "art-and-design", "anime",
    ]

    for cat in categories:
        url = f"{BASE_URL}/category/{cat}"
        logger.info(f"Fetching category: {cat}")
        html = fetch_page(url)
        if not html:
            continue

        resources = parse_resources(html)
        new_count = 0
        for r in resources:
            if r["enlace"] not in seen_urls:
                seen_urls.add(r["enlace"])
                r["categoria"] = cat.replace("-", " ").title()
                all_resources.append(r)
                new_count += 1

        logger.info(f"  {cat}: {new_count} new APIs")

    return all_resources


def save_resources(resources: list[dict]):
    """Save resources to JSON file."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    existing_urls = {r.get("enlace") for r in existing}
    new_resources = [r for r in resources if r["enlace"] not in existing_urls]

    combined = existing + new_resources
    OUTPUT_FILE.write_text(json.dumps(combined, indent=4, ensure_ascii=False), encoding="utf-8")
    logger.info(f"💾 Guardadas {len(new_resources)} APIs nuevas en {OUTPUT_FILE} (total: {len(combined)})")


def main():
    logger.info("🚀 Iniciando scraping de publicapis.io...")
    resources = scrape_all()
    logger.info(f"📊 Total extraído: {len(resources)} APIs")

    if resources:
        save_resources(resources)
        cats = {}
        for r in resources:
            c = r.get("categoria", "Sin categoría")
            cats[c] = cats.get(c, 0) + 1
        print("\n📈 Resumen por categoría:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:15]:
            print(f"  {cat}: {count}")
    else:
        logger.warning("⚠️ No se encontraron APIs")


if __name__ == "__main__":
    main()
