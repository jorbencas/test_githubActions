import os
import json
import re
import asyncio
import logging
from slugify import slugify
from bs4 import BeautifulSoup
import requests
from constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE

logger = logging.getLogger("scraper")


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


async def resumir_noticia(item: dict, client, max_prompt_chars: int = 3000) -> str | None:
    """Fetch article text + Gemini summary (3-4 lines) for a single news item."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])

    texto = extraer_texto_articulo(item["enlace"], max_chars=max_prompt_chars)
    if not texto:
        texto = item.get("titulo", "")

    prompt = f"""
    Eres un periodista de tecnología que escribe resúmenes de 3-4 líneas en español.
    Resuma la siguiente noticia de forma concisa y directa, destacando:
    - Qué ha ocurrido exactamente
    - Por qué es relevante para el sector tech
    - Un dato concreto si aparece en el texto

    TÍTULO: {item['titulo']}
    FUENTE: {item['fuente']}
    TEXTO:
    {texto[:max_prompt_chars]}

    Responde SOLO con el resumen, sin introducciones ni etiquetas. (máx 500 caracteres)
    """
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

async def obtener_recap_semanal_ia(noticias: list, client) -> dict | None:
    """Genera el resumen semanal probando varios modelos."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])

    texto_noticias = "\n".join([
        f"- [{n['fuente']}] {n['titulo']} (fecha: {n.get('fecha_publicacion', 'reciente')})"
        for n in noticias[:20]
    ])
    prompt = f"""
    Eres un editor senior de tecnología con estilo cercano pero analítico (como una mezcla de Xataka y El Pingüino de Mario).
    Analiza estos titulares y genera un RECAP SEMANAL DETALLADO.

    NORMAS DE ESTILO:
    - Voz directa, sin intro genérica tipo "en un mundo digital..."
    - Asume que el lector ya sigue tecnología, ve al grano
    - Si una noticia es hype sin sustancia, menciónalo
    - NO uses markdown dentro del JSON (ni **, ni ###, ni ---)
    - Sé específico: menciona nombres de productos, empresas, versiones
    - Aporta contexto: no solo digas qué pasó, di por qué es relevante ahora

    NOTICIAS:
    {texto_noticias}

    RESPONDE EXCLUSIVAMENTE UN JSON VÁLIDO (sin markdown ni comentarios):
    {{
      "introduccion": "Párrafo analítico de 4-6 líneas conectando las tendencias clave de la semana. Menciona al menos 2-3 temas concretos. (max 700 chars)",
      "noticias_destacadas": [
        {{
          "titulo": "Título descriptivo del primer tema destacado",
          "suceso": "Qué ocurrió exactamente, con detalles concretos (2-3 líneas)",
          "impacto": "Por qué importa para el lector y qué implicaciones tiene (2-3 líneas)"
        }},
        {{
          "titulo": "Título descriptivo del segundo tema destacado",
          "suceso": "Qué ocurrió exactamente, con detalles concretos (2-3 líneas)",
          "impacto": "Por qué importa para el lector y qué implicaciones tiene (2-3 líneas)"
        }},
        {{
          "titulo": "Título descriptivo del tercer tema destacado",
          "suceso": "Qué ocurrió exactamente, con detalles concretos (2-3 líneas)",
          "impacto": "Por qué importa para el lector y qué implicaciones tiene (2-3 líneas)"
        }}
      ],
      "repo": {{
        "nombre": "Nombre del repo/herramienta destacado de la semana",
        "url": "URL del repo",
        "desc": "Utilidad práctica en 1-2 frases, explicando el problema que resuelve"
      }},
      "tldr": ["Punto clave 1 con contexto (max 160 chars)", "Punto clave 2 con contexto (max 160 chars)", "Punto clave 3 con contexto (max 160 chars)", "Punto clave 4 con contexto (max 160 chars)"],
      "tags": ["tech", "tag_especifico1", "tag_especifico2", "tag_especifico3"],
      "sneak_peek": "Un párrafo breve sobre qué esperar la próxima semana, con predicciones concretas basadas en los temas actuales. Sin promesas vacías. (max 350 chars)",
      "nota_personal": "Reflexión genuina en 2-3 líneas, como si se lo dijeras a un colega. Menciona algún aprendizaje o sorpresa de la semana. (max 320 chars)"
    }}
    """

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
        "introduccion": "Esta semana hemos seguido de cerca las principales tendencias en tecnología y desarrollo.",
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
            
    return fallback_url or "public/img/arquitectura_web.webp"

async def traducir_titulos_ia(noticias: list, client) -> list:
    """Traduce una lista de títulos al español en un solo bloque usando Gemini."""
    if not noticias: return noticias
    
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    
    # Preparamos el texto a traducir (solo los que provienen de fuentes en inglés)
    indices_traducir = []
    lineas = []
    for i, n in enumerate(noticias):
        fuente = n.get('fuente', '').lower()
        if any(x in fuente for x in ["wired", "verge", "techcrunch", "github", "openai", "hacker news", "ars", "nvidia", "anthropic", "venturebeat", "mit", "hugging face", "google ai", "deepmind", "dev.to"]):
            indices_traducir.append(i)
            lineas.append(f"{i}|{n['titulo']}")
    
    if not lineas:
        return noticias
    
    texto_a_traducir = "\n".join(lineas)
    
    prompt = f"""
    Traduce estos titulares de tecnología al español de forma profesional y natural.
    Mantén nombres propios, marcas y acrónimos (OpenAI, NVIDIA, iPhone, etc.) sin traducir.
    Conserva el formato "id|título" en la respuesta.
    Devuelve SOLO JSON, sin markdown ni explicaciones.
    
    TEXTO:
    {texto_a_traducir}
    
    FORMATO:
    {{"traducciones": [{{"id": 0, "tr": "Título traducido 0"}}, {{"id": 1, "tr": "Título traducido 1"}}]}}
    """
    
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
    url = url.split("?")[0].split("#")[0]
    url = url.rstrip("/")
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url.lower()


def deduplicar_items(items: list, umbral_similitud: float = 0.85) -> list:
    urls_vistas: set = set()
    titulos_vistos: list[str] = []
    resultado: list = []

    for item in items:
        url = normalizar_url(item.get("enlace", ""))
        if url and url in urls_vistas:
            continue
        if url:
            urls_vistas.add(url)

        titulo = (item.get("titulo") or "").lower().strip()
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
