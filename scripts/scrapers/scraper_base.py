#!/usr/bin/env python3
"""
scraper_base.py — Clases base de extracción compartidas entre todos los scrapers.
YouTubeExtractor, WebExtractor, ScraperPro, AvatarRepository, ContentFilter.
"""
import hashlib
import html
import json
import logging
import os
import re
from datetime import datetime
from urllib.parse import urljoin

import aiohttp
import requests
from bs4 import BeautifulSoup

from scripts.utils.constants_downloadfile import ALL_KEYWORDS, CATEGORIAS, CONFIG, clasificar_noticia, YT_KEY, RSS_KEY, URL_KEY, TIPO_KEY, SUBTIPO_KEY, SELECTOR_KEY, ORIGEN_KEY, BADGE_KEY, TIPO_VAL_HERRAMIENTA, TIPO_VAL_NOTICIA, TIPO_VAL_VIDEO, TIPO_VAL_SHORTS, TIPO_VAL_LIVE, SUB_VAL_GITHUB, SUB_VAL_GITHUB_TOPIC, SUB_VAL_GITHUB_COLLECTION, SUB_VAL_PRODUCTHUNT, VAL_RSS, VAL_TECH, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, CATEGORIA_KEY, ESTRELLAS_KEY, DESCRIPCION_KEY, LENGUAJE_KEY, REPO_KEY, TS_KEY, F_KEY, FECHA_REAL_KEY, FECHA_PUB_KEY, ID_VIDEO_KEY, IMAGEN_URL_KEY
from xml.etree import ElementTree

logger = logging.getLogger("scraper_base")


class ContentFilter:
    @staticmethod
    def es_fecha_valida(fecha_relativa: str) -> bool:
        return not any(x in fecha_relativa.lower() for x in ["año", "year", "mes", "month"])

    @staticmethod
    def coincide_con_keywords(titulo: str) -> bool:
        t_low = titulo.lower()
        return any(key.lower() in t_low for key in ALL_KEYWORDS)

    @staticmethod
    def es_reto(titulo: str) -> bool:
        return any(k in titulo.lower() for k in ["reto", "challenge", "desafío"])


class AvatarRepository:
    def __init__(self, cache_path: str):
        self.cache_file = cache_path
        self.avatars = self._cargar_avatars()
        self.cambios_en_cache = False

    def _cargar_avatars(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def guardar_si_cambio(self):
        if self.cambios_en_cache:
            with open(self.cache_file, "w") as f:
                json.dump(self.avatars, f, indent=4, ensure_ascii=False)
            logger.info("💾 Caché de avatares actualizada.")

    def obtener_avatar(self, nombre: str, url_canal: str) -> str:
        if nombre in self.avatars:
            return self.avatars[nombre]
        try:
            logger.info(f"🔍 Buscando avatar real para: {nombre}...")
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                url_avatar = meta_img["content"]
                self.avatars[nombre] = url_avatar
                self.cambios_en_cache = True
                return url_avatar
        except Exception:
            pass
        return f"https://ui-avatars.com/api/?name={nombre}&background=random"


class BaseExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Cookie": "SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjYwNTI1LjA5X3AwGgJlcyACGgYIgMXT0AY; PREF=tz=Europe.Madrid",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def generar_item_base(self, titulo: str, enlace: str, fuente: str, tipo: str, fecha_relativa: str = "") -> dict:
        return {
            TITULO_KEY: html.unescape(titulo),
            ENLACE_KEY: enlace,
            FUENTE_KEY: fuente,
            TIPO_KEY: tipo,
            F_KEY: datetime.now().strftime("%d/%m"),
            FECHA_PUB_KEY: fecha_relativa,
        }

    def enriquecer_fechas(self, item: dict) -> dict:
        item.update({
            FECHA_REAL_KEY: datetime.now().strftime("%d/%m/%Y"),
            TS_KEY: datetime.now().isoformat(),
        })
        if CATEGORIA_KEY not in item:
            item[CATEGORIA_KEY] = clasificar_noticia(item.get(TITULO_KEY, ""))
        return item


class YouTubeExtractor(BaseExtractor):
    def extraer_desde_json(self, data: dict, nombre: str, target: str) -> list:
        results = []
        tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
        video_list = []
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            if "richGridRenderer" in tab_content:
                video_list = tab_content["richGridRenderer"].get("contents", [])
                break
            elif "sectionListRenderer" in tab_content:
                sections = tab_content["sectionListRenderer"].get("contents", [])
                for section in sections:
                    item_section = section.get("itemSectionRenderer", {}).get("contents", [])
                    for item in item_section:
                        if "gridRenderer" in item:
                            video_list = item["gridRenderer"].get("items", [])
                            break
                    if video_list:
                        break
                if video_list:
                    break

        logger.info(f"🛠️ Analizando {len(video_list)} elementos para {nombre}...")
        for item in video_list[:10]:
            lockup = item.get("richItemRenderer", {}).get("content", {}).get("lockupViewModel", {})
            if lockup:
                video_id = lockup.get("contentId")
                metadata = lockup.get("metadata", {}).get("lockupMetadataViewModel", {})
                titulo_limpio = metadata.get("title", {}).get("content", "")
                fecha_relativa = (
                    metadata.get("videoMetadataRenderer", {}).get("publishedTimeText", {}).get("simpleText", "Reciente")
                )
                if not ContentFilter.es_fecha_valida(fecha_relativa):
                    continue
                if video_id and titulo_limpio:
                    res_item = self.generar_item_base(
                        titulo_limpio, f"https://www.youtube.com/watch?v={video_id}", nombre, TIPO_VAL_VIDEO, fecha_relativa
                    )
                    res_item[ID_VIDEO_KEY] = video_id
                    results.append(self.enriquecer_fechas(res_item))
                continue

            s_lockup = item.get("richItemRenderer", {}).get("content", {}).get("shortsLockupViewModel", {})
            if s_lockup:
                video_id = (
                    s_lockup.get("onTap", {}).get("innertubeCommand", {}).get("reelWatchEndpoint", {}).get("videoId")
                )
                titulo_limpio = s_lockup.get("overlayMetadata", {}).get("primaryText", {}).get("content", "")
                if video_id and titulo_limpio:
                    res_item = self.generar_item_base(
                        titulo_limpio, f"https://www.youtube.com/watch?v={video_id}", nombre, TIPO_VAL_SHORTS, ""
                    )
                    res_item[ID_VIDEO_KEY] = video_id
                    results.append(self.enriquecer_fechas(res_item))
                continue

            v_data = item.get("richItemRenderer", {}).get("content", {}).get("videoRenderer", {})
            if not v_data:
                v_data = item.get("richItemRenderer", {}).get("content", {}).get("reelItemRenderer", {})
            if not v_data:
                continue

            titulo_sucio = ""
            if "title" in v_data:
                if "runs" in v_data["title"]:
                    titulo_sucio = v_data["title"]["runs"][0].get("text", "")
                elif "simpleText" in v_data["title"]:
                    titulo_sucio = v_data["title"]["simpleText"]
            elif "headline" in v_data:
                titulo_sucio = v_data["headline"].get("simpleText", "")
            titulo_limpio = html.unescape(titulo_sucio)
            if not titulo_limpio:
                continue

            badges = v_data.get("badges", [])
            es_live = any(
                b.get("metadataBadgeRenderer", {}).get("style") == "BADGE_STYLE_TYPE_LIVE_NOW" for b in badges
            )
            published_text = v_data.get("publishedTimeText", {}).get("simpleText", "").lower()
            if "emitido" in published_text or "streaming" in published_text or "directo" in published_text:
                es_live = True

            video_id = v_data.get("videoId")
            if not video_id:
                continue

            fecha_relativa = v_data.get("publishedTimeText", {}).get("simpleText", "Reciente")
            if not ContentFilter.es_fecha_valida(fecha_relativa):
                continue

            es_short = "shorts" in target.lower() or "/shorts/" in video_id or "reelItemRenderer" in str(item)
            res_item = self.generar_item_base(
                titulo_limpio,
                f"https://www.youtube.com/watch?v={video_id}",
                nombre,
                TIPO_VAL_SHORTS if es_short else (TIPO_VAL_LIVE if es_live else TIPO_VAL_VIDEO),
                fecha_relativa,
            )
            res_item[ID_VIDEO_KEY] = video_id
            results.append(self.enriquecer_fechas(res_item))

        return results

    def ejecutar_fallback(self, html_text: str, nombre: str) -> list:
        results = []
        logger.warning(f"⚠️ No se obtuvieron resultados vía JSON para {nombre}. Intentando fallback con Regex...")
        ids = list(dict.fromkeys(re.findall(r'"videoId":"(.*?)"', html_text)))
        titles = re.findall(
            r'{"videoRenderer":{"videoId":".*?","thumbnail":.*?,"title":{"runs":\[{"text":"(.*?)"}\]', html_text
        )
        for t, i in zip(titles[:5], ids[:5]):
            results.append(self.generar_item_base(t, f"https://www.youtube.com/watch?v={i}", nombre, TIPO_VAL_VIDEO))
        return results


class WebExtractor(BaseExtractor):
    def extraer_noticias(self, html_text: str, nombre: str, target: str, info: dict) -> list:
        results = []
        soup = BeautifulSoup(html_text, "html.parser")
        selector = info.get(SELECTOR_KEY, "article h2 a, h3 a, h2 a, .post-title a")
        items = soup.select(selector)[:10]

        for i in items:
            enlace = urljoin(target, i.get("href", ""))
            if not enlace or len(enlace) < 10:
                continue
            t_raw = i.get_text(strip=True)
            is_english = any(x in target for x in ["wired", "verge", "techcrunch", "github", "openai"])
            if ContentFilter.coincide_con_keywords(t_raw) or is_english:
                img_url = ""
                parent = i.find_parent(["article", "div", "section"])
                if parent:
                    img_tag = parent.find("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("srcset", "").split(" ")[0]
                fecha_pub = ""
                if parent:
                    time_tag = parent.find("time")
                    if time_tag and time_tag.get("datetime"):
                        fecha_pub = time_tag["datetime"]
                    elif time_tag:
                        fecha_pub = time_tag.get_text(strip=True)
                    if not fecha_pub:
                        meta_date = soup.find("meta", property="article:published_time")
                        if meta_date:
                            fecha_pub = meta_date["content"]
                item = self.generar_item_base(t_raw, enlace, nombre, TIPO_VAL_NOTICIA, fecha_pub)
                item.update({
                    BADGE_KEY: VAL_TECH,
                    CATEGORIA_KEY: clasificar_noticia(t_raw),
                    IMAGEN_URL_KEY: urljoin(target, img_url) if img_url else "",
                })
                results.append(self.enriquecer_fechas(item))
        return results

    def extraer_rss(self, xml_text: str, nombre: str) -> list:
        results = []
        try:
            root = ElementTree.fromstring(xml_text)
            ns = {"content": "http://purl.org/rss/1.0/modules/content/",
                  "dc": "http://purl.org/dc/elements/1.1/",
                  "atom": "http://www.w3.org/2005/Atom",
                  "media": "http://search.yahoo.com/mrss/"}
            channel = root.find("channel")
            items_xml = channel.findall("item") if channel is not None else []
            if not items_xml:
                items_xml = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                for entry in items_xml[:12]:
                    titulo = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    enlace = link_el.get("href") if link_el is not None else ""
                    fecha = entry.findtext("{http://www.w3.org/2005/Atom}published", "") or entry.findtext("{http://www.w3.org/2005/Atom}updated", "")
                    if titulo and enlace:
                        item = self.generar_item_base(titulo, enlace, nombre, TIPO_VAL_NOTICIA, fecha)
                        item.update({
                            BADGE_KEY: VAL_TECH,
                            CATEGORIA_KEY: clasificar_noticia(titulo),
                            ORIGEN_KEY: VAL_RSS,
                        })
                        results.append(self.enriquecer_fechas(item))
                return results
            for i in items_xml[:12]:
                titulo = i.findtext("title", "")
                enlace = i.findtext("link", "")
                fecha = i.findtext("pubDate", "") or i.findtext("dc:date", "", ns)
                if titulo and enlace:
                    item = self.generar_item_base(titulo, enlace, nombre, TIPO_VAL_NOTICIA, fecha)
                    item.update({
                        BADGE_KEY: VAL_TECH,
                        CATEGORIA_KEY: clasificar_noticia(titulo),
                        ORIGEN_KEY: VAL_RSS,
                    })
                    results.append(self.enriquecer_fechas(item))
        except Exception as e:
            logger.debug(f"⚠️ Error parseando RSS {nombre}: {e}")
        return results

    def extraer_herramientas(self, html_text: str, nombre: str, target: str, info: dict) -> list:
        results = []
        soup = BeautifulSoup(html_text, "html.parser")
        subtipo = info.get(SUBTIPO_KEY, "")

        if subtipo == SUB_VAL_GITHUB:
            articles = soup.select("article.Box-row") or soup.select('[class*="Box-row"]')
            for article in articles[:15]:
                h2_a = article.select_one("h2 a")
                if not h2_a:
                    continue
                href = h2_a.get("href", "")
                full_url = urljoin("https://github.com", href)
                raw_title = h2_a.get_text(strip=True)
                desc_p = article.select_one("p")
                desc = desc_p.get_text(strip=True) if desc_p else ""
                lang_span = article.select_one('span[itemprop="programmingLanguage"]')
                lang = lang_span.get_text(strip=True) if lang_span else ""
                stars_a = article.select_one('a[href*="/stargazers"]')
                stars = stars_a.get_text(strip=True) if stars_a else "0"
                stars = stars.replace("★", "").replace("☆", "").replace(",", "").strip()
                title = raw_title if raw_title else href.strip("/").split("/")[-1]
                item = self.generar_item_base(title, full_url, nombre, TIPO_VAL_HERRAMIENTA)
                item.update({
                    SUBTIPO_KEY: subtipo,
                    DESCRIPCION_KEY: desc.strip(),
                    LENGUAJE_KEY: lang.strip(),
                    ESTRELLAS_KEY: stars.strip(),
                    REPO_KEY: href.strip("/") if href else "",
                })
                results.append(self.enriquecer_fechas(item))

        elif subtipo == SUB_VAL_PRODUCTHUNT:
            next_data = soup.find("script", id="__NEXT_DATA__")
            if next_data and next_data.string:
                try:
                    data = json.loads(next_data.string)
                    posts = data.get("props", {}).get("pageProps", {}).get("posts", [])
                    for post in posts[:10]:
                        name = post.get("name", "")
                        slug = post.get("slug", "")
                        tagline = post.get("tagline", "")
                        if not name or not slug:
                            continue
                        item = self.generar_item_base(name, f"https://www.producthunt.com/posts/{slug}", nombre, TIPO_VAL_HERRAMIENTA)
                        item.update({SUBTIPO_KEY: subtipo, DESCRIPCION_KEY: tagline})
                        results.append(self.enriquecer_fechas(item))
                except (json.JSONDecodeError, AttributeError, TypeError):
                    pass
            if not results:
                for a in soup.select('a[href*="/posts/"]')[:10]:
                    href = a.get("href", "")
                    title = a.get_text(strip=True)
                    if not href or not title:
                        continue
                    full_url = urljoin("https://www.producthunt.com", href)
                    item = self.generar_item_base(title, full_url, nombre, TIPO_VAL_HERRAMIENTA)
                    item.update({SUBTIPO_KEY: subtipo})
                    results.append(self.enriquecer_fechas(item))

        elif subtipo in (SUB_VAL_GITHUB_TOPIC, SUB_VAL_GITHUB_COLLECTION):
            cards = soup.select("article.border.rounded-1") or soup.select('[class*="border rounded"]')
            for card in cards[:20]:
                h3 = card.select_one("h3")
                a = h3.select_one("a") if h3 else card.select_one("a[href*='/']")
                if not a:
                    continue
                href = a.get("href", "")
                if not href or "/" not in href.strip("/"):
                    continue
                full_url = urljoin("https://github.com", href)
                raw_title = a.get_text(strip=True)
                desc_p = card.select_one("div > p") or card.select_one("p")
                desc = desc_p.get_text(strip=True) if desc_p else ""
                lang_span = card.select_one('span[itemprop="programmingLanguage"]')
                lang = lang_span.get_text(strip=True) if lang_span else ""
                stars_a = card.select_one('a[href*="stargazers"]')
                stars_raw = stars_a.get_text(strip=True) if stars_a else "0"
                stars = stars_raw.replace("★", "").replace("☆", "").replace(",", "").strip()
                title = raw_title if raw_title else href.strip("/").split("/")[-1]
                item = self.generar_item_base(title, full_url, nombre, TIPO_VAL_HERRAMIENTA)
                item.update({
                    SUBTIPO_KEY: SUB_VAL_GITHUB,
                    DESCRIPCION_KEY: desc.strip(),
                    LENGUAJE_KEY: lang.strip(),
                    ESTRELLAS_KEY: stars.strip(),
                    REPO_KEY: href.strip("/") if href else "",
                })
                results.append(self.enriquecer_fechas(item))

        return results


class ScraperPro:
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
        target = info.get(YT_KEY) or info.get(URL_KEY) or info.get(RSS_KEY)
        results = []
        es_rss = RSS_KEY in info
        try:
            async with session.get(target, timeout=20, headers=self.yt_extractor.headers) as response:
                if response.status != 200:
                    return []
                text = await response.text()
            if es_rss:
                logger.info(f"📡 Extrayendo RSS desde: {nombre} ({target})")
                results = self.web_extractor.extraer_rss(text, nombre)
            elif YT_KEY in info:
                logger.info(f"📺 Procesando fuente de YouTube: {nombre} ({target})")
                json_data = re.search(r"ytInitialData\s*=\s*(\{.*?\});", text)
                if not json_data:
                    json_data = re.search(r'window\[["\']ytInitialData["\']\]\s*=\s*(\{.*?\});', text)
                if not json_data:
                    json_data = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.*?\});", text)
                if json_data:
                    logger.info(f"✅ JSON de YouTube encontrado para {nombre}.")
                    try:
                        data = json.loads(json_data.group(1))
                        results = self.yt_extractor.extraer_desde_json(data, nombre, target)
                    except Exception as e:
                        logger.error(f"⚠️ Error procesando JSON de YT ({nombre}): {e}", exc_info=True)
                if not results:
                    results = self.yt_extractor.ejecutar_fallback(text, nombre)
            elif info.get(TIPO_KEY) == TIPO_VAL_HERRAMIENTA:
                logger.info(f"🔧 Extrayendo herramientas desde: {nombre}")
                results = self.web_extractor.extraer_herramientas(text, nombre, target, info)
            else:
                results = self.web_extractor.extraer_noticias(text, nombre, target, info)
        except Exception as e:
            print(f"❌ Error en fuente {nombre}: {e}")
        return results
