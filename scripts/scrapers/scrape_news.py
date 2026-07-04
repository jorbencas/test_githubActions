#!/usr/bin/env python3
"""
scrape_news.py — Scrapea fuentes de noticias web y YouTube.
Actualiza noticias_historico.json con nuevos items.

Uso:
    python scrape_news.py                         # Scrapea todas las fuentes
    python scrape_news.py --limit 5                # Máximo 5 requests simultáneos
"""
import argparse
import asyncio
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import aiohttp

from scripts.utils.constants_downloadfile import CONFIG, FUENTES, YT_KEY, TIPO_KEY, QUICK_KEY, TIPO_VAL_HERRAMIENTA, ENLACE_KEY, ID_VIDEO_KEY
from scripts.scrapers.scraper_base import ScraperPro
from scripts.utils.common import load_json, save_json, traducir_titulos_ia, deduplicar_items

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/news.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("news")



def _filtrar_fuentes_por_tier(tier: str) -> dict:
    """Filtra FUENTES según el tier de scraping."""
    todas = {k: v for k, v in FUENTES.items() if v.get(TIPO_KEY) != TIPO_VAL_HERRAMIENTA}
    if tier == "full":
        return todas
    if tier == "standard":
        return {k: v for k, v in todas.items() if YT_KEY not in v}
    if tier == "light":
        return {k: v for k, v in todas.items() if v.get(QUICK_KEY)}
    logger.warning("⚠️ Tier '%s' desconocido. Usando full.", tier)
    return todas


async def run():
    parser = argparse.ArgumentParser(description="Scrape news sources")
    parser.add_argument("--limit", type=int, default=5, help="Máximo de requests simultáneos")
    parser.add_argument("--tier", choices=["light", "standard", "full"], default="full",
                        help="Tier de scraping: light (solo quick), standard (web), full (todo)")
    args = parser.parse_args()

    logger.info("🚀 Iniciando scrape_news.py (tier=%s)", args.tier)
    scr = ScraperPro()

    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    existing_urls = {n.get(ENLACE_KEY) for n in historial if n.get(ENLACE_KEY)}
    existing_video_ids = {n.get(ID_VIDEO_KEY) for n in historial if n.get(ID_VIDEO_KEY)}

    sem = asyncio.Semaphore(args.limit)

    async def con_semaforo(session, nombre, info):
        async with sem:
            await asyncio.sleep(1)
            return await scr.extraer(session, nombre, info)

    connector = aiohttp.TCPConnector(ssl=False)
    news_sources = _filtrar_fuentes_por_tier(args.tier)

    async with aiohttp.ClientSession(connector=connector) as session:
        tareas = [con_semaforo(session, nombre, info) for nombre, info in news_sources.items()]
        resultados_agrupados = await asyncio.gather(*tareas)

    nuevos = []
    for lista_res in resultados_agrupados:
        for item in lista_res:
            enlace = item.get(ENLACE_KEY)
            id_vid = item.get(ID_VIDEO_KEY)
            if enlace and enlace in existing_urls:
                continue
            if id_vid and id_vid in existing_video_ids:
                continue
            nuevos.append(item)
            if enlace:
                existing_urls.add(enlace)
            if id_vid:
                existing_video_ids.add(id_vid)

    nuevos = deduplicar_items(nuevos)
    logger.info(f"✨ Encontrados {len(nuevos)} nuevos elementos (tras dedup).")

    if nuevos:
        try:
            import google.genai as genai

            client_tr = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
            nuevos = await traducir_titulos_ia(nuevos, client_tr)
        except Exception as e:
            logger.error(f"❌ Error en traducción: {e}")

        historial = nuevos + historial
        historial = historial[:900]
        save_json(path_json, historial)
        logger.info(f"💾 {len(nuevos)} nuevos items guardados en {path_json}")

    scr.guardar_avatars()
    logger.info("✅ scrape_news.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
