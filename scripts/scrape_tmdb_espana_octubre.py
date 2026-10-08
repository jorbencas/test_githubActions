#!/usr/bin/env python3
"""
scrape_tmdb_espana_octubre.py — Scraper de series españolas para un mes/año usando TMDB API.
Crea eventos en Google Calendar. Funciona en GitHub Actions (sin navegador).

Uso:
    python scripts/scrape_tmdb_espana_octubre.py --year 2026 --month 10
    python scripts/scrape_tmdb_espana_octubre.py --year 2026 --month 10 --dry-run
    python scripts/scrape_tmdb_espana_octubre.py --year 2026 --month 10 --crear-eventos
    python scripts/scrape_tmdb_espana_octubre.py --year 2026 --month 10 --guardar-json
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

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
OUTPUT_PATH = OUTPUT_DIR / 'tmdb_espana_series.json'

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"


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
                    f"🎬 Estreno: {serie['titulo']}\n\n"
                    f"📅 Fecha: {fecha_estreno}\n"
                    f"🎭 Género: {serie.get('genero', 'N/A')}\n"
                    f"🎬 Director: {serie.get('director', 'N/A')}\n"
                    f"👥 Protagonistas: {protagonistas_str or 'N/A'}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n\n"
                    f"🔗 TMDB: https://www.themoviedb.org/tv/{serie.get('tmdb_id', '')}\n"
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


class TMDBSpainScraper:
    """Scraper de series españolas usando TMDB API."""

    def __init__(self):
        if not TMDB_API_KEY:
            raise ValueError("TMDB_API_KEY no configurado en entorno")
        self.session = requests.Session()
        self.session.params = {
            'api_key': TMDB_API_KEY,
            'language': 'es-ES',
        }

    def _fetch(self, endpoint: str, params: dict = None) -> dict:
        url = f"{TMDB_BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ❌ Error API TMDB: {e}")
            return {}

    def scrape_month(self, year: int, month: int) -> List[Dict]:
        """Busca series españolas que se estrenan en el mes/año dado."""
        print(f"🔍 Buscando series españolas: {month:02d}/{year} (TMDB)...")

        all_series = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            data = self._fetch("/discover/tv", {
                "with_origin_country": "ES",
                "first_air_date.gte": f"{year:04d}-{month:02d}-01",
                "first_air_date.lte": f"{year:04d}-{month:02d}-31",
                "sort_by": "first_air_date.asc",
                "page": page,
                "include_adult": False,
            })

            results = data.get("results", [])
            if not results:
                break

            for serie in results:
                origin = serie.get("origin_country", [])
                if "ES" not in origin:
                    continue

                first_air = serie.get("first_air_date", "")
                if not first_air:
                    continue

                try:
                    air_date = datetime.fromisoformat(first_air)
                    if air_date.month != month or air_date.year != year:
                        continue
                except:
                    continue

                # Obtener detalles completos
                detalles = self._fetch(f"/tv/{serie['id']}", {
                    "append_to_response": "credits,external_ids"
                })

                generos = [g['name'] for g in detalles.get('genres', [])]
                creadores = [c['name'] for c in detalles.get('created_by', [])]
                cast = [c['name'] for c in detalles.get('credits', {}).get('cast', [])[:5]]

                all_series.append({
                    'titulo': serie['name'],
                    'fecha_estreno': first_air,
                    'genero': ', '.join(generos),
                    'director': ', '.join(creadores) if creadores else '',
                    'protagonistas': cast,
                    'temporadas': detalles.get('number_of_seasons', 1),
                    'capitulos': detalles.get('number_of_episodes', '?'),
                    'sinopsis': detalles.get('overview', '')[:500],
                    'tmdb_id': serie['id'],
                    'poster': f"https://image.tmdb.org/t/p/w500{serie.get('poster_path')}" if serie.get('poster_path') else None,
                    'vote_average': serie.get('vote_average', 0),
                    'fecha_scrape': datetime.now().isoformat(),
                })

            total_pages = data.get("total_pages", 1)
            page += 1

        print(f"  ✅ Encontradas {len(all_series)} series españolas")
        return all_series


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
    parser = argparse.ArgumentParser(description="Scraper series España TMDB + Google Calendar")
    parser.add_argument("--year", type=int, required=True, help="Año (ej: 2026)")
    parser.add_argument("--month", type=int, required=True, help="Mes 1-12")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar/crear eventos")
    parser.add_argument("--crear-eventos", action="store_true", help="Crea eventos en Google Calendar")
    parser.add_argument("--guardar-json", action="store_true", help="Guarda resultados en JSON")

    args = parser.parse_args()

    if not (1 <= args.month <= 12):
        print("❌ Mes debe ser 1-12")
        return

    if not TMDB_API_KEY:
        print("❌ Falta TMDB_API_KEY en variables de entorno")
        print("   Consigue tu API key gratis en: https://www.themoviedb.org/settings/api")
        return

    print(f"🎬 Scraper TMDB Series España - {args.month:02d}/{args.year}")

    scraper = TMDBSpainScraper()
    series = scraper.scrape_month(args.year, args.month)

    if not series:
        print("⚠️ No se encontraron series")
        return

    print(f"\n📺 Series encontradas ({len(series)}):")
    for s in series:
        print(f"  📅 {s['fecha_estreno']} - {s['titulo']} ({s.get('genero', 'N/A')}) ★ {s.get('vote_average', 0)}")

    if args.dry_run:
        print("\n🔍 DRY RUN - No se guardan ni crean eventos")
        return

    # Merge con estado anterior
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