import os
import json
import re
import asyncio
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from google import genai
from slugify import slugify

from constants_downloadfile import (
    CONFIG, 
    WEBS_RETOS, 
    RETO_MD_TEMPLATE, 
    PROMPT_IMAGEN_TEMPLATE_RETO
)
from utils import obtener_solucion_ia, generar_imagen_noticia, traducir_titulos_ia
from solutions_db import lookup as db_lookup, generate_generic

logger = logging.getLogger("scraper")

# ==========================================
# 1. FUNCIONES DE APOYO Y NOTIFICACIÓN
# ==========================================

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
            # Corregido: Escape seguro de comillas en regex
            match = re.search(r'title:\s*["\'](.*?)["\']', content)
            if match:
                titulo = match.group(1).replace("RETO: ", "").lower().strip()
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

async def generar_retos_ia_puros(client, folder):
    """Genera retos desde cero si no se encontró nada en la web."""
    if not client:
        print("⚠️ Modo offline activo. No se pueden generar retos creativos con IA.")
        return []

    print("🤖 No se encontraron retos nuevos. Activando generación creativa de IA...")
    lenguajes = ["Svelte", "Python (FastAPI/Django)", "Go", "C#", "Astro (JS/TS)"]
    retos_generados = []

    for idx, lang in enumerate(lenguajes):
        try:
            prompt_inventar = f"Inventa un título de reto técnico para el lenguaje {lang}. Solo el título."
            # Ejecutamos la llamada síncrona del cliente genai en un hilo secundario
            res_titulo = await asyncio.to_thread(
                client.models.generate_content, 
                model="gemini-2.0-flash-lite", 
                contents=prompt_inventar
            )
            titulo_inventado = res_titulo.text.strip()
            
            if await solve_and_save(titulo_inventado, "IA Creativa", client, folder, index_hint=idx):
                retos_generados.append(titulo_inventado)
                print(f"✅ Reto IA Generado ({lang}): {titulo_inventado}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ Error generando reto IA para {lang}: {e}")
            
    return retos_generados
    

# Lenguajes del Codeember para rotación
CODEEMBER_LANGS = [
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("typescript", "TypeScript"),
    ("go", "Go"),
    ("rust", "Rust"),
    ("java", "Java"),
    ("csharp", "C#"),
    ("kotlin", "Kotlin"),
    ("swift", "Swift"),
    ("php", "PHP"),
    ("ruby", "Ruby"),
    ("dart", "Dart"),
]

async def solve_and_save(titulo, fuente, client, folder, difficulty_override=None, index_hint=0):
    """Encapsula la lógica de resolver un reto y guardarlo."""
    print(f"🎯 Procesando: {titulo}")
    
    # Corregido: Eliminada la variable global para evitar race conditions. 
    # Ahora usamos un index_hint pasado por parámetro.
    lang_id, lang_display = CODEEMBER_LANGS[index_hint % len(CODEEMBER_LANGS)]
    
    # 1️⃣ Consultar BD local (gratis, sin IA)
    sol = db_lookup(titulo, lang_id)
    if sol:
        print(f"   📦 Solución local encontrada ({lang_display}), sin llamada a IA")
    else:
        # 2️⃣ Pedir a Gemini solo si no está en la BD y tenemos cliente válido (Online)
        if client:
            sol = await obtener_solucion_ia(titulo, fuente, client, lang=lang_display)
        
        if not sol:
            # 3️⃣ Fallback: código genérico estructurado (offline o fallo de IA)
            print(f"   ⚠️ IA falló o modo offline. Usando código genérico ({lang_display})")
            sol = generate_generic(titulo, lang_id)
    
    if sol:
        titulo_es = sol.get('titulo', titulo)
        slug = f"reto-{slugify(titulo_es)[:40]}"
        path = os.path.join(folder, f"{slug}.mdx")
        
        # Generar imagen (solo si hay cliente online)
        img_url = ""
        if client:
            img_url = await generar_imagen_noticia(titulo_es, client, prompt_template=PROMPT_IMAGEN_TEMPLATE_RETO)
        
        dificultad = difficulty_override or sol.get('dificultad', 'Intermedio')
        
        # Mapeo a la taxonomía específica del blog
        taxonomia = {
            "Fácil": "Iniciación", "Iniciación": "Iniciación", "Junior": "Iniciación",
            "Intermedio": "Intermedio", "Medio": "Intermedio", "Mid": "Intermedio",
            "Difícil": "Avanzado", "Avanzado": "Avanzado", "Senior": "Avanzado"
        }
        dificultad_blog = taxonomia.get(dificultad, "Intermedio")
        tags_seo = json.dumps([lang_id, 'retos', dificultad_blog.lower()])

        # Corregido: Se quitó inspect.cleandoc para evitar deformaciones en la indentación del Markdown
        # Nota: Asegúrate de que las llaves que uses en tu RETO_MD_TEMPLATE (que no correspondan a estas variables) estén duplicadas {{ }}
        try:
            res = RETO_MD_TEMPLATE.format(
                titulo=titulo_es.replace('"', "'"),
                resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
                fecha_pub=datetime.now().strftime("%Y-%m-%d"),
                slug_name=slug,
                tags_seo=tags_seo,
                descripcion_ia=sol.get('descripcion', ''),
                ruta_imagen=img_url,
                dificultad=dificultad_blog,
                paso_1=sol.get('paso1', ''),
                paso_2=sol.get('paso2', ''),
                paso_3=sol.get('paso3', ''),
                lenguaje_lower=lang_id,
                lenguaje_display=lang_display,
                codigo_solucion=sol.get('codigo', '')
            )
            
            # Escritura de archivos delegada a un hilo para no bloquear el loop de asyncio
            await asyncio.to_thread(lambda: open(path, "w", encoding="utf-8").write(res))
            return True
        except KeyError as e:
            print(f"❌ Error de formato en el Template: Olvidaste escapar una llave en tu constante: {e}")
            return False
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
        print("💡 Modo Offline: El script solo buscará soluciones en la base de datos local (solutions_db.py).")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Contador local para asignar índices únicos a cada reto procesado secuencialmente
    reto_idx = 0

    for nombre, config in WEBS_RETOS.items():
        try:
            print(f"🔍 Buscando en: {nombre}...")
            
            # Corregido: Ejecutamos el requests.get síncrono en un hilo secundario asíncrono
            r = await asyncio.to_thread(
                lambda: requests.get(config["url"], timeout=15, headers=headers)
            )
            
            if r.status_code != 200: continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(config["selector"])[:5]
            
            # Recolectamos títulos para traducir en lote
            items_validos = []
            for i in items:
                t_raw = i.get_text(strip=True)
                if len(t_raw) >= 5:
                    items_validos.append({"obj": i, "titulo": t_raw})
            
            if items_validos and not offline and client:
                logger.info(f"🌐 Traduciendo {len(items_validos)} títulos de {nombre}...")
                items_validos = await traducir_titulos_ia(items_validos, client)

            for item_data in items_validos:
                titulo_es = item_data["titulo"]
                if await solve_and_save(titulo_es, nombre, client, folder, index_hint=reto_idx):
                    retos_nuevos.append(titulo_es)
                    reto_idx += 1
                    await asyncio.sleep(5) 
        except Exception as e: 
            print(f"⚠️ Error en {nombre}: {e}")

    # Si no se encontraron retos en la web y estamos online, la IA genera creativos
    if not retos_nuevos and not offline and client:
        retos_nuevos = await generar_retos_ia_puros(client, folder)

    if retos_nuevos:
        print(f"🏹 *Cacería:* {len(retos_nuevos)} nuevos retos.")
        
    # Limpieza final de archivos basura
    clean_challenges(folder)

if __name__ == "__main__":
    import sys
    is_offline = "--offline" in sys.argv
    asyncio.run(hunt(offline=is_offline))
