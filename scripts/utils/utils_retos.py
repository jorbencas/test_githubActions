import os
import json
import re
import asyncio
import logging
from slugify import slugify
from scripts.utils.constants_retos import CONFIG, PROMPT_IMAGEN_TEMPLATE_RETO
try:
    from scripts.solutions.solutions_db import lookup, generate_generic
except ImportError:
    def lookup(titulo, lang):
        return None
    def generate_generic(titulo, lang):
        return None

logger = logging.getLogger("scraper")

async def obtener_solucion_ia(titulo: str, fuente: str, client, lang: str = "Python") -> dict | None:
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])

    prompt = f"""
    Resuelve el reto técnico: "{titulo}" de la fuente {fuente}.
    Explica en español pero mantén términos técnicos en inglés.
    Usa el lenguaje de programación: {lang}

    NORMAS DE CÓDIGO:
    - Código COMPLETO y funcional, con imports al inicio y bloque `if __name__ == "__main__"` (si aplica)
    - Maneja edge cases: entrada vacía, tipos incorrectos, valores límite
    - Incluye comentarios explicativos en las partes clave del código
    - Sin placeholders, sin TODOs, sin "..." — debe ejecutarse sin errores

    NORMAS DE EXPLICACIÓN — EXTENSAS Y DETALLADAS:
    - Explica como si el lector fuera un estudiante: con contexto, ejemplos prácticos y justificación de cada decisión técnica
    - Paso 1: Análisis del problema — describe un ejemplo concreto entrada→salida, analiza restricciones, identifica edge cases y explica por qué el enfoque elegido es el adecuado (mínimo 800 caracteres)
    - Paso 2: Implementación — desglosa el código paso a paso, explica cada estructura de datos y algoritmo por qué se eligió y cómo contribuye a la solución (mínimo 800 caracteres)
    - Paso 3: Optimización y variantes — analiza complejidad temporal/espacial en detalle, propone variantes del algoritmo, menciona aplicaciones en proyectos reales y alternativas más avanzadas (mínimo 700 caracteres)

    RESPONDE EXCLUSIVAMENTE UN JSON VÁLIDO (sin markdown, sin comentarios):
    {{
      "titulo": "Título del reto en español (max 100 chars)",
      "descripcion": "Explicación detallada del problema con contexto, ejemplo de entrada/salida y casos de uso real (mínimo 500 caracteres, máximo 1200)",
      "paso1": "Análisis exhaustivo: ejemplo concreto, desglose del problema, restricciones, edge cases (mínimo 800 caracteres, máximo 1800)",
      "paso2": "Implementación detallada en {lang}: algoritmo explicado paso a paso, por qué se elige cada estructura, cómo maneja edge cases (mínimo 800 caracteres, máximo 1800)",
      "paso3": "Optimizaciones, complejidad detallada, variantes del algoritmo y aplicaciones en el mundo real (mínimo 700 caracteres, máximo 1500)",
      "big_o_time": "Big-O temporal detallado (ej: O(n log n) por el ordenamiento, O(n) para la búsqueda)",
      "big_o_space": "Big-O espacial detallado (ej: O(n) por el almacenamiento del hash map)",
      "test_cases": "4-5 casos de prueba: entrada | salida_esperada (separados por ;)",
      "codigo": "Código completo, ejecutable, con imports, comentarios explicativos y ejemplo de uso al final",
      "dificultad": "Fácil | Intermedio | Difícil"
    }}
    """

    for modelo in modelos:
        logger.info(f"Intentando {titulo} con modelo: {modelo}")
        for intento in range(2):
            try:
                response = client.models.generate_content(model=modelo, contents=prompt)
                match = re.search(r'(\{.*\})', response.text.strip(), re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    if data.get('codigo') and len(data['codigo']) > 80:
                        return data
            except Exception as e:
                error_str = str(e).upper()
                if "API_KEY_INVALID" in error_str or ("INVALID_ARGUMENT" in error_str and "API KEY" in error_str):
                    logger.error(f"API KEY INVÁLIDA. Configura GEMINI_API_KEY correctamente.")
                    return None
                elif "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"Cuota excedida en {modelo}. Reintentando/Cambiando...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"Error en {modelo}: {e}")
                    break
    logger.error(f"Fallo total en IA para reto: {titulo}")

    try:
        sol_local = lookup(titulo, lang.lower())
        if sol_local:
            logger.info(f"Solución recuperada de la BD local para: {titulo}")
            return sol_local
    except Exception as e:
        logger.error(f"Error al consultar solutions_db: {e}")

    logger.warning(f"Generando solución genérica funcional para: {titulo}")
    return generate_generic(titulo, lang.lower())


async def generar_imagen_noticia(titulo_noticia: str, client, prompt_template: str = PROMPT_IMAGEN_TEMPLATE_RETO, fallback_url: str | None = None) -> str:
    modelos = CONFIG.get("IMAGE_MODELS", ["imagen-3.0-generate-002"])

    slug = slugify(titulo_noticia)[:40]
    filename = f"{slug}.png"
    images_folder = CONFIG.get("IMAGES_FOLDER", "../public/img/retos")
    images_prefix = CONFIG.get("IMAGES_PATH_PREFIX", "/img/retos")
    filepath = os.path.join(os.path.dirname(__file__), images_folder, filename) if not os.path.isabs(images_folder) else os.path.join(images_folder, filename)

    if os.path.exists(filepath):
        return f"{images_prefix}/{filename}"

    prompt_completo = prompt_template.format(titulo_post=titulo_noticia)

    for modelo in modelos:
        try:
            logger.info(f"Generando imagen con {modelo} para: '{titulo_noticia}'...")
            response = client.models.generate_images(model=modelo, prompt=prompt_completo, config=dict(number_of_images=1))
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.image_bytes)
            return f"{images_prefix}/{filename}"
        except Exception as e:
            logger.warning(f"Fallo imagen con {modelo}: {e}. Intentando siguiente...")

    return fallback_url or "/img/default.jpg"


async def traducir_titulos_ia(noticias: list, client) -> list:
    if not noticias: return noticias

    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])

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
            logger.info(f"Traduciendo {len(lineas)} títulos con {modelo}...")
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
                logger.warning(f"Cuota excedida en {modelo} (traducción). Probando siguiente...")
            elif "404" in error_str or "NOT_FOUND" in error_str:
                logger.warning(f"Modelo {modelo} no disponible (404) para traducción. Saltando...")
            else:
                logger.error(f"Error traducción batch ({modelo}): {e}")
            continue

    return noticias
