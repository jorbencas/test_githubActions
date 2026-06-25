import os
import json
import re
import asyncio
import logging
from slugify import slugify
from constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE
import solutions_db

logger = logging.getLogger("scraper")

async def obtener_solucion_ia(titulo: str, fuente: str, client, lang: str = "Python") -> dict | None:
    """Obtiene solución técnica probando varios modelos si falla la cuota."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.0-flash-lite"])
    
    prompt = f"""
    Resuelve el reto técnico: "{titulo}" de la fuente {fuente}.
    Explica en español pero mantén términos técnicos en inglés.
    Usa el lenguaje de programación: {lang}

    NORMAS DE CÓDIGO:
    - Código COMPLETO y funcional, con imports al inicio y bloque `if __name__ == "__main__"` (si aplica)
    - Maneja edge cases: entrada vacía, tipos incorrectos, valores límite
    - Comentarios breves solo en partes no obvias (no comentes cada línea)
    - Sin placeholders, sin TODOs, sin "..." — debe ejecutarse sin errores

    NORMAS DE EXPLICACIÓN:
    - Explica como si el lector supiera lo básico del lenguaje pero nunca hubiera visto este problema
    - Paso 1: empieza con un ejemplo concreto entrada→salida, luego analiza restricciones
    - Paso 2: explica el algoritmo y estructuras de datos usadas, por qué se eligieron
    - Paso 3: optimizaciones viables, variantes, y en qué casos reales se aplica

    RESPONDE EXCLUSIVAMENTE UN JSON VÁLIDO (sin markdown, sin comentarios):
    {{
      "titulo": "Título del reto en español (max 80 chars)",
      "descripcion": "Explicación clara: qué pide el problema + ejemplo entrada/salida (max 300 chars)",
      "paso1": "Análisis: ejemplo concreto, restricciones, casos límite (max 500 chars)",
      "paso2": "Implementación en {lang}: algoritmo, estructuras, por qué funcionan (max 500 chars)",
      "paso3": "Optimizaciones, variantes, aplicaciones reales (max 400 chars)",
      "big_o_time": "Big-O temporal (ej: O(n log n), O(n²))",
      "big_o_space": "Big-O espacial (ej: O(n), O(1))",
      "test_cases": "3 casos de prueba: entrada | salida_esperada (separados por ;)",
      "codigo": "Código completo, ejecutable, con imports y ejemplo de uso al final",
      "dificultad": "Fácil | Intermedio | Difícil"
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
    logger.error(f"❌ Fallo total en IA para reto: {titulo}")
    
    # 1. Intentamos buscar en nuestra base de datos local de soluciones hardcoded
    try:
        sol_local = solutions_db.lookup(titulo, lang.lower())
        if sol_local:
            logger.info(f"💾 Solución recuperada de la BD local para: {titulo}")
            return sol_local
    except Exception as e:
        logger.error(f"⚠️ Error al consultar solutions_db: {e}")

    # 2. Si no existe en BD, generamos una estructura funcional genérica (mejor que 'No disponible')
    logger.warning(f"⚠️ Generando solución genérica funcional para: {titulo}")
    return solutions_db.generate_generic(titulo, lang.lower())

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
            
            # Limpiar posibles backticks markdown y extraer JSON
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
