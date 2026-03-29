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

from constants_downloadfile import (
    CONFIG, 
    WEBS_RETOS, 
    RETO_MD_TEMPLATE, 
    PROMPT_IMAGEN_TEMPLATE_RETO
)
from utils import enviar_telegram, obtener_solucion_ia, generar_imagen_noticia

# ==========================================
# 1. FUNCIONES DE APOYO Y NOTIFICACIÓN
# ==========================================

# Eliminamos enviar_telegram local - ya está en utils.py

def clean_challenges(folder="./auto-challenges"):
    """Limpia archivos basura, incompletos o duplicados."""
    print(f"🧹 Iniciando limpieza en {folder}...")
    if not os.path.exists(folder): return
    
    archivos = [f for f in os.listdir(folder) if f.endswith(('.md', '.mdx'))]
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



# Eliminamos generar_imagen_noticia local - ya está en utils.py


# ==========================================
# 2. GENERACIÓN DE CONTENIDO (IA & IMAGEN)
# ==========================================

# Eliminamos obtener_solucion_ia local - ya está en utils.py

async def generar_retos_ia_puros(client, folder):
    """Genera 5 retos desde cero si no se encontró nada en la web."""
    print("🤖 No se encontraron retos nuevos. Activando generación creativa de IA...")
    lenguajes = ["Svelte", "Python (FastAPI/Django)", "Go", "C#", "Astro (JS/TS)"]
    retos_generados = []

    for lang in lenguajes:
        try:
            prompt_inventar = f"Inventa un título de reto técnico para el lenguaje {lang}. Solo el título."
            res_titulo = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt_inventar)
            titulo_inventado = res_titulo.text.strip()
            
            if await solve_and_save(titulo_inventado, "IA Creativa", client, folder):
                retos_generados.append(titulo_inventado)
                print(f"✅ Reto IA Generado ({lang}): {titulo_inventado}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ Error generando reto IA para {lang}: {e}")
            
    return retos_generados
    
async def solve_and_save(titulo, fuente, client, folder, difficulty_override=None):
    """Encapsula la lógica de resolver un reto y guardarlo."""
    print(f"🎯 Procesando: {titulo}")
    sol = await obtener_solucion_ia(titulo, fuente, client)
    
    if sol:
        titulo_es = sol.get('titulo', titulo)
        slug = f"reto-{slugify(titulo_es)[:40]}"
        path = os.path.join(folder, f"{slug}.mdx")
        
        img_url = await generar_imagen_noticia(titulo_es, client, prompt_template=PROMPT_IMAGEN_TEMPLATE_RETO)
        lang_tag = sol.get('lenguaje', 'python').lower()
        dificultad = difficulty_override or sol.get('dificultad', 'Intermedio')
        
        # Mapeo a la taxonomía específica del blog
        taxonomia = {
            "Fácil": "Iniciación", "Iniciación": "Iniciación", "Junior": "Iniciación",
            "Intermedio": "Intermedio", "Medio": "Intermedio", "Mid": "Intermedio",
            "Difícil": "Avanzado", "Avanzado": "Avanzado", "Senior": "Avanzado"
        }
        dificultad_blog = taxonomia.get(dificultad, "Intermedio")

        res = inspect.cleandoc(RETO_MD_TEMPLATE).format(
            titulo=titulo_es.replace('"', "'"),
            resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
            fecha_pub=datetime.now().strftime("%Y-%m-%d"),
            slug_name=slug,
            tags_seo=json.dumps([lang_tag, 'retos', dificultad_blog.lower()]),
            descripcion_ia=sol.get('descripcion', ''),
            ruta_imagen=img_url,
            dificultad=dificultad_blog,
            paso_1=sol.get('paso1', ''),
            paso_2=sol.get('paso2', ''),
            paso_3=sol.get('paso3', ''),
            lenguaje_lower=lang_tag,
            codigo_solucion=sol.get('codigo', '')
        )
        
        with open(path, "w", encoding="utf-8") as f: 
            f.write(res)
        return True
    return False

async def hunt(offline=False):
    """Cacería de retos en webs externas o generación estática."""
    folder = CONFIG.get("CHALLENGES_DIR", "../blog/src/content/auto-challenges")
    os.makedirs(folder, exist_ok=True)
    
    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key:
        print("⚠️ Sin API KEY. Entrando en modo Estático/Offline...")
        offline = True
        
    client = genai.Client(api_key=api_key) if not offline else None
    retos_nuevos = []

    if offline:
        print("💡 Generando retos desde el pool estático...")
        # Lógica para generar de una lista predefinida si no hay internet/API
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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
                if await solve_and_save(titulo_es, nombre, client, folder):
                    retos_nuevos.append(titulo_es)
                    await asyncio.sleep(5) 
        except Exception as e: 
            print(f"⚠️ Error {nombre}: {e}")

    if not retos_nuevos and client:
        retos_nuevos = await generar_retos_ia_puros(client, folder)

    if retos_nuevos:
        await enviar_telegram(f"🏹 *Cacería:* {len(retos_nuevos)} nuevos retos.")
    clean_challenges(folder)

if __name__ == "__main__":
    import sys
    is_offline = "--offline" in sys.argv
    asyncio.run(hunt(offline=is_offline))
