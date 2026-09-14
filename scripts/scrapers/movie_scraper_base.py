"""
movie_scraper_base.py — Motor genérico de recopilación de noticias de películas.

Implementa todas las capacidades de scraping de scrape_eixam.py (Bing News,
YouTube, Contraste.info, Filmaffinity, fuentes directas de cine, relevancia
con señales, clasificación, envío a Telegram) de forma genérica y configurable,
siguiendo principios SOLID:

  - SRP:   Cada clase tiene una responsabilidad (RelevanceFilter, MovieClassifier,
           MovieNewsScraper, TelegramNewsSender).
  - OCP:   Se extiende pasando una MovieConfig distinta (o subclaseando
           MovieNewsScraper/RelevanceFilter) sin modificar el módulo.
  - LSP:   El contrato de ejecutar() es el mismo para cualquier config.
  - ISP:   Las interfaces son mínimas: RelevanceFilter solo filtra, Classifier
           solo clasifica, Scraper solo recopila, Sender solo envía.
  - DIP:   MovieNewsScraper depende de MovieConfig (abstracto), no de un
           módulo concreto con globals.

Uso típico:
    from movie_scraper_base import MovieConfig, MovieNewsScraper, TelegramNewsSender, ejecutar

    config = MovieConfig(pelicula="MiPeli", ...)
    scraper = MovieNewsScraper(config)
    notifier = TelegramNewsSender()   # lee env BOT_TOKEN/CHAT_ID
    ejecutar(scraper, dry_run=True, enviar=False, notifier=notifier)

Entradas concretas (scrape_eixam.py, scrape_el_nido.py) proporcionan la config.
"""
import html
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple
from urllib.parse import quote_plus

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.telegram_client import TelegramClient

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/xml,application/json,text/html,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
CHAT_ID = os.environ.get("SALUDO_CHAT_ID", os.environ.get("TIPS_CHAT_ID", ""))


# =============================================================================
# Dataclass de configuración (SRP: solo datos, sin lógica)
# =============================================================================

@dataclass
class MovieConfig:
    pelicula: str
    pelicula_es: str
    output_path: Path
    # Búsquedas
    queries: List[str]
    queries_extra: List[str] = field(default_factory=list)
    yt_queries: List[str] = field(default_factory=list)
    contraste_queries: List[str] = field(default_factory=list)
    sitios_resenias: List[Tuple[str, str]] = field(default_factory=list)
    redes_sociales: List[str] = field(default_factory=list)
    filmaffinity_queries: List[str] = field(default_factory=list)
    fuentes_cine_directas: List[dict] = field(default_factory=list)
    # Relevancia
    senales_fuertes: List[str] = field(default_factory=list)
    senales_cine: List[str] = field(default_factory=list)
    senales_negativas: List[str] = field(default_factory=list)
    anios_otros: List[str] = field(default_factory=list)
    umbral_positivas: int = 2
    titulos_clave: Tuple[str, ...] = ()
    # Clasificador
    clasificador: List[Tuple[str, List[str]]] = field(default_factory=list)
    # IA
    ia_prompt: Optional[Callable[[str], str]] = None
    ia_model: str = "gemini-2.5-flash"
    # Hook de relevancia extra (OCP): ejecutar texto,punt → None (usar umbral) |
    # True (aceptar) | False (rechazar). Por defecto sin reglas extra.
    regla_extra: Optional[Callable[[str, int], Optional[bool]]] = None
    # Filtro de contenido adulto: si se define, solo muestra noticias que contengan
    # palabras clave de esta lista (sexo, desnudez, etc.)
    filtro_adulto: List[str] = field(default_factory=list)


# =============================================================================
# SRP — RelevanceFilter: decide si un titular pertenece a la película
# =============================================================================

class RelevanceFilter:
    def __init__(self, config: MovieConfig):
        self._fuertes = config.senales_fuertes
        self._cine = config.senales_cine
        self._negativas = config.senales_negativas
        self._anios = config.anios_otros
        self._umbral = config.umbral_positivas
        self._claves = config.titulos_clave
        self._regla_extra = config.regla_extra
        self._filtro_adulto = config.filtro_adulto

    def puntuacion(self, texto: str) -> int:
        """Puntuación negativa si hay señal inequívoca de otra obra; 0-N en
        caso contrario (refuerzos fuertes + cine genéricas)."""
        texto = texto.lower()
        if any(neg in texto for neg in self._negativas):
            return -1
        puntuacion = 0
        for s in self._fuertes:
            if s in texto:
                puntuacion += 1
        for s in self._cine:
            if s in texto:
                puntuacion += 1
        return puntuacion

    def es_relevante(self, titulo: str) -> bool:
        """Devuelve True si el titular pasa todos los filtros de relevancia."""
        texto = titulo.lower()
        punt = self.puntuacion(texto)
        if punt < 0:
            return False
        # Años de otras obras homónimas (fichas de decine21, etc.)
        if any(a in texto for a in self._anios):
            return False
        # Debe aparecer el título de la película, el director u otra señal clave
        if not any(k in texto for k in self._claves):
            return False
        # Filtro de contenido adulto: si está activo, solo mostrar noticias con contenido sexual
        if self._filtro_adulto:
            if not any(palabra in texto for palabra in self._filtro_adulto):
                return False
        # Hook de reglas extra (OCP): permite subclases/configs ajustar la lógica
        # sin modificar esta función. Ej.: la regla "eixam + enjambre juntos" de Eixam.
        if self._regla_extra is not None:
            resultado = self._regla_extra(texto, punt)
            if resultado is not None:
                return resultado
        return punt >= self._umbral


# =============================================================================
# SRP — MovieClassifier: clasifica un titular por tipo de contenido
# =============================================================================

class MovieClassifier:
    def __init__(self, reglas: List[Tuple[str, List[str]]]):
        self._reglas = reglas

    def clasificar(self, texto: str) -> str:
        t = texto.lower()
        for tipo, palabras in self._reglas:
            for p in palabras:
                if p in t:
                    return tipo
        return "noticia"


# =============================================================================
# SRP — MovieNewsScraper: recopila, filtra y archiva noticias de la película
# =============================================================================

class MovieNewsScraper:
    def __init__(self, config: MovieConfig):
        self.config = config
        self._filter = RelevanceFilter(config)
        self._classifier = MovieClassifier(config.clasificador)

    # ------------------------------------------------------------------
    # URLs reales / normalización
    # ------------------------------------------------------------------
    @staticmethod
    def url_real(url: str) -> str:
        """Extrae la URL destino real de servidores de redirección (Bing apiclick)."""
        from urllib.parse import unquote
        m = re.search(r"[?&]url=", url)
        if m:
            real = unquote(url.split(m.group(0), 1)[1].split("&")[0])
            if real.startswith(("http://", "https://")):
                url = real
        m = re.search(r"https?://[^\s\"<>]+", url)
        url = m.group(0) if m else url
        if "msn.com/" in url:
            url = re.sub(r"https?://[^/]+/[a-z]{2}-[a-z]{2}/", "https://www.msn.com/", url)
            # Une variantes de categoría (other/cine/entretenimiento/noticias...) del mismo
            # contenido: conserva solo dominio + slug del artículo (vi-... o id-...).
            slug = re.search(r"/(?:vi-|id-?|AA)[A-Za-z0-9_-]+", url)
            if slug:
                url = "https://www.msn.com" + slug.group(0)
        return url

    # ------------------------------------------------------------------
    # Fetchers
    # ------------------------------------------------------------------
    @staticmethod
    def _rss_google(termino: str, ventana: str = "3h") -> list:
        url = f"https://news.google.com/rss/search?q={quote_plus(termino)}+when:{ventana}&hl=es&gl=ES&ceid=ES:es"
        items = []
        try:
            r = requests.get(url, timeout=8, headers=HEADERS)
            if r.status_code != 200 or "<html" in r.text[:500].lower():
                return []
            texto = r.text
            regex = re.compile(
                r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>.*?</item>",
                re.S,
            )
            for m in regex.finditer(texto):
                titulo = html.unescape(m.group(1)).strip()
                enlace = html.unescape(m.group(2)).strip()
                enlace = re.sub(r"^<\!\[CDATA\[|\]\]>$", "", enlace)
                fecha = m.group(3).strip()
                img_url = ""
                im = re.search(r"<img.*?src=\"(.*?)\"", m.group(0))
                if im:
                    img_url = html.unescape(im.group(1))
                items.append({
                    "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                    "medio": "Google News", "imagen": img_url,
                })
        except Exception as e:
            print(f"  ⚠️  Google RSS error ({termino}): {e}")
        return items

    @staticmethod
    def _rss_youtube(termino: str) -> list:
        """Busca vídeos en YouTube (resultados del buscador) extrayendo 'ytInitialData'
        del HTML, ya que el RSS oficial está deshabilitado (400)."""
        url = f"https://www.youtube.com/results?search_query={quote_plus(termino)}"
        items = []
        try:
            r = requests.get(url, timeout=25, headers=HEADERS)
            if r.status_code != 200:
                print(f"  ⚠️  YouTube status {r.status_code} ({termino})")
                return []
            m = re.search(r"var ytInitialData = (\{.*?\});</script>", r.text, re.S)
            if not m:
                return []
            data = json.loads(m.group(1))
            vistos = set()

            def _caminar(o):
                if isinstance(o, dict):
                    v = o.get("videoRenderer")
                    if v:
                        vid = v.get("videoId", "")
                        ti = (v.get("title", {}).get("runs", [{}])[0].get("text", "")
                              or v.get("title", {}).get("simpleText", ""))
                        canal = v.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                        if vid and vid not in vistos:
                            vistos.add(vid)
                            items.append({
                                "titulo": ti, "url": f"https://www.youtube.com/watch?v={vid}",
                                "fecha_pub": "", "fecha_ts": datetime.now().isoformat(),
                                "medio": canal or "YouTube", "imagen": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                            })
                    for val in o.values():
                        _caminar(val)
                elif isinstance(o, list):
                    for x in o:
                        _caminar(x)

            _caminar(data)
        except Exception as e:
            print(f"  ⚠️  YouTube error ({termino}): {e}")
        return items

    @staticmethod
    def _rss_contraste(termino: str) -> list:
        """Busca en Contraste.info (revista de cine) usando su feed RSS de búsqueda
        de WordPress (los directorios de reseñas a menudo salen tarde)."""
        url = f"https://contraste.info/search/{quote_plus(termino)}/feed/rss2/"
        items = []
        try:
            r = requests.get(url, timeout=20, headers=HEADERS)
            if r.status_code != 200:
                return []
            texto = r.text
            regex = re.compile(r"<item>(.*?)</item>", re.S)
            for m in regex.finditer(texto):
                item = m.group(0)
                titulo = html.unescape(re.search(r"<title>(.*?)</title>", item, re.S).group(1)).strip() if re.search(r"<title>(.*?)</title>", item, re.S) else ""
                enlace = html.unescape(re.search(r"<link>(.*?)</link>", item, re.S).group(1)).strip() if re.search(r"<link>(.*?)</link>", item, re.S) else ""
                fecha = html.unescape(re.search(r"<pubDate>(.*?)</pubDate>", item, re.S).group(1)).strip() if re.search(r"<pubDate>(.*?)</pubDate>", item, re.S) else ""
                if titulo and enlace:
                    items.append({
                        "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                        "medio": "Contraste", "imagen": "",
                    })
        except Exception as e:
            print(f"  ⚠️  Contraste error ({termino}): {e}")
        return items

    @staticmethod
    def _rss_bing(termino: str) -> list:
        url = f"https://www.bing.com/news/search?q={quote_plus(termino)}&format=rss"
        items = []
        try:
            r = requests.get(url, timeout=10, headers=HEADERS)
            if r.status_code != 200:
                return []
            texto = r.text
            regex = re.compile(r"<item>.*?</item>", re.S)
            for m in regex.finditer(texto):
                item = m.group(0)
                titulo = html.unescape(re.search(r"<title>(.*?)</title>", item, re.S).group(1)).strip() if re.search(r"<title>(.*?)</title>", item, re.S) else ""
                enlace = html.unescape(re.search(r"<link>(.*?)</link>", item, re.S).group(1)).strip() if re.search(r"<link>(.*?)</link>", item, re.S) else ""
                fecha = html.unescape(re.search(r"<pubDate>(.*?)</pubDate>", item, re.S).group(1)).strip() if re.search(r"<pubDate>(.*?)</pubDate>", item, re.S) else ""
                fuente = html.unescape(re.search(r"<News:Source>(.*?)</News:Source>", item, re.S).group(1)).strip() if re.search(r"<News:Source>(.*?)</News:Source>", item, re.S) else ""
                img_url = ""
                im = re.search(r"<News:Image.*?<News:Url>(.*?)</News:Url>", item, re.S) or re.search(r"<Image.*?<Url>(.*?)</Url>", item, re.S)
                if im:
                    img_url = html.unescape(im.group(1))
                if titulo and enlace:
                    items.append({
                        "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                        "medio": fuente or "Bing News", "imagen": img_url,
                    })
        except Exception as e:
            print(f"  ⚠️  Bing RSS error ({termino}): {e}")
        return items

    def _scrape_filmaffinity(self) -> list:
        """Busca críticas de Filmaffinity vía Bing (sitio bloquea peticiones directas)."""
        items = []
        for query in self.config.filmaffinity_queries:
            try:
                bing_items = self._rss_bing(query)
                for it in bing_items:
                    url = it.get("url", "")
                    titulo = it.get("titulo", "")
                    if "filmaffinity.com" not in url:
                        continue
                    es_profesional = any(k in titulo.lower() for k in (
                        "crítica de prensa", "critica de prensa", "reseña de prensa",
                        "review de prensa", "crítica profesional", "critica profesional",
                    ))
                    es_usuario = any(k in titulo.lower() for k in (
                        "opinión de usuarios", "opiniones de usuarios", "crítica de usuario",
                        "critica de usuario", "reseña de usuario",
                    ))
                    if es_profesional:
                        it["tipo"] = "critica_profesional"
                    elif es_usuario:
                        it["tipo"] = "critica_usuario"
                    else:
                        it["tipo"] = "critica"
                    it["medio"] = "Filmaffinity"
                    items.append(it)
            except Exception as e:
                print(f"  ⚠️  Filmaffinity Bing error: {e}")
        return items

    def _scrape_cine_directo(self) -> list:
        """Scrapea fuentes de cine directamente (sin Bing)."""
        items = []
        for fuente in self.config.fuentes_cine_directas:
            try:
                url = fuente["url"]
                selector = fuente.get("selector", "a[href]")
                medio = fuente.get("medio", "Cine")
                r = requests.get(url, timeout=15, headers=HEADERS)
                if r.status_code != 200:
                    continue
                links = re.findall(r'href="([^"]*)"[^>]*>([^<]*)</a>', r.text, re.S)
                for href, texto in links:
                    texto_limpio = html.unescape(re.sub(r'<[^>]+>', '', texto)).strip()
                    if not texto_limpio or len(texto_limpio) < 5:
                        continue
                    texto_lower = texto_limpio.lower()
                    if not any(k in texto_lower for k in self.config.titulos_clave):
                        continue
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    items.append({
                        "titulo": texto_limpio, "url": href, "fecha_pub": "", "fecha_ts": datetime.now().isoformat(),
                        "medio": medio, "imagen": "", "tipo": "critica",
                    })
            except Exception as e:
                print(f"  ⚠️  Fuente cine directa error ({fuente.get('medio', '?')}): {e}")
        return items

    # ------------------------------------------------------------------
    # Anexar filtrado
    # ------------------------------------------------------------------
    def _anexar(self, items, resultados, vistos):
        """Añade a resultados los items relevantes y no duplicados."""
        for it in items:
            if not self._filter.es_relevante(it["titulo"]):
                continue
            url = self.url_real(it["url"])
            if not url or url in vistos:
                continue
            vistos.add(url)
            it["url"] = url
            it["tipo"] = self._classifier.clasificar(it["titulo"])
            it["relevancia"] = self._filter.puntuacion(it["titulo"])
            it["pelicula"] = self.config.pelicula
            resultados.append(it)

    # ------------------------------------------------------------------
    # Orquestación principal de scraping
    # ------------------------------------------------------------------
    def recopilar(self) -> list:
        resultados = []
        vistos = set()
        for termino in self.config.queries:
            self._anexar(self._rss_bing(termino), resultados, vistos)
        for termino in self.config.queries_extra:
            self._anexar(self._rss_bing(termino), resultados, vistos)
        for termino in self.config.yt_queries:
            self._anexar(self._rss_youtube(termino), resultados, vistos)
        for termino in self.config.contraste_queries:
            self._anexar(self._rss_contraste(termino), resultados, vistos)
        self._anexar(self._scrape_filmaffinity(), resultados, vistos)
        self._anexar(self._scrape_cine_directo(), resultados, vistos)
        for dominio, termino in self.config.sitios_resenias:
            for it in self._rss_bing(f"site:{dominio} {termino}"):
                self._anexar([it], resultados, vistos)
        for termino in self.config.redes_sociales:
            for it in self._rss_bing(termino):
                self._anexar([it], resultados, vistos)
        return resultados

    def cargar_existente(self):
        if self.config.output_path.exists():
            try:
                return json.loads(self.config.output_path.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    # ------------------------------------------------------------------
    # Validación IA (OCP: prompt configurable, modelo configurable)
    # ------------------------------------------------------------------
    def validar_ia(self, items) -> list:
        """Usa Gemini para confirmar si cada título pertenece a la película
        configurada. Devuelve los items confirmados. Fail-open sin API key."""
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key or not items or not self.config.ia_prompt:
            return items
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            numerados = "\n".join(f"{i+1}. {it['titulo']} — {it['url']}" for i, it in enumerate(items))
            prompt = self.config.ia_prompt(numerados)
            resp = client.models.generate_content(model=self.config.ia_model, contents=prompt)
            texto = (resp.text or "").strip()
            aceptados = set()
            for part in re.findall(r"\d+", texto):
                idx = int(part)
                if 1 <= idx <= len(items):
                    aceptados.add(idx - 1)
            if not aceptados and texto:
                return items
            return [it for i, it in enumerate(items) if i in aceptados]
        except Exception as e:
            print(f"  ⚠️  Validación IA opcional no disponible ({e}) — sigo con filtros locales.")
            return items


# =============================================================================
# SRP — TelegramNewsSender: envía novedades a Telegram (con foto si la hay)
# =============================================================================

class TelegramNewsSender:
    """Envía novedades a Telegram con thumbnail + enlace. Inyecta el transporte
    `TelegramClient` (DIP); por defecto lee BOT_TOKEN/CHAT_ID de las variables
    de entorno al importar (mismo comportamiento que antes)."""

    def __init__(self, client: TelegramClient = None):
        self.client = client or TelegramClient(bot_token=BOT_TOKEN, chat_id=CHAT_ID)

    def enviar(self, nuevos: list, por_tipo: dict, total: int, todos: list = None) -> list:
        """Envía la lista de novedades a Telegram. Devuelve la lista de items
        enviados con éxito (para marcar enviada=True después)."""
        if not self.client.bot_token or not self.client.chat_id:
            print("⚠️  TIPS_BOT_TOKEN / SALUDO_CHAT_ID no configurados; no se envía.")
            return []

        try:
            menciones = {
                "trailer": "🎬", "video": "🎬", "foto": "🖼️", "poster": "🎞️",
                "critica": "📝", "noticia": "📰", "entrevista": "🎙️", "fotograma": "🗂️",
            }

            def _send_message(msg):
                try:
                    r = self.client.send_message(msg, parse_mode="Markdown", timeout=60)
                    return r is not None and r.status_code == 200
                except Exception:
                    return False

            def _send_photo(it):
                emoji = menciones.get(it.get("tipo", "•"), "•")
                caption = (f"{emoji} *[{it.get('tipo', 'noticia')}]* {it.get('titulo', '').replace('*', '')}"
                           f"\n{it.get('url', '')}")
                img = (it.get("imagen") or "").strip()
                if img:
                    try:
                        r = self.client.send_photo(img, caption=caption, timeout=60)
                        if r is not None and r.status_code == 200:
                            return True
                    except Exception:
                        pass
                return _send_message(f"{emoji} *[{it.get('tipo', 'noticia')}]* {it.get('titulo', '').replace('*', '')}\n{it.get('url', '')}")

            if not nuevos:
                if todos:
                    lista = [f"{menciones.get(e['tipo'], '•')} [{e['tipo']}] {e['titulo'].replace('*', '')}"
                             f"\n{e['url']}" for e in todos]
                    parte = ["*Registro completo acumulado:*"]
                    bloque = ""
                    for linea in lista:
                        if bloque and len(bloque) + len(linea) + 1 > 3500:
                            parte.append(bloque)
                            bloque = linea
                        else:
                            bloque = f"{bloque}\n{linea}" if bloque else linea
                    if bloque:
                        parte.append(bloque)
                    for p in parte:
                        _send_message(p)
                else:
                    _send_message("_No hay contenido nuevo desde la última vez._")
            else:
                enviados = []
                for n in nuevos:
                    if _send_photo(n):
                        enviados.append(n)
                print(f"✅ Enviado a Telegram ({len(enviados)} novedad(es))."
                      if enviados else "❌ Telegram: falló algún envío.")
                return enviados
        except Exception as e:
            print(f"❌ Error enviando Telegram: {e}")
            return []


# =============================================================================
# Función de orquestación (SRP: ejecutar el flujo completo desde fuera)
# =============================================================================

def ejecutar(scraper: MovieNewsScraper, dry_run: bool = False, enviar: bool = False,
             notifier: TelegramNewsSender = None):
    """Ejecuta el flujo completo: recopilar → filtrar → mostrar → (guardar) → (enviar).
    Comportamiento idéntico al main() original de scrape_eixam.py, sin la
    parte de IMDb parental (que se orquesta desde el entry point concreto)."""
    cfg = scraper.config
    print(f"🎬 Recopilando información sobre '{cfg.pelicula}' ({cfg.pelicula_es})...")

    nuevos = scraper.recopilar()
    nuevos = scraper.validar_ia(nuevos)
    existentes = scraper.cargar_existente()
    urls_existentes = {e["url"] for e in existentes}

    realmente_nuevos = [n for n in nuevos if n["url"] not in urls_existentes]

    todos = existentes + realmente_nuevos
    por_tipo = {}
    for t in todos:
        tipo = t.get("tipo", "noticia")
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    print(f"\n📚 Previamente archivados: {len(existentes)}")
    print(f"✨ Nuevos encontrados ahora: {len(realmente_nuevos)}")
    print(f"📊 Total archivo: {len(todos)}")
    print("\nDistribución por tipo:")
    for tipo, n in sorted(por_tipo.items(), key=lambda x: -x[1]):
        print(f"   • {tipo}: {n}")

    if realmente_nuevos:
        print("\n🆕 Nuevos elementos:")
        for n in realmente_nuevos[:30]:
            print(f"   [{n['tipo']}] {n['titulo'][:80]}")
            print(f"        {n['url']}")

    if dry_run:
        print("\n--- DRY RUN: no se guarda nada ---")
        return

    if realmente_nuevos:
        cfg.output_path.parent.mkdir(parents=True, exist_ok=True)
        cfg.output_path.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n💾 Guardado: {len(todos)} entradas en {cfg.output_path}")
    else:
        print("\n✅ Sin novedades: no hay contenido nuevo que archivar.")

    por_enviar = [n for n in realmente_nuevos if not n.get("enviada", False)]

    if enviar and por_enviar and notifier:
        enviados = notifier.enviar(por_enviar, por_tipo, len(todos), todos)
        if enviados:
            urls_enviadas = {e["url"] for e in enviados}
            for item in todos:
                if item["url"] in urls_enviadas:
                    item["enviada"] = True
            cfg.output_path.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"💾 Archivo actualizado: {len(urls_enviadas)} items marcados como enviados.")
    elif enviar:
        print("\n📭 No hay elementos nuevos sin enviar.")