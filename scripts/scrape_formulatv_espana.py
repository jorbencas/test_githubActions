#!/usr/bin/env python3
"""
scrape_formulatv_espana.py — Scraper de estrenos de series en FormulaTV (HTML data-tip).
Extrae datos de los atributos data-tip de las píldoras del calendario en https://www.formulatv.com/calendario/series/
(Solo mes actual - ideal para GitHub Action cada 2 días)
Crea eventos en Google Calendar a las 09:00 con recordatorio 30 min.
Evita duplicados. Funciona en GitHub Actions (sin navegador, sin API key).

Uso:
    python scripts/scrape_formulatv_espana.py
    python scripts/scrape_formulatv_espana.py --dry-run
    python scripts/scrape_formulatv_espana.py --crear-eventos
    python scripts/scrape_formulatv_espana.py --guardar-json
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
import re
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_DIR / 'scripts'))

from utils.common import load_json, save_json

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

# Configuración
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CONFIG_DIR = REPO_DIR / 'config'
CREDENTIALS_FILE = CONFIG_DIR / 'google_credentials.json'
TOKEN_FILE = CONFIG_DIR / 'google_token.json'
OUTPUT_DIR = REPO_DIR / 'files'
OUTPUT_PATH = OUTPUT_DIR / 'formulatv_espana_series.json'

FORMULATV_BASE = "https://www.formulatv.com"
FORMULATV_CALENDARIO = f"{FORMULATV_BASE}/calendario/series/"

# Cadenas/plataformas españolas (para filtrar solo series españolas)
# Incluye: broadcasters españoles + plataformas streaming que producen originales españoles
# Excluye: cadenas US tradicionales (CBS, NBC, ABC, Hulu, etc.)
CADENAS_ESPAÑOLAS = {
    # Movistar (principal productor español)
    'movistar+', 'movistar plus', 'movistar', '#0', '#vamos',
    # RTVE (público)
    'rtve', 'la 1', 'la 2', 'clan', 'teledeporte', '24h', 'rtve play',
    # Atresmedia
    'atresplayer', 'atresmedia', 'antena 3', 'la sexta', 'nova', 'mega', 'neox', 'atrplayer premium',
    # Mediaset
    'mediaset', 'telecinco', 'cuatro', 'factoría de ficción', 'energy', 'divinity', 'be mad', 'mitv', 'mitele',
    # Filmin (plataforma española)
    'filmin',
    # Grandes plataformas streaming que producen originales españoles
    'netflix', 'prime video', 'disney+', 'hbo max', 'max', 'paramount+', 'skyshowtime',
    'apple tv+', 'rakuten tv', 'rakuten',
    # Canales autonómicos/regionales
    'telemadrid', 'tv3', 'canal sur', 'eitb', 'etb', 'à punt', 'cmm', 'tpa', 'ib3', 'tv canaria', '7rm', 'cyltv', 'aragon tv', 'tvgalicia',
    # Otros canales españoles
    'paramount network españa', 'paramount network',
    'disney channel españa', 'disney channel',
    'nickelodeon españa', 'nickelodeon',
    'boing españa', 'boing',
    'discovery max', 'dkiss', 'gtv',
}

def _es_cadena_española(cadena: str) -> bool:
    """Verifica si una cadena/plataforma es española."""
    if not cadena:
        return False
    cadena_lower = cadena.lower().strip()
    return any(c in cadena_lower for c in CADENAS_ESPAÑOLAS)


class GoogleCalendarManager:
    """Gestor de Google Calendar para crear eventos de estrenos."""

    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        if not GOOGLE_CALENDAR_AVAILABLE:
            print("⚠️  Google Calendar API no disponible")
            return

        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    print(f"⚠️  No se encuentra {CREDENTIALS_FILE}")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)

            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar autenticado correctamente")

    def crear_evento_estreno(self, serie: dict) -> bool:
        if not self.service:
            return False

        try:
            fecha_estreno = serie.get('fecha_estreno', '')
            if not fecha_estreno:
                print(f"  ⚠️  {serie.get('titulo', 'Sin título')}: Sin fecha")
                return False

            try:
                fecha_dt = datetime.fromisoformat(fecha_estreno)
            except ValueError:
                print(f"  ⚠️  {serie.get('titulo')}: Fecha inválida '{fecha_estreno}'")
                return False

            # Verificar duplicados
            start_of_day = fecha_dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            end_of_day = fecha_dt.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

            existing = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day,
                timeMax=end_of_day,
                q=serie['titulo'],
                singleEvents=True
            ).execute()

            existe = any(e.get('summary') == f"🎬 Estreno: {serie['titulo']}" for e in existing.get('items', []))
            if existe:
                print(f"  ⏭️  Ya existe: {serie['titulo']} ({fecha_estreno})")
                return False

            protagonistas_str = ', '.join(serie.get('protagonistas', []))

            # Evento a las 09:00, duración 1h
            start_dt = fecha_dt.replace(hour=9, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=1)

            evento = {
                'summary': f"🎬 Estreno: {serie['titulo']}",
                'description': (
                    f"🎬 Estreno: {serie['titulo']}\n\n"
                    f"📅 Fecha: {fecha_estreno}\n"
                    f"🎭 Género: {serie.get('genero', 'N/A')}\n"
                    f"🎬 Cadena/Plataforma: {serie.get('cadena', 'N/A')}\n"
                    f"👥 Protagonistas: {protagonistas_str or 'N/A'}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n\n"
                    f"🔗 FormulaTV: {serie.get('url', FORMULATV_BASE)}\n"
                ),
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }

            evento = self.service.events().insert(
                calendarId='primary',
                body=evento
            ).execute()

            print(f"✅ Evento creado: {evento.get('htmlLink')}")
            return True

        except Exception as e:
            print(f"❌ Error creando evento para {serie.get('titulo')}: {e}")
            return False


class FormulaTVScraper:
    """Scraper de estrenos de series en FormulaTV (HTML data-tip attributes)."""

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

    def _parse_calendar_pills(self, html: str, solo_españolas: bool = True) -> List[Dict]:
        """Extrae series de los atributos data-tip de las píldoras del calendario."""
        import re
        soup = BeautifulSoup(html, 'html.parser')
        series = []

        # Buscar todas las píldoras del calendario
        pills = soup.find_all('a', class_=re.compile(r'cal-pill'))
        
        for pill in pills:
            try:
                # Extraer atributos data-tip
                data_tip = {}
                for attr, value in pill.attrs.items():
                    if attr.startswith('data-tip-'):
                        key = attr[len('data-tip-'):]
                        data_tip[key] = value

                if not data_tip:
                    continue

                # Título
                titulo = data_tip.get('title', '').strip()
                if not titulo or len(titulo) < 3:
                    continue

                # Fecha
                fecha_str = data_tip.get('date', '')
                if not fecha_str:
                    continue
                try:
                    fecha_dt = datetime.fromisoformat(fecha_str)
                    fecha_estreno = fecha_dt.date().isoformat()
                except:
                    continue

                # URL
                url = pill.get('href', '')
                if url and url.startswith('/'):
                    url = f"{FORMULATV_BASE}{url}"

                # Cadena/Plataforma
                cadena = data_tip.get('plat', '') or data_tip.get('plat-logo', '')

                # FILTRO: Solo series de cadenas/plataformas españolas (si se solicita)
                if solo_españolas and not _es_cadena_española(cadena):
                    continue

                # Género
                genero = data_tip.get('genre', '')

                # Temporadas/Capítulos
                try:
                    temporadas = int(data_tip.get('temps', 1))
                except:
                    temporadas = 1
                try:
                    capitulos = int(data_tip.get('caps', '0'))
                except:
                    capitulos = '?'

                # Descripción
                descripcion = data_tip.get('desc', '')
                if descripcion:
                    # Limpiar entidades HTML
                    descripcion = descripcion.replace('&#039;', "'").replace('"', '"').replace('&', '&')
                    # Limpiar tags HTML básicos
                    import re
                    descripcion = re.sub(r'<[^>]+>', '', descripcion)[:500]

                # Protagonistas - no disponible en data-tip, requeriría scrape individual
                protagonistas = []

                # URL completa
                url = pill.get('href', '')
                if url and url.startswith('/'):
                    url = f"{FORMULATV_BASE}{url}"

                series.append({
                    'titulo': data_tip.get('title', '').strip(),
                    'fecha_estreno': fecha_str,
                    'genero': data_tip.get('genre', ''),
                    'cadena': data_tip.get('plat', ''),
                    'protagonistas': [],
                    'temporadas': int(data_tip.get('temps', 1)),
                    'capitulos': data_tip.get('caps', '?'),
                    'sinopsis': descripcion,
                    'url': url if url.startswith('http') else f"{FORMULATV_BASE}{url}",
                    'fuente': 'FormulaTV',
                    'fecha_scrape': datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"  ⚠️ Error parseando píldora: {e}")
                continue

        return series

    def scrape_current_month(self, solo_españolas: bool = True) -> List[Dict]:
        """Scrapea el mes actual del calendario FormulaTV."""
        print(f"🔍 Scrapeando FormulaTV calendario (mes actual)...")

        html = self._fetch_page(FORMULATV_CALENDARIO)
        if not html:
            print("  ❌ No se pudo descargar la página")
            return []

        series = self._parse_calendar_pills(html, solo_españolas=solo_españolas)

        # Deduplicar
        seen = set()
        unicas = []
        for s in series:
            key = (s['titulo'], s['fecha_estreno'])
            if key not in seen:
                seen.add(key)
                unicas.append(s)

        print(f"  ✅ Encontradas {len(unicas)} series únicas")
        return unicas

    def _fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ❌ Error descargando {url}: {e}")
            return None


def cargar_estado_anterior() -> List[Dict]:
    if OUTPUT_PATH.exists():
        try:
            return json.loads(OUTPUT_PATH.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def guardar_estado(series: List[Dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(series, ensure_ascii=False, indent=2), encoding='utf-8')


def crear_eventos_google_calendar(series: List[Dict]) -> int:
    calendar = GoogleCalendarManager()
    if not calendar.service:
        return 0

    creados = 0
    for serie in series:
        if calendar.crear_evento_estreno(serie):
            print(f"✅ Evento creado: {serie['titulo']} ({serie['fecha_estreno']})")
            creados += 1
        time.sleep(0.5)
    return creados


def main():
    parser = argparse.ArgumentParser(description="Scraper FormulaTV Series España (mes actual) + Google Calendar")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar/crear eventos")
    parser.add_argument("--crear-eventos", action="store_true", help="Crea eventos en Google Calendar")
    parser.add_argument("--guardar-json", action="store_true", help="Guarda resultados en JSON")
    parser.add_argument("--solo-españolas", action="store_true", default=True, help="Filtrar solo series de plataformas españolas (default: True)")
    parser.add_argument("--todas", action="store_false", dest="solo_españolas", help="No filtrar por plataforma (todas las series)")

    args = parser.parse_args()

    print(f"🎬 Scraper FormulaTV Series España (mes actual)")

    scraper = FormulaTVScraper()
    series = scraper.scrape_current_month(solo_españolas=args.solo_españolas)

    if not series:
        print("⚠️ No se encontraron series")
        return

    print(f"\n📺 Series encontradas ({len(series)}):")
    for s in series:
        print(f"  📅 {s['fecha_estreno']} - {s['titulo']} ({s.get('cadena', s.get('genero', 'N/A'))})")

    if args.dry_run:
        print("\n🔍 DRY RUN - No se guardan ni crean eventos")
        return

    anteriores = cargar_estado_anterior()
    series_por_key = {f"{s['titulo']}|{s['fecha_estreno']}": s for s in anteriores}

    for s in series:
        key = f"{s['titulo']}|{s['fecha_estreno']}"
        if key not in series_por_key:
            series_por_key[key] = s

    series_finales = list(series_por_key.values())

    if args.guardar_json:
        guardar_estado(series_finales)
        print(f"💾 Guardado en {OUTPUT_PATH}")

    if args.crear_eventos:
        print("\n📅 Creando eventos en Google Calendar...")
        creados = crear_eventos_google_calendar(series)
        print(f"\n✅ Creados {creados} eventos")


if __name__ == "__main__":
    main()