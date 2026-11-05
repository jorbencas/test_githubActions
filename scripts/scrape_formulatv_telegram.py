#!/usr/bin/env python3
"""
scrape_formulatv_telegram.py — Estrenos del día (series + películas) → Telegram topic "report img".

Fuentes (sin tokens; HTML/JSON estático):
  1. FormulaTV    — calendario de estrenos de series (data-tip)
  2. SensaCine    — estrenos de cine en España
  3. Filmaffinity — cartelera de estrenos en España (main.html)
  4. TVMaze       — API schedule (ES), solo estrenos S1E1

Reglas:
  - SOLO items con fecha == fecha de ejecución (Europe/Madrid)
  - Blocklist TITULOS_EXCLUIR (p. ej. "Los ilusos 13+13")
  - Sin duplicados entre ejecuciones (files/formulatv_sent.json, clave titulo|fecha)
  - Si una fuente falla, se envían las demás

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
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent
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
          sinopsis: str = "", capitulos: str = "?", temporadas: int = 1) -> Dict:
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
# Fuente 4 — TVMaze (schedule ES, solo estrenos S1E1)
# =============================================================================
def _limpiar_html(texto: str) -> str:
    if not texto:
        return ""
    return re.sub(r'<[^>]+>', '', texto).strip()


def parse_tvmaze(data: list, hoy: date) -> List[Dict]:
    """Extrae estrenos de serie (temporada 1, episodio 1) del schedule de TVMaze ES."""
    items: List[Dict] = []
    hoy_str = hoy.isoformat()

    for ep in data or []:
        try:
            if ep.get('season') != 1 or ep.get('number') != 1:
                continue  # solo estrenos de serie nuevos
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
    """Añade clave al set de enviados y guarda (máx. 1000)."""
    enviados = cargar_enviados()
    enviados.add(key)
    if len(enviados) > 1000:
        enviados = set(list(enviados)[-1000:])
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SENT_FILE.write_text(json.dumps(list(enviados), ensure_ascii=False), encoding='utf-8')


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
    """Formatea el mensaje para Telegram agrupando por cadena/plataforma."""
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
        lines.append(f"📍 <b>{cadena}</b>")
        for s in items:
            titulo = s['titulo']
            genero = f" ({s['genero']})" if s.get('genero') else ""
            temp = f" T{s['temporadas']}" if s.get('temporadas', 1) > 1 else ""
            tipo = " 🎬 Película" if s.get('capitulos') in ['?', '1', 1] and s.get('temporadas', 1) == 1 else f"{temp}"
            lines.append(f"🔸 <b>{titulo}</b>{genero}{tipo}")
            if s.get('sinopsis'):
                lines.append(f"     {s['sinopsis'][:200]}")
            if s.get('url'):
                lines.append(f"     🔗 Leer artículo ({s['url']})")
        lines.append("")

    fuentes = sorted({s.get('fuente', 'FormulaTV') for s in series})
    lines.append(f"📡 <i>Fuentes: {' · '.join(fuentes)}</i>")
    lines.append(f"🤖 <i>Bot automático — {hoy.strftime('%H:%M')}</i>")

    return "\n".join(lines)


# =============================================================================
# Orquestación
# =============================================================================
def recopilar_estrenos(hoy: date, solo_espanolas: bool = True) -> List[Dict]:
    """Recopila estrenos de las 4 fuentes. Si una falla, siguen las demás."""
    items: List[Dict] = []

    # HTML: FormulaTV, SensaCine, Filmaffinity
    for nombre, url, parse in (
        ("FormulaTV", FORMULATV_CALENDARIO, lambda h: parse_formulatv(h, hoy, solo_espanolas)),
        ("SensaCine", SENSACINE_ESTRENOS, lambda h: parse_sensacine(h, hoy)),
        ("Filmaffinity", FILMAFFINITY_MAIN, lambda h: parse_filmaffinity(h, hoy)),
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
        print(f"  ✅ TVMaze: {len(encontrados)} S1E1 de hoy")
        items += encontrados
    except Exception as e:
        print(f"  ⚠️ TVMaze falló (sigo con las demás): {e}")

    return deduplicar(filtrar_estrenos(items, hoy))


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

    print(f"\n📺 {len(nuevos)} estrenos NUEVOS de hoy:")
    for s in nuevos:
        print(f"  📅 {s['fecha_estreno']} - {s['titulo']} ({s.get('cadena', 'N/A')})")

    if args.dry_run:
        print("\n🔍 DRY RUN - No se envía")
        mensaje = formatear_mensaje(nuevos)
        print("\n--- MENSAJE ---")
        print(mensaje)
        return

    # Enviar a Telegram
    mensaje = formatear_mensaje(nuevos)
    print(f"\n📤 Enviando a Telegram (chat: {chat_id}, topic: {topic_id or 'general'})...")

    ok = enviar_telegram(mensaje, chat_id, token, topic_id)
    if ok:
        print("✅ Mensaje enviado")
        for s in nuevos:
            guardar_enviado(clave_item(s))
    else:
        print("❌ Error enviando")


if __name__ == "__main__":
    main()
