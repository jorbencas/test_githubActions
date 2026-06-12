import hashlib
import locale
import inspect
import os, json, re, requests, asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
from google import genai
import edge_tts
from constants_downloadfile import FUENTES, CONFIG, HTML_TEMPLATE, EMAIL_TEMPLATE, ALL_KEYWORDS, BECAS_KEYWORDS, MD_TEMPLATE, RETO_MD_TEMPLATE, URL_API_DESCARGA, URL_API_SALUD
from utils import obtener_solucion_ia, generar_imagen_noticia, obtener_recap_semanal_ia, traducir_titulos_ia
from slugify import slugify 
import html
import aiohttp
import html2text
import logging
from logging.handlers import RotatingFileHandler

# =====================================================================
# 4. CAPA DE INFRAESTRUCTURA (FRAMEWORKS & DRIVERS)
# =====================================================================

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

# Auto-añadir secciones de Shorts alternativos
for nombre in list(FUENTES): 
    if "yt" in FUENTES[nombre]:
        url_s = FUENTES[nombre]["yt"].replace("/videos", "/shorts")
        FUENTES[f"{nombre} Shorts"] = {"yt": url_s}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)
os.makedirs("./auto-news", exist_ok=True)


# =====================================================================
# 1. CAPA DE DOMINIO (CORE BUSINESS LOGIC & ENTITIES)
# =====================================================================

class ContentFilter:
    """Reglas de negocio puras para filtrado y clasificación de contenido."""
    
    @staticmethod
    def es_fecha_valida(fecha_relativa: str) -> bool:
        return not any(x in fecha_relativa.lower() for x in ["año", "year", "mes", "month"])

    @staticmethod
    def coincide_con_keywords(titulo: str) -> bool:
        t_low = titulo.lower()
        return any(key.lower() in t_low for key in ALL_KEYWORDS)

    @staticmethod
    def es_beca(titulo: str) -> bool:
        return any(k in titulo.lower() for k in BECAS_KEYWORDS)

    @staticmethod
    def es_reto(titulo: str) -> bool:
        return any(k in titulo.lower() for k in ["reto", "challenge", "desafío"])


# =====================================================================
# 3. CAPA DE INTERFACE ADAPTERS (REPOSITORIES & DATA SOURCES)
# =====================================================================

class AvatarRepository:
    """Encargado de la persistencia y recuperación de los avatares en cache."""
    
    def __init__(self, cache_path: str):
        self.cache_file = cache_path
        self.avatars = self._cargar_avatars()
        self.cambios_en_cache = False

    def _cargar_avatars(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except: 
                return {}
        return {}

    def guardar_si_cambio(self):
        if self.cambios_en_cache:
            with open(self.cache_file, 'w') as f: 
                json.dump(self.avatars, f, indent=4, ensure_ascii=False)
            logger.info("💾 Caché de avatares actualizada.")

    def obtener_avatar(self, nombre: str, url_canal: str) -> str:
        if nombre in self.avatars: 
            return self.avatars[nombre]
        
        try:
            logger.info(f"🔍 Buscando avatar real para: {nombre}...")
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                url_avatar = meta_img['content']
                self.avatars[nombre] = url_avatar
                self.cambios_en_cache = True 
                return url_avatar
        except: 
            pass
        
        return f"https://ui-avatars.com/api/?name={nombre}&background=random"


class BaseExtractor:
    """Estructura base compartida para los extractores de datos."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cookie': 'SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjYwNTI1LjA5X3AwGgJlcyACGgYIgMXT0AY; PREF=tz=Europe.Madrid',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    def generar_item_base(self, titulo: str, enlace: str, fuente: str, tipo: str) -> dict:
        return {
            "titulo": html.unescape(titulo),
            "enlace": enlace,
            "fuente": fuente,
            "tipo": tipo,
            "f": datetime.now().strftime("%d/%m")
        }

    def enriquecer_fechas(self, item: dict) -> dict:
        item.update({
            "fecha_real": datetime.now().strftime("%d/%m/%Y"),
            "ts": datetime.now().isoformat()
        })
        return item


class YouTubeExtractor(BaseExtractor):
    """Adaptador especializado en la extracción y parsing de contenido de YouTube."""

    def extraer_desde_json(self, data: dict, nombre: str, target: str) -> list:
        results = []
        tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        video_list = []
        for tab in tabs:
            tab_content = tab.get('tabRenderer', {}).get('content', {})
            if 'richGridRenderer' in tab_content:
                video_list = tab_content['richGridRenderer'].get('contents', [])
                break
            elif 'sectionListRenderer' in tab_content:
                sections = tab_content['sectionListRenderer'].get('contents', [])
                for section in sections:
                    item_section = section.get('itemSectionRenderer', {}).get('contents', [])
                    for item in item_section:
                        if 'gridRenderer' in item:
                            video_list = item['gridRenderer'].get('items', [])
                            break
                if video_list: break

        logger.info(f"🛠️ Analizando {len(video_list)} elementos para {nombre}...")
        for item in video_list[:10]:
            lockup = item.get('richItemRenderer', {}).get('content', {}).get('lockupViewModel', {})
            if lockup:
                video_id = lockup.get('contentId')
                metadata = lockup.get('metadata', {}).get('lockupMetadataViewModel', {})
                titulo_limpio = metadata.get('title', {}).get('content', '')
                fecha_relativa = metadata.get('videoMetadataRenderer', {}).get('publishedTimeText', {}).get('simpleText', 'Reciente')
                
                if not ContentFilter.es_fecha_valida(fecha_relativa):
                    continue

                if video_id and titulo_limpio:
                    res_item = self.generar_item_base(titulo_limpio, f"https://www.youtube.com/watch?v={video_id}", nombre, "video")
                    res_item["id_video"] = video_id
                    results.append(self.enriquecer_fechas(res_item))
                continue

            s_lockup = item.get('richItemRenderer', {}).get('content', {}).get('shortsLockupViewModel', {})
            if s_lockup:
                video_id = s_lockup.get('onTap', {}).get('innertubeCommand', {}).get('reelWatchEndpoint', {}).get('videoId')
                titulo_limpio = s_lockup.get('overlayMetadata', {}).get('primaryText', {}).get('content', '')
                
                if video_id and titulo_limpio:
                    res_item = self.generar_item_base(titulo_limpio, f"https://www.youtube.com/watch?v={video_id}", nombre, "shorts")
                    res_item["id_video"] = video_id
                    results.append(self.enriquecer_fechas(res_item))
                continue

            v_data = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
            if not v_data: 
                v_data = item.get('richItemRenderer', {}).get('content', {}).get('reelItemRenderer', {})
            if not v_data: 
                continue

            titulo_sucio = ""
            if 'title' in v_data:
                if 'runs' in v_data['title']:
                    titulo_sucio = v_data['title']['runs'][0].get('text', '')
                elif 'simpleText' in v_data['title']:
                    titulo_sucio = v_data['title']['simpleText']
            elif 'headline' in v_data:
                titulo_sucio = v_data['headline'].get('simpleText', '')

            titulo_limpio = html.unescape(titulo_sucio)
            if not titulo_limpio: 
                continue

            badges = v_data.get('badges', [])
            es_live = any(b.get('metadataBadgeRenderer', {}).get('style') == "BADGE_STYLE_TYPE_LIVE_NOW" for b in badges)
            published_text = v_data.get('publishedTimeText', {}).get('simpleText', '').lower()
            if "emitido" in published_text or "streaming" in published_text or "directo" in published_text:
                es_live = True

            video_id = v_data.get('videoId')
            if not video_id: 
                continue

            fecha_relativa = v_data.get('publishedTimeText', {}).get('simpleText', 'Reciente')
            if not ContentFilter.es_fecha_valida(fecha_relativa):
                continue

            es_short = "shorts" in target.lower() or "/shorts/" in video_id or "reelItemRenderer" in str(item)

            res_item = self.generar_item_base(titulo_limpio, f"https://www.youtube.com/watch?v={video_id}", nombre, "shorts" if es_short else ("live" if es_live else "video"))
            res_item["id_video"] = video_id
            results.append(self.enriquecer_fechas(res_item))
            
        return results

    def ejecutar_fallback(self, html_text: str, nombre: str) -> list:
        results = []
        logger.warning(f"⚠️ No se obtuvieron resultados vía JSON para {nombre}. Intentando fallback con Regex...")
        ids = list(dict.fromkeys(re.findall(r'"videoId":"(.*?)"', html_text)))
        titles = re.findall(r'{"videoRenderer":{"videoId":".*?","thumbnail":.*?,"title":{"runs":\[{"text":"(.*?)"}\]', html_text)
        
        for t, i in zip(titles[:5], ids[:5]):
            results.append(self.generar_item_base(t, f"https://www.youtube.com/watch?v={i}", nombre, "video"))
        return results


class WebExtractor(BaseExtractor):
    """Adaptador especializado en scraping tradicional de portales web."""

    def extraer_noticias(self, html_text: str, nombre: str, target: str, info: dict) -> list:
        results = []
        soup = BeautifulSoup(html_text, 'html.parser')
        selector = info.get("selector", 'article h2 a, h3 a, h2 a, .post-title a')
        items = soup.select(selector)[:10]

        for i in items:
            enlace = urljoin(target, i.get('href', ''))
            if not enlace or len(enlace) < 10: 
                continue

            t_raw = i.get_text(strip=True)
            is_english = any(x in target for x in ["wired", "verge", "techcrunch", "github", "openai"])

            if ContentFilter.coincide_con_keywords(t_raw) or is_english:
                img_url = ""
                parent = i.find_parent(['article', 'div', 'section'])
                if parent:
                    img_tag = parent.find('img')
                    if img_tag:
                        img_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset', '').split(' ')[0]

                item = self.generar_item_base(t_raw, enlace, nombre, "noticia")
                item.update({
                    "badge": "Beca" if ContentFilter.es_beca(t_raw) else "Tech",
                    "imagen_url_original": urljoin(target, img_url) if img_url else ""
                })
                results.append(self.enriquecer_fechas(item))
        return results


class ScraperPro:
    """Fachada (Facade) que centraliza las operaciones de scraping."""
    
    def __init__(self):
        self.avatar_repo = AvatarRepository(os.path.join(CONFIG["FOLDER"], "avatars_cache.json"))
        self.yt_extractor = YouTubeExtractor()
        self.web_extractor = WebExtractor()

    @property
    def cambios_en_cache(self):
        return self.avatar_repo.cambios_en_cache

    def cargar_avatars(self):
        return self.avatar_repo.avatars

    def guardar_avatars(self):
        self.avatar_repo.guardar_si_cambio()

    def obtener_avatar_canal(self, nombre, url_canal):
        return self.avatar_repo.obtener_avatar(nombre, url_canal)

    async def extraer(self, session, nombre, info):
        target = info.get("yt") or info.get("url")
        results = []
        try:
            async with session.get(target, timeout=20, headers=self.yt_extractor.headers) as response:
                if response.status != 200: 
                    return []
                html_text = await response.text()

            if "yt" in info:
                logger.info(f"📺 Procesando fuente de YouTube: {nombre} ({target})")
                json_data = re.search(r'ytInitialData\s*=\s*(\{.*?\});', html_text)
                if not json_data:
                    json_data = re.search(r'window\[["\']ytInitialData["\']\]\s*=\s*(\{.*?\});', html_text)
                if not json_data:
                    json_data = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\});', html_text)

                if json_data:
                    logger.info(f"✅ JSON de YouTube encontrado para {nombre}.")
                    try:
                        data = json.loads(json_data.group(1))
                        results = self.yt_extractor.extraer_desde_json(data, nombre, target)
                    except Exception as e:
                        logger.error(f"⚠️ Error procesando JSON de YT ({nombre}): {e}", exc_info=True)
                
                if not results:
                    results = self.yt_extractor.ejecutar_fallback(html_text, nombre)
            else:
                results = self.web_extractor.extraer_noticias(html_text, nombre, target, info)

        except Exception as e:
            print(f"❌ Error en fuente {nombre}: {e}")
        
        return results


# =====================================================================
# 2. CAPA DE APLICACIÓN (USE CASES & ORCHESTRATION)
# =====================================================================

async def generar_retos_individuales(noticias_web, fecha_iso, client):
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)

    for n in noticias_web:
        if ContentFilter.es_reto(n.get('titulo', 'video-sin-nombre')):
            slug_reto = f"reto-{slugify(n.get('titulo', 'video-sin-nombre'))[:40]}"
            path = f"{folder}/{slug_reto}.md"
            
            if os.path.exists(path): 
                continue

            logger.info(f"🎯 Procesando reto: {n.get('titulo', 'video-sin-nombre')}")
            lang_fav = CONFIG.get("DEFAULT_LANG", "Python")
            sol = await obtener_solucion_ia(n['titulo'], n['fuente'], client, lang=lang_fav)
            
            if sol:
                img_reto = await generar_imagen_noticia(f"Reto de programación {n['titulo']}", client)
                lang = sol.get('lenguaje', 'python').lower()
                await asyncio.sleep(3)
                try:
                    reto_md = inspect.cleandoc(RETO_MD_TEMPLATE).format(
                        titulo=n.get('titulo', 'video-sin-nombre').replace('"', "'"),
                        resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
                        fecha_pub=fecha_iso,
                        slug_name=slug_reto,
                        tags_seo=json.dumps([lang, 'retos', 'ia']),
                        ruta_imagen=img_reto,
                        descripcion_ia=sol.get('descripcion', ''),
                        dificultad=sol.get('dificultad', 'Intermedio'), 
                        paso_1=sol.get('paso1', 'Analizando...'),
                        paso_2=sol.get('paso2', 'Ejecutando...'),
                        paso_3=sol.get('paso3', 'Optimizando...'),
                        lenguaje_display=lang,
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
    soup = BeautifulSoup(html, "html.parser")
    html_limpio = str(soup)

    if to_markdown:
        md = html2text.html2text(html_limpio)
        return md.strip()

    return html_limpio.strip()


async def generar_blog_astro(noticias_web, fecha_iso, year, week, client):
    noticias_blog = [n for n in noticias_web if "yout" not in n['enlace']]
    if not noticias_blog: 
        return None

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    path_md = f"./auto-news/{semana_slug}.md"

    if os.path.exists(path_md) and not noticias_web:
        logger.info(f"⏭️  Recap semanal {semana_slug} ya existe. Saltando generación IA.")
        with open(path_md, "r", encoding="utf-8") as f:
            match = re.search(r'description: "(.*?)"', f.read())
            return match.group(1) if match else "Recap semanal disponible."

    data_ia = await obtener_recap_semanal_ia(noticias_blog, client)
    if not data_ia: 
        return None
    img_recap = await generar_imagen_noticia(f"Recap {week}", client)
    await asyncio.sleep(3)

    introduccion = limpiar_html_para_mdx(data_ia.get('introduccion', ''), to_markdown=True)
    bloque_noticias = limpiar_html_para_mdx(data_ia.get('noticias_destacadas', ''), to_markdown=True)

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
    
    return introduccion


def generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia):
    v_html, n_html = "", ""
    canales_vistos = []
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    
    try: 
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        try: 
            locale.setlocale(locale.LC_TIME, "es_ES.utf8")
        except: 
            pass

    conteo_meses = Counter()
    for n in historial:
        try:
            dt_n = datetime.fromisoformat(n.get('ts'))
            mes_key = dt_n.strftime('%B %Y').capitalize()
            conteo_meses[mes_key] += 1
        except: 
            continue

    bloque_semanas = '<div class="chip active" data-inicio="all_recent" onclick="filtrarSemana(this)">🔄 Últimas 2 Semanas</div>'
    selector_html = '<select id="selectorSemanas" onchange="filtrarDesdeSelector(this)" style="padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
    selector_html += '<option value="all">📅 Archivo Histórico...</option>'

    mes_actual = ""
    for i in range(26):
        inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=6, hours=23, minutes=59, seconds=59)
        nombre_mes = inicio.strftime('%B %Y').capitalize()
        
        if nombre_mes != mes_actual:
            if mes_actual != "": 
                selector_html += '</optgroup>'
            total_mes = conteo_meses.get(nombre_mes, 0)
            selector_html += f'<optgroup label="── {nombre_mes} ({total_mes} ítems) ──">'
            mes_actual = nombre_mes
        
        txt_semana = f"Semana {inicio.strftime('%d/%m/%y')}"
        val_ini = inicio.isoformat()
        val_fin = fin.isoformat()
        
        selector_html += f'<option value="{val_ini}|{val_fin}">{txt_semana}</option>'
    
    selector_html += '</optgroup></select>'
    bloque_semanas_completo = f'<div class="filter-group" style="display:flex; align-items:center; flex-wrap:wrap; gap:10px;">{bloque_semanas} {selector_html}</div>'

    chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
    chips_html += '<div class="chip active" data-filtro="\'all\'" onclick="filtrarCanal(\'all\', this)"><span>Todos</span></div>'
    
    for n_item in historial[:200]:
        fuente_limpia = n_item['fuente'].replace(" Shorts", "")
        ts = n_item.get('ts', ahora.isoformat())
        fecha_display = n_item.get('fecha_real', n_item.get('f', 'S/D'))
        meta = f"{n_item['fuente']} | {fecha_display}"

        if fuente_limpia not in canales_vistos:
            url_c = next((info.get('yt') for name, info in FUENTES.items() if name.startswith(fuente_limpia) and info.get('yt')), None)
            if url_c:
                img_avatar = scr.obtener_avatar_canal(fuente_limpia, url_c)
                chips_html += f'<div class="chip" data-filtro="{fuente_limpia}" onclick="filtrarCanal(\'{fuente_limpia}\', this)"><img class="chip-img" src="{img_avatar}"><span class="chip-text">{fuente_limpia}</span></div>'
                canales_vistos.append(fuente_limpia)

        if n_item.get('id_video'):            
            tipo = n_item.get('tipo', 'video')
            es_live = n_item.get('is_live', False) or tipo == "live"
            clase = "tipo-live" if es_live else ("tipo-shorts" if n_item.get('tipo') == "shorts" else "tipo-video")
            badge_live = '<span class="badge-live">● EN DIRECTO</span>' if es_live else ""
            # Corrección exacta del botón dentro de generar_dashboard_html
            btn_download = f"""<button onclick="descargarVideo('{n_item.get('enlace')}', this)" target="_blank" class="btn-download">📥</button>"""
            
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
    token_oculto = hashlib.sha256(semilla.encode()).hexdigest()

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(
            fecha_hoy=fecha_h, 
            resumen=resumen_ia, 
            bloque_chips=chips_html, 
            bloque_videos=v_html, 
            bloque_noticias=n_html,
            bloque_semanas=bloque_semanas_completo, 
            api_token=token_oculto, api_url=URL_API_DESCARGA, api_salud=URL_API_SALUD
        ))
    logger.info("✅ Dashboard HTML generado con Chips y Vídeos.")


def enviar_email_reporte(resumen_html, nuevos):
    """Genera y envía el reporte por email con diseño curado estilo newsletter."""
    if not CONFIG["MAIL_KEY"] or not nuevos:
        return
        
    c_tech = len([x for x in nuevos if x.get('badge') == 'Tech'])
    c_becas = len([x for x in nuevos if x.get('badge') == 'Beca'])
    c_vids = len([x for x in nuevos if x.get('id_video')])
    
    filas_noticias = ""
    for n in nuevos[:15]:  
        icon = "📺" if n.get('id_video') else ("🎓" if n.get('badge') == "Beca" else "💻")
        
        filas_noticias += f"""
        <tr>
            <td style="padding: 16px 0; border-bottom: 1px solid #f1f5f9;">
                <span style="font-size: 18px; margin-right: 8px; vertical-align: middle;">{icon}</span>
                <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; vertical-align: middle;">{n['fuente']}</span><br>
                <div style="margin-top: 4px;">
                    <a href="{n['enlace']}" target="_blank" style="color: #4f46e5; text-decoration: none; font-weight: 600; font-size: 15px; line-height: 1.4;">{n['titulo']}</a>
                </div>
            </td>
        </tr>
        """

    top_titular = nuevos[0]['titulo']
    asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"
    temas_clave = ", ".join(list(set([n['fuente'] for n in nuevos[:3]])))

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

    try:
        url_mailgun = f"https://api.mailgun.net/v3/{CONFIG.get('MAIL_DOMAIN')}/messages"
        auth_mailgun = ("api", CONFIG["MAIL_KEY"])
        data_mailgun = {
            "from": f"Tech Pulse <mailgun@{CONFIG.get('MAIL_DOMAIN')}>",
            "to": [CONFIG.get("EMAIL_TO")],
            "subject": asunto,
            "html": html_final
        }
        r = requests.post(url_mailgun, auth=auth_mailgun, data=data_mailgun, timeout=15)
        if r.status_code == 200:
            logger.info("📩 Newsletter enviado exitosamente.")
        else:
            logger.error(f"❌ Error Mailgun API ({r.status_code}): {r.text}")
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")


async def enviar_telegram_con_audio(resumen, nuevos):
    """Envía el resumen vía Telegram y opcionalmente un audio generado por TTS."""
    if not CONFIG["TELEGRAM_TOKEN"] or not CONFIG["TELEGRAM_CHAT_ID"]:
        return

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
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendVoice"

        with open(audio_path, "rb") as audio_file:
            files = {'voice': (audio_path, audio_file, 'audio/mpeg')}
            payload = {
                "chat_id": CONFIG["TELEGRAM_CHAT_ID"], 
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


async def publicar_contenidos(historial, noticias_web, scr):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

    resumen_ia = await generar_blog_astro(noticias_web, fecha_iso, year, week, client)

    if not resumen_ia or "no ha sido posible" in resumen_ia or len(resumen_ia) < 50:
        logger.warning("⚠️ Generando resumen de emergencia con titulares.")
        titulares = [f"• {n['titulo']}" for n in noticias_web[:10]]
        resumen_ia = "Resumen de hoy:\n\n" + "\n".join(titulares)

    await generar_retos_individuales(noticias_web, fecha_iso, client)

    generar_dashboard_html(historial, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.")

    enviar_email_reporte(resumen_ia, noticias_web)
    await enviar_telegram_con_audio(resumen_ia, noticias_web)


# =====================================================================
# FUNCTION PRINCIPAL (ORQUESTADOR DE FLUJO ASÍNCRONO)
# =====================================================================

async def main():
    logger.info("🚀 Iniciando Scraper de Actualización Tecnológica Avanzado...")
    scr = ScraperPro()
    
    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = []
    if os.path.exists(path_json):
        try:
            with open(path_json, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        except Exception as e:
            logger.error(f"❌ Error cargando histórico base: {e}")

    # Semáforo para limitar la concurrencia en descargas a un máximo de 5 peticiones simultáneas
    sem = asyncio.Semaphore(5)
    
    async def con_semaforo(session, nombre, info):
        async with sem:
            # Retraso prudencial variable para no saturar servidores
            await asyncio.sleep(1)
            return await scr.extraer(session, nombre, info)

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tareas = [con_semaforo(session, nombre, info) for nombre, info in FUENTES.items()]
        resultados_agrupados = await asyncio.gather(*tareas)

    nuevos_elementos = []
    enlaces_existentes = {n.get('enlace') for n in historial}
    ids_video_existentes = {n.get('id_video') for n in historial if n.get('id_video')}

    for lista_res in resultados_agrupados:
        for item in lista_res:
            enlace = item.get('enlace')
            id_vid = item.get('id_video')
            
            # Control estricto de duplicación
            if enlace in enlaces_existentes:
                continue
            if id_vid and id_vid in ids_video_existentes:
                continue
                
            nuevos_elementos.append(item)
            enlaces_existentes.add(enlace)
            if id_vid:
                ids_video_existentes.add(id_vid)

    logger.info(f"✨ Extracción masiva terminada. Encontrados {len(nuevos_elementos)} nuevos elementos.")

    if nuevos_elementos:
        # Combinar nuevos datos respetando la persistencia histórica
        historial = nuevos_elementos + historial
        # Truncar archivo histórico para evitar ralentización del DOM en despliegue (máx 900 registros)
        historial = historial[:900]
        
        with open(path_json, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=4, ensure_ascii=False)
        logger.info("💾 Historial JSON local persistido de forma segura.")

    # Generación y distribución de entregables
    await publicar_contenidos(historial, nuevos_elementos, scr)
    
    # Consolidar caché de Avatares en disco si sufrió actualizaciones
    scr.guardar_avatars()
    logger.info("🎯 Proceso de automatización terminado correctamente.")

if __name__ == "__main__":
    asyncio.run(main())