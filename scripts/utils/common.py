import os
import json
import re
import random
import asyncio
import logging
from pathlib import Path
from slugify import slugify
from bs4 import BeautifulSoup
import requests
from PIL import Image
from scripts.utils.constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE, PROMPT_RESUMIR_NOTICIA, PROMPT_RESUMIR_LOTE, PROMPT_RECAP_SEMANAL, PROMPT_TRADUCIR_TITULOS, FALLBACK_IMAGE_URL, FALLBACK_RECAP_INTRO, ORIGEN_KEY, VAL_RSS, ENLACE_KEY, TITULO_KEY, CATEGORIA_KEY, FUENTE_KEY, BADGE_KEY

logger = logging.getLogger("scraper")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
    """Fetch article text + Gemini summary (1-2 lines) for a single news item."""
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
                if len(resumen) > 255:
                    resumen = resumen[:252] + "..."
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
    fecha_actual: str = "",
    semana_info: str = "",
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
        fecha_actual=fecha_actual,
        semana_info=semana_info,
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

async def _generar_imagen_noticia(
    titulo_noticia: str,
    client,
    *,
    prompt_template: str,
    images_folder: str,
    images_prefix: str,
    fallback_url: str,
) -> str:
    modelos = CONFIG.get("IMAGE_MODELS", ["imagen-3.0-generate-002"])
    slug = slugify(titulo_noticia)[:40]
    filename = f"{slug}.png"

    folder = Path(images_folder)
    if not folder.is_absolute():
        folder = PROJECT_ROOT / folder
    filepath = folder / filename

    if filepath.exists():
        return f"{images_prefix}/{filename}"

    prompt_completo = prompt_template.format(titulo_post=titulo_noticia)

    for modelo in modelos:
        for intento in range(3):
            try:
                logger.info(f"🎨 Generando imagen con {modelo} para: '{titulo_noticia}'...")
                response = client.models.generate_images(
                    model=modelo, prompt=prompt_completo,
                    config=dict(number_of_images=1)
                )
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(response.image_bytes)

                # Validación post-generación
                try:
                    img = Image.open(filepath)
                    img.verify()
                    img = Image.open(filepath)
                    w, h = img.size
                    if w < 200 or h < 200:
                        raise ValueError(f"Imagen demasiado pequeña: {w}x{h}")
                except Exception as ve:
                    logger.warning(f"⚠️ Imagen inválida: {ve}. Reintentando...")
                    filepath.unlink(missing_ok=True)
                    continue

                # Strip metadata
                clean = Image.new(img.mode, img.size)
                clean.paste(img)

                # Constrain size
                if clean.width > 1920:
                    ratio = 1920 / clean.width
                    clean = clean.resize((1920, int(clean.height * ratio)), Image.LANCZOS)

                clean.save(filepath, format="PNG")

                # WebP sidecar
                webp_path = filepath.with_suffix(".webp")
                clean.save(webp_path, format="WEBP", quality=85, method=6)

                return f"{images_prefix}/{filename}"

            except Exception as e:
                error_str = str(e).upper()
                if "429" in error_str or "RATE_LIMIT" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = 2 ** intento + random.random() * 0.5
                    logger.warning(f"⏳ Rate limit en {modelo}, esperando {wait:.1f}s...")
                    await asyncio.sleep(wait)
                elif "API_KEY_INVALID" in error_str:
                    logger.error("🔑 API KEY INVÁLIDA.")
                    return fallback_url
                else:
                    logger.warning(f"⚠️ Fallo imagen con {modelo}: {e}. Intentando siguiente...")
                    break

    return fallback_url


async def generar_imagen_noticia(titulo_noticia: str, client, prompt_template: str = PROMPT_IMAGEN_TEMPLATE, fallback_url: str | None = None) -> str:
    return await _generar_imagen_noticia(
        titulo_noticia, client,
        prompt_template=prompt_template,
        images_folder=CONFIG.get("IMAGES_FOLDER", "images"),
        images_prefix=CONFIG.get("IMAGES_PATH_PREFIX", "public/optimizado"),
        fallback_url=fallback_url or FALLBACK_IMAGE_URL,
    )

async def traducir_titulos_ia(noticias: list, client) -> list:
    """Traduce una lista de títulos al español en un solo bloque usando Gemini.
    Solo traduce items que NO tengan 'traducido=True'."""
    if not noticias: return noticias
    
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    
    # Preparamos el texto a traducir (solo los que no están traducidos)
    indices_traducir = []
    lineas = []
    for i, n in enumerate(noticias):
        if n.get('traducido'):
            continue
        titulo = n.get('titulo', '').strip()
        if titulo:
            indices_traducir.append(i)
            lineas.append(f"{i}|{titulo}")
    
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
                    n['traducido'] = True

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

    # Gemini falló en todos los modelos → fallback con IA local (Ollama)
    _traducir_con_ollama(noticias, indices_traducir, lineas)

    return noticias


def _traducir_con_ollama(noticias: list, indices: list, lineas: list):
    """Fallback local: traduce títulos con Ollama (qwen2.5) si Gemini falla.
    Silenciosamente no hace nada si no hay Ollama disponible (timeout corto).
    Marca 'traducido=True' solo en los que consiga traducir."""
    import urllib.request
    # El workflow puede desactivar el fallback (ej: Gemini pasó el ping)
    if os.environ.get("OLLAMA_DISABLED") == "1":
        logger.info("ℹ️ Fallback Ollama desactivado por configuración")
        return 0
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")

    # Ping rápido (GET /api/tags): ¿está Ollama corriendo? Sin generar nada.
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=3) as r:
            r.read()
    except Exception:
        logger.info("ℹ️ Ollama no disponible; sin fallback de traducción")
        return 0

    prompt = PROMPT_TRADUCIR_TITULOS.format(texto_a_traducir="\n".join(lineas))
    try:
        req = urllib.request.Request(
            f"{url}/api/generate",
            data=json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = json.loads(r.read().decode()).get("response", "")
        clean = re.sub(r'```(?:json)?\s*|\s*```', '', raw.strip())
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        data = json.loads(match.group(0)) if match else json.loads(clean)
        traducciones = {int(item['id']): item['tr']
                        for item in data.get('traducciones', [])}
        ok = 0
        for i in indices:
            tr = traducciones.get(i)
            if tr and len(tr.strip()) > 5:
                noticias[i]['titulo'] = tr
                noticias[i]['traducido'] = True
                ok += 1
        if ok:
            logger.info(f"🦙 {ok} títulos traducidos con {model} (fallback local)")
        return ok
    except Exception as e:
        logger.warning(f"⚠️ Fallback Ollama falló: {e}")
        return 0


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
