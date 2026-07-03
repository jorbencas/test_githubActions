#!/usr/bin/env python3
"""
scrape_social.py — Scraper para redes sociales (Instagram, Threads, X/Twitter, TikTok)
que requieren Playwright para renderizar contenido dinámico.
"""
import argparse
import asyncio
import json
import logging
import os
import re
import sys

from scripts.utils.common import load_json, save_json, deduplicar_items
from scripts.utils.constants_downloadfile import (
    ENLACE_KEY, TITULO_KEY, FUENTE_KEY, TIPO_KEY, F_KEY, FECHA_REAL_KEY,
    TS_KEY, TIPO_VAL_SOCIAL, FUENTES, PLAYWRIGHT_SOURCES
)
from datetime import datetime
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/social.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("social")

CONFIG_DIR = "files"
NEWS_FILE = os.path.join(CONFIG_DIR, "noticias_historico.json")


def _fuentes_sociales() -> dict:
    return {k: v for k, v in FUENTES.items()
            if any(kw.lower() in k.lower() for kw in PLAYWRIGHT_SOURCES)}


async def _extraer_twitter(page, nombre: str, url: str) -> list:
    results = []
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        tweets = await page.locator("article[data-testid='tweet'] div[lang]").all()
        logger.info(f"  🐦 {nombre}: {len(tweets)} tweets encontrados")
        for tweet in tweets[:10]:
            try:
                text = await tweet.inner_text(timeout=3000)
                if text:
                    results.append({
                        TITULO_KEY: text[:200],
                        ENLACE_KEY: url,
                        FUENTE_KEY: nombre,
                        TIPO_KEY: TIPO_VAL_SOCIAL,
                        F_KEY: datetime.now().strftime("%d/%m"),
                        FECHA_REAL_KEY: datetime.now().strftime("%d/%m/%Y"),
                        TS_KEY: datetime.now().isoformat(),
                    })
            except Exception as e:
                logger.warning(f"    ⚠️ Error en tweet: {e}")
    except Exception as e:
        logger.warning(f"  ⚠️ Twitter ({nombre}): {e}")
    return results


async def _extraer_threads(page, nombre: str, url: str) -> list:
    results = []
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        posts = await page.locator("article a[href*='/post/']").all()
        logger.info(f"  🧵 {nombre}: {len(posts)} posts encontrados")
        for post in posts[:10]:
            try:
                href = await post.get_attribute("href", timeout=3000)
                text = await post.inner_text(timeout=3000)
                if href and text:
                    if not href.startswith("http"):
                        href = f"https://www.threads.net{href}"
                    results.append({
                        TITULO_KEY: text[:200],
                        ENLACE_KEY: href,
                        FUENTE_KEY: nombre,
                        TIPO_KEY: TIPO_VAL_SOCIAL,
                        F_KEY: datetime.now().strftime("%d/%m"),
                        FECHA_REAL_KEY: datetime.now().strftime("%d/%m/%Y"),
                        TS_KEY: datetime.now().isoformat(),
                    })
            except Exception as e:
                logger.warning(f"    ⚠️ Error en post: {e}")
    except Exception as e:
        logger.warning(f"  ⚠️ Threads ({nombre}): {e}")
    return results


async def _extraer_instagram(page, nombre: str, url: str) -> list:
    results = []
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        posts = await page.locator("article a[href*='/p/']").all()
        logger.info(f"  📸 {nombre}: {len(posts)} posts encontrados")
        for post in posts[:10]:
            try:
                href = await post.get_attribute("href", timeout=3000)
                text = await post.inner_text(timeout=3000)
                if href and text:
                    if not href.startswith("http"):
                        href = f"https://www.instagram.com{href}"
                    results.append({
                        TITULO_KEY: text[:200],
                        ENLACE_KEY: href,
                        FUENTE_KEY: nombre,
                        TIPO_KEY: TIPO_VAL_SOCIAL,
                        F_KEY: datetime.now().strftime("%d/%m"),
                        FECHA_REAL_KEY: datetime.now().strftime("%d/%m/%Y"),
                        TS_KEY: datetime.now().isoformat(),
                    })
            except Exception as e:
                logger.warning(f"    ⚠️ Error en post: {e}")
    except Exception as e:
        logger.warning(f"  ⚠️ Instagram ({nombre}): {e}")
    return results


async def _extraer_tiktok(page, nombre: str, url: str) -> list:
    results = []
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        items = await page.locator("div[data-e2e='user-post-item']").all()
        logger.info(f"  🎵 {nombre}: {len(items)} posts encontrados")
        for item in items[:10]:
            try:
                link_el = item.locator("a")
                count = await link_el.count()
                href = await link_el.get_attribute("href", timeout=3000) if count > 0 else ""
                title = await item.inner_text(timeout=3000) if href else ""
                title = title.split("\n")[0][:80]
                if href and not href.startswith("http"):
                    href = f"https://www.tiktok.com{href}"
                if href and title:
                    results.append({
                        TITULO_KEY: title.strip(),
                        ENLACE_KEY: href,
                        FUENTE_KEY: nombre,
                        TIPO_KEY: TIPO_VAL_SOCIAL,
                        F_KEY: datetime.now().strftime("%d/%m"),
                        FECHA_REAL_KEY: datetime.now().strftime("%d/%m/%Y"),
                        TS_KEY: datetime.now().isoformat(),
                    })
            except Exception as e:
                logger.warning(f"    ⚠️ Error en item: {e}")
    except Exception as e:
        logger.warning(f"  ⚠️ TikTok ({nombre}): {e}")
    return results


EXTRACTORS = {
    "twitter": _extraer_twitter,
    "threads": _extraer_threads,
    "instagram": _extraer_instagram,
    "tiktok": _extraer_tiktok,
}


async def run():
    parser = argparse.ArgumentParser(description="Scrape social media sources (Playwright)")
    parser.add_argument("--source", choices=["instagram", "twitter", "threads", "tiktok", "all"],
                        default="all", help="Plataforma a scrapear")
    args = parser.parse_args()

    logger.info("🚀 Iniciando scrape_social.py (Playwright)")

    from playwright.async_api import async_playwright

    historial = load_json(NEWS_FILE)
    existing_urls = {n.get(ENLACE_KEY) for n in historial if n.get(ENLACE_KEY)}
    all_new = []

    fuentes = _fuentes_sociales()
    logger.info(f"📡 {len(fuentes)} fuentes sociales configuradas")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        for nombre, info in fuentes.items():
            platform = None
            for p in ["instagram", "threads", "twitter", "tiktok"]:
                if p in nombre.lower():
                    platform = p
                    break
            if not platform:
                continue
            if args.source != "all" and platform != args.source:
                continue

            logger.info(f"📡 Procesando: {nombre} ({platform})")
            extractor = EXTRACTORS.get(platform)
            if not extractor:
                logger.warning(f"  ⚠️ Sin extractor para {platform}")
                continue

            # Health check rápido: validar que la URL responde
            try:
                import urllib.request
                loop = asyncio.get_event_loop()
                req = urllib.request.Request(info["url"], method="HEAD")
                resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=10))
                logger.info(f"  ✓ {nombre}: HTTP {resp.status}")
                resp.close()
            except Exception as e:
                logger.warning(f"  ⚠️ {nombre}: URL no accesible ({e}) — se omite")
                continue

            page = await context.new_page()
            try:
                results = await extractor(page, nombre, info["url"])
                for item in results:
                    enlace = item.get(ENLACE_KEY)
                    if enlace and enlace not in existing_urls:
                        all_new.append(item)
                        existing_urls.add(enlace)
            except Exception as e:
                logger.error(f"❌ Error en {nombre}: {e}")
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

        await browser.close()

    all_new = deduplicar_items(all_new)
    logger.info(f"✨ {len(all_new)} nuevos items de redes sociales")

    if all_new:
        try:
            import google.genai as genai
            client_tr = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or "")
            from scripts.utils.common import traducir_titulos_ia
            all_new = await traducir_titulos_ia(all_new, client_tr)
        except Exception as e:
            logger.warning(f"⚠️ Traducción no disponible: {e}")

        historial = all_new + historial
        historial = historial[:900]
        save_json(NEWS_FILE, historial)
        logger.info(f"💾 {len(all_new)} nuevos items guardados en {NEWS_FILE}")
    else:
        logger.info("📭 No hay novedades sociales.")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        logger.error(f"❌ Error fatal en scrape_social.py: {e}")
        sys.exit(1)
