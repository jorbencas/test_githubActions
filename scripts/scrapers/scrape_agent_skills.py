#!/usr/bin/env python3
"""
scrape_agent_skills.py — Scrapea skills de agentes IA desde múltiples fuentes.
Fuentes: skills.sh, agentskills.io, GitHub Topics.
Guarda en files/agent_skills.json.

Uso:
    python -m scripts.scrapers.scrape_agent_skills
"""
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from logging.handlers import RotatingFileHandler

import aiohttp

from scripts.utils.constants_downloadfile import (
    CONFIG, ENLACE_KEY, TITULO_KEY, DESCRIPCION_KEY,
    FUENTE_KEY, TIPO_KEY, TS_KEY, LOGS_DIR, LOG_FILES,
)
from scripts.utils.common import load_json, save_json

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(
            os.path.join(LOGS_DIR, "agent_skills.log"),
            maxBytes=1024 * 1024 * 5, backupCount=3, encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("agent_skills")

AGENT_SKILLS_FILENAME = "agent_skills.json"


def _parse_frontmatter(text: str) -> dict:
    """Extrae frontmatter YAML de un SKILL.md."""
    meta = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


async def fetch_skills_sh(session: aiohttp.ClientSession) -> list:
    """Fetch skills del directorio oficial skills.sh."""
    items = []
    try:
        # skills.sh tiene un índice JSON
        url = "https://skills.sh/index.json"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.warning(f"skills.sh returned {resp.status}")
                return []
            data = await resp.json()
        
        for skill in data.get("skills", []):
            name = skill.get("name", "")
            desc = skill.get("description", "")
            repo = skill.get("repo", "")
            author = skill.get("author", "")
            platforms = skill.get("platforms", [])
            category = skill.get("category", "")
            
            if not name:
                continue
            
            items.append({
                TITULO_KEY: name,
                ENLACE_KEY: f"https://skills.sh/{author}/{name}" if author else f"https://skills.sh/{name}",
                DESCRIPCION_KEY: desc[:200],
                FUENTE_KEY: "skills.sh",
                TIPO_KEY: "skill",
                "_platforms": platforms,
                "_category": category,
                "_author": author,
                "_repo": repo,
                "_source_type": "skills_sh",
            })
        logger.info(f"📦 skills.sh: {len(items)} skills obtenidas")
    except Exception as e:
        logger.error(f"❌ Error skills.sh: {e}")
    return items


async def fetch_agentskills_io(session: aiohttp.ClientSession) -> list:
    """Scrapea skills de agentskills.io."""
    items = []
    try:
        url = "https://agentskills.io/api/skills"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                # Intentar la página principal y parsear
                logger.warning(f"agentskills.io API returned {resp.status}, intentando scraping web...")
                return await _scrape_agentskills_web(session)
            data = await resp.json()
        
        for skill in data.get("skills", []):
            name = skill.get("name", "")
            desc = skill.get("description", "")
            slug = skill.get("slug", name.lower().replace(" ", "-"))
            platforms = skill.get("platforms", [])
            category = skill.get("category", "")
            
            if not name:
                continue
            
            items.append({
                TITULO_KEY: name,
                ENLACE_KEY: f"https://agentskills.io/skills/{slug}",
                DESCRIPCION_KEY: desc[:200],
                FUENTE_KEY: "agentskills.io",
                TIPO_KEY: "skill",
                "_platforms": platforms,
                "_category": category,
                "_source_type": "agentskills_io",
            })
        logger.info(f"🎯 agentskills.io: {len(items)} skills obtenidas")
    except Exception as e:
        logger.error(f"❌ Error agentskills.io: {e}")
    return items


async def _scrape_agentskills_web(session: aiohttp.ClientSession) -> list:
    """Fallback: scrapea la página web de agentskills.io."""
    items = []
    try:
        url = "https://agentskills.io/skills"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
        
        # Parsear links de skills del HTML
        skill_links = re.findall(r'href="/skills/([^"]+)"', html)
        for slug in set(skill_links):
            name = slug.replace("-", " ").title()
            items.append({
                TITULO_KEY: name,
                ENLACE_KEY: f"https://agentskills.io/skills/{slug}",
                DESCRIPCION_KEY: f"Skill: {name}",
                FUENTE_KEY: "agentskills.io",
                TIPO_KEY: "skill",
                "_platforms": [],
                "_category": "",
                "_source_type": "agentskills_io",
            })
        logger.info(f"🎯 agentskills.io (web): {len(items)} skills obtenidas")
    except Exception as e:
        logger.error(f"❌ Error agentskills.io web: {e}")
    return items


async def fetch_github_skills(session: aiohttp.ClientSession) -> list:
    """Busca repos de skills en GitHub."""
    items = []
    queries = [
        "agent-skills SKILL.md",
        "claude-skills SKILL.md",
        "opencode-skills",
        "ai-agent-skills",
    ]
    seen_urls = set()
    
    for q in queries:
        url = "https://api.github.com/search/repositories"
        params = {"q": q, "sort": "stars", "order": "desc", "per_page": 10}
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    logger.warning(f"GitHub Search returned {resp.status} for '{q}'")
                    await asyncio.sleep(2)
                    continue
                data = await resp.json()
            
            for r in data.get("items", []):
                full_name = r.get("full_name", "")
                html_url = r.get("html_url", "")
                if html_url in seen_urls:
                    continue
                seen_urls.add(html_url)
                desc = r.get("description", "") or ""
                stars = r.get("stargazers_count", 0)
                topics = r.get("topics", [])
                
                items.append({
                    TITULO_KEY: full_name,
                    ENLACE_KEY: html_url,
                    DESCRIPCION_KEY: desc[:200],
                    FUENTE_KEY: "GitHub",
                    TIPO_KEY: "skill",
                    "_stars": stars,
                    "_topics": topics,
                    "_source_type": "github_repo",
                })
        except Exception as e:
            logger.error(f"❌ Error GitHub Search ({q}): {e}")
        await asyncio.sleep(2)
    
    logger.info(f"🐙 GitHub: {len(items)} repos de skills obtenidos")
    return items


def deduplicate(all_items: list) -> list:
    """Elimina duplicados por URL, manteniendo la entrada de mayor calidad."""
    seen = {}
    for item in all_items:
        url = item.get(ENLACE_KEY, "")
        if not url:
            continue
        if url in seen:
            existing = seen[url]
            existing_stars = int(existing.get("_stars", 0) or 0)
            new_stars = int(item.get("_stars", 0) or 0)
            if new_stars > existing_stars:
                seen[url] = item
        else:
            seen[url] = item
    return list(seen.values())


async def run():
    logger.info("🚀 Iniciando scrape_agent_skills.py")
    skills_path = os.path.join(CONFIG["FOLDER"], AGENT_SKILLS_FILENAME)
    
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        skills_sh, agentskills, github = await asyncio.gather(
            fetch_skills_sh(session),
            fetch_agentskills_io(session),
            fetch_github_skills(session),
        )
    
    all_items = deduplicate(skills_sh + agentskills + github)
    
    # Añadir timestamp
    now = datetime.now().isoformat()
    for item in all_items:
        if TS_KEY not in item:
            item[TS_KEY] = now
    
    # Cargar existentes y combinar
    existing = load_json(skills_path)
    existing_urls = {s.get(ENLACE_KEY) for s in existing if s.get(ENLACE_KEY)}
    truly_new = [s for s in all_items if s.get(ENLACE_KEY) not in existing_urls]
    
    if truly_new:
        combined = truly_new + existing
        combined = combined[:200]  # Mantener max 200
        save_json(skills_path, combined)
        logger.info(f"💾 {len(truly_new)} skills nuevas guardadas en {skills_path}")
    else:
        logger.info("📭 No hay skills nuevas.")
    
    logger.info("✅ scrape_agent_skills.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
