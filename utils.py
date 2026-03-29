import os
import json
import re
import asyncio
import requests
from datetime import datetime
from slugify import slugify
from google import genai
from constants_downloadfile import CONFIG, PROMPT_IMAGEN_TEMPLATE

def enviar_telegram(mensaje, parse_mode="Markdown"):
    """Envía notificación al Telegram del usuario."""
    token = CONFIG.get("BOT_TOKEN")
    chat_id = CONFIG.get("CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            res = requests.post(url, data={
                "chat_id": chat_id, 
                "text": mensaje, 
                "parse_mode": parse_mode
            }, timeout=10)
            return res.ok
        except Exception as e:
            print(f"⚠️ Error enviando Telegram: {e}")
    return False

async def obtener_solucion_ia(titulo, fuente, client, model="gemini-2.0-flash-lite", custom_prompt=None):
    """Obtiene solución técnica con esquema JSON estricto."""
    prompt = custom_prompt or f"""
    Resuelve el reto técnico: "{titulo}" de la fuente {fuente}.
    Explica en español pero mantén términos técnicos en inglés.
    
    RESPONDE EXCLUSIVAMENTE UN OBJETO JSON con este formato:
    {{
      "descripcion": "explicación breve",
      "paso1": "análisis del problema",
      "paso2": "lógica de programación",
      "paso3": "complejidad o Big O",
      "codigo": "código completo comentado",
      "lenguaje": "nombre del lenguaje",
      "dificultad": "Fácil, Intermedio o Difícil"
    }}
    """
    for intento in range(3):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            match = re.search(r'(\{.*\})', response.text.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            if "429" in str(e) or "QUOTA" in str(e).upper():
                await asyncio.sleep(45 * (intento + 1))
            else:
                print(f"⚠️ Error Gemini en '{titulo}': {e}")
                break
    return None

async def generar_imagen_noticia(titulo_noticia, client, prompt_template=PROMPT_IMAGEN_TEMPLATE, fallback_url=None):
    """Genera una imagen usando Gemini 3 con reintentos."""
    slug = slugify(titulo_noticia)[:40]
    filename = f"{slug}.png"
    
    images_folder = CONFIG.get("IMAGES_FOLDER", "images")
    images_prefix = CONFIG.get("IMAGES_PATH_PREFIX", "public/optimizado")
    filepath = os.path.join(images_folder, filename)

    if os.path.exists(filepath):
        return f"{images_prefix}/{filename}"

    max_intentos = 3
    prompt_completo = prompt_template.format(titulo_post=titulo_noticia)

    for intento in range(max_intentos):
        try:
            print(f"🎨 Generando imagen IA para: '{titulo_noticia}'...")
            response = client.models.generate_image(
                model="gemini-3-flash-image",
                prompt=prompt_completo
            )

            os.makedirs(images_folder, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.image_bytes)
                
            return f"{images_prefix}/{filename}"

        except Exception as e:
            if "429" in str(e) or "QUOTA" in str(e).upper():
                await asyncio.sleep(40 * (intento + 1))
            else:
                print(f"⚠️ Error imagen: {e}")
                break

    return fallback_url or "public/img/arquitectura_web.webp"
