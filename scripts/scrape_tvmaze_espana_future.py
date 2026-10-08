#!/usr/bin/env python3
"""
scrape_tvmaze_espana_future.py — Scraper TVMaze para series españolas con fechas futuras.
Usa TVMaze API (gratis, sin key) buscando shows con country ES y premiereDate futura.
Crea eventos en Google Calendar a las 09:00 con recordatorio 30 min.
Evita duplicados. Funciona en GitHub Actions (sin navegador, sin API key).

Uso:
    python scripts/scrape_tvmaze_espana_future.py --year 2026 --month 10
    python scripts/scrape_tvmaze_espana_future.py --year 2026 --month 10 --dry-run
    python scripts/scrape_tvmaze_espana_future.py --year 2026 --month 10 --crear-eventos
    python scripts/scrape_tvmaze_espana_future.py --year 2026 --month 10 --guardar-json
"""
import argparse
import json
import os
import sys
import time
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
OUTPUT_PATH = OUTPUT_DIR / 'tvmaze_espana_series.json'

TVMAZE_BASE_URL = "https://api.tvmaze.com"


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
                    f"🎬 Cadena: {serie.get('cadena', 'N/A')}\n"
                    f"👥 Protagonistas: {protagonistas_str or 'N/A'}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n\n"
                    f"🔗 TVMaze: https://www.tvmaze.com/shows/{serie.get('tvmaze_id', '')}\n"
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


class TVMazeSpainScraper:
    """Scraper de series españolas usando TVMaze API (gratis, sin key)."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def _fetch(self, endpoint: str, params: dict = None) -> Any:
        url = f"{TVMAZE_BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ❌ Error API TVMaze: {e}")
            return None

    def _fetch_show_details(self, show_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de un show (embed cast, crew, episodes)."""
        data = self._fetch(f"/shows/{show_id}", {"embed": "cast,crew,episodes"})
        return data

    def _is_spanish_show(self, show: dict) -> bool:
        """Verifica si un show es español basándose en network/webChannel country."""
        network = show.get('network') or show.get('webChannel')
        if network and network.get('country'):
            return network['country'].get('code') == 'ES'
        return False

    def scrape_month(self, year: int, month: int) -> List[Dict]:
        """Busca series españolas que se estrenan en el mes/año dado."""
        print(f"🔍 Buscando series españolas: {month:02d}/{year} (TVMaze)...")

        all_series = []
        page = 0
        empty_pages = 0

        while page < 100 and empty_pages < 5:  # Límite seguridad
            data = self._fetch("/shows", {"page": page})
            if not data:
                break

            page_found = 0
            for show in data:
                if not self._is_spanish_show(show):
                    continue

                # Verificar si tiene fecha de estreno en el mes/año objetivo
                premiered = show.get('premiered')
                if not premiered:
                    continue

                try:
                    air_date = datetime.fromisoformat(premiered)
                    if air_date.month != month or air_date.year != year:
                        continue
                except:
                    continue

                # Obtener detalles completos
                show_id = show['id']
                detalles = self._fetch_show_details(show_id)
                if not detalles:
                    continue

                # Géneros
                generos = detalles.get('genres', [])

                # Creadores
                creadores = []
                for crew in detalles.get('_embedded', {}).get('crew', []):
                    if crew.get('type') in ('Creator', 'Executive Producer', 'Writer'):
                        person = crew.get('person', {})
                        if person.get('name'):
                            creadores.append(person['name'])

                # Reparto
                protagonistas = []
                for cast_member in detalles.get('_embedded', {}).get('cast', [])[:5]:
                    person = cast_member.get('person', {})
                    if person.get('name'):
                        protagonistas.append(person['name'])

                # Cadena
                network = show.get('network') or show.get('webChannel')
                cadena = network.get('name', '') if network else ''

                # Episodios
                episodes = detalles.get('_embedded', {}).get('episodes', [])
                temporadas = max([e.get('season', 0) for e in episodes]) if episodes else 1
                capitulos = len(episodes) if episodes else '?'

                # Sinopsis
                sinopsis = detalles.get('summary', '').replace('<p>', '').replace('</p>', '').replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')[:500] if detalles.get('summary') else ''

                all_series.append({
                    'titulo': show['name'],
                    'fecha_estreno': premiered,
                    'genero': ', '.join(generos),
                    'cadena': cadena,
                    'protagonistas': protagonistas,
                    'temporadas': temporadas,
                    'capitulos': capitulos,
                    'sinopsis': sinopsis,
                    'tvmaze_id': show_id,
                    'fecha_scrape': datetime.now().isoformat(),
                })
                page_found += 1

            if page_found == 0:
                empty_pages += 1
            else:
                empty_pages = 0

            page += 1
            time.sleep(0.1)

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
    parser = argparse.ArgumentParser(description="Scraper series España TVMaze + Google Calendar")
    parser.add_argument("--year", type=int, required=True, help="Año (ej: 2026)")
    parser.add_argument("--month", type=int, required=True, help="Mes 1-12")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar/crear eventos")
    parser.add_argument("--crear-eventos", action="store_true", help="Crea eventos en Google Calendar")
    parser.add_argument("--guardar-json", action="store_true", help="Guarda resultados en JSON")

    args = parser.parse_args()

    if not (1 <= args.month <= 12):
        print("❌ Mes debe ser 1-12")
        return

    print(f"🎬 Scraper TVMaze Series España - {args.month:02d}/{args.year}")

    scraper = TVMazeSpainScraper()
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