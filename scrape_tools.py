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

from constants_downloadfile import CONFIG, FUENTES
from scraper_base import ScraperPro

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/tools.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("tools")


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
    logger.info("🚀 Iniciando scrape_tools.py")
    scr = ScraperPro()

    herramientas_path = os.path.join(CONFIG["FOLDER"], "herramientas.json")
    herramientas_hist = load_json(herramientas_path)
    existing_urls = {h.get("enlace") for h in herramientas_hist if h.get("enlace")}

    tool_sources = {k: v for k, v in FUENTES.items() if v.get("tipo") == "herramienta"}
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
            enlace = item.get("enlace")
            if enlace and enlace in existing_urls:
                continue
            nuevas.append(item)
            if enlace:
                existing_urls.add(enlace)

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
