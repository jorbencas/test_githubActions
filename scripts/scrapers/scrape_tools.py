#!/usr/bin/env python3
"""
scrape_tools.py — Scrapea GitHub Trending + Product Hunt para herramientas.
Actualiza files/herramientas.json con nuevos descubrimientos.

Uso:
    python scrape_tools.py
"""
import asyncio
import json
import logging
import os
from logging.handlers import RotatingFileHandler

import aiohttp

from scripts.utils.constants_downloadfile import CONFIG, FUENTES, TIPO_KEY, TIPO_VAL_HERRAMIENTA, ENLACE_KEY, HERRAMIENTAS_FILENAME, LOGS_DIR, LOG_FILES
from scripts.utils.common import load_json, save_json
from scripts.scrapers.scraper_base import ScraperPro

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(LOGS_DIR, LOG_FILES["tools"]), maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("tools")


async def get_homepage_from_github(session: aiohttp.ClientSession, repo: str) -> str | None:
    """Obtiene la homepage URL de un repo de GitHub via API."""
    if not repo or "/" not in repo:
        return None
    try:
        url = f"https://api.github.com/repos/{repo}"
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            homepage = data.get("homepage", "").strip()
            if homepage and homepage.startswith("http"):
                return homepage
    except Exception as e:
        logger.debug(f"⚠️ Error obteniendo homepage para {repo}: {e}")
    return None


async def enrich_with_homepages(items: list) -> list:
    """Para cada herramienta de GitHub, intenta obtener su homepage URL."""
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(5)

        async def process_item(item):
            async with sem:
                repo = item.get("repo", "")
                if not repo:
                    return item
                homepage = await get_homepage_from_github(session, repo)
                if homepage:
                    item["enlace"] = homepage
                    item["homepage"] = homepage
                    logger.info(f"🏠 {repo} → {homepage}")
                return item

        tasks = [process_item(item) for item in items]
        return await asyncio.gather(*tasks)



async def run():
    logger.info("🚀 Iniciando scrape_tools.py")
    scr = ScraperPro()

    herramientas_path = os.path.join(CONFIG["FOLDER"], HERRAMIENTAS_FILENAME)
    herramientas_hist = load_json(herramientas_path)
    existing_urls = {h.get(ENLACE_KEY) for h in herramientas_hist if h.get(ENLACE_KEY)}

    tool_sources = {k: v for k, v in FUENTES.items() if v.get(TIPO_KEY) == TIPO_VAL_HERRAMIENTA}
    logger.info(f"🔧 Fuentes de herramientas: {list(tool_sources.keys())}")

    sem = asyncio.Semaphore(3)

    async def con_semaforo(session, nombre, info):
        async with sem:
            await asyncio.sleep(1)
            return await scr.extraer(session, nombre, info)

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tareas = [con_semaforo(session, nombre, info) for nombre, info in tool_sources.items()]
        resultados_agrupados = await asyncio.gather(*tareas)

    nuevas = []
    for lista_res in resultados_agrupados:
        for item in lista_res:
            enlace = item.get(ENLACE_KEY)
            if enlace and enlace in existing_urls:
                continue
            nuevas.append(item)
            if enlace:
                existing_urls.add(enlace)

    # Enriquecer con homepages de GitHub API
    if nuevas:
        logger.info(f"🏠 Obteniendo homepages de GitHub para {len(nuevas)} herramientas...")
        nuevas = await enrich_with_homepages(nuevas)

    if nuevas:
        herramientas_hist = nuevas + herramientas_hist
        herramientas_hist = herramientas_hist[:200]
        save_json(herramientas_path, herramientas_hist)
        logger.info(f"🔧 {len(nuevas)} herramientas nuevas guardadas en {herramientas_path}")
    else:
        logger.info("📭 No hay herramientas nuevas.")

    scr.guardar_avatars()
    logger.info("✅ scrape_tools.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
