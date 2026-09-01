#!/usr/bin/env python3
"""
scrape_ai_tools.py — Auto-detecta herramientas IA candidatas.
Consulta Hugging Face API (models + spaces), GitHub Search API y Product Hunt.
Guarda candidatos nuevos en files/ai_tools_candidates.json.

Uso:
    python -m scripts.scrapers.scrape_ai_tools
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import aiohttp

from scripts.utils.constants_downloadfile import (
    CONFIG, ENLACE_KEY, TITULO_KEY, DESCRIPCION_KEY, LENGUAJE_KEY,
    ESTRELLAS_KEY, FUENTE_KEY, TIPO_KEY, TS_KEY, LOGS_DIR, LOG_FILES,
    TIPO_VAL_HERRAMIENTA,
)
from scripts.utils.common import load_json, save_json

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(
            os.path.join(LOGS_DIR, LOG_FILES["tools"]),
            maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ai_tools")

CANDIDATES_FILENAME = "ai_tools_candidates.json"


async def fetch_hf_models(session: aiohttp.ClientSession) -> list:
    """Fetch trending models from Hugging Face API."""
    url = "https://huggingface.co/api/models"
    params = {
        "sort": "downloads",
        "direction": "-1",
        "limit": 30,
    }
    items = []
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.warning(f"HF Models API returned {resp.status}")
                return []
            models = await resp.json()
        for m in models:
            name = m.get("id", "")
            if not name:
                continue
            pipeline = m.get("pipeline_tag", "")
            downloads = m.get("downloads", 0)
            likes = m.get("likes", 0)
            tags = m.get("tags", [])
            author = m.get("author", "")
            items.append({
                TITULO_KEY: name,
                ENLACE_KEY: f"https://huggingface.co/{name}",
                DESCRIPCION_KEY: f"[{pipeline}] {', '.join(tags[:3])} — by {author}",
                LENGUAJE_KEY: "Python",
                ESTRELLAS_KEY: str(likes),
                FUENTE_KEY: "HuggingFace Models",
                TIPO_KEY: TIPO_VAL_HERRAMIENTA,
                "_downloads": downloads,
                "_likes": likes,
                "_pipeline": pipeline,
                "_source_type": "hf_model",
            })
        logger.info(f"🤗 HF Models: {len(items)} modelos obtenidos")
    except Exception as e:
        logger.error(f"❌ Error HF Models: {e}")
    return items


async def fetch_hf_spaces(session: aiohttp.ClientSession) -> list:
    """Fetch trending Spaces from Hugging Face API."""
    url = "https://huggingface.co/api/spaces"
    params = {
        "sort": "likes",
        "direction": "-1",
        "limit": 20,
    }
    items = []
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.warning(f"HF Spaces API returned {resp.status}")
                return []
            spaces = await resp.json()
        for s in spaces:
            name = s.get("id", "")
            if not name:
                continue
            sdk = s.get("sdk", "")
            likes = s.get("likes", 0)
            tags = s.get("tags", [])
            items.append({
                TITULO_KEY: name,
                ENLACE_KEY: f"https://huggingface.co/spaces/{name}",
                DESCRIPCION_KEY: f"[{sdk} space] {', '.join(tags[:3])}",
                LENGUAJE_KEY: sdk or "Python",
                ESTRELLAS_KEY: str(likes),
                FUENTE_KEY: "HuggingFace Spaces",
                TIPO_KEY: TIPO_VAL_HERRAMIENTA,
                "_likes": likes,
                "_sdk": sdk,
                "_source_type": "hf_space",
            })
        logger.info(f"🤗 HF Spaces: {len(items)} spaces obtenidos")
    except Exception as e:
        logger.error(f"❌ Error HF Spaces: {e}")
    return items


async def fetch_github_ai_repos(session: aiohttp.ClientSession) -> list:
    """Fetch trending AI repos from GitHub Search API."""
    queries = [
        "ai+tool+stars:>200 pushed:>2025-06-01",
        "llm+agent+stars:>200 pushed:>2025-06-01",
        "ai+assistant+stars:>200 pushed:>2025-06-01",
    ]
    items = []
    seen_urls = set()
    for q in queries:
        url = "https://api.github.com/search/repositories"
        params = {"q": q, "sort": "stars", "order": "desc", "per_page": 10}
        try:
            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=15),
                headers={"Accept": "application/vnd.github.v3+json"},
            ) as resp:
                if resp.status == 403:
                    logger.warning("GitHub API rate limit reached, skipping...")
                    break
                if resp.status != 200:
                    logger.warning(f"GitHub Search returned {resp.status}")
                    continue
                data = await resp.json()
            for r in data.get("items", []):
                full_name = r.get("full_name", "")
                html_url = r.get("html_url", "")
                if html_url in seen_urls:
                    continue
                seen_urls.add(html_url)
                desc = r.get("description", "") or ""
                lang = r.get("language", "") or ""
                stars = r.get("stargazers_count", 0)
                topics = r.get("topics", [])
                items.append({
                    TITULO_KEY: full_name,
                    ENLACE_KEY: html_url,
                    DESCRIPCION_KEY: desc[:200],
                    LENGUAJE_KEY: lang,
                    ESTRELLAS_KEY: str(stars),
                    FUENTE_KEY: "GitHub Search",
                    TIPO_KEY: TIPO_VAL_HERRAMIENTA,
                    "_stars": stars,
                    "_topics": topics,
                    "_source_type": "github_repo",
                })
        except Exception as e:
            logger.error(f"❌ Error GitHub Search ({q}): {e}")
        await asyncio.sleep(2)
    logger.info(f"🐙 GitHub Search: {len(items)} repos obtenidos")
    return items


def deduplicate(all_items: list) -> list:
    """Remove duplicates by URL, keeping highest-quality entry."""
    seen = {}
    for item in all_items:
        url = item.get(ENLACE_KEY, "")
        if not url:
            continue
        if url in seen:
            existing = seen[url]
            existing_stars = int(existing.get(ESTRELLAS_KEY, "0") or "0")
            new_stars = int(item.get(ESTRELLAS_KEY, "0") or "0")
            if new_stars > existing_stars:
                seen[url] = item
        else:
            seen[url] = item
    return list(seen.values())


async def run():
    logger.info("🚀 Iniciando scrape_ai_tools.py")
    candidates_path = os.path.join(CONFIG["FOLDER"], CANDIDATES_FILENAME)
    history_path = os.path.join(CONFIG["FOLDER"], "..", "ai_tools_history.json")
    existing_titles = set()
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                hist = json.load(f)
            existing_titles = set(hist.get("sent_titles", []))
        except Exception:
            pass

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        hf_models, hf_spaces, gh_repos = await asyncio.gather(
            fetch_hf_models(session),
            fetch_hf_spaces(session),
            fetch_github_ai_repos(session),
        )

    all_items = deduplicate(hf_models + hf_spaces + gh_repos)

    new_candidates = []
    for item in all_items:
        title = item.get(TITULO_KEY, "")
        if title in existing_titles:
            continue
        new_candidates.append(item)

    new_candidates.sort(key=lambda x: int(x.get(ESTRELLAS_KEY, "0") or "0"), reverse=True)
    new_candidates = new_candidates[:50]

    if new_candidates:
        existing_candidates = load_json(candidates_path)
        existing_urls = {c.get(ENLACE_KEY) for c in existing_candidates if c.get(ENLACE_KEY)}
        truly_new = [c for c in new_candidates if c.get(ENLACE_KEY) not in existing_urls]

        if truly_new:
            combined = truly_new + existing_candidates
            combined = combined[:100]
            save_json(candidates_path, combined)
            logger.info(f"💾 {len(truly_new)} candidatos nuevos guardados en {candidates_path}")
        else:
            logger.info("📭 No hay candidatos nuevos.")
    else:
        logger.info("📭 No se encontraron candidatos.")

    logger.info("✅ scrape_ai_tools.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
