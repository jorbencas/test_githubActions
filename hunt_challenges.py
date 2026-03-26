import os
import json
import re
import asyncio
import requests
import inspect  # Necesario para limpiar el template
from bs4 import BeautifulSoup
from mtranslate import translate
from datetime import datetime
from google import genai
from slugify import slugify

# Importamos tus constantes personalizadas
from constants_downloadfile import (
    CONFIG, 
    WEBS_RETOS, 
    RETO_MD_TEMPLATE, 
    PROMPT_IMAGEN_TEMPLATE_RETO
)

# ==========================================
# 1. FUNCIONES DE APOYO Y NOTIFICACIÓN
# ==========================================

async def enviar_telegram(mensaje):
    """Envía notificación al Telegram del usuario."""
    token = CONFIG.get("BOT_TOKEN")
    chat_id = CONFIG.get("CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
        except Exception as e:
            print(f"⚠️ Error enviando Telegram: {e}")

def clean_challenges(folder="./auto-challenges"):
    """Limpia archivos basura, incompletos o duplicados."""
    print(f"🧹 Iniciando limpieza en {folder}...")
    if not os.path.exists(folder): return
    
    archivos = [f for f in os.listdir(folder) if f.endswith('.md')]
    borrados = 0
    titulos_vistos = set()

    for archivo in archivos:
        path = os.path.join(folder, archivo)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Borrar si el contenido falló o está incompleto
            if len(content) < 300 or "{codigo_solucion}" in content or "{lenguaje_lower}" in content:
                os.remove(path)
                borrados += 1
                continue

            # Detectar duplicados por título en el frontmatter
            match = re.search(r'title: ".*?RETO: (.*?)"', content)
            if match:
                titulo = match.group(1).lower().strip()
                if titulo in titulos_vistos:
                    os.remove(path)
                    borrados += 1
                    continue
                titulos_vistos.add(titulo)

            # Borrar si no tiene bloques de código
            if "```" not in content:
                os.remove(path)
                borrados += 1
        except Exception as e:
            print(f"⚠️ Error limpiando {archivo}: {e}")

    print(f"✨ Limpieza terminada. Se eliminaron {borrados} archivos.")



async def generar_imagen_noticia(titulo_noticia, client):
    """Genera imagen rápida con Gemini 3 Flash Image."""
    slug = slugify(titulo_noticia)[:40]
    filename = f"{slug}.png"
    filepath = os.path.join(CONFIG["IMAGES_FOLDER"], filename)

    if os.path.exists(filepath):
        return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"

    try:
        print(f"🎨 Generando imagen para: '{titulo_noticia}'...")
        prompt_completo = PROMPT_IMAGEN_TEMPLATE_RETO.format(titulo_post=titulo_noticia)
        
        response = client.models.generate_image(
            model="gemini-3-flash-image",
            prompt=prompt_completo
        )

        os.makedirs(CONFIG["IMAGES_FOLDER"], exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.image_bytes)
            
        return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"
    except Exception as e:
        print(f"❌ Error Imagen: {e}")
        return "public/img/arquitectura_web.webp"


# ==========================================
# 2. GENERACIÓN DE CONTENIDO (IA & IMAGEN)
# ==========================================

async def obtener_solucion_ia(titulo, fuente, client):
    """Obtiene solución técnica con esquema JSON estricto y extracción robusta."""
    prompt = f"""
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
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            # Extracción robusta del JSON entre llaves
            match = re.search(r'(\{.*\})', response.text.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            if "429" in str(e):
                await asyncio.sleep(45 * (intento + 1))
            else:
                print(f"⚠️ Error Gemini en '{titulo}': {e}")
                break
    return None

async def generar_retos_ia_puros(client, folder):
    """Genera 5 retos desde cero si no se encontró nada en la web."""
    print("🤖 No se encontraron retos nuevos. Activando generación creativa de IA...")
    lenguajes = ["Svelte", "Python (FastAPI/Django)", "Go", "C#", "Astro (JS/TS)"]
    retos_generados = []

    for lang in lenguajes:
        # Prompt para inventar un reto temático
        prompt_inventar = f"Inventa un título de reto técnico avanzado para el lenguaje {lang}. Solo el título, corto y profesional."
        try:
            res_titulo = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt_inventar)
            titulo_inventado = res_titulo.text.strip()
            
            sol = await obtener_solucion_ia(titulo_inventado, "IA Creativa", client, lenguaje_fijo=lang)
            
            if sol:
                titulo_final = sol.get('titulo_final', titulo_inventado)
                slug = f"reto-ia-{slugify(titulo_final)[:40]}"
                path = f"{folder}/{slug}.md"
                
                img_url = await generar_imagen_noticia(titulo_final, client)
                lang_tag = sol.get('lenguaje', lang).lower()
                
                res = inspect.cleandoc(RETO_MD_TEMPLATE).format(
                    titulo=titulo_final.replace('"', "'"),
                    resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
                    fecha_pub=datetime.now().strftime("%Y-%m-%d"),
                    slug_name=slug,
                    tags_seo=json.dumps([lang_tag, 'retos-ia', 'master-dev']),
                    descripcion_ia=sol.get('descripcion', ''),
                    ruta_imagen=img_url,
                    dificultad=sol.get('dificultad', 'Avanzado'),
                    paso_1=sol.get('paso1', ''),
                    paso_2=sol.get('paso2', ''),
                    paso_3=sol.get('paso3', ''),
                    lenguaje_lower=lang_tag,
                    codigo_solucion=sol.get('codigo', '')
                )
                
                with open(path, "w", encoding="utf-8") as f:
                    f.write(res)
                retos_generados.append(titulo_final)
                print(f"✅ Reto IA Generado ({lang}): {titulo_final}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ Error generando reto IA para {lang}: {e}")
            
    return retos_generados
    
async def hunt():
    """Cacería de retos en webs externas."""
    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key: return print("❌ Sin API KEY.")
        
    client = genai.Client(api_key=api_key)
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    retos_nuevos = []
    
    for nombre, config in WEBS_RETOS.items():
        try:
            print(f"🔍 Buscando en: {nombre}...")
            r = requests.get(config["url"], timeout=15, headers=headers)
            if r.status_code != 200: continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(config["selector"])[:5]
            
            for i in items:
                titulo_raw = i.get_text(strip=True)
                if len(titulo_raw) < 5: continue
                
                titulo_es = translate(titulo_raw, 'es')
                slug = f"reto-{slugify(titulo_es)[:40]}"
                path = f"{folder}/{slug}.md"
                
                if not os.path.exists(path):
                    print(f"🎯 Cazado: {titulo_es}")
                    sol = await obtener_solucion_ia(titulo_es, nombre, client)
                    
                    if sol:
                        img_url = await generar_imagen_noticia(titulo_es, client)
                        lang = sol.get('lenguaje', 'python').lower()
                        
                        # Inyección limpia en el Template
                        res = inspect.cleandoc(RETO_MD_TEMPLATE).format(
                            titulo=titulo_es.replace('"', "'"),
                            resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
                            fecha_pub=datetime.now().strftime("%Y-%m-%d"),
                            slug_name=slug,
                            tags_seo=json.dumps([lang, 'retos', 'ia']),
                            descripcion_ia=sol.get('descripcion', ''),
                            ruta_imagen=img_url,
                            dificultad=sol.get('dificultad', 'Intermedio'),
                            paso_1=sol.get('paso1', ''),
                            paso_2=sol.get('paso2', ''),
                            paso_3=sol.get('paso3', ''),
                            lenguaje_lower=lang,
                            codigo_solucion=sol.get('codigo', '')
                        )
                        
                        with open(path, "w", encoding="utf-8") as f: 
                            f.write(res)
                        retos_nuevos.append(titulo_es)
                        await asyncio.sleep(5) 
                else:
                    print(f"⏭️ Existe: {slug}")
        except Exception as e: 
            print(f"⚠️ Error {nombre}: {e}")

    if not retos_nuevos:
        retos_nuevos = await generar_retos_ia_puros(client, folder)

    if retos_nuevos:
        await enviar_telegram(f"🏹 *Cacería:* {len(retos_nuevos)} nuevos retos.")
    clean_challenges(folder)

if __name__ == "__main__":
    asyncio.run(hunt())
