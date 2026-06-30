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

from constants_downloadfile import CONFIG, FUENTES
from scraper_base import ScraperPro
from utils import traducir_titulos_ia, deduplicar_items

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


async def run():
    parser = argparse.ArgumentParser(description="Scrape news sources")
    parser.add_argument("--limit", type=int, default=5, help="Máximo de requests simultáneos")
    args = parser.parse_args()

    logger.info("🚀 Iniciando scrape_news.py")
    scr = ScraperPro()

    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    existing_urls = {n.get("enlace") for n in historial if n.get("enlace")}
    existing_video_ids = {n.get("id_video") for n in historial if n.get("id_video")}

    sem = asyncio.Semaphore(args.limit)

    async def con_semaforo(session, nombre, info):
        async with sem:
            await asyncio.sleep(1)
            return await scr.extraer(session, nombre, info)

    connector = aiohttp.TCPConnector(ssl=False)
    news_sources = {k: v for k, v in FUENTES.items() if v.get("tipo") != "herramienta"}

    async with aiohttp.ClientSession(connector=connector) as session:
        tareas = [con_semaforo(session, nombre, info) for nombre, info in news_sources.items()]
        resultados_agrupados = await asyncio.gather(*tareas)

    nuevos = []
    for lista_res in resultados_agrupados:
        for item in lista_res:
            enlace = item.get("enlace")
            id_vid = item.get("id_video")
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
