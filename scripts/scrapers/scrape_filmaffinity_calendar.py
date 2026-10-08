#!/usr/bin/env python3
"""
scrape_filmaffinity_calendar.py — Scraper del calendario de TV de Filmaffinity.
Extrae series españolas de https://www.filmaffinity.com/es/calendar-tv.php?reg=es&date=YYYY-MM&chv=1

Uso:
    python scripts/scrapers/scrape_filmaffinity_calendar.py --year 2026 --month 10
    python scripts/scrapers/scrape_filmaffinity_calendar.py --year 2026 --month 10 --dry-run
    python scripts/scrapers/scrape_filmaffinity_calendar.py --year 2026 --month 10 --crear-eventos
"""
import argparse
import sys
import json
import os
import re
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
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
CREDENTIALS_FILE = REPO_DIR / 'config' / 'google_credentials.json'
TOKEN_FILE = REPO_DIR / 'config' / 'google_token.json'
OUTPUT_DIR = REPO_DIR / 'files'
OUTPUT_PATH = OUTPUT_DIR / 'filmaffinity_calendar_series.json'

# URL base del calendario de Filmaffinity
FILMAFFINITY_CALENDAR_URL = "https://www.filmaffinity.com/es/calendar-tv.php"
FILMAFFINITY_BASE = "https://www.filmaffinity.com"


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
                datetime.fromisoformat(fecha_estreno)
            except ValueError:
                print(f"  ⚠️  {serie.get('titulo')}: Fecha inválida '{fecha_estreno}'")
                return False

            protagonistas_str = ', '.join(serie.get('protagonistas', []))

            evento = {
                'summary': f"🎬 Estreno: {serie['titulo']}",
                'description': (
                    f"🎬 Estreno en Filmaffinity/Filmin: {serie['titulo']}\n\n"
                    f"📅 Fecha: {fecha_estreno}\n"
                    f"🎭 Género: {serie.get('genero', 'N/A')}\n"
                    f"🎬 Director: {serie.get('director', 'N/A')}\n"
                    f"👥 Protagonistas: {protagonistas_str or 'N/A'}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n\n"
                    f"🔗 Filmaffinity: {serie.get('url', FILMAFFINITY_BASE)}\n"
                ),
                'start': {
                    'date': fecha_estreno,
                    'timeZone': 'Europe/Madrid',
                },
                'end': {
                    'date': (datetime.fromisoformat(fecha_estreno) + timedelta(days=1)).date().isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
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


class FilmaffinityCalendarScraper:
    """Scraper del calendario de TV de Filmaffinity."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

    def _fetch_calendar_page(self, year: int, month: int) -> Optional[str]:
        """Descarga la página del calendario para un mes/año dado."""
        params = {
            'reg': 'es',
            'date': f"{year:04d}-{month:02d}",
            'chv': '1'
        }
        url = f"{FILMAFFINITY_CALENDAR_URL}?{urllib.parse.urlencode(params)}"
        print(f"  📥 Descargando: {url}")

        # Primero visitar la página principal para establecer cookies
        try:
            self.session.get("https://www.filmaffinity.com/es/", timeout=10)
            time.sleep(1)
        except Exception:
            pass

        try:
            response = self.session.get(url, timeout=15)
            print(f"  📥 HTTP {response.status_code}")
            if response.status_code != 200:
                # Intentar sin chv
                params_no_chv = {'reg': 'es', 'date': f"{year:04d}-{month:02d}"}
                url2 = f"{FILMAFFINITY_CALENDAR_URL}?{urllib.parse.urlencode(params_no_chv)}"
                response = self.session.get(url2, timeout=15)
                print(f"  📥 Retry sin chv: HTTP {response.status_code}")
            if response.status_code != 200:
                return None
            return response.text
        except Exception as e:
            print(f"  ❌ Error descargando: {e}")
            return None

    def _parse_calendar(self, html: str, year: int, month: int) -> List[Dict]:
        """Parsea el HTML del calendario y extrae las series."""
        soup = BeautifulSoup(html, 'html.parser')
        series = []

        # El calendario tiene una tabla con días
        calendar_table = soup.find('table', class_='calendar') or soup.find('table', id='calendar')
        if not calendar_table:
            calendar_table = soup.find('table')
            if not calendar_table:
                print("  ⚠️ No se encontró tabla de calendario")
                return []

        day_cells = calendar_table.find_all('td', class_=re.compile(r'day|cal-day|calendar-day'))
        if not day_cells:
            day_cells = calendar_table.find_all('td')

        for cell in day_cells:
            day_text = cell.get_text(strip=True)
            day_match = re.match(r'^(\d{1,2})', day_text)
            if not day_match:
                continue
            day = int(day_match.group(1))

            try:
                fecha = datetime(year, month, day)
            except ValueError:
                continue

            links = cell.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if '/es/film' in href:
                    serie = self._extract_serie_from_link(link, cell, fecha, href)
                    if serie:
                        series.append(serie)

            serie_divs = cell.find_all('div', class_=re.compile(r'show|series|program|item'))
            for div in serie_divs:
                link = div.find('a', href=True)
                if link and '/es/film' in link.get('href', ''):
                    serie = self._extract_serie_from_link(link, div, fecha, link.get('href', ''))
                    if serie:
                        series.append(serie)

        return series

    def _extract_serie_from_link(self, link, container, fecha: datetime, href: str) -> Optional[Dict]:
        title = link.get_text(strip=True)
        if not title or len(title) < 3:
            return None

        noise_keywords = ['ver más', 'más', 'ver todo', 'calendar', 'anterior', 'siguiente', 'mes', 'año']
        if any(kw in title.lower() for kw in noise_keywords):
            return None

        if href.startswith('/'):
            url = f"{FILMAFFINITY_BASE}{href}"
        elif href.startswith('http'):
            url = href
        else:
            url = f"{FILMAFFINITY_BASE}/{href}"

        detalles = self._fetch_serie_details(url)

        return {
            'titulo': title,
            'fecha_estreno': fecha.date().isoformat(),
            'url': url,
            'director': detalles.get('director', ''),
            'protagonistas': detalles.get('protagonistas', []),
            'genero': detalles.get('genero', ''),
            'temporadas': detalles.get('temporadas', 1),
            'capitulos': detalles.get('capitulos', '?'),
            'sinopsis': detalles.get('sinopsis', ''),
            'fecha_scrape': datetime.now(timezone.utc).isoformat(),
        }

    def _fetch_serie_details(self, url: str) -> Dict:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {}

            soup = BeautifulSoup(response.text, 'html.parser')

            titulo_elem = soup.find('h1', id='main-title') or soup.find('h1', class_='mc-title')
            titulo_real = titulo_elem.get_text(strip=True) if titulo_elem else ''

            ano = ''
            ano_elem = soup.find('span', id='year') or soup.find('dd', class_='year')
            if ano_elem:
                ano = ano_elem.get_text(strip=True)

            genero = ''
            genero_elem = soup.find('dd', class_='genre') or soup.find('div', class_='genres')
            if genero_elem:
                genero = genero_elem.get_text(strip=True)

            director = ''
            director_elem = soup.find('dd', class_='director') or soup.find('span', itemprop='director')
            if director_elem:
                director = director_elem.get_text(strip=True)

            protagonistas = []
            reparto = soup.find('div', id='cast') or soup.find('div', class_='cast')
            if reparto:
                actores = reparto.find_all('a')
                for actor in actores[:5]:
                    nombre = actor.get_text(strip=True)
                    if nombre:
                        protagonistas.append(nombre)

            sinopsis = ''
            sinopsis_elem = soup.find('div', id='sinopsis') or soup.find('div', class_='synopsis')
            if sinopsis_elem:
                sinopsis = sinopsis_elem.get_text(strip=True)[:500]

            return {
                'titulo': titulo_real,
                'año': ano,
                'genero': genero,
                'director': director,
                'protagonistas': protagonistas,
                'sinopsis': sinopsis,
            }
        except Exception as e:
            print(f"    ⚠️ Error obteniendo detalles de {url}: {e}")
            return {}

    def scrape_month(self, year: int, month: int) -> List[Dict]:
        print(f"🔍 Scrapeando Filmaffinity calendario: {month:02d}/{year}")

        html = self._fetch_calendar_page(year, month)
        if not html:
            return []

        series = self._parse_calendar(html, year, month)

        seen = set()
        unicas = []
        for s in series:
            key = (s['titulo'], s['fecha_estreno'])
            if key not in seen:
                seen.add(key)
                unicas.append(s)

        print(f"  ✅ Encontradas {len(unicas)} series únicas")
        return unicas


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
    parser = argparse.ArgumentParser(description="Scraper Filmaffinity Calendar TV + Google Calendar")
    parser.add_argument("--year", type=int, required=True, help="Año (ej: 2026)")
    parser.add_argument("--month", type=int, required=True, help="Mes 1-12")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar/crear eventos")
    parser.add_argument("--crear-eventos", action="store_true", help="Crea eventos en Google Calendar")
    parser.add_argument("--guardar-json", action="store_true", help="Guarda resultados en JSON")

    args = parser.parse_args()

    if not (1 <= args.month <= 12):
        print("❌ Mes debe ser 1-12")
        return

    print(f"🎬 Scraper Filmaffinity Calendar TV - {args.month:02d}/{args.year}")

    scraper = FilmaffinityCalendarScraper()
    series = scraper.scrape_month(args.year, args.month)

    if not series:
        print("⚠️ No se encontraron series")
        return

    print(f"\n📺 Series encontradas ({len(series)}):")
    for s in series:
        print(f"  📅 {s['fecha_estreno']} - {s['titulo']} ({s.get('genero', 'N/A')})")

    if args.dry_run:
        print("\n🔍 DRY RUN - No se guardan ni crean eventos")
        return

    anteriores = cargar_estado_anterior()
    series_por_fecha = {f"{s['titulo']}|{s['fecha_estreno']}": s for s in anteriores}

    for s in series:
        key = f"{s['titulo']}|{s['fecha_estreno']}"
        if key not in series_por_fecha:
            series_por_fecha[key] = s

    series_finales = list(series_por_fecha.values())

    if args.guardar_json:
        guardar_estado(series_finales)
        print(f"💾 Guardado en {OUTPUT_PATH}")

    if args.crear-eventos:
        print("\n📅 Creando eventos en Google Calendar...")
        creados = crear_eventos_google_calendar(series)
        print(f"\n✅ Creados {creados} eventos")


if __name__ == "__main__":
    main()