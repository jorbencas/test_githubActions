#!/usr/bin/env python3
"""
update_resource_format.py — Actualiza todos los ResourceCard al nuevo formato con headline, features y platform.

Uso:
    python scripts/tools/update_resource_format.py                  # Procesar todos los archivos
    python scripts/tools/update_resource_format.py --dry-run        # Sin escribir cambios
    python scripts/tools/update_resource_format.py --limit 10       # Procesar solo 10 cards
    python scripts/tools/update_resource_format.py --file resources3.mdx  # Solo un archivo
"""
import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

from google import genai

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.constants_downloadfile import CONFIG, LOGS_DIR, LOG_FILES

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, LOG_FILES.get("manage_resources", "manage_resources.log")), mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

CARD_PATTERN = re.compile(
    r'<ResourceCard\n  href="([^"]+)"\n  title="([^"]+)"\n  description="([^"]*)"\n/>',
    re.DOTALL,
)

PROMPT_TEMPLATE = """\
Analiza este recurso y genera una descripción estructurada en español.

Título: {title}
URL: {url}
Descripción actual: {description}

Genera UN OBJETO JSON con estas claves:
- "headline": Una frase ganadora que explique qué es el recurso (máx 80 caracteres). Ejemplo: "Un Claude Cowork pero de código abierto"
- "features": Lista de 3-4 características clave, cada una corta (máx 50 caracteres). Empiezan con mayúscula, sin punto al final.
- "platform": Plataforma disponible. Solo uno de estos valores: "macOS, Windows y Linux" | "macOS y Linux" | "Windows y Linux" | "Solo macOS" | "Solo Windows" | "Solo Linux" | "Navegador web" | "API" | "Terminal" | ""

Ejemplo de respuesta:
```json
{{"headline": "Ejecuta LLMs localmente en tu máquina", "features": ["Soporta +100 modelos", "Interfaz web incluida", "Compatible con GPU", "100% open source"], "platform": "macOS, Windows y Linux"}}
```

Responde SOLO con el JSON, sin texto adicional."""


# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_cards_from_file(content: str) -> list[dict]:
    """Extract all ResourceCard entries from a file."""
    cards = []
    for match in CARD_PATTERN.finditer(content):
        url, title, description = match.group(1), match.group(2), match.group(3)
        cards.append({
            "url": url,
            "title": title,
            "description": description,
            "start": match.start(),
            "end": match.end(),
            "original": match.group(0),
        })
    return cards


def generate_structured_description(client, title: str, url: str, description: str, retries: int = 3) -> dict | None:
    """Use Gemini to generate headline, features, and platform."""
    prompt = PROMPT_TEMPLATE.format(title=title, url=url, description=description)
    
    models = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    
    for attempt in range(retries):
        for modelo in models:
            try:
                response = client.models.generate_content(model=modelo, contents=prompt)
                if not response or not response.text:
                    continue
                
                raw = response.text.strip()
                # Clean markdown code blocks
                raw = re.sub(r'```(?:json)?\s*|\s*```', '', raw)
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if not match:
                    continue
                
                data = json.loads(match.group(0))
                
                # Validate required fields
                headline = data.get("headline", "").strip()
                features = data.get("features", [])
                platform = data.get("platform", "").strip()
                
                if not headline or not features:
                    continue
                
                # Ensure features is a list of strings
                if not isinstance(features, list):
                    continue
                features = [str(f).strip() for f in features if f and str(f).strip()]
                
                return {
                    "headline": headline[:100],
                    "features": features[:4],
                    "platform": platform[:50],
                }
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_str = str(e).upper()
                if "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"⏳ Cuota excedida en {modelo}. Esperando 30s...")
                    time.sleep(30)
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    continue
                else:
                    logger.error(f"❌ Error con {modelo}: {e}")
                continue
        
        if attempt < retries - 1:
            time.sleep(5)
    
    return None


def escape_attr(text: str) -> str:
    """Escape text for MDX attribute."""
    return text.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def format_new_card(url: str, title: str, description: str, headline: str, features: list, platform: str) -> str:
    """Format a ResourceCard with the new structure."""
    title_esc = escape_attr(title)
    desc_esc = escape_attr(description)
    headline_esc = escape_attr(headline)
    platform_esc = escape_attr(platform)
    
    features_str = "[" + ", ".join('"' + escape_attr(f) + '"' for f in features) + "]"
    
    return f"""<ResourceCard
  href="{url}"
  title="{title_esc}"
  description="{desc_esc}"
  headline="{headline_esc}"
  features={features_str}
  platform="{platform_esc}"
/>"""


# ── Main ─────────────────────────────────────────────────────────────────────

def process_file(filepath: Path, client, dry_run: bool = False, limit: int = 0) -> int:
    """Process a single resource file. Returns number of cards updated."""
    content = filepath.read_text(encoding="utf-8")
    cards = extract_cards_from_file(content)
    
    if not cards:
        logger.info(f"📄 {filepath.name}: sin ResourceCard encontrados")
        return 0
    
    # Filter cards that already have new format
    cards_to_update = [c for c in cards if "headline" not in c["original"]]
    
    if not cards_to_update:
        logger.info(f"✅ {filepath.name}: todos los cards ya tienen el nuevo formato")
        return 0
    
    logger.info(f"📝 {filepath.name}: {len(cards_to_update)} cards para actualizar")
    
    updated = 0
    for i, card in enumerate(cards_to_update):
        if limit and updated >= limit:
            break
        
        logger.info(f"  [{i+1}/{len(cards_to_update)}] {card['title'][:50]}...")
        
        result = generate_structured_description(client, card["title"], card["url"], card["description"])
        
        if not result:
            logger.warning(f"  ⚠️ No se pudo generar estructura para: {card['title'][:50]}")
            continue
        
        new_card = format_new_card(
            card["url"],
            card["title"],
            card["description"],
            result["headline"],
            result["features"],
            result["platform"],
        )
        
        content = content.replace(card["original"], new_card)
        updated += 1
        
        # Rate limiting
        time.sleep(1)
    
    if updated > 0 and not dry_run:
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"💾 {filepath.name}: {updated} cards actualizados")
    elif dry_run:
        logger.info(f"🔍 Dry-run: {updated} cards se actualizarían en {filepath.name}")
    
    return updated


def main():
    parser = argparse.ArgumentParser(description="Update ResourceCard to new format with headline, features, platform")
    parser.add_argument("--blog-path", default=None, help="Ruta al checkout del blog")
    parser.add_argument("--dry-run", action="store_true", help="Sin escribir cambios")
    parser.add_argument("--limit", type=int, default=0, help="Máximo de cards a procesar (0 = todos)")
    parser.add_argument("--file", default=None, help="Procesar solo un archivo específico")
    args = parser.parse_args()
    
    blog_path = Path(args.blog_path) if args.blog_path else Path(os.path.expanduser("~/dev/blog"))
    posts_dir = blog_path / "src" / "content" / "posts"
    
    if not posts_dir.exists():
        logger.error(f"❌ No se encontró: {posts_dir}")
        return
    
    api_key = CONFIG.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ No se encontró GEMINI_KEY")
        return
    
    client = genai.Client(api_key=api_key)
    
    if args.file:
        files = [posts_dir / args.file]
        if not files[0].exists():
            logger.error(f"❌ No se encontró: {files[0]}")
            return
    else:
        files = sorted(posts_dir.glob("resources*.mdx"), key=lambda p: p.name)
    
    total_updated = 0
    for f in files:
        updated = process_file(f, client, args.dry_run, args.limit)
        total_updated += updated
        if args.limit and total_updated >= args.limit:
            break
    
    logger.info(f"\n✅ Total: {total_updated} cards actualizados")


if __name__ == "__main__":
    main()
