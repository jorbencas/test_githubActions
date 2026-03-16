import os, json, re, asyncio, requests
from bs4 import BeautifulSoup
from mtranslate import translate
from datetime import datetime
from google import genai
# Importamos CONFIG para las claves y la nueva WEBS_RETOS específica para este script
from constants_downloadfile import CONFIG, WEBS_RETOS, RETO_MD_TEMPLATE, PROMPT_IMAGEN_TEMPLATE 
from slugify import slugify # Instalar: pip install python-slugify

async def enviar_telegram(mensaje):
    """Envía notificación al Telegram del usuario."""
    token = CONFIG.get("BOT_TOKEN")
    chat_id = CONFIG.get("CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Escapamos caracteres que rompen el Markdown simple si fuera necesario
        try:
            requests.post(url, data={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
        except Exception as e:
            print(f"⚠️ Error enviando Telegram: {e}")

async def obtener_solucion_ia(titulo, nombre, client):
    """Obtiene la solución de Gemini con sistema de reintentos para evitar errores de cuota (429)."""
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            prompt = f"Resuelve el reto técnico: {titulo} de {nombre}. Explica en español pero mantén términos técnicos en inglés (array, push, async, etc). JSON requerido: descripcion, paso1, paso2, paso3, codigo, lenguaje."
            
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            
            # Limpieza profunda del JSON
            texto_limpio = response.text.strip()
            if "```json" in texto_limpio:
                coincidencia = re.search(r'```json\s*(.*?)\s*```', texto_limpio, re.DOTALL)
                if coincidencia:
                    texto_limpio = coincidencia.group(1)
            elif "```" in texto_limpio:
                coincidencia = re.search(r'```\s*(.*?)\s*```', texto_limpio, re.DOTALL)
                if coincidencia:
                    texto_limpio = coincidencia.group(1)
            
            return json.loads(texto_limpio)

        except Exception as e:
            # Si el error contiene "429", es un error de cuota (RESOURCE_EXHAUSTED)
            if "429" in str(e):
                espera = 35 * (intento + 1)
                print(f"⏳ Cuota excedida para '{titulo}'. Reintentando en {espera}s...")
                await asyncio.sleep(espera)
            else:
                print(f"⚠️ Error en Gemini para '{titulo}': {e}")
                break
    return None


async def generar_imagen_noticia(titulo_noticia):
    """
    Genera una imagen usando Gemini 3 Flash Image (Nano Banana 2).
    Mantiene la misma lógica de guardado y caché.
    """
    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key:
        print("⚠️ No GEMINI_KEY found. Skipping image generation.")
        return None

    slug = slugify(titulo_noticia)
    filename = f"{slug}.png"
    filepath = os.path.join(CONFIG["IMAGES_FOLDER"], filename)

    # 1. Caché: Si ya existe, no gastamos créditos
    if os.path.exists(filepath):
        return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"

    try:
        print(f"🎨 Generando imagen con Gemini para: '{titulo_noticia}'...")
        
        # 2. Preparamos el cliente (puedes usar el que ya tienes global)
        client = genai.Client(api_key=api_key)
        
        # 3. Prompt optimizado para Gemini
        prompt_completo = PROMPT_IMAGEN_TEMPLATE.format(titulo_post=titulo_noticia)

        # 4. Generación de imagen
        # Usamos el modelo de imagen de Gemini (Nano Banana 2)
        response = client.models.generate_image(
            model="gemini-3-flash-image", # O el nombre del modelo de imagen activo en tu tier
            prompt=prompt_completo
        )

        # 5. Guardar el objeto binario directamente
        os.makedirs(CONFIG["IMAGES_FOLDER"], exist_ok=True)
        
        # Gemini suele devolver la imagen en bytes directamente en la respuesta
        with open(filepath, 'wb') as f:
            f.write(response.image_bytes)
            
        print(f"✅ Imagen de Gemini guardada en: {filepath}")
        return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"

    except Exception as e:
        print(f"❌ Error en Gemini Image: {e}")
        return None



async def hunt():
    # Inicializamos el cliente de Gemini usando la clave centralizada
    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key:
        print("❌ Error: No se ha encontrado la clave GEMINI_KEY en CONFIG.")
        return
        
    client = genai.Client(api_key=api_key)
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)
    
    # Headers para simular un navegador y evitar bloqueos
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9'
    }
    
    retos_nuevos = []
    
    # Iteramos sobre la configuración específica de retos
    for nombre, config in WEBS_RETOS.items():
        try:
            print(f"🔍 Buscando retos en: {nombre}...")
            r = requests.get(config["url"], timeout=15, headers=headers)
            if r.status_code != 200:
                print(f"❌ Error {r.status_code} al acceder a {nombre}")
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(config["selector"])[:5] # Tomamos los 5 más recientes
            
            for i in items:
                titulo_raw = i.get_text(strip=True)
                if not titulo_raw: continue
                
                # Traducimos el título al español
                try:
                    titulo_es = translate(titulo_raw, 'es')
                except Exception as e:
                    print(f"⚠️ Error traduciendo título '{titulo_raw}': {e}")
                    titulo_es = titulo_raw # Fallback al título original
                    
                # Creamos un slug limpio y único para el archivo
                slug = f"reto-{re.sub(r'[^a-z0-9]', '-', titulo_es.lower())[:40]}".strip("-")
                path = f"{folder}/{slug}.md"
                
                # Solo procesamos si el reto no existe localmente
                if not os.path.exists(path):
                    print(f"🤖 Procesando nuevo reto: {titulo_es}")
                    # Llamamos a Gemini con el sistema de reintentos integrado
                    sol = await obtener_solucion_ia(titulo_es, nombre, client)
                    
                    if sol and isinstance(sol, dict):
                        # Reemplazamos los placeholders en la plantilla
                        res = RETO_MD_TEMPLATE.replace("{titulo}", titulo_es)\
                            .replace("{resumen_corto}", sol.get('descripcion','')[:150].replace('"', "'") + "...")\
                            .replace("{fecha_pub}", datetime.now().strftime("%Y-%m-%d"))\
                            .replace("{slug_name}", slug)\
                            .replace("{tags_seo}", str([sol.get('lenguaje','ia').lower(), 'retos']))\
                            .replace("{descripcion_ia}", sol.get('descripcion',''))\
                            .replace("{ruta_imagen}", generar_imagen_noticia(titulo_es))\
                            .replace("{paso_1}", sol.get('paso1',''))\
                            .replace("{paso_2}", sol.get('paso2',''))\
                            .replace("{paso_3}", sol.get('paso3',''))\
                            .replace("{codigo_solucion}", sol.get('codigo',''))
                        
                        # Guardamos el archivo markdown
                        with open(path, "w", encoding="utf-8") as f: 
                            f.write(res)
                            
                        retos_nuevos.append(titulo_es)
                        print(f"✅ Guardado: {slug}")
                        # Pequeño respiro entre retos para no saturar mtranslate ni Gemini
                        await asyncio.sleep(5) 
                else:
                    print(f"⏭️ El reto ya existe: {slug}")

        except Exception as e: 
            print(f"⚠️ Error general en fuente {nombre}: {e}")

    # Notificar por Telegram si se cazaron nuevos retos
    if retos_nuevos:
        lista_retos = "\n".join([f"- {n}" for n in retos_nuevos])
        await enviar_telegram(f"🏹 *¡Cacería exitosa!*\nHe encontrado {len(retos_nuevos)} nuevos retos:\n{lista_retos}")
    else:
        print("📭 No se han encontrado retos nuevos hoy.")

if __name__ == "__main__":
    # Ejecutamos la función asíncrona principal
    asyncio.run(hunt())