import os
import json
import re
import asyncio
import requests
import logging
from datetime import datetime
from slugify import slugify
from google import genai
from constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE

logger = logging.getLogger("scraper")

async def obtener_solucion_ia(titulo, fuente, client, lang="Python"):
    """Obtiene solución técnica probando varios modelos si falla la cuota."""
    from constants_downloadfile import CONFIG
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])
    
    prompt = f"""
    Resuelve el reto técnico: "{titulo}" de la fuente {fuente}.
    Explica en español pero mantén términos técnicos en inglés.
    Usa el lenguaje de programación: {lang}
    
    RESPONDE EXCLUSIVAMENTE UN OBJETO JSON con este formato:
    {{
      "titulo": "Título del reto en español",
      "descripcion": "explicación clara del problema con ejemplo de entrada/salida",
      "paso1": "análisis detallado del problema y restricciones",
      "paso2": "explicación de la implementación en {lang}: algoritmo y estructuras usadas",
      "paso3": "complejidad temporal O(?) y espacial O(?), posibles optimizaciones",
      "codigo": "código completo y funcional en {lang} con comentarios y ejemplo de uso. Sin placeholders ni TODOs.",
      "dificultad": "Fácil, Intermedio o Difícil"
    }}
    """

    for modelo in modelos:
        logger.info(f"🧠 Intentando {titulo} con modelo: {modelo}")
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
                    logger.error(f"🔑 API KEY INVÁLIDA. Configura GEMINI_API_KEY correctamente.")
                    return None
                elif "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"⏳ Cuota excedida en {modelo}. Reintentando/Cambiando...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ Error en {modelo}: {e}")
                    break
    return None

async def obtener_recap_semanal_ia(noticias, client):
    """Genera el resumen semanal probando varios modelos."""
    from constants_downloadfile import CONFIG
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])
    
    texto_noticias = "\n".join([f"- {n['fuente']}: {n['titulo']}" for n in noticias[:15]])
    prompt = f"""
    Actúa como un Editor Senior de Tecnología. Analiza estos titulares y genera un RECAP SEMANAL.
    
    NOTICIAS:
    {texto_noticias}
    
    INSTRUCCIONES DE FORMATO (RESPONDE SOLO EN JSON):
    {{
      "introduccion": "Un párrafo analítico de 3 líneas sobre la tendencia de esta semana (úsalo para el Dashboard).",
      "noticias_destacadas": "Genera 3 secciones siguiendo este formato exacto: ### 1. [Título]\\n**El suceso:** [Explicación]\\n**Impacto:** [Por qué importa]\\n---",
      "repo": {{"nombre": "Repo", "url": "url", "desc": "desc"}},
      "tldr": "3 puntos clave breves",
      "tags": ["tag1", "tag2", "tag3"],
      "nota_personal": "Reflexión breve."
    }}
    """

    for modelo in modelos:
        logger.info(f"🗞️ Generando Recap con modelo: {modelo}")
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            raw_text = response.text if response.text else "{}"
            clean_json = re.sub(r'```json|```', '', raw_text).strip()
            return json.loads(clean_json)
        except Exception as e:
            error_str = str(e).upper()
            if "API_KEY_INVALID" in error_str or ("INVALID_ARGUMENT" in error_str and "API KEY" in error_str):
                logger.error(f"🔑 API KEY INVÁLIDA. Configura GEMINI_API_KEY correctamente.")
                return None
            elif "429" in error_str or "QUOTA" in error_str:
                logger.warning(f"⏳ Pasando al siguiente modelo por cuota en {modelo}...")
                continue
            logger.error(f"❌ Error Recap ({modelo}): {e}")
    return None

async def generar_imagen_noticia(titulo_noticia, client, prompt_template=PROMPT_IMAGEN_TEMPLATE, fallback_url=None):
    """Genera imagen con fallback de modelos."""
    from constants_downloadfile import CONFIG
    modelos = CONFIG.get("IMAGE_MODELS", ["gemini-3-flash-image"])
    
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
            response = client.models.generate_image(model=modelo, prompt=prompt_completo)
            os.makedirs(images_folder, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.image_bytes)
            return f"{images_prefix}/{filename}"
        except Exception as e:
            logger.warning(f"⚠️ Fallo imagen con {modelo}: {e}. Intentando siguiente...")
            
    return fallback_url or "public/img/arquitectura_web.webp"
