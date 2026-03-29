import hashlib
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
from constants_downloadfile import FUENTES, CONFIG, HTML_TEMPLATE, EMAIL_TEMPLATE, ALL_KEYWORDS, BECAS_KEYWORDS, MD_TEMPLATE, RETO_MD_TEMPLATE, PROMPT_IMAGEN_TEMPLATE, URL_API_DESCARGA, URL_API_SALUD
from slugify import slugify 
import html
# En tu script del Dashboard (el que genera el HTML)


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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        try:
            r = requests.get(target, timeout=20, headers=headers)
            if r.status_code != 200: return []

            if "yt" in info:
                # --- MEJORA YOUTUBE: BUSCAR EL JSON INTERNO ---
                # Este bloque contiene la información real que YouTube renderiza
                json_data = re.search(r'var ytInitialData = (\{.*?\});', r.text)
                
                if json_data:
                    try:
                        data = json.loads(json_data.group(1))
                        # Navegamos por la estructura compleja de YouTube para llegar a los videos
                        # Dependiendo de la pestaña (/videos, /shorts, /streams) la ruta cambia levemente
                        contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
                        # Buscamos la pestaña activa que tiene el contenido
                        video_list = []
                        for tab in contents:
                            if 'content' in tab['tabRenderer']:
                                rich_grid = tab['tabRenderer']['content'].get('richGridRenderer', {})
                                items = rich_grid.get('contents', [])
                                if items:
                                    video_list = items
                                    break
                        
                        for item in video_list[:6]: # Limitamos a los 6 más recientes
                            v_data = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                            if not v_data: 
                                # Si no es videoRenderer, podría ser un 'reelItemRenderer' (Shorts específicos)
                                v_data = item.get('richItemRenderer', {}).get('content', {}).get('reelItemRenderer', {})

                            # 1. DETECTAR DIRECTOS (LIVE)
                            # Buscamos la etiqueta "En directo" o "LIVE" en los badges
                            badges = v_data.get('badges', [])
                            es_live = any(b.get('metadataBadgeRenderer', {}).get('style') == "BADGE_STYLE_TYPE_LIVE_NOW" for b in badges)
                            # Refuerzo: Si el tiempo de publicación dice "Emitido hace..."
                            published_text = v_data.get('publishedTimeText', {}).get('simpleText', '').lower()
                            if "emitido" in published_text or "streaming" in published_text:
                                es_live = True

                            # 2. DETECTAR SHORTS
                            # Los Shorts suelen venir en un objeto llamado 'reelItemRenderer' o tener la URL /shorts/
                            es_short = "reelItemRenderer" in str(item) or "/shorts/" in target.lower()

                            video_id = v_data.get('videoId')
                            titulo_sucio = v_data.get('title', {}).get('runs', [{}])[0].get('text', '')
                            titulo_limpio = html.unescape(titulo_sucio.encode().decode('unicode-escape'))
                            
                            
                            fecha_relativa = v_data.get('publishedTimeText', {}).get('simpleText', 'Reciente')
                            
                            # Ignorar vídeos de hace años
                            if any(x in fecha_relativa.lower() for x in ["año", "year", "meses", "months"]):
                                continue

                            es_short = "shorts" in target.lower() or "/shorts/" in video_id
                            es_live = "badges" in v_data and "LIVE" in str(v_data["badges"])

                            results.append({
                                "titulo": titulo_limpio,
                                "enlace": f"https://www.youtube.com/watch?v={video_id}",
                                "id_video": video_id,
                                "fuente": nombre,
                                "tipo": "shorts" if es_short else ("live" if es_live else "video"),
                                "fecha_real": datetime.now().strftime("%d/%m/%Y"), # Fallback
                                "f": datetime.now().strftime("%d/%m"),
                                "ts": datetime.now().isoformat()
                            })
                    except Exception as e:
                        print(f"⚠️ Error procesando JSON de YT: {e}")
                
                # --- FALLBACK: Si el JSON falla, usamos tus Regex mejoradas ---
                if not results:
                    ids = list(dict.fromkeys(re.findall(r'"videoId":"(.*?)"', r.text)))
                    # Patrón más robusto para títulos
                    titles = re.findall(r'{"videoRenderer":{"videoId":".*?","thumbnail":.*?,"title":{"runs":\[{"text":"(.*?)"}\]', r.text)
                    
                    for t, i in zip(titles[:5], ids[:5]):
                        results.append({
                            "titulo": t.encode().decode('unicode-escape'),
                            "enlace": f"https://www.youtube.com/watch?v={i}",
                            "id_video": i, "fuente": nombre, "tipo": "video",
                            "f": datetime.now().strftime("%d/%m")
                        })

            else:
                # --- MEJORA WEB: SCRAPING TRADICIONAL ---
                soup = BeautifulSoup(r.text, 'html.parser')
                selector = info.get("selector", 'article h2 a, h3 a, h2 a, .post-title a')
                items = soup.select(selector)[:10]

                for i in items:
                    enlace = urljoin(target, i.get('href', ''))
                    if not enlace or len(enlace) < 10: continue

                    t_raw = i.get_text(strip=True)
                    t_low = t_raw.lower()

                    # Solo procesar si hay keywords o es una web de confianza
                    is_english = any(x in target for x in ["wired", "verge", "techcrunch", "github", "openai"])
                    match_keyword = any(key.lower() in t_low for key in ALL_KEYWORDS)

                    if match_keyword or is_english:
                        img_url = ""
                        # Buscar imagen subiendo al contenedor padre para ser más precisos
                        parent = i.find_parent(['article', 'div', 'section'])
                        if parent:
                            img_tag = parent.find('img')
                            if img_tag:
                                img_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset', '').split(' ')[0]

                        results.append({
                            "titulo": t_raw,
                            "enlace": enlace,
                            "fuente": nombre,
                            "tipo": "noticia",
                            "badge": "Beca" if any(k in t_low for k in BECAS_KEYWORDS) else "Tech",
                            "imagen_url_original": urljoin(target, img_url) if img_url else "",
                            "f": datetime.now().strftime("%d/%m"),
                            "ts": datetime.now().isoformat()
                        })

        except Exception as e:
            print(f"❌ Error en fuente {nombre}: {e}")
        
        return results

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
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
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
        titulo_low = n.get('title', 'video-sin-nombre').lower()
        if any(k in titulo_low for k in ["reto", "challenge", "desafío"]):
            slug_reto = f"reto-{slugify(n.get('title', 'video-sin-nombre'))[:40]}"
            path = f"{folder}/{slug_reto}.md"
            
            if os.path.exists(path): continue

            print(f"🎯 Procesando reto: {n.get('title', 'video-sin-nombre')}")
            sol = await obtener_solucion_ia(n.get('title', 'video-sin-nombre'), n.get('fuente', 'Web'), client)
            
            if sol:
                img_reto = await generar_imagen_noticia(n.get('title', 'video-sin-nombre'), "", client)
                lang = sol.get('lenguaje', 'python').lower()
                await asyncio.sleep(3)
                try:
                    # Usamos inspect.cleandoc para que el Frontmatter (---) empiece en la columna 0
                    reto_md = inspect.cleandoc(RETO_MD_TEMPLATE).format(
                        titulo=n.get('title', 'video-sin-nombre').replace('"', "'"),
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
    max_intentos = 3

    for intento in range(max_intentos):
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
            error_str = str(e).upper()
            # Si el error es de Cuota (429) o Sobrecarga (503)
            if "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                tiempo_espera = 35 * (intento + 1) # Esperamos 35s, 70s...
                if intento < max_intentos - 1:
                    print(f"⏳ Límite de Gemini alcanzado. Esperando {tiempo_espera}s para reintentar...")
                    await asyncio.sleep(tiempo_espera)
                else:
                    print("❌ Se agotaron los reintentos de cuota para el Blog.")
            else:
                print(f"❌ Error en obtener_recap_semanal_ia: {e}")
                break
    return None

async def generar_blog_astro(noticias_web, fecha_iso, year, week, client):
    # FILTRO: Cero YouTube en el Blog para evitar errores en Vercel
    noticias_blog = [n for n in noticias_web if "yout" not in n['enlace']]
    if not noticias_blog: return None

    # Usamos el prompt nuevo que devuelve JSON
    data_ia = await obtener_recap_semanal_ia(noticias_blog, client)
    if not data_ia: return None

    await asyncio.sleep(5)

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    img_recap = await generar_imagen_noticia(f"Recap {week}", noticias_blog[0].get('imagen_url_original', ''), client)
    await asyncio.sleep(3)

    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=data_ia.get('introduccion', '')[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap or "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true",
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


def generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia):
    v_html, n_html = "", ""
    canales_vistos = []
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    # --- GENERAR CHIPS DE SEMANAS ---
    conteo_meses = Counter()
    for n in historial:
        try:
            # Extraemos el mes y año de la fecha de la noticia (ts)
            dt_n = datetime.fromisoformat(n.get('ts'))
            mes_key = dt_n.strftime('%B %Y').capitalize()
            conteo_meses[mes_key] += 1
        except: continue

    # --- 2. GENERAR NAVEGACIÓN POR SEMANAS ---
    try: locale.setlocale(locale.LC_TIME, "es_ES.UTF-8") 
    except: pass

    # Chip rápido (Últimas 2 semanas)
    bloque_semanas = '<div class="chip active" data-inicio="all_recent" onclick="filtrarSemana(this)">🔄 Últimas 2 Semanas</div>'
    
    selector_html = '<select id="selectorSemanas" onchange="filtrarDesdeSelector(this)" style="padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
    selector_html += '<option value="all">📅 Archivo Histórico...</option>'

    mes_actual = ""
    # Recorremos las últimas 26 semanas
    for i in range(26):
        inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        nombre_mes = inicio.strftime('%B %Y').capitalize()
        
        # Si cambia el mes, cerramos el grupo anterior y abrimos el nuevo con el CONTADOR
        if nombre_mes != mes_actual:
            if mes_actual != "": selector_html += '</optgroup>'
            total_mes = conteo_meses.get(nombre_mes, 0)
            selector_html += f'<optgroup label="── {nombre_mes} ({total_mes} ítems) ──">'
            mes_actual = nombre_mes
        
        txt_semana = f"Semana {inicio.strftime('%d/%m/%y')}"
        val_ini = inicio.isoformat()
        val_fin = fin.isoformat()
        
        selector_html += f'<option value="{val_ini}|{val_fin}">{txt_semana}</option>'
    
    selector_html += '</optgroup></select>'
    
    # Bloque final para el template
    bloque_semanas_completo = f'<div class="filter-group" style="display:flex; align-items:center; flex-wrap:wrap; gap:10px;">{bloque_semanas} {selector_html}</div>'

    # Chips iniciales
    chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
    chips_html += '<div class="chip active" data-filtro="\'all\'" onclick="filtrarCanal(\'all\', this)"><span>Todos</span></div>'
    
    for n_item in historial[:200]:
        fuente_limpia = n_item['fuente'].replace(" Shorts", "")
        ts = n_item.get('ts', ahora.isoformat())
        fecha_display = n_item.get('fecha_real', n_item.get('f', 'S/D'))
        meta = f"{n_item['fuente']} | {fecha_display}"

        # Generar Chips de canales con Avatar
        if fuente_limpia not in canales_vistos:
            url_c = next((info.get('yt') for name, info in FUENTES.items() if name.startswith(fuente_limpia) and info.get('yt')), None)
            if url_c:
                img_avatar = scr.obtener_avatar_canal(fuente_limpia, url_c)
                chips_html += f'<div class="chip" data-filtro="{fuente_limpia}" onclick="filtrarCanal(\'{fuente_limpia}\', this)"><img class="chip-img" src="{img_avatar}"><span class="chip-text">{fuente_limpia}</span></div>'
                canales_vistos.append(fuente_limpia)

        # HTML de Vídeos/Shorts y Noticias (Web)
        if n_item.get('id_video'):            
            tipo = n_item.get('tipo', 'video')
            es_live = n_item.get('is_live', False) or tipo == "live"
            clase = "tipo-live" if es_live else ("tipo-shorts" if n_item.get('tipo') == "shorts" else "tipo-video")
            
            # Badge de Directo
            badge_live = '<span class="badge-live">● EN DIRECTO</span>' if es_live else ""
            
            # Botón de Descarga (Link dinámico)
            btn_download = f"""
            <button onclick="descargarVideo(`{n_item.get('enlace')}`, this)" target="_blank" class="btn-download">📥</button>
            """
            
            v_html += f"""
            <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_limpia}">
                {badge_live}
                {btn_download}
                <a href="{n_item['enlace']}" target="_blank"><img src="https://img.youtube.com/vi/{n_item['id_video']}/mqdefault.jpg"></a>
                <div class="card-content"><div class="meta">{meta}</div><a href="{n_item['enlace']}">{n_item['titulo']}</a></div>
            </div>"""
        else:
            badge_class = "badge-beca" if n_item.get('badge') == "Beca" else "badge-tech"
            n_html += f'<li class="news-item" data-ts="{ts}" data-fuente="{fuente_limpia}"><div class="meta">{meta}</div><span class="badge {badge_class}">{n_item.get("badge", "Tech")}</span><a href="{n_item["enlace"]}">{n_item["titulo"]}</a></li>'

    chips_html += "</div>"


    palabra_maestra = CONFIG.get("DOWNLOADER_API_TOKEN")
    fecha_hoy = datetime.utcnow().strftime("%Y-%m-%d")
    semilla = f"{palabra_maestra}-{fecha_hoy}"
    
    # Este es el token que el JS usará hoy
    token_oculto = hashlib.sha256(semilla.encode()).hexdigest()

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(
            fecha_hoy=fecha_h, 
            resumen=resumen_ia, 
            bloque_chips=chips_html, 
            bloque_videos=v_html, 
            bloque_noticias=n_html,
            bloque_semanas=bloque_semanas_completo, # Puedes rellenar esto con tu lógica de semanas
            api_token=token_oculto, api_url=URL_API_DESCARGA, api_salud=URL_API_SALUD
        ))
    print("✅ Dashboard HTML generado con Chips y Vídeos.")

async def publicar_contenidos(historial, noticias_web, scr):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

    # 1. Generamos el Blog y sacamos el resumen para el dashboard
    # (Ya no necesitas llamar a obtener_resumen_ia por separado)
    resumen_ia = await generar_blog_astro(noticias_web, fecha_iso, year, week, client)

    if not resumen_ia:
        resumen_ia = "Hoy no ha sido posible generar el resumen automático. Consulta los enlaces directos abajo."

    await generar_retos_individuales(noticias_web, fecha_iso, client)

    generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.")

    enviar_email_reporte(resumen_ia, noticias_web)
    await enviar_telegram_con_audio(resumen_ia, noticias_web)

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

    resumen_md = resumen.replace("<p style='margin-bottom:15px; line-height:1.6;'>", "").replace("</p>", "\n\n")

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
    return url_imagen_scrap if url_imagen_scrap else "public/img/arquitectura_web.webp"

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

    # Guardar la caché de avatares para la próxima vez
    scr.guardar_avatars()
    # Filtramos noticias web para la IA
    noticias_web = filtrar_solo_noticias(nuevos)

    await publicar_contenidos(total, noticias_web, scr)

    if noticias_web:
        total = noticias_web + historial
        with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4, ensure_ascii=False)
        print(f"✅ {len(noticias_web)} noticias nuevas procesadas.")
    else:
        print("☕ Sin cambios hoy.")

if __name__ == "__main__":
    asyncio.run(main())
