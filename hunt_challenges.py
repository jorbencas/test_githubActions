import os
import json
import re
import asyncio
import requests
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

# ==========================================
# 2. GENERACIÓN DE CONTENIDO (IA & IMAGEN)
# ==========================================

async def obtener_solucion_ia(titulo, nombre, client):
    """Obtiene la solución de Gemini con sistema de reintentos."""
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            prompt = f"Resuelve el reto técnico: {titulo} de {nombre}. Explica en español pero mantén términos técnicos en inglés. JSON requerido: descripcion, paso1, paso2, paso3, codigo, lenguaje."
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            
            texto_limpio = response.text.strip()
            # Extraer JSON de bloques de código si existen
            if "```json" in texto_limpio:
                texto_limpio = re.search(r'```json\s*(.*?)\s*```', texto_limpio, re.DOTALL).group(1)
            elif "```" in texto_limpio:
                texto_limpio = re.search(r'```\s*(.*?)\s*```', texto_limpio, re.DOTALL).group(1)
            
            return json.loads(texto_limpio)
        except Exception as e:
            if "429" in str(e):
                espera = 35 * (intento + 1)
                print(f"⏳ Cuota excedida. Reintentando en {espera}s...")
                await asyncio.sleep(espera)
            else:
                print(f"⚠️ Error Gemini para '{titulo}': {e}")
                break
    return None

async def generar_imagen_noticia(titulo_noticia, client):
    """Genera imagen rápida con Gemini 3 Flash Image."""
    slug = slugify(titulo_noticia)
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
        return "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true"

# ==========================================
# 3. CORE: PROCESO DE "HUNT" (CACERÍA)
# ==========================================

async def hunt():
    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key: return print("❌ No GEMINI_KEY.")
        
    client = genai.Client(api_key=api_key)
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0...'}
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
                if not titulo_raw: continue
                
                titulo_es = translate(titulo_raw, 'es')
                slug = f"reto-{slugify(titulo_es)[:40]}"
                path = f"{folder}/{slug}.md"
                
                if not os.path.exists(path):
                    print(f"🤖 Nuevo reto: {titulo_es}")
                    sol = await obtener_solucion_ia(titulo_es, nombre, client)
                    
                    if sol and isinstance(sol, dict):
                        lang = sol.get('lenguaje', 'python').lower()
                        img_url = await generar_imagen_noticia(titulo_es, client)
                        
                        # Inyección en el template
                        res = RETO_MD_TEMPLATE.replace("{titulo}", titulo_es)\
                            .replace("{resumen_corto}", sol.get('descripcion','')[:150].replace('"', "'") + "...")\
                            .replace("{fecha_pub}", datetime.now().strftime("%Y-%m-%d"))\
                            .replace("{slug_name}", slug)\
                            .replace("{tags_seo}", json.dumps([lang, 'retos']))\
                            .replace("{descripcion_ia}", sol.get('descripcion',''))\
                            .replace("{ruta_imagen}", img_url)\
                            .replace("{paso_1}", sol.get('paso1',''))\
                            .replace("{paso_2}", sol.get('paso2',''))\
                            .replace("{paso_3}", sol.get('paso3',''))\
                            .replace("{lenguaje_lower}", lang)\
                            .replace("{codigo_solucion}", sol.get('codigo',''))
                        
                        with open(path, "w", encoding="utf-8") as f: 
                            f.write(res)
                            
                        retos_nuevos.append(titulo_es)
                        await asyncio.sleep(5) 
                else:
                    print(f"⏭️ Existe: {slug}")

        except Exception as e: 
            print(f"⚠️ Error fuente {nombre}: {e}")

    # Notificaciones y limpieza final
    if retos_nuevos:
        await enviar_telegram(f"🏹 *¡Cacería exitosa!*\n{len(retos_nuevos)} nuevos retos.")
    
    clean_challenges(folder)

if __name__ == "__main__":
    asyncio.run(hunt())