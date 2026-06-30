#!/usr/bin/env python3
"""
scrape_trends.py — Scraper para fuentes JS-heavy (Google Trends, TikTok)
que requieren Playwright para renderizar contenido dinámico.

Uso:
    python scrape_trends.py                     # Scrapea todas las fuentes configuradas
    python scrape_trends.py --source trends     # Solo Google Trends
    python scrape_trends.py --source tiktok     # Solo TikTok

Workflow independiente, sin depender de downloadFile.py.
"""
import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ── Logging ──
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/trends.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("trends")

# ── Config ──
CONFIG_DIR = "files"
TRENDS_FILE = os.path.join(CONFIG_DIR, "trends.json")
NEWS_FILE = os.path.join(CONFIG_DIR, "noticias_historico.json")
os.makedirs(CONFIG_DIR, exist_ok=True)

TRENDS_SOURCES = {
    "Google Trends Tecnología": {
        "url": "https://trends.google.com/trends/trendingsearches/daily?geo=ES&cat=tech",
        "selector": "div.mZvaOc",
        "type": "trend",
    },
    "TikTok Tech": {
        "url": "https://www.tiktok.com/@tech",
        "selector": "div[data-e2e='user-post-item']",
        "type": "social",
    },
}


def load_json(path: str) -> list:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_json(path: str, data: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_duplicate(enlace: str, existentes: set) -> bool:
    return enlace in existentes


def load_existing_urls(historial: list) -> set:
    return {n.get("enlace") for n in historial if n.get("enlace")}


def scrape_google_trends(page) -> list:
    """Extrae trending searches de Google Trends."""
    results = []
    try:
        items = page.locator("div.mZvaOc").all()
        logger.info(f"📊 Google Trends: {len(items)} elementos encontrados")
        for item in items[:15]:
            try:
                title_el = item.locator("div[role='heading']")
                title = title_el.inner_text(timeout=3000) if title_el.count() > 0 else ""
                if not title:
                    title = item.inner_text(timeout=3000).split("\n")[0]

                link = f"https://trends.google.com/trends/trendingsearches/detail?q={title}&geo=ES"
                results.append(
                    {
                        "titulo": title.strip(),
                        "enlace": link,
                        "fuente": "Google Trends Tecnología",
                        "tipo": "trend",
                        "f": datetime.now().strftime("%d/%m"),
                        "fecha_real": datetime.now().strftime("%d/%m/%Y"),
                        "ts": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.warning(f"  ⚠️ Error en item de Trends: {e}")
    except Exception as e:
        logger.error(f"❌ Error scraping Google Trends: {e}")
    return results


def scrape_tiktok(page, source_name: str, url: str) -> list:
    """Extrae posts de TikTok (limitado por restricciones de la plataforma)."""
    results = []
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        items = page.locator("div[data-e2e='user-post-item']").all()
        logger.info(f"🎵 TikTok ({source_name}): {len(items)} elementos")
        for item in items[:10]:
            try:
                link_el = item.locator("a")
                href = link_el.get_attribute("href", timeout=3000) if link_el.count() > 0 else ""
                title = item.inner_text(timeout=3000).split("\n")[0][:80] if href else ""
                if href and not href.startswith("http"):
                    href = f"https://www.tiktok.com{href}"
                if href and title:
                    results.append(
                        {
                            "titulo": title.strip(),
                            "enlace": href,
                            "fuente": source_name,
                            "tipo": "social",
                            "f": datetime.now().strftime("%d/%m"),
                            "fecha_real": datetime.now().strftime("%d/%m/%Y"),
                            "ts": datetime.now().isoformat(),
                        }
                    )
            except Exception as e:
                logger.warning(f"  ⚠️ Error en item TikTok: {e}")
    except Exception as e:
        logger.warning(f"⚠️ TikTok ({source_name}): {e}")
    return results


async def run():
    parser = argparse.ArgumentParser(description="Scrape JS-heavy sources")
    parser.add_argument("--source", choices=["trends", "tiktok", "all"], default="all")
    args = parser.parse_args()

    logger.info("🚀 Iniciando scrape_trends.py (Playwright)")

    from playwright.async_api import async_playwright

    historial = load_json(NEWS_FILE)
    existing_urls = load_existing_urls(historial)
    all_new = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        for name, info in TRENDS_SOURCES.items():
            if args.source != "all" and args.source not in info["type"]:
                continue

            logger.info(f"📡 Procesando: {name}")
            page = await context.new_page()

            try:
                if "trends" in info["type"]:
                    await page.goto(info["url"], timeout=30000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)
                    results = scrape_google_trends(page)
                elif "social" in info["type"]:
                    results = scrape_tiktok(page, name, info["url"])
                else:
                    results = []

                for item in results:
                    if not is_duplicate(item["enlace"], existing_urls):
                        all_new.append(item)
                        existing_urls.add(item["enlace"])

            except Exception as e:
                logger.error(f"❌ Error en {name}: {e}")
            finally:
                await page.close()

        await browser.close()

    if all_new:
        historial = all_new + historial
        historial = historial[:900]
        save_json(NEWS_FILE, historial)
        logger.info(f"✅ {len(all_new)} nuevos items guardados en {NEWS_FILE}")
    else:
        logger.info("📭 No hay novedades de trends.")

    # Guardar también en archivo específico de trends
    trends_hist = load_json(TRENDS_FILE)
    trends_existing = {t.get("enlace") for t in trends_hist}
    for item in all_new:
        if item["enlace"] not in trends_existing:
            trends_hist.append(item)
            trends_existing.add(item["enlace"])
    trends_hist = trends_hist[:200]
    save_json(TRENDS_FILE, trends_hist)
    logger.info(f"📊 Trends guardados en {TRENDS_FILE} (total: {len(trends_hist)})")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
