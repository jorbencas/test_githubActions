import locale
import inspect
import os, json, re, requests, asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
from mtranslate import translate
from google import genai
import edge_tts
from constants_downloadfile import FUENTES, CONFIG, HTML_TEMPLATE, EMAIL_TEMPLATE, ALL_KEYWORDS, BECAS_KEYWORDS, MD_TEMPLATE, RETO_MD_TEMPLATE, PROMPT_IMAGEN_TEMPLATE
from slugify import slugify # Instalar: pip install python-slugify

# Auto-añadir secciones de Shorts
for nombre in list(FUENTES): # Usamos list() para poder modificar el dict mientras iteramos
    if "yt" in FUENTES[nombre]:
        url_s = FUENTES[nombre]["yt"].replace("/videos", "/shorts")
        FUENTES[f"{nombre} Shorts"] = {"yt": url_s}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)
os.makedirs("./auto-news", exist_ok=True)

# --- 3. FUNCIONES ---
class ScraperPro:
    def __init__(self):
        self.cache_file = os.path.join(CONFIG["FOLDER"], "avatars_cache.json")
        self.avatars = self.cargar_avatars()
        self.cambios_en_cache = False

    def cargar_avatars(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def guardar_avatars(self):
        if self.cambios_en_cache:
            with open(self.cache_file, 'w') as f: 
                json.dump(self.avatars, f, indent=4, ensure_ascii=False)
            print("💾 Caché de avatares actualizada.")

    def obtener_avatar_canal(self, nombre, url_canal):
        # Si ya lo tenemos en caché, no entramos a YouTube
        if nombre in self.avatars: return self.avatars[nombre]
        
        try:
            print(f"🔍 Buscando avatar real para: {nombre}...")
            # Limpiamos la URL para ir al home del canal
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                url_avatar = meta_img['content']
                self.avatars[nombre] = url_avatar
                self.cambios_en_cache = True 
                return url_avatar
        except: pass
        
        # Si falla, usamos avatar por defecto y no guardamos en caché para reintentar luego
        return f"https://ui-avatars.com/api/?name={nombre}&background=random"

    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'es-ES,es;q=0.9'
            }
            r = requests.get(target, timeout=15, headers=headers)
            if r.status_code != 200: return []
            if "yt" in info:
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                clean_ids = list(dict.fromkeys(ids))
                # 2. Extraer Títulos (Diferentes patrones según si es /videos o /shorts)
                # Patrón para videos normales
                titles_video = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                # Patrón específico para Shorts (overlayMetadata)
                titles_shorts = re.findall(r'"overlayMetadata":\{"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                
                # Combinamos o elegimos según el tipo
                titles = titles_shorts if "shorts" in target.lower() else titles_video
                
                # Si fallan ambos, intentamos un patrón genérico de accesibilidad
                if not titles:
                    titles = re.findall(r'title="([^"]*)"[^>]*aria-describedby', r.text)

                for t, i in zip(titles[:5], clean_ids[:5]):
                    es_short = "shorts" in target or "Shorts" in nombre
                    t_clean = t.encode().decode('unicode-escape').replace('"', '')
                    results.append({
                        "titulo": translate(t_clean, 'es'),
                        "enlace": f"https://youtube.com/shorts/{i}" if es_short else f"https://youtube.com/watch?v={i}",
                        "id_video": i, "fuente": nombre.replace(" Shorts", ""), 
                        "tipo": "shorts" if es_short else "video",
                        "ultima_verificacion": datetime.now().isoformat(),
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                selector_custom = info.get("selector", 'article h2 a, .post-title a, h3 a, .title a, h2 a')
                items = soup.select(selector_custom)[:10] # Pillamos 10 para filtrar luego

                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '')
                    t_low = t_raw.lower()
                        
                    # DETERMINAR IDIOMA: Si la URL contiene términos comunes de webs inglesas
                    is_english = any(x in target for x in ["wired", "verge", "techcrunch", "slashdot", "github", "openai", "hacker-news"])

                    # FILTRO INTELIGENTE:
                    # Si es inglés, permitimos pasar si tiene keywords universales (AI, GPT, Python, NVIDIA...)
                    # o si Gemini se encargará de filtrarlo luego.
                    match_keyword = any(key.lower() in t_low for key in ALL_KEYWORDS)
                    # Si es una web inglesa de confianza, bajamos la guardia del filtro 
                    # porque palabras como "AI" o "Cloud" coinciden, pero "Beca" no.
                    if match_keyword or is_english:
                        raw_content = t_low
                        # Clasificamos: Si tiene algo de becas, es "Beca", si no "Tech"
                        categoria = "Beca" if any(k in t_low for k in BECAS_KEYWORDS) else "Tech"
                        # BUSCAR LA IMAGEN (IMG TAG)
                        img_tag = i.select_one('img')
                        img_url = ""
                        if img_tag:
                            # Probamos src o data-src (muchas webs usan lazy loading)
                            img_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset')

                        results.append({
                            "titulo": translate(t_raw, 'es') if is_english else t_raw,                            
                            "enlace": urljoin(target, i.get('href')),
                            "fuente": nombre, "tipo": "noticia",
                            "ultima_verificacion": datetime.now().isoformat(),
                            "badge": categoria, # Nueva propiedad
                            "raw": raw_content, # <--- NUEVO: Para que Gemini analice el reto
                            "imagen_url_original": urljoin(target, img_url) if img_url else "",
                            "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                        })
        except: pass
        return results

# async def obtener_resumen_ia(noticias):
#     if not CONFIG["GEMINI_KEY"] or not noticias: return "Sin novedades para resumir hoy."
#     try:
#         client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
#         texto = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
#         prompt = (
#             "Actúa como un editor de noticias tecnológicas. "
#             "Resume los siguientes titulares en 3 párrafos claros y concisos en español. "
#             f"Aquí tienes las noticias:\n{texto}"
#         )

#         # 4. Llamada al modelo 'flash-lite' (El mejor para el Tier Gratuito)
#         response = client.models.generate_content(
#             model="gemini-2.5-flash-lite",
#             contents=prompt
#         )
#         await asyncio.sleep(2)
#         raw_text = response.text if response.text else "Resumen no disponible."
#         # --- FORMATEO PARA WEB ---
#         # Convertimos Markdown de la IA (**texto**) a HTML (<b>texto</b>)
#         html_text = raw_text.replace("**", "<b>").replace("**", "</b>")
#         # Convertimos saltos de línea dobles en párrafos HTML
#         parrafos = html_text.split("\n\n")
#         resumen_formateado = "".join([f"<p style='margin-bottom:15px; line-height:1.6;'>{p}</p>" for p in parrafos if p.strip()])
#         return resumen_formateado
#     except Exception as e:
#         # Imprime el error real en tu terminal para saber qué pasa exactamente
#         print(f"❌ Error en obtener_resumen_ia: {e}")
        
#         # Mensajes amigables según el tipo de error
#         if "429" in str(e):
#             return "Límite de cuota alcanzado. Inténtalo en unos minutos."
#         return "Resumen no disponible en este momento. Revisa los enlaces directos."

async def obtener_solucion_ia(titulo, fuente, client):
    prompt = f"""
    Resuelve el reto técnico: "{titulo}" de la fuente {fuente}.
    Explica en español pero mantén términos técnicos en inglés.
    
    RESPONDE EXCLUSIVAMENTE UN OBJETO JSON con este formato:
    {{
      "descripcion": "explicación",
      "paso1": "análisis",
      "paso2": "lógica",
      "paso3": "complejidad",
      "codigo": "código completo",
      "lenguaje": "nombre del lenguaje",
      "dificultad": "Fácil, Intermedio o Difícil"
    }}
    """
    for intento in range(3):
        try:
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            match = re.search(r'(\{.*\})', response.text.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            if "429" in str(e): await asyncio.sleep(40 * (intento + 1))
            else: break
    return None


async def generar_retos_individuales(noticias_web, fecha_iso, client):
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)

    for n in noticias_web:
        titulo_low = n['titulo'].lower()
        if any(k in titulo_low for k in ["reto", "challenge", "desafío"]):
            slug_reto = f"reto-{slugify(n['titulo'])[:40]}"
            path = f"{folder}/{slug_reto}.md"
            
            if os.path.exists(path): continue

            print(f"🎯 Procesando reto: {n['titulo']}")
            sol = await obtener_solucion_ia(n['titulo'], n.get('fuente', 'Web'), client)
            
            if sol:
                img_reto = await generar_imagen_noticia(n['titulo'], "", client)
                lang = sol.get('lenguaje', 'python').lower()

                try:
                    # Usamos inspect.cleandoc para que el Frontmatter (---) empiece en la columna 0
                    reto_md = inspect.cleandoc(RETO_MD_TEMPLATE).format(
                        titulo=n['titulo'].replace('"', "'"),
                        resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
                        fecha_pub=fecha_iso,
                        slug_name=slug_reto,
                        tags_seo=json.dumps([lang, 'retos', 'ia']),
                        ruta_imagen=img_reto,
                        descripcion_ia=sol.get('descripcion', ''),
                        dificultad=sol.get('dificultad', 'Intermedio'), # <--- Campo clave para tu componente Astro
                        paso_1=sol.get('paso1', 'Analizando...'),
                        paso_2=sol.get('paso2', 'Ejecutando...'),
                        paso_3=sol.get('paso3', 'Optimizando...'),
                        lenguaje_lower=lang,
                        codigo_solucion=sol.get('codigo', '')
                    )

                    with open(path, "w", encoding="utf-8") as f:
                        f.write(reto_md)
                    print(f"✅ Archivo creado: {path}")
                    await asyncio.sleep(2)

                except KeyError as e:
                    print(f"❌ Error: El template espera la llave {e} pero no se envió.")
                except Exception as e:
                    print(f"❌ Error inesperado en '{slug_reto}': {e}")

async def obtener_recap_semanal_ia(noticias, client):
    """
    Sustituye a obtener_resumen_ia. 
    Analiza las noticias y genera el contenido estructurado para el Blog y el Dashboard.
    """
    try:
        
        # Preparamos los titulares para que la IA los procese
        texto_noticias = "\n".join([f"- {n['fuente']}: {n['titulo']}" for n in noticias[:15]])
        
        prompt = f"""
        Actúa como un Editor Senior de Tecnología. Analiza estos titulares y genera un RECAP SEMANAL.
        
        NOTICIAS:
        {texto_noticias}
        
        INSTRUCCIONES DE FORMATO (RESPONDE SOLO EN JSON):
        {{
          "introduccion": "Un párrafo analítico de 3 líneas sobre la tendencia de esta semana (úsalo para el Dashboard).",
          "noticias_destacadas": "Genera 3 secciones siguiendo este formato exacto: 
                                  ### 1. [Título de la Noticia]\\n**El suceso:** [Explicación]\\n**Impacto:** [Por qué importa]\\n---",
          "repo": {{
            "nombre": "Nombre de una herramienta o repo trend de los titulares o relacionado",
            "url": "URL del recurso",
            "desc": "Por qué un dev debería probarlo"
          }},
          "tldr": "3 puntos clave breves en formato lista Markdown",
          "tags": ["lista", "de", "3", "tags", "en", "minusculas"],
          "nota_personal": "Una reflexión breve sobre el día a día del programador."
        }}
        """

        # Usamos flash-lite para velocidad y ahorro de cuota
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        
        # Limpieza de la respuesta por si la IA incluye ```json ... ```
        raw_text = response.text if response.text else "{}"
        clean_json = re.sub(r'```json|```', '', raw_text).strip()
        
        data = json.loads(clean_json)
        return data

    except Exception as e:
        print(f"❌ Error en obtener_recap_semanal_ia: {e}")
        # Retornamos un objeto vacío con la misma estructura para evitar errores de .get()
        return None

async def generar_blog_astro(noticias_web, fecha_iso, year, week, client):
    # FILTRO: Cero YouTube en el Blog para evitar errores en Vercel
    noticias_blog = [n for n in noticias_web if "yout" not in n['enlace']]
    if not noticias_blog: return None

    # Usamos el prompt nuevo que devuelve JSON
    data_ia = await obtener_recap_semanal_ia(noticias_blog, client)
    if not data_ia: return None

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    img_recap = await generar_imagen_noticia(f"Recap {week}", noticias_blog[0].get('imagen_url_original', ''), client)
    
    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=data_ia.get('introduccion', '')[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap or "/img/recap-default.webp",
        tags=json.dumps(data_ia.get('tags', ["tech"])),
        slug_name=semana_slug,
        introduccion=data_ia.get('introduccion', ''),
        bloque_noticias=data_ia.get('noticias_destacadas', ''),
        repo_name=data_ia.get('repo', {}).get('nombre', 'Tool'),
        repo_url=data_ia.get('repo', {}).get('url', '#'),
        repo_desc=data_ia.get('repo', {}).get('desc', ''),
        conclusion_tldr=data_ia.get('tldr', ''),
        nota_personal=data_ia.get('nota_personal', 'Keep coding!')
    )
    
    with open(f"./auto-news/{semana_slug}.md", "w", encoding="utf-8") as f:
        f.write(final_md)
    
    # Devolvemos la introducción para usarla como "resumen" en el Dashboard
    return data_ia.get('introduccion', '')


def generar_dashboard_html(historial, scr, fecha_h, ahora):
    v_html, n_html = "", ""
    canales_vistos = []
    
    # Chips iniciales
    chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
    chips_html += '<div class="chip active" data-filtro="\'all\'" onclick="filtrarCanal(\'all\', this)"><span>Todos</span></div>'
    
    for n_item in historial[:200]:
        fuente_limpia = n_item['fuente'].replace(" Shorts", "")
        ts = n_item.get('ts', ahora.isoformat())
        meta = f"{n_item['fuente']} | {n_item.get('f', '')}"

        # Generar Chips de canales con Avatar
        if fuente_limpia not in canales_vistos:
            url_c = next((info['yt'] for name, info in FUENTES.items() if name.startswith(fuente_limpia)), None)
            if url_c:
                img_avatar = scr.obtener_avatar_canal(fuente_limpia, url_c)
                chips_html += f'<div class="chip" data-filtro="{fuente_limpia}" onclick="filtrarCanal(\'{fuente_limpia}\', this)"><img src="{img_avatar}">{fuente_limpia}</div>'
                canales_vistos.append(fuente_limpia)

        # HTML de Vídeos/Shorts y Noticias (Web)
        if n_item.get('id_video'):
            clase = "tipo-shorts" if n_item.get('tipo') == "shorts" else "tipo-video"
            v_html += f"""
            <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_limpia}">
                <a href="{n_item['enlace']}" target="_blank"><img src="https://img.youtube.com/vi/{n_item['id_video']}/mqdefault.jpg"></a>
                <div class="card-content"><div class="meta">{meta}</div><a href="{n_item['enlace']}">{n_item['titulo']}</a></div>
            </div>"""
        else:
            badge_class = "badge-beca" if n_item.get('badge') == "Beca" else "badge-tech"
            n_html += f'<li class="news-item" data-ts="{ts}" data-fuente="{fuente_limpia}"><div class="meta">{meta}</div><span class="badge {badge_class}">{n_item.get("badge", "Tech")}</span><a href="{n_item["enlace"]}">{n_item["titulo"]}</a></li>'

    chips_html += "</div>"

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(
            fecha_hoy=fecha_h, 
            resumen="Resumen diario disponible en el Blog.", 
            bloque_chips=chips_html, 
            bloque_videos=v_html, 
            bloque_noticias=n_html,
            bloque_semanas="" # Puedes rellenar esto con tu lógica de semanas
        ))
    print("✅ Dashboard HTML generado con Chips y Vídeos.")

async def publicar_contenidos(historial, nuevos, scr):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    # Filtramos noticias web para la IA
    noticias_web = filtrar_solo_noticias(nuevos)

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

    # 1. Generamos el Blog y sacamos el resumen para el dashboard
    # (Ya no necesitas llamar a obtener_resumen_ia por separado)
    resumen_ia = await generar_blog_astro(noticias_web, fecha_iso, year, week, client)

    # 2. Generamos los Retos (¡Ya no me los paso por el forro!)
    await generar_retos_individuales(noticias_web, fecha_iso, client)

    # 3. Generamos el Dashboard HTML (con vídeos, chips y el resumen de la IA)
    generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.")


# async def publicar_contenidos(historial, nuevos, resumen_ia, scr ):
#     ahora = datetime.now()
#     fecha_h = ahora.strftime("%d/%m/%Y")
#     fecha_pub = ahora.strftime("%Y/%m/%d")
#     fecha_iso = ahora.strftime("%Y-%m-%d")
#     historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    
#     # --- GENERAR CHIPS DE SEMANAS ---
#     conteo_meses = Counter()
#     for n in historial:
#         try:
#             # Extraemos el mes y año de la fecha de la noticia (ts)
#             dt_n = datetime.fromisoformat(n.get('ts'))
#             mes_key = dt_n.strftime('%B %Y').capitalize()
#             conteo_meses[mes_key] += 1
#         except: continue

#     # --- 2. GENERAR NAVEGACIÓN POR SEMANAS ---
#     try: locale.setlocale(locale.LC_TIME, "es_ES.UTF-8") 
#     except: pass

#     # Chip rápido (Últimas 2 semanas)
#     bloque_semanas = '<div class="chip active" data-inicio="all_recent" onclick="filtrarSemana(this)">🔄 Últimas 2 Semanas</div>'
    
#     selector_html = '<select id="selectorSemanas" onchange="filtrarDesdeSelector(this)" style="padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
#     selector_html += '<option value="all">📅 Archivo Histórico...</option>'

#     mes_actual = ""
#     # Recorremos las últimas 26 semanas
#     for i in range(26):
#         inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
#         inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
#         fin = inicio + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
#         nombre_mes = inicio.strftime('%B %Y').capitalize()
        
#         # Si cambia el mes, cerramos el grupo anterior y abrimos el nuevo con el CONTADOR
#         if nombre_mes != mes_actual:
#             if mes_actual != "": selector_html += '</optgroup>'
#             total_mes = conteo_meses.get(nombre_mes, 0)
#             selector_html += f'<optgroup label="── {nombre_mes} ({total_mes} ítems) ──">'
#             mes_actual = nombre_mes
        
#         txt_semana = f"Semana {inicio.strftime('%d/%m/%y')}"
#         val_ini = inicio.isoformat()
#         val_fin = fin.isoformat()
        
#         selector_html += f'<option value="{val_ini}|{val_fin}">{txt_semana}</option>'
    
#     selector_html += '</optgroup></select>'
    
#     # Bloque final para el template
#     bloque_semanas_completo = f'<div class="filter-group" style="display:flex; align-items:center; flex-wrap:wrap; gap:10px;">{bloque_semanas} {selector_html}</div>'

#     v_html, n_html, md_links = "", "", ""
#     resumen_final = resumen_ia if resumen_ia else "Actualización diaria de tecnología."

#     # --- GENERAR CHIPS DE FILTRADO ---
#     chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
#     chips_html += '<div class="chip active" data-filtro="\'all\'" onclick="filtrarCanal(\'all\', this)"><span class="chip-text">Todos</span></div>'

#     canales_vistos = []
#     for n, info in FUENTES.items():
#         nombre_c = n.replace(" Shorts", "")
#         if "yt" in info and nombre_c not in canales_vistos:
#             img_url = scr.obtener_avatar_canal(nombre_c, info["yt"])
#             chips_html += f"""
#             <div class="chip" data-filtro="{nombre_c}" onclick="filtrarCanal('{nombre_c}', this)">
#                 <img src="{img_url}" alt="{nombre_c}" class="chip-img">
#                 <span class="chip-text">{nombre_c}</span>
#             </div>"""
#             canales_vistos.append(nombre_c)
#     chips_html += "</div>"

#     # Generar bloques para la WEB (Acumulativo 200)
#     for n in historial[:200]:
#         fecha_display = f" | {n['f']}" if n.get('f') else ""
#         meta = f"{n['fuente']}{fecha_display}"
#         fuente_limpia = n['fuente'].replace(" Shorts", "")
#         ts = n.get('ts', ahora.isoformat())

#         if n.get('id_video'):
#             clase = "tipo-shorts" if n.get('tipo') == "shorts" else "tipo-video"

#             v_html += f"""
#             <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_limpia}">
#                 <a href="{n['enlace']}" target="_blank">
#                     <img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg">
#                 </a>
#                 <div class="card-content">
#                     <div class="meta">{meta}</div>
#                     <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
#                 </div>
#             </div>"""
#         else:
#             # Determinar qué badge poner
#             badge_type = n.get('badge')
#             badge_class = "badge-beca" if badge_type == "Beca" else "badge-tech"
#             if "youtube.com" not in n['enlace'] and "youtu.be" not in n['enlace']:
#                 n_html += f'''
#                 <li class="news-item" data-ts="{ts}" data-fuente="{fuente_limpia}">
#                     <div class="meta">{meta}</div> 
#                     <span class="badge {badge_class}">{badge_type}</span> 
#                     <a href="{n["enlace"]}" target="_blank">{n["titulo"]}</a>
#                 </li>'''

#     # Guardar HTML
#     with open("public/index.html", "w", encoding="utf-8") as f:
#         f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_final, bloque_semanas=bloque_semanas_completo, bloque_chips=chips_html, bloque_videos=v_html, bloque_noticias=n_html))

#     # Guardar MD (Solo si hay nuevos)
#     if nuevos:
#         fecha_iso = ahora.strftime("%Y-%m-%d")
#         for n in nuevos:
#             titulo_low = n['titulo'].lower()
#             # Ampliamos las keywords para que sea más sensible
#             keywords_reto = ["reto", "challenge", "kata", "ejercicio", "hack", "desafío", "aprende a programar", "coding"]
#             es_reto = any(k in titulo_low for k in keywords_reto)

#             # DIAGNÓSTICO: Esto aparecerá en los logs de GitHub Actions
#             if "reto" in titulo_low or "desafío" in titulo_low:
#                 print(f"DEBUG: Posible reto detectado -> {n['titulo']}")
#             slug = f"post-{re.sub(r'[^a-z0-9]', '-', n['titulo'].lower())[:30]}"

#             if es_reto:
#                 print(f"🚀 Procesando Reto con IA: {n['titulo']}")
#                 # 1. Obtener solución de la IA
#                 sol = await obtener_solucion_reto_ia(n) # Ejecución síncrona dentro de la función
#                 if sol:
#                     res = RETO_MD_TEMPLATE
#                     res = res.replace("{titulo}", str(n['titulo']))
#                     res = res.replace("{resumen_corto}", "Reto técnico resuelto paso a paso.")
#                     res = res.replace("{fecha_pub}", str(fecha_pub))
#                     res = res.replace("{slug_name}", f"{slug}")
#                     res = res.replace("{descripcion_ia}", str(sol.get('descripcion', '')))
#                     res = res.replace("{ruta_imagen}", await generar_imagen_noticia(str(n['titulo']), sol.get('imagen_url_original')))
#                     res = res.replace("{paso_1}", str(sol.get('paso1', '')))
#                     res = res.replace("{paso_2}", str(sol.get('paso2', '')))
#                     res = res.replace("{paso_3}", str(sol.get('paso3', '')))
#                     res = res.replace("{codigo_solucion}", str(sol.get('codigo', '')))
                    
#                     with open(f"./auto-challenges/reto-{fecha_iso}-{slug}.md", "w", encoding="utf-8") as f:
#                         f.write(res)
#                     continue
#             elif "youtube.com" not in n['enlace'] and "youtu.be" not in n['enlace']:
#                 md_links += f"- **{n['fuente']}**: [{n['titulo']}]({n['enlace']})\n"

#         if md_links:
#             # Guardar MD
#             slug = f"reporte-{fecha_iso}"
#             # Creamos la variable que faltaba y limpiamos comillas para evitar errores en Astro
#             sopa = BeautifulSoup(resumen_final[:150], "html.parser")
#             texto_limpio = sopa.get_text()
#             resumen_corto_limpio = texto_limpio.replace("\\n", " ").replace('"', '') + "..."
            
#             with open(f"./auto-news/{slug}.md", "w", encoding="utf-8") as f:
#                 f.write(MD_TEMPLATE.format(
#                     titulo=f"Reporte Tech {fecha_h}",
#                     resumen_corto=resumen_corto_limpio,
#                     fecha_pub=fecha_pub,
#                     slug_name=f"{slug}",
#                     ruta_imagen="/public/img/arquitectura_web.webp",
#                     contenido=resumen_final,
#                     lista_enlaces=md_links
#                 ))




#         noticias_blog = [n for n in nuevos if n.get('tipo') == 'noticia' and "yout" not in n['enlace']]
    
#     if noticias_blog:
#         data_ia = await obtener_recap_semanal_ia(noticias_blog)
#         if data_ia:
#             semana_slug = f"{year}-w{week:02d}-tech-recap"
#             img_recap = await generar_imagen_noticia(f"Recap {week}", noticias_blog[0].get('imagen_url_original', ''))
            
#             # Template limpio para Vercel
#             res_recap = inspect.cleandoc(RECAP_TEMPLATE).format(
#                 titulo=f"Weekly Tech Recap W{week}",
#                 description=data_ia.get('introduccion', '')[:150].replace('"', "'"),
#                 fecha_iso=fecha_iso,
#                 author="Jorge Beneyto Castelló",
#                 ruta_imagen=img_recap or "/img/recap-default.webp",
#                 tags=json.dumps(data_ia.get('tags', ["tech"])),
#                 slug_name=semana_slug,
#                 introduccion=data_ia.get('introduccion', ''),
#                 bloque_noticias=data_ia.get('noticias_destacadas', ''),
#                 repo_name=data_ia.get('repo', {}).get('nombre', 'Tool'),
#                 repo_url=data_ia.get('repo', {}).get('url', '#'),
#                 repo_desc=data_ia.get('repo', {}).get('desc', ''),
#                 conclusion_tldr=data_ia.get('tldr', ''),
#                 nota_personal=data_ia.get('nota_personal', 'Keep coding!')
#             )
#             with open(f"./src/content/posts/{semana_slug}.md", "w", encoding="utf-8") as f:
#                 f.write(res_recap)


# async def publicar_contenidos(historial, nuevos, scr):
#     ahora = datetime.now()
#     year, week, _ = ahora.isocalendar()
    
#     # 1. FILTRAR: Solo noticias web (Cero YouTube para el Blog)
#     noticias_para_blog = [
#         n for n in nuevos 
#         if n['tipo'] == 'noticia' and "youtube.com" not in n['enlace'] and "youtu.be" not in n['enlace']
#     ]

#     if noticias_para_blog:
#         print(f"📦 Procesando {len(noticias_para_blog)} noticias para el Recap Semanal...")
        
#         # Obtener la curación de Gemini
#         data = await obtener_recap_semanal_ia(noticias_para_blog)
        
#         if data:
#             semana_slug = f"{year}-w{week:02d}-tech-recap"
            
#             # Generar imagen de portada (IA con fallback a la primera noticia)
#             img_portada = await generar_imagen_noticia(
#                 f"Tecnología Semana {week} {year}", 
#                 noticias_para_blog[0].get('imagen_url_original', '')
#             )

#             # Construir el Markdown con el template limpio (sin espacios a la izquierda)
#             # Usamos inspect.cleandoc para asegurar que el Frontmatter empiece en la columna 0
#             final_md = inspect.cleandoc(RECAP_TEMPLATE).format(
#                 titulo=f"Weekly Tech Recap W{week}: El avance de la IA y herramientas Dev",
#                 description=data.get('introduccion', '')[:150].replace('"', "'"),
#                 fecha_iso=ahora.strftime("%Y-%m-%d"),
#                 author="Jorge Beneyto Castelló",
#                 ruta_imagen=img_portada,
#                 tags=json.dumps(data.get('tags', ["tech", "weekly"])),
#                 slug_name=semana_slug,
#                 introduccion=data.get('introduccion', ''),
#                 bloque_noticias=data.get('noticias_destacadas', ''),
#                 repo_name=data.get('repo', {}).get('nombre', 'Herramienta útil'),
#                 repo_url=data.get('repo', {}).get('url', '#'),
#                 repo_desc=data.get('repo', {}).get('desc', 'Sin descripción'),
#                 conclusion_tldr=data.get('tldr', ''),
#                 nota_personal=data.get('nota_personal', 'Feliz semana de código.')
#             )

#             # Guardar en la carpeta de contenido de Astro
#             path_posts = "./src/content/posts"
#             os.makedirs(path_posts, exist_ok=True)
            
#             with open(f"{path_posts}/{semana_slug}.md", "w", encoding="utf-8") as f:
#                 f.write(final_md)
            
#             print(f"✅ Post Semanal creado con éxito: {semana_slug}")

#     # --- LÓGICA DE RETOS INDIVIDUALES (También sin YouTube) ---
#     for n in noticias_para_blog:
#         titulo_low = n['titulo'].lower()
#         if any(k in titulo_low for k in ["reto", "challenge", "desafío"]):
#             print(f"🎯 Generando post de reto: {n['titulo']}")
#             sol = await obtener_solucion_reto_ia(n)
#             if sol:
#                 slug_reto = f"reto-{slugify(n['titulo'])[:40]}"
#                 img_reto = await generar_imagen_noticia(n['titulo'], n.get('imagen_url_original', ''))
                
#                 reto_md = inspect.cleandoc(RETO_MD_TEMPLATE).format(
#                     titulo=n['titulo'],
#                     resumen_corto="Desafío técnico resuelto paso a paso.",
#                     fecha_pub=ahora.strftime("%Y-%m-%d"),
#                     slug_name=slug_reto,
#                     descripcion_ia=sol.get('descripcion', ''),
#                     ruta_imagen=img_reto,
#                     paso_1=sol.get('paso1', ''),
#                     paso_2=sol.get('paso2', ''),
#                     paso_3=sol.get('paso3', ''),
#                     codigo_solucion=sol.get('codigo', '')
#                 )
                
#                 with open(f"./src/content/posts/{slug_reto}.md", "w", encoding="utf-8") as f:
#                     f.write(reto_md)

























def filtrar_solo_noticias(nuevos):
    """Retorna solo items que NO sean vídeos ni shorts."""
    return [n for n in nuevos if n.get('tipo') == 'noticia']


def enviar_email_reporte(resumen_html, nuevos):
    """Genera y envía el reporte por email con diseño anti-spam y estadísticas."""
    if not CONFIG["MAIL_KEY"] or not nuevos:
        return
    # 1. Cálculos para el "Minigráfico" de actividad
    c_tech = len([x for x in nuevos if x.get('badge') == 'Tech'])
    c_becas = len([x for x in nuevos if x.get('badge') == 'Beca'])
    c_vids = len([x for x in nuevos if x.get('id_video')])
    
    # 2. Construir la lista de noticias en formato tabla HTML
    filas_noticias = ""
    for n in nuevos[:15]:  # Limitamos a 15 para no saturar el correo
        icon = "📺" if n.get('id_video') else ("🎓" if n.get('badge') == "Beca" else "💻")
        
        filas_noticias += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #edf2f7;">
                <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
                <span style="color: #718096; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">{n['fuente']}</span><br>
                <a href="{n['enlace']}" target="_blank" style="color: #1a73e8; text-decoration: none; font-weight: 600; font-size: 15px; line-height: 1.4;">{n['titulo']}</a>
            </td>
        </tr>
        """

    # 3. Asunto Dinámico Anti-Spam (basado en la noticia principal)
    # Evitamos asuntos repetitivos como "Reporte diario" que van directo a SPAM
    top_titular = nuevos[0]['titulo']
    asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"
    
    # Temas clave para el preheader invisible
    temas_clave = ", ".join(list(set([n['fuente'] for n in nuevos[:3]])))

    # 4. Componer el HTML final
    html_final = EMAIL_TEMPLATE.format(
        fecha_hoy=datetime.now().strftime("%d de %B, %Y"),
        contenido_html=resumen_html,
        lista_email=filas_noticias,
        count_tech=c_tech,
        count_becas=c_becas,
        count_vids=c_vids,
        total_noticias=len(nuevos),
        temas_clave=temas_clave
    )

    # 5. Envío mediante Mailgun API
    try:
        r = requests.post(
            f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages",
            auth=("api", CONFIG["MAIL_KEY"]),
            data={
                "from": f"Tech Pulse Newsletter <newsletter@{CONFIG['MAIL_DOMAIN']}>",
                "to": [CONFIG["EMAIL_TO"]],
                "subject": asunto,
                "html": html_final
            }
        )
        if r.status_code == 200:
            print(f"📧 Email enviado con éxito: {asunto}")
    except Exception as e:
        print(f"⚠️ Fallo en el envío de email: {e}")

async def enviar_telegram_con_audio(resumen, nuevos):
    if not CONFIG["BOT_TOKEN"] or not CONFIG["CHAT_ID"]: return
    # 1. Limpiar el resumen HTML para que sea compatible con Markdown de Telegram
    # Quitamos los tags de párrafo y los convertimos en saltos de línea
    resumen_md = resumen.replace("<p style='margin-bottom:15px; line-height:1.6;'>", "").replace("</p>", "\n\n")
    # Convertimos negritas HTML <b> a Markdown *
    resumen_md = resumen_md.replace("<b>", "*").replace("</b>", "*")
    fecha_str = datetime.now().strftime('%d/%m')
    caption = f"🤖 *RESUMEN IA - {fecha_str}*\n"
    
    # Añadimos el resumen (limitamos a 600 caracteres para dejar espacio a los links)
    resumen_recortado = (resumen_md[:600] + '...') if len(resumen_md) > 600 else resumen_md
    caption += f"{resumen_recortado.strip()}\n\n"
    caption += f"📋 *TOP ENLACES:*\n"

    # 3. Añadir enlaces controlando el espacio restante
    # Dejamos un margen de seguridad (100 caracteres para el botón y despedida)
    LIMITE_TELEGRAM = 1024
    MARGEN_SEGURIDAD = 100

    for n in nuevos:
        if n.get('id_video'): icono = "📺"
        elif n.get('badge') == "Beca": icono = "🎓"
        else: icono = "💻"
        
        nuevo_item = f"{icono} [{n['fuente']}]({n['enlace']}) "
        
        # Si añadir este link supera el límite, paramos
        if len(caption) + len(nuevo_item) > (LIMITE_TELEGRAM - MARGEN_SEGURIDAD):
            caption += "\n\n⚠️ _Hay más enlaces en el Dashboard..._"
            break
        else:
            caption += nuevo_item


    VOZ_ELEGIDA = "es-ES-AlvaroNeural" # Otras: es-ES-ElviraNeural, es-MX-JorgeNeural
    audio_path = "resumen.mp3"
    texto_para_voz = resumen_recortado[:800] # Álvaro lee mejor textos de esta longitud
    try:
        # Generamos el archivo de audio
        communicate = edge_tts.Communicate(texto_para_voz, VOZ_ELEGIDA)
        await communicate.save(audio_path)

        # 4. ENVÍO A TELEGRAM (Corregido el error de binary mode y el envío)
        url = f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendVoice"
        
        with open(audio_path, "rb") as audio_file:
            files = {'voice': (audio_path, audio_file, 'audio/mpeg')}
            payload = {
                "chat_id": CONFIG["CHAT_ID"], 
                "caption": caption, 
                "parse_mode": "Markdown",
                "reply_markup": json.dumps({
                    "inline_keyboard": [[{"text": "🌐 Dashboard", "url": "http://jorbencasdownloaderdocument.surge.sh"}]]
                }, ensure_ascii=False)
            }
            # El post debe ir dentro del 'with' para que el archivo esté abierto
            r = requests.post(url, data=payload, files=files)

        if not r.ok:
            # FALLBACK: Si falla el Markdown por caracteres raros, reintentamos sin Markdown
            print(f"⚠️ Reintentando envío sin Markdown por error: {r.text}")
            payload.pop("parse_mode")
            # Limpiamos el caption de caracteres de escape para texto plano
            payload["caption"] = caption.replace("\\_", "_").replace("\\*", "*")
            with open(audio_path, "rb") as audio_file:
                files = {'voice': (audio_path, audio_file, 'audio/mpeg')}
                r = requests.post(url, data=payload, files=files)
        # Limpieza: Borramos el archivo temporal
        if os.path.exists(audio_path): os.remove(audio_path)
        
        if r.status_code == 200: print("✅ Telegram con voz humana enviado")
        else: print(f"❌ Error Telegram: {r.text}")

    except Exception as e:
        print(f"⚠️ Error en TTS Humano: {e}")

async def generar_imagen_noticia(titulo_noticia, url_imagen_scrap, client):
    """
    Genera una imagen usando Gemini 3 con reintentos.
    Si falla tras los intentos, devuelve la imagen scrapeada original.
    """

    slug = slugify(titulo_noticia)
    filename = f"{slug}.png"
    filepath = os.path.join(CONFIG["IMAGES_FOLDER"], filename)

    # 1. Caché: Si ya existe, no gastamos créditos
    if os.path.exists(filepath):
        return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"

    # 2. Configuración de reintentos
    max_intentos = 3
    prompt_completo = PROMPT_IMAGEN_TEMPLATE.format(titulo_post=titulo_noticia)

    for intento in range(max_intentos):
        try:
            print(f"🎨 Generando imagen IA para: '{titulo_noticia}' (Intento {intento+1})...")
            
            # Generación de imagen
            response = client.models.generate_image(
                model="gemini-3-flash-image",
                prompt=prompt_completo
            )

            # Guardar el objeto binario
            os.makedirs(CONFIG["IMAGES_FOLDER"], exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(response.image_bytes)
                
            print(f"✅ Imagen de Gemini guardada en: {filepath}")
            return f"{CONFIG['IMAGES_PATH_PREFIX']}/{filename}"

        except Exception as e:
            # Manejo de limitaciones (Error 429 / Resource Exhausted)
            if "429" in str(e) or "QUOTA" in str(e).upper():
                tiempo_espera = 40 * (intento + 1)
                if intento < max_intentos - 1:
                    print(f"⏳ Límite alcanzado. Reintentando en {tiempo_espera}s...")
                    await asyncio.sleep(tiempo_espera)
                else:
                    print("❌ Agotados los reintentos de cuota para imagen.")
            else:
                print(f"⚠️ Error inesperado en imagen: {e}")
                break # Si es otro tipo de error (ej. prompt bloqueado), no reintentamos

    # 3. EL GRAN FALLBACK: Si todo falla, devolvemos la imagen scrapeada
    print(f"🔄 Usando imagen original de la fuente para: {titulo_noticia}")
    return url_imagen_scrap if url_imagen_scrap else "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true"

# --- FUNCIONALIDAD LINK CHECKER ---
async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos if n['enlace'] not in vistos]
    total = nuevos + historial

   # resumen = await obtener_resumen_ia(nuevos) if nuevos else "Todo al día por ahora."
    await publicar_contenidos(total, nuevos, scr)

    # Guardar la caché de avatares para la próxima vez
    scr.guardar_avatars()
    
    if nuevos:
        noticias_texto_nuevas = filtrar_solo_noticias(nuevos)
        if len(noticias_texto_nuevas) > 0:
            enviar_email_reporte("", noticias_texto_nuevas)
            await enviar_telegram_con_audio("", noticias_texto_nuevas)
            total = noticias_texto_nuevas + historial
            with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4, ensure_ascii=False)
        print(f"✅ {len(nuevos)} noticias nuevas procesadas.")
    else:
        print("☕ Sin cambios hoy.")

if __name__ == "__main__":
    asyncio.run(main())