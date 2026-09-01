#!/usr/bin/env python3
"""
scrape_concepts.py — Scrapea conceptos de programación desde fuentes web españolas.
Guarda conceptos nuevos en files/concepts_database.json.

Fuentes:
  - refactoring.guru/es (patrones de diseño)
  - java-design-patterns.com/es (patrones Java)
  - midudev.com (JS, Docker, conceptos)
  - programacion.net (programación general)
  - metaok.com (seguridad, JWT, Docker)
  - coderhouse.com/coderlibrary (RAG, IA)

Uso:
    python -m scripts.scrapers.scrape_concepts --tier full
    python -m scripts.scrapers.scrape_concepts --tier light
    python -m scripts.scrapers.scrape_concepts --source refactorizando
"""
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from scripts.utils.constants_downloadfile import (
    CONFIG, LOGS_DIR, LOG_FILES,
    CONCEPTS_FILENAME, CONCEPTS_PATH_DEFAULT,
    CONCEPTS_MAX, CONCEPTS_PRUNE_BATCH, CONCEPTS_MIN_INTERVIEW,
)

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(
            os.path.join(LOGS_DIR, LOG_FILES.get("concepts", "concepts.log")),
            maxBytes=1024 * 1024 * 5, backupCount=3, encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("concepts")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

# ── Categorías del sistema ──
CONCEPT_CATEGORIES = {
    "patrones_diseno": "Patrones de Diseño",
    "poo": "POO",
    "seguridad_web": "Seguridad Web",
    "kafka": "Kafka y Mensajería",
    "multithread": "Multithreading",
    "rag_ai": "RAG e IA",
    "entrevistas": "Entrevistas Técnicas",
    "arquitectura": "Arquitectura",
    "bases_datos": "Bases de Datos",
    "concurrency": "Concurrencia",
    "rendering": "Renderizado",
    "devops": "DevOps",
    "habilidades": "Habilidades y Skills",
}

# Mapeo de contenido detectado → categoría
KEYWORD_TO_CAT = {
    # Patrones de diseño
    "singleton": ("patrones_diseno", 2),
    "factory": ("patrones_diseno", 2),
    "abstract factory": ("patrones_diseno", 3),
    "observer": ("patrones_diseno", 2),
    "strategy": ("patrones_diseno", 2),
    "decorator": ("patrones_diseno", 2),
    "adapter": ("patrones_diseno", 2),
    "proxy": ("patrones_diseno", 3),
    "command": ("patrones_diseno", 2),
    "builder": ("patrones_diseno", 2),
    "patrón de diseño": ("patrones_diseno", 2),
    "design pattern": ("patrones_diseno", 2),
    "solid": ("patrones_diseno", 2),
    # POO
    "herencia": ("poo", 1),
    "polimorfismo": ("poo", 2),
    "encapsulamiento": ("poo", 1),
    "abstracción": ("poo", 2),
    "composición": ("poo", 2),
    "orientado a objetos": ("poo", 1),
    # Seguridad
    "csrf": ("seguridad_web", 2),
    "xss": ("seguridad_web", 2),
    "sql injection": ("seguridad_web", 2),
    "jwt": ("seguridad_web", 2),
    "oauth": ("seguridad_web", 3),
    "token": ("seguridad_web", 2),
    "seguridad web": ("seguridad_web", 2),
    # Kafka
    "kafka": ("kafka", 3),
    "consumer group": ("kafka", 3),
    "partition": ("kafka", 3),
    "message broker": ("kafka", 3),
    "event streaming": ("kafka", 3),
    # Multithread
    "executorservice": ("multithread", 3),
    "executor service": ("multithread", 3),
    "completablefuture": ("multithread", 3),
    "threading": ("multithread", 2),
    "multithread": ("multithread", 2),
    "goroutine": ("multithread", 3),
    "asyncio": ("multithread", 3),
    "coroutine": ("multithread", 3),
    "worker thread": ("multithread", 3),
    # RAG / IA
    "rag": ("rag_ai", 3),
    "retrieval augmented": ("rag_ai", 3),
    "graphrag": ("rag_ai", 3),
    "embedding": ("rag_ai", 3),
    "vector database": ("rag_ai", 3),
    "ai agent": ("rag_ai", 3),
    # Entrevistas
    "big o": ("entrevistas", 2),
    "entrevista": ("entrevistas", 2),
    "system design": ("entrevistas", 3),
    "data structure": ("entrevistas", 2),
    # Arquitectura
    "microservicio": ("arquitectura", 3),
    "microservice": ("arquitectura", 3),
    "event driven": ("arquitectura", 3),
    "cqrs": ("arquitectura", 3),
    "saga": ("arquitectura", 3),
    "circuit breaker": ("arquitectura", 3),
    # Bases de datos
    "acid": ("bases_datos", 2),
    "índice": ("bases_datos", 2),
    "b-tree": ("bases_datos", 3),
    "replicación": ("bases_datos", 3),
    "sharding": ("bases_datos", 3),
    # Concurrency
    "deadlock": ("concurrency", 3),
    "race condition": ("concurrency", 2),
    "thread pool": ("concurrency", 2),
    "async/await": ("concurrency", 2),
    # Rendering
    "game loop": ("rendering", 2),
    "frame rate": ("rendering", 2),
    "ray tracing": ("rendering", 3),
    "ecs": ("rendering", 3),
    # DevOps
    "docker": ("devops", 2),
    "kubernetes": ("devops", 3),
    "ci/cd": ("devops", 2),
    # Habilidades
    "refactor": ("habilidades", 2),
    "refactoring": ("habilidades", 2),
    "dry": ("habilidades", 2),
    "code smell": ("habilidades", 2),
    "technical debt": ("habilidades", 2),
    "deuda técnica": ("habilidades", 2),
    "automatizar": ("habilidades", 1),
    "automatización": ("habilidades", 2),
    "abstracción": ("habilidades", 2),
    "skill": ("habilidades", 1),
    "habilidad": ("habilidades", 1),
    "yagni": ("habilidades", 2),
    "boy scout": ("habilidades", 1),
    "clean code": ("habilidades", 2),
    "separación de concerns": ("habilidades", 2),
    "srp": ("habilidades", 2),
    "single responsibility": ("habilidades", 2),
    # Interfaces y Abstract
    "interface": ("interfaces", 2),
    "abstract class": ("interfaces", 2),
    "clase abstracta": ("interfaces", 2),
    "contrato": ("interfaces", 2),
    "dependency inversion": ("interfaces", 2),
    "inversión de dependencias": ("interfaces", 2),
    # CSS Moderno
    "css grid": ("css_moderno", 2),
    "container queries": ("css_moderno", 2),
    ":has()": ("css_moderno", 2),
    "css nesting": ("css_moderno", 1),
    "css variables": ("css_moderno", 1),
    "custom properties": ("css_moderno", 1),
    "flexbox": ("css_moderno", 1),
    "clamp()": ("css_moderno", 2),
    "aspect-ratio": ("css_moderno", 1),
    "object-fit": ("css_moderno", 1),
    # Patrones por Lenguaje
    "bff": ("patrones_lenguajes", 3),
    "backend for frontend": ("patrones_lenguajes", 3),
    "repository pattern": ("patrones_lenguajes", 2),
    "dto": ("patrones_lenguajes", 2),
    "data transfer object": ("patrones_lenguajes", 2),
    "value object": ("patrones_lenguajes", 2),
    "aggregate": ("patrones_lenguajes", 3),
}


def fetch_page(url: str, timeout: int = 15) -> str:
    """Fetch a URL and return HTML content."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.debug(f"⚠️ Error fetching {url}: {e}")
        return ""


def classify_concept(title: str, text: str) -> tuple:
    """Classify a concept into category and difficulty based on keywords."""
    combined = (title + " " + text).lower()
    best_cat = "patrones_diseno"
    best_diff = 2
    max_score = 0
    for keyword, (cat, diff) in KEYWORD_TO_CAT.items():
        if keyword in combined:
            score = len(keyword)
            if score > max_score:
                max_score = score
                best_cat = cat
                best_diff = diff
    return best_cat, best_diff


def extract_code_blocks(soup) -> list:
    """Extract code blocks from HTML."""
    codes = []
    for pre in soup.find_all("pre"):
        code_tag = pre.find("code")
        if code_tag:
            text = code_tag.get_text(strip=True)
        else:
            text = pre.get_text(strip=True)
        if text and len(text) > 10 and len(text) < 3000:
            codes.append(text)
    return codes


# ── Parsers por fuente ──

def parse_refactoring_guru() -> list:
    """Scrape design patterns from refactoring.guru/es."""
    concepts = []
    base_url = "https://refactoring.guru/es/design-patterns"
    patterns = [
        "singleton", "factory-method", "abstract-factory", "builder",
        "prototype", "adapter", "bridge", "composite", "decorator",
        "facade", "flyweight", "proxy", "chain-of-responsibility",
        "command", "iterator", "mediator", "memento", "observer",
        "state", "strategy", "template-method", "visitor",
    ]
    logger.info(f"🏗️ Scraping {len(patterns)} patrones desde refactoring.guru...")
    for pattern_slug in patterns:
        url = f"{base_url}/{pattern_slug}"
        html = fetch_page(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else pattern_slug.replace("-", " ").title()
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 30 and "refactoring.guru" not in text.lower():
                paragraphs.append(text)
        explanation = " ".join(paragraphs[:4])[:1500]
        if not explanation:
            continue
        codes = extract_code_blocks(soup)
        code_example = codes[0] if codes else ""
        concepts.append({
            "title": f"Patrón {title}",
            "summary": explanation[:200] + ("..." if len(explanation) > 200 else ""),
            "explanation": explanation,
            "code_example": code_example,
            "use_cases": [],
            "difficulty": 2,
            "language": "general",
            "interview_relevant": True,
            "interview_question": f"¿Cuándo usarías el patrón {title}?",
            "interview_answer": "",
            "source": "refactoring.guru",
            "tags": ["design-patterns", "gof", pattern_slug],
            "cat": "patrones_diseno",
            "scraped_at": datetime.now().isoformat(),
        })
        time.sleep(1)
    logger.info(f"🏗️ refactoring.guru: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_java_design_patterns() -> list:
    """Scrape from java-design-patterns.com/es."""
    concepts = []
    base_url = "https://java-design-patterns.com/es"
    logger.info("☕ Scraping java-design-patterns.com/es...")
    try:
        html = fetch_page(base_url)
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/es/article/" in href:
                name = link.get_text(strip=True)
                if not name or len(name) < 3:
                    continue
                article_url = f"{base_url}{href}" if href.startswith("/") else href
                article_html = fetch_page(article_url)
                if not article_html:
                    continue
                article_soup = BeautifulSoup(article_html, "html.parser")
                paragraphs = []
                for p in article_soup.find_all("p"):
                    text = p.get_text(strip=True)
                    if len(text) > 30:
                        paragraphs.append(text)
                explanation = " ".join(paragraphs[:3])[:1200]
                if explanation:
                    concepts.append({
                        "title": name,
                        "summary": explanation[:200],
                        "explanation": explanation,
                        "code_example": "",
                        "use_cases": [],
                        "difficulty": 2,
                        "language": "java",
                        "interview_relevant": True,
                        "interview_question": f"Explícame el patrón {name}.",
                        "interview_answer": "",
                        "source": "java-design-patterns.com",
                        "tags": ["design-patterns", "java"],
                        "cat": "patrones_diseno",
                        "scraped_at": datetime.now().isoformat(),
                    })
                time.sleep(1)
                if len(concepts) >= 15:
                    break
    except Exception as e:
        logger.error(f"❌ Error java-design-patterns: {e}")
    logger.info(f"☕ java-design-patterns: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_midudev() -> list:
    """Scrape programming concepts from midudev.com."""
    concepts = []
    base_url = "https://midu.dev"
    logger.info(" midudev.com scraping...")
    try:
        html = fetch_page(f"{base_url}/articulos/")
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/articulos/" in href and href != "/articulos/":
                article_links.append(href)
        seen = set()
        for href in article_links[:30]:
            if href in seen:
                continue
            seen.add(href)
            url = f"{base_url}{href}" if href.startswith("/") else href
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else href.split("/")[-1]
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "javascript",
                "interview_relevant": cat in ("entrevistas", "kafka", "rag_ai", "multithread"),
                "interview_question": "",
                "interview_answer": "",
                "source": "midudev.com",
                "tags": ["web", "javascript", cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 20:
                break
    except Exception as e:
        logger.error(f"❌ Error midudev: {e}")
    logger.info(f" midudev: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_programacion_net() -> list:
    """Scrape from programacion.net."""
    concepts = []
    base_url = "https://programacion.net"
    logger.info(" programacion.net scraping...")
    try:
        html = fetch_page(f"{base_url}/articulo/")
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/articulo/" in href and href != "/articulo/":
                article_links.append(href)
        seen = set()
        for href in article_links[:25]:
            if href in seen:
                continue
            seen.add(href)
            url = f"{base_url}{href}" if href.startswith("/") else href
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else href.split("/")[-1]
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "general",
                "interview_relevant": False,
                "interview_question": "",
                "interview_answer": "",
                "source": "programacion.net",
                "tags": [cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 15:
                break
    except Exception as e:
        logger.error(f"❌ Error programacion.net: {e}")
    logger.info(f" programacion.net: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_metaok() -> list:
    """Scrape from metaok.com/blog (security, Docker, JWT)."""
    concepts = []
    base_url = "https://www.metaok.com/blog"
    logger.info(" metaok.com scraping...")
    try:
        html = fetch_page(base_url)
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/blog/" in href and href != "/blog/":
                article_links.append(href)
        seen = set()
        for href in article_links[:20]:
            if href in seen:
                continue
            seen.add(href)
            url = f"https://www.metaok.com{href}" if href.startswith("/") else href
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else href.split("/")[-1]
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "general",
                "interview_relevant": cat in ("seguridad_web", "kafka", "devops"),
                "interview_question": "",
                "interview_answer": "",
                "source": "metaok.com",
                "tags": ["security", "devops", cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 10:
                break
    except Exception as e:
        logger.error(f"❌ Error metaok: {e}")
    logger.info(f" metaok: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_coderhouse() -> list:
    """Scrape from coderhouse.com/coderlibrary (RAG, AI)."""
    concepts = []
    base_url = "https://www.coderhouse.com/coderlibrary"
    logger.info(" coderhouse.com scraping...")
    try:
        html = fetch_page(base_url)
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/coderlibrary/" in href and href != "/coderlibrary/":
                article_links.append(href)
        seen = set()
        for href in article_links[:15]:
            if href in seen:
                continue
            seen.add(href)
            url = f"https://www.coderhouse.com{href}" if href.startswith("/") else href
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else href.split("/")[-1]
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "python",
                "interview_relevant": cat in ("rag_ai", "entrevistas"),
                "interview_question": "",
                "interview_answer": "",
                "source": "coderhouse.com",
                "tags": ["ai", "rag", cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 10:
                break
    except Exception as e:
        logger.error(f"❌ Error coderhouse: {e}")
    logger.info(f" coderhouse: {len(concepts)} conceptos obtenidos")
    return concepts


def deduplicate_concepts(all_concepts: list) -> list:
    """Remove duplicate concepts by title, keeping the longest explanation."""
    seen = {}
    for concept in all_concepts:
        title = concept.get("title", "").lower().strip()
        if not title:
            continue
        if title in seen:
            existing = seen[title]
            if len(concept.get("explanation", "")) > len(existing.get("explanation", "")):
                seen[title] = concept
        else:
            seen[title] = concept
    return list(seen.values())


def prune_database(concepts: list) -> list:
    """Prune database to CONCEPTS_MAX, keeping interview-relevant concepts."""
    if len(concepts) <= CONCEPTS_MAX:
        return concepts
    interview_concepts = [c for c in concepts if c.get("interview_relevant")]
    non_interview = [c for c in concepts if not c.get("interview_relevant")]
    if len(interview_concepts) < CONCEPTS_MIN_INTERVIEW:
        keep_interview = interview_concepts
        need = CONCEPTS_MAX - len(keep_interview)
        non_interview.sort(key=lambda x: x.get("scraped_at", ""), reverse=False)
        keep_non_interview = non_interview[:need]
    else:
        interview_concepts.sort(key=lambda x: x.get("scraped_at", ""), reverse=False)
        keep_interview = interview_concepts[CONCEPTS_PRUNE_BATCH:]
        remaining = CONCEPTS_MAX - len(keep_interview)
        non_interview.sort(key=lambda x: x.get("scraped_at", ""), reverse=False)
        keep_non_interview = non_interview[:remaining]
    result = keep_interview + keep_non_interview
    logger.info(f"✂️ Pruned: {len(concepts)} → {len(result)} conceptos")
    return result


def load_existing_concepts() -> list:
    """Load existing concepts database."""
    path = CONCEPTS_PATH_DEFAULT
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("concepts", [])
    except Exception:
        return []


def save_concepts(concepts: list):
    """Save concepts to database."""
    path = CONCEPTS_PATH_DEFAULT
    categories = list(set(c.get("cat", "general") for c in concepts))
    data = {
        "meta": {
            "version": "1.0",
            "description": "Base de datos de conceptos de programación con niveles y preguntas de entrevista",
            "total_concepts": len(concepts),
            "categories": sorted(categories),
            "last_scraped": datetime.now().isoformat(),
        },
        "concepts": concepts,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"💾 {len(concepts)} conceptos guardados en {path}")


# ── Parsers para Habilidades ──

def parse_refactorizando() -> list:
    """Scrape from refactorizando.com (refactoring, clean code, best practices)."""
    concepts = []
    base_url = "https://refactorizando.com"
    logger.info("🧹 Scraping refactorizando.com...")
    try:
        html = fetch_page(f"{base_url}/category/clean-code/")
        if not html:
            html = fetch_page(base_url)
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if href.startswith(base_url) and href != base_url and "/category/" not in href:
                article_links.append(href)
        seen = set()
        for url in article_links[:20]:
            if url in seen:
                continue
            seen.add(url)
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else url.split("/")[-2].replace("-", " ").title()
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "python",
                "interview_relevant": cat == "habilidades",
                "interview_question": "",
                "interview_answer": "",
                "source": "refactorizando.com",
                "tags": ["clean-code", "refactoring", cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 15:
                break
    except Exception as e:
        logger.error(f"❌ Error refactorizando.com: {e}")
    logger.info(f"🧹 refactorizando.com: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_mouredev() -> list:
    """Scrape from moure.dev (programming best practices, challenges)."""
    concepts = []
    base_url = "https://moure.dev"
    logger.info("🔥 Scraping moure.dev...")
    try:
        html = fetch_page(f"{base_url}/blog/")
        if not html:
            return concepts
        soup = BeautifulSoup(html, "html.parser")
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "/blog/" in href and href != "/blog/" and "moure.dev" in href:
                article_links.append(href)
        seen = set()
        for href in article_links[:15]:
            if href in seen:
                continue
            seen.add(href)
            url = href if href.startswith("http") else f"{base_url}{href}"
            article_html = fetch_page(url)
            if not article_html:
                continue
            article_soup = BeautifulSoup(article_html, "html.parser")
            title_tag = article_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else href.split("/")[-2].replace("-", " ").title()
            paragraphs = []
            for p in article_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    paragraphs.append(text)
            explanation = " ".join(paragraphs[:4])[:1500]
            if not explanation or len(explanation) < 100:
                continue
            cat, diff = classify_concept(title, explanation)
            codes = extract_code_blocks(article_soup)
            concepts.append({
                "title": title,
                "summary": explanation[:200],
                "explanation": explanation,
                "code_example": codes[0] if codes else "",
                "use_cases": [],
                "difficulty": diff,
                "language": "kotlin",
                "interview_relevant": cat in ("habilidades", "entrevistas"),
                "interview_question": "",
                "interview_answer": "",
                "source": "moure.dev",
                "tags": ["best-practices", cat],
                "cat": cat,
                "scraped_at": datetime.now().isoformat(),
            })
            time.sleep(1)
            if len(concepts) >= 10:
                break
    except Exception as e:
        logger.error(f"❌ Error moure.dev: {e}")
    logger.info(f"🔥 moure.dev: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_devto() -> list:
    """Scrape from dev.to (programming articles about skills, best practices)."""
    concepts = []
    logger.info(" dev.to scraping (habilidades)...")
    tags = ["clean-code", "refactoring", "best-practices", "programming", "career", "beginners"]
    seen_urls = set()
    for tag in tags:
        try:
            url = f"https://dev.to/t/{tag}?top=7"
            html = fetch_page(url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            article_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if href.startswith("/") and len(href) > 10 and "/t/" not in href:
                    article_links.append(f"https://dev.to{href}")
            for article_url in article_links[:5]:
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)
                article_html = fetch_page(article_url)
                if not article_html:
                    continue
                article_soup = BeautifulSoup(article_html, "html.parser")
                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 10:
                    continue
                paragraphs = []
                for p in article_soup.find_all("p"):
                    text = p.get_text(strip=True)
                    if len(text) > 40:
                        paragraphs.append(text)
                explanation = " ".join(paragraphs[:4])[:1500]
                if not explanation or len(explanation) < 100:
                    continue
                cat, diff = classify_concept(title, explanation)
                codes = extract_code_blocks(article_soup)
                concepts.append({
                    "title": title,
                    "summary": explanation[:200],
                    "explanation": explanation,
                    "code_example": codes[0] if codes else "",
                    "use_cases": [],
                    "difficulty": diff,
                    "language": "general",
                    "interview_relevant": cat in ("habilidades", "entrevistas"),
                    "interview_question": "",
                    "interview_answer": "",
                    "source": "dev.to",
                    "tags": [tag, cat],
                    "cat": cat,
                    "scraped_at": datetime.now().isoformat(),
                })
                time.sleep(1)
                if len(concepts) >= 10:
                    break
        except Exception as e:
            logger.error(f"❌ Error dev.to ({tag}): {e}")
        if len(concepts) >= 10:
            break
    logger.info(f" dev.to: {len(concepts)} conceptos obtenidos")
    return concepts


def parse_css_modern() -> list:
    """Scrape from web.dev and css-tricks (modern CSS features)."""
    concepts = []
    logger.info("🎨 Scraping CSS moderno...")
    sources = [
        ("web.dev", "https://web.dev/learn/css"),
        ("css-tricks", "https://css-tricks.com"),
    ]
    seen_urls = set()
    for source_name, base_url in sources:
        try:
            html = fetch_page(base_url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            article_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if source_name == "web.dev" and "/css/" in href:
                    url = href if href.startswith("http") else f"https://web.dev{href}"
                    article_links.append(url)
                elif source_name == "css-tricks" and href.startswith("/") and len(href) > 10:
                    article_links.append(f"https://css-tricks.com{href}")
            for url in article_links[:12]:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                article_html = fetch_page(url)
                if not article_html:
                    continue
                article_soup = BeautifulSoup(article_html, "html.parser")
                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title or len(title) < 10:
                    continue
                paragraphs = []
                for p in article_soup.find_all("p"):
                    text = p.get_text(strip=True)
                    if len(text) > 40:
                        paragraphs.append(text)
                explanation = " ".join(paragraphs[:4])[:1500]
                if not explanation or len(explanation) < 100:
                    continue
                cat, diff = classify_concept(title, explanation)
                if cat not in ("css_moderno", "habilidades", "interfaces"):
                    cat = "css_moderno"
                codes = extract_code_blocks(article_soup)
                concepts.append({
                    "title": title,
                    "summary": explanation[:200],
                    "explanation": explanation,
                    "code_example": codes[0] if codes else "",
                    "use_cases": [],
                    "difficulty": diff,
                    "language": "css",
                    "interview_relevant": cat in ("habilidades", "interfaces"),
                    "interview_question": "",
                    "interview_answer": "",
                    "source": source_name,
                    "tags": ["css", "modern", cat],
                    "cat": cat,
                    "scraped_at": datetime.now().isoformat(),
                })
                time.sleep(1)
                if len(concepts) >= 10:
                    break
        except Exception as e:
            logger.error(f"❌ Error {source_name}: {e}")
        if len(concepts) >= 10:
            break
    logger.info(f"🎨 CSS moderno: {len(concepts)} conceptos obtenidos")
    return concepts


SOURCES = {
    "refactorizando": parse_refactoring_guru,
    "java_dp": parse_java_design_patterns,
    "midudev": parse_midudev,
    "programacion": parse_programacion_net,
    "metaok": parse_metaok,
    "coderhouse": parse_coderhouse,
    "refactorizando_clean": parse_refactorizando,
    "mouredev": parse_mouredev,
    "devto": parse_devto,
    "css_modern": parse_css_modern,
}

TIER_LIGHT = ["midudev", "programacion", "refactorizando_clean", "css_modern"]
TIER_FULL = list(SOURCES.keys())


def main():
    args = sys.argv[1:]
    tier = "full"
    source_filter = None
    for i, arg in enumerate(args):
        if arg == "--tier" and i + 1 < len(args):
            tier = args[i + 1]
        if arg == "--source" and i + 1 < len(args):
            source_filter = args[i + 1]

    sources_to_run = TIER_FULL if tier == "full" else TIER_LIGHT
    if source_filter:
        if source_filter in SOURCES:
            sources_to_run = [source_filter]
        else:
            logger.error(f"❌ Fuente desconocida: {source_filter}. Disponibles: {list(SOURCES.keys())}")
            sys.exit(1)

    logger.info(f"🚀 Iniciando scrape_concepts (tier={tier}, sources={sources_to_run})")

    existing = load_existing_concepts()
    existing_titles = {c.get("title", "").lower().strip() for c in existing}
    logger.info(f"📂 Conceptos existentes: {len(existing)}")

    all_new = []
    for source_name in sources_to_run:
        parser_fn = SOURCES[source_name]
        try:
            new_concepts = parser_fn()
            for c in new_concepts:
                title_lower = c.get("title", "").lower().strip()
                if title_lower not in existing_titles:
                    all_new.append(c)
                    existing_titles.add(title_lower)
            logger.info(f"✅ {source_name}: {len(new_concepts)} conceptos scrapeados, {len([c for c in new_concepts if c.get('title', '').lower().strip() in existing_titles])} nuevos")
        except Exception as e:
            logger.error(f"❌ Error en {source_name}: {e}")
        time.sleep(2)

    if all_new:
        combined = existing + all_new
        combined = deduplicate_concepts(combined)
        combined = prune_database(combined)
        save_concepts(combined)
        logger.info(f"📊 Total: {len(existing)} existentes + {len(all_new)} nuevos = {len(combined)} finales")
    else:
        logger.info("📭 No se encontraron conceptos nuevos.")
        save_concepts(existing)

    logger.info("✅ scrape_concepts.py completado.")


if __name__ == "__main__":
    main()
