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
from constants_downloadfile import FUENTES, CONFIG, HTML_TEMPLATE, EMAIL_TEMPLATE, ALL_KEYWORDS, BECAS_KEYWORDS, MD_TEMPLATE, RETO_MD_TEMPLATE, URL_API_DESCARGA, URL_API_SALUD
from utils import obtener_solucion_ia, generar_imagen_noticia, obtener_recap_semanal_ia
from slugify import slugify 
import html
import aiohttp
import html2text
import logging
from logging.handlers import RotatingFileHandler

# --- CONFIGURACIÓN DE LOGS ---
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "scraper.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scraper")
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
                with open(self.cache_file, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {}
        return {}

    def guardar_avatars(self):
        if self.cambios_en_cache:
            with open(self.cache_file, 'w') as f: 
                json.dump(self.avatars, f, indent=4, ensure_ascii=False)
            logger.info("💾 Caché de avatares actualizada.")

    def obtener_avatar_canal(self, nombre, url_canal):
        # Si ya lo tenemos en caché, no entramos a YouTube
        if nombre in self.avatars: return self.avatars[nombre]
        
        try:
            logger.info(f"🔍 Buscando avatar real para: {nombre}...")
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

    async def extraer(self, session, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cookie': 'SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjYwNTI1LjA5X3AwGgJlcyACGgYIgMXT0AY; PREF=tz=Europe.Madrid',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        try:
            async with session.get(target, timeout=20, headers=headers) as response:
                if response.status != 200: return []
                html_text = await response.text()

            if "yt" in info:
                logger.info(f"📺 Procesando fuente de YouTube: {nombre} ({target})")
                # --- MEJORA YOUTUBE: BUSCAR EL JSON INTERNO ---
                # Regex más flexible para ytInitialData
                json_data = re.search(r'ytInitialData\s*=\s*(\{.*?\});', html_text)
                if not json_data:
                    json_data = re.search(r'window\[["\']ytInitialData["\']\]\s*=\s*(\{.*?\});', html_text)
                
                if json_data:
                    logger.info(f"✅ 'ytInitialData' encontrado para {nombre}.")
                    try:
                        data = json.loads(json_data.group(1))
                        # Navegamos por la estructura compleja de YouTube
                        tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
                        video_list = []
                        for tab in tabs:
                            content = tab.get('tabRenderer', {}).get('content', {})
                            if 'richGridRenderer' in content:
                                video_list = content['richGridRenderer'].get('contents', [])
                                break
                        
                        logger.info(f"🛠️ Analizando {len(video_list)} elementos para {nombre}...")
                        for item in video_list[:10]: # Aumentamos un poco el rango para encontrar videos válidos
                            # 1. IDENTIFICAR EL RENDERER (Video, Short, Live o el nuevo lockupViewModel)
                            v_data = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                            
                            # NUEVA ESTRUCTURA: lockupViewModel (Videos normales 2024/2025)
                            if not v_data:
                                lockup = item.get('richItemRenderer', {}).get('content', {}).get('lockupViewModel', {})
                                if lockup:
                                    video_id = lockup.get('contentId')
                                    metadata = lockup.get('metadata', {}).get('lockupMetadataViewModel', {})
                                    titulo_limpio = metadata.get('title', {}).get('content', '')
                                    
                                    # Para videos normales en lockupViewModel, la fecha está en metadata
                                    fecha_relativa = metadata.get('videoMetadataRenderer', {}).get('publishedTimeText', {}).get('simpleText', 'Reciente')
                                    if any(x in fecha_relativa.lower() for x in ["año", "year", "mes", "month"]):
                                        continue

                                    if video_id and titulo_limpio:
                                        results.append({
                                            "titulo": html.unescape(titulo_limpio),
                                            "enlace": f"https://www.youtube.com/watch?v={video_id}",
                                            "id_video": video_id,
                                            "fuente": nombre,
                                            "tipo": "video",
                                            "fecha_real": datetime.now().strftime("%d/%m/%Y"),
                                            "f": datetime.now().strftime("%d/%m"),
                                            "ts": datetime.now().isoformat()
                                        })
                                    continue

                            # NUEVA ESTRUCTURA: shortsLockupViewModel (Shorts 2024/2025)
                            if not v_data:
                                s_lockup = item.get('richItemRenderer', {}).get('content', {}).get('shortsLockupViewModel', {})
                                if s_lockup:
                                    video_id = s_lockup.get('onTap', {}).get('innertubeCommand', {}).get('reelWatchEndpoint', {}).get('videoId')
                                    titulo_limpio = s_lockup.get('overlayMetadata', {}).get('primaryText', {}).get('content', '')
                                    
                                    if video_id and titulo_limpio:
                                        # Los Shorts no suelen tener fecha en la parrilla, los damos por válidos (recientes)
                                        results.append({
                                            "titulo": html.unescape(titulo_limpio),
                                            "enlace": f"https://www.youtube.com/watch?v={video_id}",
                                            "id_video": video_id,
                                            "fuente": nombre,
                                            "tipo": "shorts",
                                            "fecha_real": datetime.now().strftime("%d/%m/%Y"),
                                            "f": datetime.now().strftime("%d/%m"),
                                            "ts": datetime.now().isoformat()
                                        })
                                    continue

                            if not v_data: 
                                v_data = item.get('richItemRenderer', {}).get('content', {}).get('reelItemRenderer', {})

                            if not v_data: continue

                            # 2. EXTRAER TÍTULO (Diferente estructura para Shorts vs Videos)
                            titulo_sucio = ""
                            if 'title' in v_data:
                                if 'runs' in v_data['title']:
                                    titulo_sucio = v_data['title']['runs'][0].get('text', '')
                                elif 'simpleText' in v_data['title']:
                                    titulo_sucio = v_data['title']['simpleText']
                            elif 'headline' in v_data: # Estructura común en Shorts (reelItemRenderer)
                                titulo_sucio = v_data['headline'].get('simpleText', '')

                            titulo_limpio = html.unescape(titulo_sucio)
                            if not titulo_limpio: continue

                            # 3. DETECTAR DIRECTO (LIVE)
                            badges = v_data.get('badges', [])
                            es_live = any(b.get('metadataBadgeRenderer', {}).get('style') == "BADGE_STYLE_TYPE_LIVE_NOW" for b in badges)
                            published_text = v_data.get('publishedTimeText', {}).get('simpleText', '').lower()
                            if "emitido" in published_text or "streaming" in published_text or "directo" in published_text:
                                es_live = True

                            video_id = v_data.get('videoId')
                            if not video_id: continue

                            fecha_relativa = v_data.get('publishedTimeText', {}).get('simpleText', 'Reciente')
                            
                            # FILTRO DE RECIENCIA: Solo hoy, ayer o esta semana (máximo 7-10 días)
                            if any(x in fecha_relativa.lower() for x in ["año", "year", "mes", "month"]):
                                continue

                            es_short = "shorts" in target.lower() or "/shorts/" in video_id or "reelItemRenderer" in str(item)

                            results.append({
                                "titulo": titulo_limpio,
                                "enlace": f"https://www.youtube.com/watch?v={video_id}",
                                "id_video": video_id,
                                "fuente": nombre,
                                "tipo": "shorts" if es_short else ("live" if es_live else "video"),
                                "fecha_real": datetime.now().strftime("%d/%m/%Y"),
                                "f": datetime.now().strftime("%d/%m"),
                                "ts": datetime.now().isoformat()
                            })
                        logger.info(f"📊 {len(results)} videos/shorts válidos extraídos de {nombre}.")
                    except Exception as e:
                        logger.error(f"⚠️ Error procesando JSON de YT ({nombre}): {e}", exc_info=True)
                
                # --- FALLBACK: Regex ---
                if not results:
                    logger.warning(f"⚠️ No se obtuvieron resultados vía JSON para {nombre}. Intentando fallback con Regex...")
                    ids = list(dict.fromkeys(re.findall(r'"videoId":"(.*?)"', html_text)))
                    titles = re.findall(r'{"videoRenderer":{"videoId":".*?","thumbnail":.*?,"title":{"runs":\[{"text":"(.*?)"}\]', html_text)
                    
                    for t, i in zip(titles[:5], ids[:5]):
                        results.append({
                            "titulo": html.unescape(t),
                            "enlace": f"https://www.youtube.com/watch?v={i}",
                            "id_video": i, "fuente": nombre, "tipo": "video",
                            "f": datetime.now().strftime("%d/%m")
                        })

            else:
                # --- MEJORA WEB: SCRAPING TRADICIONAL ---
                soup = BeautifulSoup(html_text, 'html.parser')
                selector = info.get("selector", 'article h2 a, h3 a, h2 a, .post-title a')
                items = soup.select(selector)[:10]

                for i in items:
                    enlace = urljoin(target, i.get('href', ''))
                    if not enlace or len(enlace) < 10: continue

                    t_raw = i.get_text(strip=True)
                    t_low = t_raw.lower()

                    is_english = any(x in target for x in ["wired", "verge", "techcrunch", "github", "openai"])
                    match_keyword = any(key.lower() in t_low for key in ALL_KEYWORDS)

                    if match_keyword or is_english:
                        img_url = ""
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

# Eliminamos obtener_solucion_ia local - ya está en utils.py


async def generar_retos_individuales(noticias_web, fecha_iso, client):
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)

    for n in noticias_web:
        titulo_low = n.get('title', 'video-sin-nombre').lower()
        if any(k in titulo_low for k in ["reto", "challenge", "desafío"]):
            slug_reto = f"reto-{slugify(n.get('title', 'video-sin-nombre'))[:40]}"
            path = f"{folder}/{slug_reto}.md"
            
            if os.path.exists(path): continue

            logger.info(f"🎯 Procesando reto: {n.get('title', 'video-sin-nombre')}")
            sol = await obtener_solucion_ia(n['titulo'], n['fuente'], client, lang=lang)
            
            if sol:
                img_reto = await generar_imagen_noticia(f"Reto de programación {n['titulo']}", client)
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
                    logger.info(f"✅ Archivo creado: {path}")
                    await asyncio.sleep(2)

                except KeyError as e:
                    logger.error(f"❌ Error: El template espera la llave {e} pero no se envió.")
                except Exception as e:
                    logger.error(f"❌ Error inesperado en '{slug_reto}': {e}")

def limpiar_html_para_mdx(html: str, to_markdown: bool = False) -> str:
    if not html:
        return ""

    # 1. Arregla HTML roto
    soup = BeautifulSoup(html, "html.parser")

    html_limpio = str(soup)

    # 2. Opcional: convertir a Markdown (recomendado)
    if to_markdown:
        md = html2text.html2text(html_limpio)
        return md.strip()

    return html_limpio.strip()

async def generar_blog_astro(noticias_web, fecha_iso, year, week, client):
    # FILTRO: Cero YouTube en el Blog para evitar errores en Vercel
    noticias_blog = [n for n in noticias_web if "yout" not in n['enlace']]
    if not noticias_blog: return None

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    path_md = f"./auto-news/{semana_slug}.md"

    # OPTIMIZACIÓN: Si ya existe el recap de esta semana y no hay noticias urgentes, saltar
    if os.path.exists(path_md) and not noticias_web:
        logger.info(f"⏭️  Recap semanal {semana_slug} ya existe. Saltando generación IA.")
        with open(path_md, "r", encoding="utf-8") as f:
            match = re.search(r'description: "(.*?)"', f.read())
            return match.group(1) if match else "Recap semanal disponible."

    # Usamos el prompt nuevo que devuelve JSON
    data_ia = await obtener_recap_semanal_ia(noticias_blog, client)
    if not data_ia: return None
    img_recap = await generar_imagen_noticia(f"Recap {week}", client)
    await asyncio.sleep(3)

    introduccion = limpiar_html_para_mdx(
        data_ia.get('introduccion', ''), 
        to_markdown=True
    )

    bloque_noticias = limpiar_html_para_mdx(
        data_ia.get('noticias_destacadas', ''), 
        to_markdown=True
    )

    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=introduccion[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap or "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true",
        tags=json.dumps(data_ia.get('tags', ["tech"])),
        slug_name=semana_slug,
        introduccion=introduccion,
        bloque_noticias=bloque_noticias,
        repo_name=data_ia.get('repo', {}).get('nombre', 'Tool'),
        repo_url=data_ia.get('repo', {}).get('url', '#'),
        repo_desc=data_ia.get('repo', {}).get('desc', ''),
        conclusion_tldr=data_ia.get('tldr', ''),
        nota_personal=data_ia.get('nota_personal', 'Keep coding!')
    )
    
    with open(f"./auto-news/{semana_slug}.md", "w", encoding="utf-8") as f:
        f.write(final_md)
    
    # Devolvemos la introducción para usarla como "resumen" en el Dashboard
    return introduccion


def generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia):
    v_html, n_html = "", ""
    canales_vistos = []
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    # Establecer locale ANTES del conteo para que las claves coincidan con los labels
    try: locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        try: locale.setlocale(locale.LC_TIME, "es_ES.utf8")
        except: pass
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
    # locale ya establecido arriba

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
            <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_limpia}" style="aspect-ratio: 16/9; contain: layout style;">
                {badge_live}
                {btn_download}
                <a href="{n_item['enlace']}" target="_blank">
                    <img src="https://img.youtube.com/vi/{n_item['id_video']}/mqdefault.jpg" 
                         alt="{n_item['titulo']}" 
                         width="320" height="180" 
                         loading="lazy" 
                         style="width:100%; height:auto; aspect-ratio: 16/9; background: #eee;">
                </a>
                <div class="card-content"><div class="meta">{meta}</div><a href="{n_item['enlace']}" target="_blank">{n_item['titulo']}</a></div>
            </div>"""
        else:
            badge_class = "badge-beca" if n_item.get('badge') == "Beca" else "badge-tech"
            n_html += f'<li class="news-item" data-ts="{ts}" data-fuente="{fuente_limpia}"><div class="meta">{meta}</div><span class="badge {badge_class}">{n_item.get("badge", "Tech")}</span><a href="{n_item["enlace"]}" target="_blank">{n_item["titulo"]}</a></li>'

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
    logger.info("✅ Dashboard HTML generado con Chips y Vídeos.")

async def publicar_contenidos(historial, noticias_web, scr):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

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
        temas_clave=temas_clave,
        year=datetime.now().year
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
            logger.info(f"📧 Email enviado con éxito: {asunto}")
    except Exception as e:
        logger.error(f"⚠️ Fallo en el envío de email: {e}")


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
            logger.warning(f"⚠️ Reintentando envío sin Markdown por error: {r.text}")
            payload.pop("parse_mode")
            # Limpiamos el caption de caracteres de escape para texto plano
            payload["caption"] = caption.replace("\\_", "_").replace("\\*", "*")
            with open(audio_path, "rb") as audio_file:
                files = {'voice': (audio_path, audio_file, 'audio/mpeg')}
                r = requests.post(url, data=payload, files=files)
        # Limpieza: Borramos el archivo temporal
        if os.path.exists(audio_path): os.remove(audio_path)
        
        if r.status_code == 200: logger.info("✅ Telegram con voz humana enviado")
        else: logger.error(f"❌ Error Telegram: {r.text}")

    except Exception as e:
        logger.error(f"⚠️ Error en TTS Humano: {e}")



# --- FUNCIONALIDAD LINK CHECKER ---
async def main():
    scr = ScraperPro()
    
    # --- SCRAPING ASÍNCRONO ---
    async with aiohttp.ClientSession() as session:
        tasks = [scr.extraer(session, n, info) for n, info in FUENTES.items()]
        paginas_datos = await asyncio.gather(*tasks)
    
    datos = [item for sublist in paginas_datos for item in sublist]

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos if n['enlace'] not in vistos]
    total = nuevos + historial

    scr.guardar_avatars()
    noticias_web = filtrar_solo_noticias(nuevos)

    await publicar_contenidos(total, noticias_web, scr)

    if noticias_web:
        total = noticias_web + historial
        with open(archivo_h, 'w', encoding='utf-8') as f: 
            json.dump(total[:600], f, indent=4, ensure_ascii=False)
        logger.info(f"✅ {len(noticias_web)} noticias nuevas procesadas.")
    else:
        logger.info("☕ Sin cambios hoy.")

if __name__ == "__main__":
    asyncio.run(main())
