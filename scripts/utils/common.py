import os
import json
import re
import asyncio
import logging
from slugify import slugify
from bs4 import BeautifulSoup
import requests
from scripts.utils.constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE, PROMPT_RESUMIR_NOTICIA, PROMPT_RESUMIR_LOTE, PROMPT_RECAP_SEMANAL, PROMPT_TRADUCIR_TITULOS, FALLBACK_IMAGE_URL, FALLBACK_RECAP_INTRO, FUENTES_INGLES, ORIGEN_KEY, VAL_RSS, ENLACE_KEY, TITULO_KEY, CATEGORIA_KEY, FUENTE_KEY, BADGE_KEY

logger = logging.getLogger("scraper")


def load_json(path: str) -> list:
    """Load JSON file, return [] on any failure."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json(path: str, data: list):
    """Save list to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


HEADERS_ARTICLE = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def extraer_texto_articulo(url: str, max_chars: int = 4000) -> str:
    """Fetch a URL, extract readable text content via BeautifulSoup, return first max_chars chars."""
    try:
        r = requests.get(url, timeout=15, headers=HEADERS_ARTICLE)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
            tag.decompose()
        for selector in ["article", "main", ".post-content", ".entry-content", ".article-body",
                         '[role="main"]', ".content", "#content", ".story-body"]:
            main = soup.select_one(selector)
            if main:
                text = main.get_text(separator=" ", strip=True)
                break
        else:
            text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception as e:
        logger.debug(f"⚠️ No se pudo extraer texto de {url}: {e}")
        return ""


async def resumir_lote_noticias(noticias: list, client) -> str | None:
    """Generates a short 2-3 line intro paragraph for a batch of headlines."""
    if not noticias:
        return None
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    texto = "\n".join(f"- [{n.get('fuente','?')}] {n.get('titulo','?')}" for n in noticias[:8])
    prompt = PROMPT_RESUMIR_LOTE.format(texto=texto)
    for modelo in modelos:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            if response and response.text:
                return response.text.strip()[:300]
        except Exception:
            continue
    return None


async def resumir_noticia(item: dict, client, max_prompt_chars: int = 3000) -> str | None:
    """Fetch article text + Gemini summary (3-4 lines) for a single news item."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])

    texto = extraer_texto_articulo(item[ENLACE_KEY], max_chars=max_prompt_chars)
    if not texto:
        texto = item.get(TITULO_KEY, "")

    prompt = PROMPT_RESUMIR_NOTICIA.format(titulo=item['titulo'], fuente=item['fuente'], texto=texto[:max_prompt_chars])
    for modelo in modelos:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            if response and response.text:
                resumen = response.text.strip()
                if len(resumen) > 500:
                    resumen = resumen[:497] + "..."
                return resumen
        except Exception as e:
            logger.warning(f"⚠️ Error resumiendo con {modelo}: {e}")
            continue
    return None

async def obtener_recap_semanal_ia(
    noticias: list,
    client,
    resumen_cats: str | None = None,
    total_rss: int | None = None,
    texto_noticias: str | None = None,
    fuentes_top: list | None = None,
    categorias_ordenadas: list | None = None,
) -> dict | None:
    """Genera el resumen semanal probando varios modelos."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])

    # Si no se proporcionan pre-calculados, calcular aquí
    if resumen_cats is None:
        categorias = {}
        for n in noticias[:30]:
            cat = n.get(CATEGORIA_KEY, "💡 General")
            categorias.setdefault(cat, []).append(n[TITULO_KEY])
        resumen_cats = "\n".join(
            f"  [{cat}] ({len(items)} noticias)" for cat, items in sorted(categorias.items(), key=lambda x: -len(x[1]))[:5]
        )
    if total_rss is None:
        total_rss = sum(1 for n in noticias if n.get(ORIGEN_KEY) == VAL_RSS)
    if texto_noticias is None:
        texto_noticias = "\n".join([
            f"- [{n[FUENTE_KEY]}] {n[TITULO_KEY]} (categoria: {n.get(CATEGORIA_KEY, '💡 General')}, badge: {n.get(BADGE_KEY, 'Tech')}, origen: {n.get(ORIGEN_KEY, 'web')})"
            for n in noticias[:25]
        ])
    if fuentes_top is None:
        fuente_count = {}
        for n in noticias:
            fuente_count[n[FUENTE_KEY]] = fuente_count.get(n[FUENTE_KEY], 0) + 1
        fuentes_top = sorted(fuente_count.items(), key=lambda x: -x[1])[:5]

    prompt = PROMPT_RECAP_SEMANAL.format(
        resumen_cats=resumen_cats,
        total_rss=total_rss,
        texto_noticias=texto_noticias,
    )

    for modelo in modelos:
        logger.info(f"🗞️ Generando Recap con modelo: {modelo}")
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            raw_text = response.text if response.text else "{}"
            # Extracción robusta de JSON con Regex
            match = re.search(r'(\{.*\})', raw_text.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Fallback simple si falla regex
            clean_json = re.sub(r'```json|```', '', raw_text).strip()
            return json.loads(clean_json)
        except Exception as e:
            error_str = str(e).upper()
            if "API_KEY_INVALID" in error_str or ("INVALID_ARGUMENT" in error_str and "API KEY" in error_str):
                logger.error(f"🔑 API KEY INVÁLIDA. Configura GEMINI_API_KEY correctamente.")
                return None
            elif "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"⏳ Cuota excedida en {modelo}. Probando siguiente...")
                continue
            elif "404" in error_str or "NOT_FOUND" in error_str:
                logger.warning(f"⚠️ Modelo {modelo} no encontrado (404). Saltando...")
                continue
            logger.error(f"❌ Error Recap ({modelo}): {e}")
    logger.error("❌ Fallo total en Recap IA. Generando fallback básico.")
    # Fallback básico si falla la IA: usamos los títulos originales
    recap_fallback = "\n".join([f"### {n['titulo']}\n---" for n in noticias[:5]])
    return {
        "introduccion": FALLBACK_RECAP_INTRO,
        "noticias_destacadas": recap_fallback,
        "repo": {"nombre": "GitHub", "url": "https://github.com/jorbencas/", "desc": "Proyectos destacados."},
        "tldr": "Novedades semanales en el sector tecnológico.",
        "tags": ["tech", "semanal"],
        "nota_personal": "Fallo en IA: Generado contenido de reserva."
    }

async def generar_imagen_noticia(titulo_noticia: str, client, prompt_template: str = PROMPT_IMAGEN_TEMPLATE, fallback_url: str | None = None) -> str:
    """Genera imagen con fallback de modelos."""

    modelos = CONFIG.get("IMAGE_MODELS", ["imagen-3.0-generate-002"])

    slug = slugify(titulo_noticia)[:40]
    filename = f"{slug}.png"
    images_folder = CONFIG.get("IMAGES_FOLDER", "images")
    images_prefix = CONFIG.get("IMAGES_PATH_PREFIX", "public/optimizado")
    filepath = os.path.join(images_folder, filename)

    if os.path.exists(filepath):
        return f"{images_prefix}/{filename}"

    prompt_completo = prompt_template.format(titulo_post=titulo_noticia)

    for modelo in modelos:
        try:
            logger.info(f"🎨 Generando imagen con {modelo} para: '{titulo_noticia}'...")
            response = client.models.generate_images(model=modelo, prompt=prompt_completo, config=dict(number_of_images=1))
            os.makedirs(images_folder, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.image_bytes)
            return f"{images_prefix}/{filename}"
        except Exception as e:
            logger.warning(f"⚠️ Fallo imagen con {modelo}: {e}. Intentando siguiente...")
            
    return fallback_url or FALLBACK_IMAGE_URL

async def traducir_titulos_ia(noticias: list, client) -> list:
    """Traduce una lista de títulos al español en un solo bloque usando Gemini."""
    if not noticias: return noticias
    
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    
    # Preparamos el texto a traducir (solo los que provienen de fuentes en inglés)
    indices_traducir = []
    lineas = []
    for i, n in enumerate(noticias):
        fuente = n.get('fuente', '').lower()
        if any(x in fuente for x in FUENTES_INGLES):
            indices_traducir.append(i)
            lineas.append(f"{i}|{n['titulo']}")
    
    if not lineas:
        return noticias
    
    texto_a_traducir = "\n".join(lineas)
    
    prompt = PROMPT_TRADUCIR_TITULOS.format(texto_a_traducir=texto_a_traducir)
    
    for modelo in modelos:
        try:
            logger.info(f"🌐 Traduciendo {len(lineas)} títulos con {modelo}...")
            response = client.models.generate_content(model=modelo, contents=prompt)
            raw_text = response.text if response.text else "{}"

            clean = re.sub(r'```(?:json)?\s*|\s*```', '', raw_text.strip())
            match = re.search(r'\{.*\}', clean, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                data = json.loads(clean)

            traducciones = {item['id']: item['tr'] for item in data.get('traducciones', [])}

            for i, n in enumerate(noticias):
                if i in traducciones and traducciones[i] and len(traducciones[i].strip()) > 5:
                    n['titulo'] = traducciones[i]

            return noticias
        except Exception as e:
            error_str = str(e).upper()
            if "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"⏳ Cuota excedida en {modelo} (traducción). Probando siguiente...")
            elif "404" in error_str or "NOT_FOUND" in error_str:
                logger.warning(f"⚠️ Modelo {modelo} no disponible (404) para traducción. Saltando...")
            else:
                logger.error(f"❌ Error traducción batch ({modelo}): {e}")
            continue

    return noticias


def normalizar_url(url: str) -> str:
    if not url:
        return ""
    # Preserve YouTube video IDs (v= param) and other query-based IDs
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    # For YouTube, keep the v= parameter in the normalized URL
    if "youtube.com" in (parsed.hostname or "") and "v" in params:
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?v={params['v'][0]}"
    else:
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    normalized = normalized.rstrip("/")
    return normalized.lower()


def deduplicar_items(items: list, umbral_similitud: float = 0.85) -> list:
    urls_vistas: set = set()
    titulos_vistos: list[str] = []
    resultado: list = []

    for item in items:
        url = normalizar_url(item.get(ENLACE_KEY, ""))
        if url and url in urls_vistas:
            continue
        if url:
            urls_vistas.add(url)

        titulo = (item.get(TITULO_KEY) or "").lower().strip()
        if titulo:
            duplicado = False
            for t in titulos_vistos:
                min_len = min(len(titulo), len(t))
                if min_len > 10:
                    prefijo = int(min_len * umbral_similitud)
                    if titulo[:prefijo] == t[:prefijo]:
                        duplicado = True
                        break
            if duplicado:
                continue
            titulos_vistos.append(titulo)

        resultado.append(item)

    return resultado
