#!/usr/bin/env python3
"""
scrape_formulatv_telegram.py — Estrenos del día (series + películas) → Telegram topic "report img".

Fuentes (sin tokens; HTML/JSON/XML estático):
  1. FormulaTV    — calendario de estrenos de series (data-tip)
  2. SensaCine    — estrenos de cine en España
  3. Filmaffinity — cartelera de estrenos en España (main.html)
  4. TVMaze       — API schedule (ES), estrenos de temporada (episodio 1 de cualquier temporada)
  5. À Punt       — noticias de la serie "Bambalina" (notas de premsa + RSS)
  6. Movistar+    — «Hoy en M+ Estrenos» (EPG del canal de estrenos)
  7. RSS series/cine — FormulaTV, Fotogramas y SensaCine (noticias con ventana + dedup)

Reglas:
  - Estrenos: SOLO items con fecha == fecha de ejecución (Europe/Madrid)
  - Noticias (À Punt + RSS): ventana de 14 días; se envían una sola vez vía dedup
  - Backfill silencioso: noticias con más de VENTANA_ENVIO_NOTICIAS_DIAS días se
    marcan como enviadas SIN enviar (evita inundar el canal en la primera ejecución)
  - Blocklist TITULOS_EXCLUIR (p. ej. "Los ilusos 13+13")
  - Sin duplicados entre ejecuciones (files/formulatv_sent.json, clave titulo|fecha)
  - Si una fuente falla, se envían las demás
  - Mensajes con parse_mode HTML: enlaces como <a href> y datos escapados

Uso:
    python scripts/scrape_formulatv_telegram.py
    python scripts/scrape_formulatv_telegram.py --dry-run
    python scripts/scrape_formulatv_telegram.py --todas  # sin filtro español (solo FormulaTV)
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from html import escape as esc_html
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent  # scripts/ → raíz del repo (antes sobraba un nivel)
sys.path.insert(0, str(REPO_DIR / 'scripts'))

# Configuración
OUTPUT_DIR = REPO_DIR / 'files'
SENT_FILE = OUTPUT_DIR / 'formulatv_sent.json'

FORMULATV_BASE = "https://www.formulatv.com"
FORMULATV_CALENDARIO = f"{FORMULATV_BASE}/calendario/series/"
SENSACINE_BASE = "https://www.sensacine.com"
SENSACINE_ESTRENOS = f"{SENSACINE_BASE}/peliculas/estrenos/"
FILMAFFINITY_MAIN = "https://www.filmaffinity.com/es/main.html"
TVMAZE_SCHEDULE = "https://api.tvmaze.com/schedule"
APUNT_NOTAS = "https://www.apuntmedia.es/sala-de-premsa/notes-de-premsa/"
APUNT_RSS = "https://www.apuntmedia.es/rss"
MOVISTAR_ESTRENOS = "https://www.movistarplus.es/canal/m-plus-estrenos?id=mv1"
# Fuentes RSS de noticias de series/cine → ventana + dedup (igual que À Punt)
NOTICIAS_RSS = {
    "FormulaTV": "https://www.formulatv.com/xml/formulatv.xml",
    "Fotogramas": "https://www.fotogramas.es/rss/all.xml",
    "SensaCine": "https://www.sensacine.com/rss/noticias.xml",
}

# Keywords de la fuente À Punt (noticias de series propias)
NOTICIA_KEYWORDS = ["bambalina"]
# Ventana de días hacia atrás para noticias (los estrenos son estrictos: solo hoy)
VENTANA_NOTICIAS_DIAS = 14
# Las noticias con más de N días se marcan como enviadas SIN enviar (backfill)
VENTANA_ENVIO_NOTICIAS_DIAS = 3

# Títulos que NUNCA se envían a este canal (substring, case-insensitive)
TITULOS_EXCLUIR = [
    "los ilusos 13+13",
]

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

# Cadenas/plataformas españolas (producen originales españoles)
CADENAS_ESPAÑOLAS = {
    'movistar+', 'movistar plus', 'movistar', '#0', '#vamos',
    'rtve', 'la 1', 'la 2', 'clan', 'teledeporte', '24h', 'rtve play',
    'atresplayer', 'atresmedia', 'antena 3', 'la sexta', 'nova', 'mega', 'neox', 'atrplayer premium',
    'mediaset', 'telecinco', 'cuatro', 'factoría de ficción', 'energy', 'divinity', 'be mad', 'mitv', 'mitele',
    'filmin',
    'netflix', 'prime video', 'disney+', 'hbo max', 'max', 'paramount+', 'skyshowtime',
    'apple tv+', 'rakuten tv', 'rakuten',
    'telemadrid', 'tv3', 'canal sur', 'eitb', 'etb', 'à punt', 'cmm', 'tpa', 'ib3', 'tv canaria', '7rm', 'cyltv', 'aragon tv', 'tvgalicia',
}

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
})


def fecha_ejecucion() -> date:
    """Fecha de HOY en España (Europe/Madrid) — la referencia para filtrar."""
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def _es_cadena_española(cadena: str) -> bool:
    if not cadena:
        return False
    cadena_lower = cadena.lower().strip()
    return any(c in cadena_lower for c in CADENAS_ESPAÑOLAS)


def _norm(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "")).strip().casefold()


def excluido(titulo: str) -> bool:
    """True si el título está en la blocklist (p. ej. 'Los ilusos 13+13')."""
    t = _norm(titulo)
    return any(b in t for b in TITULOS_EXCLUIR)


def parse_fecha_es(texto: str, anio_default: int) -> Optional[date]:
    """Parsea fechas en español → date.

    Soporta: '30 de octubre de 2026', '(30 de octubre)', '30oct.'
    Sin año (p. ej. Filmaffinity) usa `anio_default` (el año de ejecución).
    """
    if not texto:
        return None
    t = texto.strip().strip("()")
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóúñ]+)(?:\s+de\s+(\d{4}))?", t, re.I)
    if m:
        dia, mes_txt, anio = int(m.group(1)), m.group(2).lower(), m.group(3)
    else:
        m = re.search(r"(\d{1,2})\s*([a-záéíóú]{3})\.?", t, re.I)
        if not m:
            return None
        dia, mes_txt, anio = int(m.group(1)), m.group(2).lower(), None
    if mes_txt not in MESES:
        return None
    anio = int(anio) if anio else anio_default
    try:
        return date(anio, MESES[mes_txt], dia)
    except ValueError:
        return None


def _fetch(url: str, params: Optional[dict] = None) -> Optional[str]:
    try:
        response = SESSION.get(url, params=params or {}, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ❌ Error descargando {url}: {e}")
        return None


def _item(titulo: str, fecha: date, fuente: str, cadena: str, url: str,
          sinopsis: str = "", capitulos: Optional[str] = "?", temporadas: int = 1) -> Dict:
    return {
        'titulo': titulo,
        'fecha_estreno': fecha.isoformat(),
        'genero': '',
        'cadena': cadena or fuente,
        'protagonistas': [],
        'temporadas': temporadas,
        'capitulos': capitulos,
        'sinopsis': sinopsis,
        'url': url,
        'fuente': fuente,
        'fecha_scrape': datetime.now().isoformat(),
    }


# =============================================================================
# Fuente 1 — FormulaTV (calendario de estrenos de series)
# =============================================================================
def parse_formulatv(html: str, hoy: date, solo_espanolas: bool = True) -> List[Dict]:
    """Extrae estrenos del calendario FormulaTV (pills con data-tip)."""
    soup = BeautifulSoup(html, 'html.parser')
    items: List[Dict] = []
    hoy_str = hoy.isoformat()

    for pill in soup.find_all('a', class_=re.compile(r'cal-pill')):
        try:
            data_tip = {}
            for attr, value in pill.attrs.items():
                if attr.startswith('data-tip-'):
                    data_tip[attr[len('data-tip-'):]] = value

            if not data_tip:
                continue

            titulo = (data_tip.get('title') or '').strip()
            if not titulo or len(titulo) < 3:
                continue

            fecha_str = (data_tip.get('date') or '').strip()
            if not fecha_str or fecha_str != hoy_str:
                continue  # solo estrenos de HOY

            url = pill.get('href', '')
            if url and url.startswith('/'):
                url = f"{FORMULATV_BASE}{url}"

            cadena = data_tip.get('plat', '') or data_tip.get('plat-logo', '')
            if solo_espanolas and not _es_cadena_española(cadena):
                continue

            genero = data_tip.get('genre', '')
            try:
                temporadas = int(data_tip.get('temps', 1))
            except (TypeError, ValueError):
                temporadas = 1
            capitulos = data_tip.get('caps', '0') or '0'

            descripcion = data_tip.get('desc', '') or ''
            if descripcion:
                descripcion = descripcion.replace('&#039;', "'").replace('&quot;', '"').replace('&amp;', '&')
                descripcion = re.sub(r'<[^>]+>', '', descripcion)[:500]

            it = _item(titulo, hoy, 'FormulaTV', cadena, url,
                       sinopsis=descripcion, capitulos=capitulos, temporadas=temporadas)
            it['genero'] = genero
            items.append(it)
        except Exception as e:
            print(f"  ⚠️ Error parseando pill: {e}")
            continue

    return items


# =============================================================================
# Fuente 2 — SensaCine (estrenos de cine en España)
# =============================================================================
def parse_sensacine(html: str, hoy: date) -> List[Dict]:
    """Extrae estrenos de cine de sensacine.com/peliculas/estrenos/."""
    soup = BeautifulSoup(html, 'html.parser')
    items: List[Dict] = []

    for card in soup.select('.entity-card-list'):
        a = card.select_one('a.meta-title-link')
        d = card.select_one('.meta-body-info span.date') or card.select_one('span.date')
        if not a or not d:
            continue
        titulo = a.get_text(strip=True)
        fecha = parse_fecha_es(d.get_text(strip=True), hoy.year)
        if not titulo or not fecha:
            continue
        href = a.get('href', '')
        url = href if href.startswith('http') else f"{SENSACINE_BASE}{href}"
        items.append(_item(titulo, fecha, 'SensaCine', 'SensaCine', url))

    return items


# =============================================================================
# Fuente 3 — Filmaffinity (cartelera con fechas en main.html)
# =============================================================================
def parse_filmaffinity(html: str, hoy: date) -> List[Dict]:
    """Extrae estrenos de filmaffinity.com/es/main.html (fecha sin año → año actual)."""
    soup = BeautifulSoup(html, 'html.parser')
    items: List[Dict] = []

    for small in soup.find_all('small'):
        txt = small.get_text(strip=True)
        if not re.match(r"^\(\d{1,2}\s+de\s+[a-záéíóúñ]+\)$", txt, re.I):
            continue
        fecha = parse_fecha_es(txt, hoy.year)
        if not fecha:
            continue
        card = small.find_parent(class_='card-footer')
        if not card:
            continue
        t_el = card.select_one('.mtitle')
        link_el = small.find_parent('a')
        if not t_el or not link_el:
            continue
        titulo = t_el.get_text(strip=True)
        if not titulo:
            continue
        url = link_el.get('href', '')
        items.append(_item(titulo, fecha, 'Filmaffinity', 'Filmaffinity', url))

    return items


# =============================================================================
# Fuente 4 — TVMaze (schedule ES, estrenos de temporada: episodio 1)
# =============================================================================
def _limpiar_html(texto: str) -> str:
    if not texto:
        return ""
    return re.sub(r'<[^>]+>', '', texto).strip()


def parse_tvmaze(data: list, hoy: date) -> List[Dict]:
    """Extrae estrenos de temporada (episodio 1 de cualquier temporada) del schedule ES."""
    items: List[Dict] = []
    hoy_str = hoy.isoformat()

    for ep in data or []:
        try:
            if ep.get('number') != 1:
                continue  # estrenos de temporada: S1E1, S2E1, S3E1…
            if ep.get('airdate') != hoy_str:
                continue  # solo la fecha de ejecución
            show = ep.get('show') or {}
            net = show.get('network') or show.get('webChannel') or {}
            cadena = net.get('name') if isinstance(net, dict) else None
            titulo = (show.get('name') or ep.get('name') or '').strip()
            if not titulo:
                continue
            items.append(_item(
                titulo, hoy, 'TVMaze', cadena or 'TVMaze',
                ep.get('url') or show.get('url') or '',
                sinopsis=_limpiar_html(ep.get('summary') or show.get('summary') or ''),
                capitulos='1',
            ))
        except Exception as e:
            print(f"  ⚠️ Error parseando episodio TVMaze: {e}")
            continue

    return items


# =============================================================================
# Fuente 6 — Movistar+ («Hoy en M+ Estrenos», EPG del canal)
# =============================================================================
def parse_movistar_estrenos(html: str, hoy: date) -> List[Dict]:
    """Extrae el EPG de hoy del canal M+ Estrenos (sección «Hoy en M+ Estrenos»).

    Solo se toma el contenido de la primera colección («Hoy en…»); las
    siguientes («Si te gusta…», «Descubre…») son recomendaciones y se ignoran.
    """
    soup = BeautifulSoup(html, 'html.parser')
    items: List[Dict] = []

    header = None
    for h2 in soup.find_all('h2'):
        if 'Hoy en M+ Estrenos' in h2.get_text(' ', strip=True):
            header = h2
            break
    if not header:
        return items

    content = header.find_next(class_='mplus-collection__content')
    if not content:
        return items

    for li in content.find_all('li'):
        a = li.find('a', href=True)
        sub = li.select_one('.mplus-collection__subtitle')
        if not a or not sub:
            continue
        titulo = sub.get_text(strip=True)
        if not titulo or len(titulo) < 2:
            continue
        items.append(_item(titulo, hoy, 'Movistar+', 'Movistar+', a['href']))

    return items


# =============================================================================
# Fuente 7 — RSS de noticias de series/cine (FormulaTV, Fotogramas, SensaCine)
# =============================================================================
def parse_rss_noticias(xml_text: str, fuente: str) -> List[Dict]:
    """Items de un feed RSS/Atom de noticias (title + link + pubDate/published)."""
    items: List[Dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  ⚠️ RSS {fuente} ilegible: {e}")
        return items

    for node in root.iter():
        if node.tag.split('}')[-1].lower() not in ('item', 'entry'):
            continue
        try:
            titulo = link = fecha_s = ''
            for child in node:
                tag = child.tag.split('}')[-1].lower()
                if tag == 'title' and not titulo:
                    titulo = (child.text or '').strip()
                elif tag == 'link' and not link:
                    link = (child.text or '').strip() or (child.get('href') or '').strip()
                elif tag in ('pubdate', 'published', 'updated') and not fecha_s:
                    fecha_s = (child.text or '').strip()
            if not titulo or not link or not fecha_s:
                continue
            try:
                fecha = parsedate_to_datetime(fecha_s).date()
            except (TypeError, ValueError):
                fecha = datetime.fromisoformat(fecha_s.replace('Z', '+00:00')).date()
            items.append(_item(titulo, fecha, fuente, fuente, link, capitulos=None))
        except Exception as e:
            print(f"  ⚠️ Error parseando item RSS {fuente}: {e}")
            continue

    return items


# =============================================================================
# Fuente 5 — À Punt (noticias de la serie "Bambalina")
# =============================================================================
def parse_apunt_notas(html: str) -> List[Dict]:
    """Notas de prensa de apuntmedia.es que mencionan NOTICIA_KEYWORDS.

    El listing /sala-de-premsa/notes-de-premsa/ trae por artículo un <article>
    con enlace (title/texto) y fecha dd/mm/yyyy en .content-info.
    """
    soup = BeautifulSoup(html, 'html.parser')
    items: List[Dict] = []
    vistos = set()

    for art in soup.find_all('article'):
        try:
            a = art.find('a', href=True)
            if not a:
                continue
            url = a['href']
            if url in vistos:
                continue
            titulo = (a.get('title') or a.get_text(' ', strip=True)).strip()
            if not titulo:
                continue
            hay = f"{titulo} {url}".lower()
            if not any(k in hay for k in NOTICIA_KEYWORDS):
                continue
            m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", art.get_text(' ', strip=True))
            if not m:
                continue
            try:
                fecha = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                continue
            p = art.find('p')
            sinopsis = p.get_text(' ', strip=True)[:200] if p else ""
            vistos.add(url)
            items.append(_item(titulo, fecha, 'À Punt', 'À Punt', url,
                               sinopsis=sinopsis, capitulos=None))
        except Exception as e:
            print(f"  ⚠️ Error parseando nota À Punt: {e}")
            continue

    return items


def parse_apunt_rss(xml_text: str) -> List[Dict]:
    """Items del RSS de À Punt que mencionan NOTICIA_KEYWORDS (artículos /noticies/)."""
    items: List[Dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  ⚠️ RSS À Punt ilegible: {e}")
        return items

    for node in root.findall('.//item'):
        try:
            titulo = (node.findtext('title') or '').strip()
            url = (node.findtext('link') or '').strip()
            if not titulo or not url:
                continue
            hay = f"{titulo} {url}".lower()
            if not any(k in hay for k in NOTICIA_KEYWORDS):
                continue
            fecha = parsedate_to_datetime(node.findtext('pubDate') or '').date()
            items.append(_item(titulo, fecha, 'À Punt', 'À Punt', url, capitulos=None))
        except Exception as e:
            print(f"  ⚠️ Error parseando item RSS À Punt: {e}")
            continue

    return items


# =============================================================================
# Filtros centrales: fecha de ejecución + blocklist + dedup
# =============================================================================
def filtrar_estrenos(items: List[Dict], hoy: date) -> List[Dict]:
    """Deja SOLO items con fecha == fecha de ejecución y fuera de la blocklist."""
    out = []
    for it in items:
        if excluido(it.get('titulo', '')):
            continue
        if it.get('fecha_estreno') != hoy.isoformat():
            continue
        out.append(it)
    return out


def filtrar_noticias(items: List[Dict], hoy: date,
                     ventana_dias: int = VENTANA_NOTICIAS_DIAS) -> List[Dict]:
    """Noticias (fuente À Punt): blocklist + ventana [hoy - ventana_dias, hoy].

    A diferencia de los estrenos, no exige fecha == hoy: una nota de premsa de
    días anteriores sigue siendo válida y el dedup garantiza un solo envío.
    """
    desde = (hoy - timedelta(days=ventana_dias)).isoformat()
    hoy_str = hoy.isoformat()
    out = []
    for it in items:
        if excluido(it.get('titulo', '')):
            continue
        f = it.get('fecha_estreno', '')
        if not (desde <= f <= hoy_str):
            continue
        out.append(it)
    return out


def clave_item(it: Dict) -> str:
    return f"{it.get('titulo', '')}|{it.get('fecha_estreno', '')}"


def deduplicar(items: List[Dict]) -> List[Dict]:
    """Quita duplicados dentro de la misma ejecución (clave titulo|fecha)."""
    vistos = set()
    unicos = []
    for it in items:
        k = clave_item(it)
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(it)
    return unicos


def filtrar_nuevos(items: List[Dict], enviados: set) -> List[Dict]:
    """Quita los ya enviados en ejecuciones anteriores."""
    return [it for it in items if clave_item(it) not in enviados]


# =============================================================================
# Telegram
# =============================================================================
def cargar_enviados() -> set:
    """Carga set de claves ya enviadas (titulo|fecha)."""
    if SENT_FILE.exists():
        try:
            data = json.loads(SENT_FILE.read_text(encoding='utf-8'))
            return set(data) if isinstance(data, list) else set()
        except Exception:
            return set()
    return set()


def guardar_enviado(key: str):
    """Añade clave al set de enviados y guarda (máx. 1000, se descartan las más antiguas)."""
    lista: List[str] = []
    if SENT_FILE.exists():
        try:
            data = json.loads(SENT_FILE.read_text(encoding='utf-8'))
            if isinstance(data, list):
                lista = [x for x in data if isinstance(x, str)]
        except Exception:
            lista = []
    if key in lista:
        lista.remove(key)
    lista.append(key)
    if len(lista) > 1000:
        lista = lista[-1000:]
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SENT_FILE.write_text(json.dumps(lista, ensure_ascii=False), encoding='utf-8')


def enviar_telegram(mensaje: str, chat_id: str, token: str, topic_id: Optional[str] = None) -> bool:
    """Envía mensaje a Telegram (topic 'report img' si se indica)."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': mensaje,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    if topic_id:
        data['message_thread_id'] = topic_id

    try:
        r = requests.post(url, json=data, timeout=10)
        return r.ok
    except Exception as e:
        print(f"❌ Error Telegram: {e}")
        return False


def formatear_mensaje(series: List[Dict]) -> str:
    """Formatea el mensaje para Telegram (parse_mode HTML) agrupando por cadena.

    Los datos interpolados van escapados y los enlaces son <a href> reales.
    """
    if not series:
        return ""

    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    hoy = datetime.now(ZoneInfo("Europe/Madrid"))
    hoy_fmt = f"{hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

    lines = [
        f"📰 <b>Estrenos del día: {hoy_fmt}</b>",
        "",
        "¡Buenos días! Aquí están los estrenos de hoy. 👇",
        ""
    ]

    # Agrupar por cadena/plataforma
    por_cadena: Dict[str, List[Dict]] = {}
    for s in series:
        c = s.get('cadena') or s.get('fuente') or 'Sin plataforma'
        por_cadena.setdefault(c, []).append(s)

    for cadena, items in sorted(por_cadena.items()):
        lines.append(f"📍 <b>{esc_html(cadena)}</b>")
        for s in items:
            titulo = esc_html(s['titulo'])
            genero = f" ({esc_html(s['genero'])})" if s.get('genero') else ""
            temp = f" T{s['temporadas']}" if s.get('temporadas', 1) > 1 else ""
            tipo = " 🎬 Película" if s.get('capitulos') in ['?', '1', 1] and s.get('temporadas', 1) == 1 else f"{temp}"
            lines.append(f"🔸 <b>{titulo}</b>{genero}{tipo}")
            if s.get('sinopsis'):
                lines.append(f"     {esc_html(s['sinopsis'][:200])}")
            if s.get('url'):
                lines.append(f'     🔗 <a href="{esc_html(s["url"], quote=True)}">Leer artículo</a>')
        lines.append("")

    fuentes = sorted({s.get('fuente', 'FormulaTV') for s in series})
    lines.append(f"📡 <i>Fuentes: {esc_html(' · '.join(fuentes))}</i>")
    lines.append(f"🤖 <i>Bot automático — {hoy.strftime('%H:%M')}</i>")

    return "\n".join(lines)


# =============================================================================
# Orquestación
# =============================================================================
def recopilar_estrenos(hoy: date, solo_espanolas: bool = True) -> List[Dict]:
    """Recopila estrenos de las fuentes + noticias (À Punt y RSS). Si una falla, siguen las demás."""
    items: List[Dict] = []
    noticias: List[Dict] = []

    # HTML: FormulaTV, SensaCine, Filmaffinity, Movistar+
    for nombre, url, parse in (
        ("FormulaTV", FORMULATV_CALENDARIO, lambda h: parse_formulatv(h, hoy, solo_espanolas)),
        ("SensaCine", SENSACINE_ESTRENOS, lambda h: parse_sensacine(h, hoy)),
        ("Filmaffinity", FILMAFFINITY_MAIN, lambda h: parse_filmaffinity(h, hoy)),
        ("Movistar+", MOVISTAR_ESTRENOS, lambda h: parse_movistar_estrenos(h, hoy)),
    ):
        html = _fetch(url)
        if not html:
            continue
        try:
            encontrados = parse(html)
            print(f"  ✅ {nombre}: {len(encontrados)} anuncios parseados")
            items += encontrados
        except Exception as e:
            print(f"  ⚠️ {nombre} falló (sigo con las demás): {e}")

    # JSON: TVMaze
    try:
        r = SESSION.get(TVMAZE_SCHEDULE, params={'country': 'ES', 'date': hoy.isoformat()}, timeout=15)
        r.raise_for_status()
        encontrados = parse_tvmaze(r.json(), hoy)
        print(f"  ✅ TVMaze: {len(encontrados)} estrenos de temporada de hoy")
        items += encontrados
    except Exception as e:
        print(f"  ⚠️ TVMaze falló (sigo con las demás): {e}")

    # Fuente 5 — À Punt: noticias de "Bambalina" (ventana de días, no solo hoy)
    html = _fetch(APUNT_NOTAS)
    if html:
        try:
            encontrados = parse_apunt_notas(html)
            print(f"  ✅ À Punt notas: {len(encontrados)} noticias de Bambalina")
            noticias += encontrados
        except Exception as e:
            print(f"  ⚠️ À Punt notas falló (sigo con las demás): {e}")

    try:
        r = SESSION.get(APUNT_RSS, timeout=15)
        r.raise_for_status()
        encontrados = parse_apunt_rss(r.text)
        print(f"  ✅ À Punt RSS: {len(encontrados)} noticias de Bambalina")
        noticias += encontrados
    except Exception as e:
        print(f"  ⚠️ À Punt RSS falló (sigo con las demás): {e}")

    # Fuente 7 — RSS de noticias de series/cine (ventana + dedup)
    for nombre, url in NOTICIAS_RSS.items():
        xml_text = _fetch(url)
        if not xml_text:
            continue
        try:
            encontrados = parse_rss_noticias(xml_text, nombre)
            print(f"  ✅ RSS {nombre}: {len(encontrados)} noticias")
            noticias += encontrados
        except Exception as e:
            print(f"  ⚠️ RSS {nombre} falló (sigo con las demás): {e}")

    for n in noticias:
        n['noticia'] = True

    return deduplicar(
        filtrar_estrenos(items, hoy) + filtrar_noticias(noticias, hoy)
    )


def partir_backfill(nuevos: List[Dict], hoy: date) -> Tuple[List[Dict], List[Dict]]:
    """Divide en (para_enviar, backfill).

    Las noticias con fecha < hoy - VENTANA_ENVIO_NOTICIAS_DIAS se marcan como
    enviadas sin enviar (backfill silencioso): evita inundar el canal con el
    histórico en la primera ejecución o tras una caída larga.
    """
    corte = (hoy - timedelta(days=VENTANA_ENVIO_NOTICIAS_DIAS)).isoformat()
    enviar: List[Dict] = []
    backfill: List[Dict] = []
    for it in nuevos:
        if it.get('noticia') and it.get('fecha_estreno', '') < corte:
            backfill.append(it)
        else:
            enviar.append(it)
    return enviar, backfill


def main():
    parser = argparse.ArgumentParser(description="Estrenos del día → Telegram (topic report img)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra mensaje sin enviar")
    parser.add_argument("--todas", action="store_true", help="Sin filtro plataformas españolas (solo FormulaTV)")
    parser.add_argument("--chat-id", help="Telegram chat ID (sobrescribe env)")
    parser.add_argument("--topic-id", help="Telegram topic ID (report img)")
    parser.add_argument("--token", help="Telegram bot token (sobrescribe env)")

    args = parser.parse_args()

    # Config desde env o args - usa SALUDO_CHAT_ID (mismo que saludo/greetings)
    chat_id = args.chat_id or os.getenv('SALUDO_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')
    topic_id = args.topic_id or os.getenv('TELEGRAM_REPORT_IMG_TOPIC_ID')
    token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')

    if not chat_id or not token:
        if args.dry_run:
            chat_id = chat_id or "DRY_RUN_CHAT_ID"
            token = token or "DRY_RUN_TOKEN"
        else:
            print("❌ Falta TELEGRAM_CHAT_ID y/o TELEGRAM_BOT_TOKEN en env/args")
            return

    hoy = fecha_ejecucion()
    print(f"🎬 Estrenos del día {hoy} (Europe/Madrid) → Telegram")

    todos = recopilar_estrenos(hoy, solo_espanolas=not args.todas)

    if not todos:
        print("⚠️ No hay estrenos hoy")
        return

    # Filtrar duplicados ya enviados
    nuevos = filtrar_nuevos(todos, cargar_enviados())

    if not nuevos:
        print("✅ Todos los estrenos de hoy ya fueron enviados")
        return

    # Backfill silencioso: noticias antiguas se marcan sin enviar
    para_enviar, backfill = partir_backfill(nuevos, hoy)
    if backfill:
        print(f"🗄️ {len(backfill)} noticias con más de {VENTANA_ENVIO_NOTICIAS_DIAS} días: "
              f"se marcan sin enviar")

    if not para_enviar:
        if not args.dry_run:
            for s in backfill:
                guardar_enviado(clave_item(s))
        print("✅ Nada nuevo que enviar" + (" (solo backfill)" if backfill else ""))
        return

    print(f"\n📺 {len(para_enviar)} elementos NUEVOS de hoy:")
    for s in para_enviar:
        marca = "📰" if s.get('noticia') else "📅"
        print(f"  {marca} {s['fecha_estreno']} - {s['titulo']} ({s.get('cadena', 'N/A')})")

    if args.dry_run:
        print("\n🔍 DRY RUN - No se envía")
        mensaje = formatear_mensaje(para_enviar)
        print("\n--- MENSAJE ---")
        print(mensaje)
        return

    # Enviar a Telegram
    mensaje = formatear_mensaje(para_enviar)
    print(f"\n📤 Enviando a Telegram (chat: {chat_id}, topic: {topic_id or 'general'})...")

    ok = enviar_telegram(mensaje, chat_id, token, topic_id)
    if ok:
        print("✅ Mensaje enviado")
        for s in list(para_enviar) + backfill:
            guardar_enviado(clave_item(s))
    else:
        print("❌ Error enviando")


if __name__ == "__main__":
    main()
