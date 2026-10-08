#!/usr/bin/env python3
"""
scrape_formulatv_telegram.py — Scraper de estrenos HOY en FormulaTV → Telegram.
Solo estrenos DE HOY (no días anteriores), filtro plataformas españolas,
sin duplicados, envía a Telegram topic "report img".
Sin Google Calendar, sin tokens, sin secrets.

Uso:
    python scripts/scrape_formulatv_telegram.py
    python scripts/scrape_formulatv_telegram.py --dry-run
    python scripts/scrape_formulatv_telegram.py --todas  # sin filtro español
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_DIR / 'scripts'))

from utils.common import load_json, save_json

# Configuración
OUTPUT_DIR = REPO_DIR / 'files'
SENT_FILE = OUTPUT_DIR / 'formulatv_sent.json'

FORMULATV_BASE = "https://www.formulatv.com"
FORMULATV_CALENDARIO = f"{FORMULATV_BASE}/calendario/series/"

# Usa SALUDO_CHAT_ID (mismo que saludo/greetings) para el topic "report img"

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

def _es_cadena_española(cadena: str) -> bool:
    if not cadena:
        return False
    cadena_lower = cadena.lower().strip()
    return any(c in cadena_lower for c in CADENAS_ESPAÑOLAS)


class FormulaTVScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })

    def _fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ❌ Error descargando {url}: {e}")
            return None

    def _parse_today_premieres(self, html: str, solo_españolas: bool = True) -> List[Dict]:
        """Extrae SOLO estrenos de HOY del calendario."""
        import re
        soup = BeautifulSoup(html, 'html.parser')
        series = []

        pills = soup.find_all('a', class_=re.compile(r'cal-pill'))
        hoy = datetime.now().date().isoformat()

        for pill in pills:
            try:
                data_tip = {}
                for attr, value in pill.attrs.items():
                    if attr.startswith('data-tip-'):
                        key = attr[len('data-tip-'):]
                        data_tip[key] = value

                if not data_tip:
                    continue

                titulo = data_tip.get('title', '').strip()
                if not titulo or len(titulo) < 3:
                    continue

                fecha_str = data_tip.get('date', '')
                if not fecha_str:
                    continue

                # SOLO estrenos de HOY
                if fecha_str != hoy:
                    continue

                try:
                    fecha_dt = datetime.fromisoformat(fecha_str)
                except:
                    continue

                url = pill.get('href', '')
                if url and url.startswith('/'):
                    url = f"{FORMULATV_BASE}{url}"

                cadena = data_tip.get('plat', '') or data_tip.get('plat-logo', '')

                # Filtro plataformas españolas (configurable)
                if solo_españolas and not _es_cadena_española(cadena):
                    continue

                genero = data_tip.get('genre', '')
                try:
                    temporadas = int(data_tip.get('temps', 1))
                except:
                    temporadas = 1
                try:
                    capitulos = int(data_tip.get('caps', '0'))
                except:
                    capitulos = '?'

                descripcion = data_tip.get('desc', '')
                if descripcion:
                    descripcion = descripcion.replace('&#039;', "'").replace('"', '"').replace('&', '&')
                    descripcion = re.sub(r'<[^>]+>', '', descripcion)[:500]

                url = pill.get('href', '')
                if url and url.startswith('/'):
                    url = f"{FORMULATV_BASE}{url}"

                series.append({
                    'titulo': data_tip.get('title', '').strip(),
                    'fecha_estreno': fecha_str,
                    'genero': genero,
                    'cadena': cadena,
                    'protagonistas': [],
                    'temporadas': int(data_tip.get('temps', 1)),
                    'capitulos': data_tip.get('caps', '?'),
                    'sinopsis': descripcion,
                    'url': url if url.startswith('http') else f"{FORMULATV_BASE}{url}",
                    'fuente': 'FormulaTV',
                    'fecha_scrape': datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"  ⚠️ Error parseando: {e}")
                continue

        return series

    def scrape_today(self, solo_españolas: bool = True) -> List[Dict]:
        print(f"🔍 Buscando estrenos DE HOY ({datetime.now().date()})...")

        html = self._fetch_page(FORMULATV_CALENDARIO)
        if not html:
            print("  ❌ No se pudo descargar")
            return []

        series = self._parse_today_premieres(html, solo_españolas=solo_españolas)

        seen = set()
        unicas = []
        for s in series:
            key = (s['titulo'], s['fecha_estreno'])
            if key not in seen:
                seen.add(key)
                unicas.append(s)

        print(f"  ✅ {len(unicas)} estrenos HOY")
        return unicas

    def _fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None


def cargar_enviados() -> set:
    """Carga set de títulos ya enviados (key: titulo|fecha)."""
    if SENT_FILE.exists():
        try:
            data = json.loads(SENT_FILE.read_text(encoding='utf-8'))
            return set(data) if isinstance(data, list) else set()
        except Exception:
            return set()
    return set()


def guardar_enviado(key: str):
    """Añade key al set de enviados y guarda."""
    enviados = cargar_enviados()
    enviados.add(key)
    # Mantener solo últimos 1000 para no crecer indefinidamente
    if len(enviados) > 1000:
        enviados = set(list(enviados)[-1000:])
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SENT_FILE.write_text(json.dumps(list(enviados), ensure_ascii=False), encoding='utf-8')


def enviar_telegram(mensaje: str, chat_id: str, token: str, topic_id: Optional[str] = None) -> bool:
    """Envía mensaje a Telegram."""
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
    """Formatea el mensaje para Telegram estilo noticias (esquema solicitado)."""
    if not series:
        return ""

    meses = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']
    hoy = datetime.now()
    hoy_fmt = f"{hoy.day} de {meses[hoy.month-1]} de {hoy.year}"

    lines = [
        f"📰 <b>Estrenos del día: {hoy_fmt}</b>",
        "",
        "¡Buenos días! Aquí están los estrenos de hoy en plataformas españolas. 👇",
        ""
    ]

    # Agrupar por cadena/plataforma
    por_cadena = {}
    for s in series:
        c = s.get('cadena', 'Sin plataforma')
        if c not in por_cadena:
            por_cadena[c] = []
        por_cadena[c].append(s)

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

    lines.append("📡 <i>Fuente: FormulaTV calendario</i>")
    lines.append(f"🤖 <i>Bot automático — {datetime.now().strftime('%H:%M')}</i>")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Estrenos HOY FormulaTV → Telegram")
    parser.add_argument("--dry-run", action="store_true", help="Muestra mensaje sin enviar")
    parser.add_argument("--todas", action="store_true", help="Sin filtro plataformas españolas")
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

    print(f"🎬 Estrenos HOY FormulaTV → Telegram")

    scraper = FormulaTVScraper()
    series = scraper.scrape_today(solo_españolas=not args.todas)

    if not series:
        print("⚠️ No hay estrenos HOY")
        return

    # Filtrar duplicados ya enviados
    enviados = cargar_enviados()
    nuevos = []
    for s in series:
        key = f"{s['titulo']}|{s['fecha_estreno']}"
        if key not in enviados:
            nuevos.append(s)

    if not nuevos:
        print("✅ Todos los estrenos de hoy ya fueron enviados")
        return

    print(f"\n📺 {len(nuevos)} estrenos NUEVOS de HOY:")
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
            key = f"{s['titulo']}|{s['fecha_estreno']}"
            guardar_enviado(key)
    else:
        print("❌ Error enviando")


if __name__ == "__main__":
    main()