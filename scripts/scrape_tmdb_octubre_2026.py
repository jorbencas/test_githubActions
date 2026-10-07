#!/usr/bin/env python3
"""
Scraper de series españolas de octubre 2026 para Google Calendar
Usa TMDB API para encontrar series españolas que se estrenan en octubre 2026
y las añade a Google Calendar.
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Cargar variables de entorno
load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

# Configuración
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Configuración Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Obtiene servicio autenticado de Google Calendar."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    token_file = Path('token.json')
    creds = None

    if Path('token.json').exists():
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                        "redirect_uris": [os.getenv('GOOGLE_CALLBACK_URL')],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def buscar_series_espana_octubre_2026():
    """Busca series españolas que se estrenan en octubre 2026 usando TMDB API."""
    if not TMDB_API_KEY:
        print("❌ Falta TMDB_API_KEY en .env")
        return []

    print("🔍 Buscando series españolas que se estrenan en octubre 2026...")

    series_encontradas = []
    page = 1

    while True:
        url = f"{TMDB_BASE_URL}/discover/tv"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "es-ES",
            "with_origin_country": "ES",
            "first_air_date.gte": "2026-10-01",
            "first_air_date.lte": "2026-10-31",
            "sort_by": "first_air_date.asc",
            "page": page,
            "include_adult": False,
        }

        try:
            response = requests.get(TMDB_BASE_URL + "/discover/tv", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            for serie in results:
                # Filtrar solo series españolas (origin_country ES ya filtra, pero doble check)
                origin = serie.get("origin_country", [])
                if "ES" not in origin and "ES" not in [c.upper() for c in origin]:
                    continue

                first_air = serie.get("first_air_date", "")
                if not first_air:
                    continue

                try:
                    air_date = datetime.fromisoformat(first_air)
                    if air_date.month != 10 or air_date.year != 2026:
                        continue
                except:
                    continue

                serie_info = {
                    "fecha": serie["first_air_date"],
                    "titulo": serie["name"],
                    "descripcion": serie.get("overview", "")[:200],
                    "todo_dia": True,
                    "fuente": "TMDB",
                    "tmdb_id": serie["id"],
                    "poster": f"https://image.tmdb.org/t/p/w500{serie.get('poster_path', '')}" if serie.get("poster_path") else None,
                    "vote_average": serie.get("vote_average", 0),
                }
                series_encontradas.append({
                    "fecha": serie["first_air_date"],
                    "titulo": serie["name"],
                    "descripcion": serie.get("overview", "")[:200],
                    "todo_dia": True,
                    "fuente": "TMDB",
                    "tmdb_id": serie["id"],
                })

            page += 1
            if page > data.get("total_pages", 1):
                break

        except requests.RequestException as e:
            print(f"❌ Error en API TMDB: {e}")
            break
        except Exception as e:
            print(f"❌ Error procesando página {page}: {e}")
            break

    # Ordenar por fecha
    series_encontradas.sort(key=lambda x: x["fecha"])
    return series_encontradas


def get_calendar_service():
    """Obtiene servicio autenticado de Google Calendar."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    token_file = Path('token.json')
    creds = None

    if Path('token.json').exists():
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                        "redirect_uris": [os.getenv('GOOGLE_CALLBACK_URL')],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def crear_eventos(service, eventos):
    """Crea eventos en Google Calendar evitando duplicados."""
    creados = 0
    for evento in eventos:
        try:
            # Verificar si ya existe
            existing = service.events().list(
                calendarId='primary',
                timeMin=evento['fecha'] + 'T00:00:00Z',
                timeMax=evento['fecha'] + 'T23:59:59Z',
                q=evento['titulo'],
                singleEvents=True
            ).execute()

            existe = any(e.get('summary') == evento['titulo'] for e in existing.get('items', []))

            if existe:
                print(f"  ⏭️  Ya existe: {evento['titulo']} ({evento['fecha']})")
                continue

            event_body = {
                'summary': evento['titulo'],
                'description': f"{evento.get('descripcion', '')}\n\nFuente: {evento.get('fuente', 'TMDB')}\nTMDB ID: {evento.get('tmdb_id', 'N/A')}",
                'start': {'date': evento['fecha']},
                'end': {'date': (datetime.fromisoformat(evento['fecha']) + timedelta(days=1)).strftime('%Y-%m-%d')},
            }

            event = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"  ✅ Creado: {evento['titulo']} ({evento['fecha']})")

        except Exception as e:
            print(f"  ❌ Error con {evento['titulo']}: {e}")


def main():
    print("🗓️  Buscando series españolas de octubre 2026 y añadiendo a Google Calendar")
    print("=" * 70)

    # Cargar credenciales
    load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

    # Verificar TMDB API Key
    if not os.getenv('TMDB_API_KEY'):
        print("❌ Falta TMDB_API_KEY en .env")
        print("   Consigue tu API key gratis en: https://www.themoviedb.org/settings/api")
        return

    # Verificar credenciales Google
    if not all([os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'), os.getenv('GOOGLE_CALLBACK_URL')]):
        print("❌ Faltan credenciales Google en .env")
        return

    print("✅ Credenciales cargadas")

    # 1. Buscar series
    print("\n🔍 Buscando series españolas de octubre 2026 en TMDB...")
    series = buscar_series_espana_octubre_2026()

    if not series:
        print("⚠️  No se encontraron series españolas para octubre 2026")
        return

    print(f"\n📋 Encontradas {len(series)} series:")
    for s in series:
        print(f"  📅 {s['fecha']} - {s['titulo']} (TMDB ID: {s['tmdb_id']}, ★ {s.get('vote_average', 0)})")

    confirm = input("\n¿Crear estos eventos en Google Calendar? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return

    # Autenticar Google Calendar
    print("\n🔐 Autenticando con Google Calendar...")
    service = get_calendar_service()
    print("✅ Autenticado correctamente")

    # Crear eventos
    print("\n📤 Creando eventos en Google Calendar...")
    service = get_calendar_service()
    crear_eventos(service, series_para_calendar)

    print("\n✅ Proceso completado")


if __name__ == '__main__':
    main()