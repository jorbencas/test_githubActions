#!/usr/bin/env python3
"""
scrape_publicapis.py — Extrae APIs de publicapis.io y las guarda en formato compatible con el pipeline de recursos.
Salida: files/publicapis_apis.json (formato igual a herramientas.json para manage_resources.py).

Incluye detección automática de pricing: visita la web de cada API y busca indicadores
de planes de pago (pricing, plans, enterprise, etc.)
"""
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("scrape_publicapis")

BASE_URL = "https://publicapis.io"
OUTPUT_FILE = Path("files/publicapis_apis.json")

# Overrides manuales para APIs con información incorrecta en publicapis.io
# Formato: {"titulo": "pricing"}
PRICING_OVERRIDES = {
    "Connexun": "paid",  # 500€/month - incorrectly marked as free on publicapis.io
}

# Palabras clave que indican planes de pago
PAID_KEYWORDS = [
    "pricing", "plans", "enterprise", "business", "pro plan", "starter plan",
    "basic plan", "premium", "per month", "per year", "/mo", "/yr",
    "starts at", "starting at", "price", "subscription", "free tier",
    "free plan", "limited free", "free trial", "credit card",
]

# Palabras clave que indican que es completamente gratuito
FREE_KEYWORDS = [
    "completely free", "100% free", "no credit card", "always free",
    "free forever", "no payment", "open source", "github.com",
]


def fetch_page(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def check_pricing_from_website(api_url: str) -> str:
    """Visita la web de la API y busca indicadores de pricing.
    
    Returns: "free", "paid", "freemium", o "" (desconocido)
    """
    try:
        # Normalizar URL
        if not api_url.startswith("http"):
            return ""
        
        html = fetch_page(api_url)
        if not html:
            return ""
        
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text().lower()
        
        # Buscar enlaces a páginas de pricing
        pricing_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            link_text = a.get_text().lower()
            if any(kw in href or kw in link_text for kw in ["pricing", "plans", "enterprise", "business"]):
                pricing_links.append(a["href"])
        
        # Si hay enlaces a pricing, probablemente tiene planes de pago
        if pricing_links:
            # Visitar la primera página de pricing para más detalles
            pricing_url = urljoin(api_url, pricing_links[0])
            pricing_html = fetch_page(pricing_url)
            if pricing_html:
                pricing_text = pricing_html.lower()
                
                # Buscar precios específicos
                price_patterns = [
                    r'\$\d+', r'€\d+', r'£\d+',
                    r'\d+\s*/\s*month', r'\d+\s*/\s*year',
                    r'per\s+month', r'per\s+year',
                ]
                for pattern in price_patterns:
                    if re.search(pattern, pricing_text):
                        return "paid"
                
                # Buscar indicadores de free tier
                if any(kw in pricing_text for kw in FREE_KEYWORDS):
                    return "freemium"
                
                # Si tiene página de pricing pero no encontramos precios claros
                return "paid"
        
        # Buscar en el texto principal indicadores de pago
        for kw in PAID_KEYWORDS:
            if kw in text:
                # Verificar si también hay indicadores de free
                if any(fk in text for fk in FREE_KEYWORDS):
                    return "freemium"
                return "paid"
        
        # No se encontraron indicadores de pago
        return "free"
        
    except Exception as e:
        logger.debug(f"Error checking pricing for {api_url}: {e}")
        return ""


def parse_resources(html: str) -> list[dict]:
    """Parse resources from publicapis.io HTML page."""
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

        # Title
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
            "pricing": PRICING_OVERRIDES.get(title, ""),
        })

    return resources


def enrich_pricing(resources: list[dict]) -> list[dict]:
    """Enriquece los recursos con información de pricing de sus webs."""
    logger.info("🔍 Verificando pricing de APIs...")
    checked = 0
    enriched = 0
    
    for r in resources:
        # Si ya tiene pricing (override), saltar
        if r.get("pricing"):
            continue
        
        # Solo verificar APIs nuevas o sin pricing
        api_url = r.get("enlace", "")
        if not api_url or "publicapis.io" in api_url:
            continue
        
        pricing = check_pricing_from_website(api_url)
        if pricing:
            r["pricing"] = pricing
            enriched += 1
        
        checked += 1
        if checked % 50 == 0:
            logger.info(f"  Verificadas {checked} APIs ({enriched} con pricing encontrado)")
    
    logger.info(f"✅ Pricing verificado: {checked} APIs revisadas, {enriched} con pricing detectado")
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
        # Enriquecer con pricing solo para APIs nuevas
        resources = enrich_pricing(resources)
        save_resources(resources)
        cats = {}
        for r in resources:
            c = r.get("categoria", "Sin categoría")
            cats[c] = cats.get(c, 0) + 1
        print("\n📈 Resumen por categoría:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:15]:
            print(f"  {cat}: {count}")
        
        # Resumen de pricing
        pricing_counts = {}
        for r in resources:
            p = r.get("pricing", "unknown")
            pricing_counts[p] = pricing_counts.get(p, 0) + 1
        print("\n💰 Resumen de pricing:")
        for p, count in sorted(pricing_counts.items(), key=lambda x: -x[1]):
            print(f"  {p}: {count}")
    else:
        logger.warning("⚠️ No se encontraron APIs")


if __name__ == "__main__":
    main()
