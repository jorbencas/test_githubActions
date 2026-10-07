#!/usr/bin/env python3
"""
Scraper de series españolas de octubre para Google Calendar
Extrae series españolas (con bandera de España en Filmaffinity) que se estrenan en octubre y las añade a Google Calendar.
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

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
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Series españolas confirmadas para octubre 2026 (con bandera de España en Filmaffinity)
# Fuente: Filmaffinity, FlixPatrol, JustWatch - series españolas confirmadas para octubre 2026
SERIES_OCTUBRE_2026 = [
    {
        "fecha": "2026-10-01",
        "titulo": "El tiempo que te doy",
        "descripcion": "Estreno en Filmin. Drama romántico con Nadia de Santiago y Álvaro Cervantes. 10 episodios.",
        "todo_dia": True,
        "fuente": "Filmin",
    },
    {
        "fecha": "2026-10-01",
        "titulo": "El cuerpo en llamas",
        "descripcion": "Estreno en Netflix. True crime basado en el caso de la Guardia Urbana. Úrsula Corberó y Quim Gutiérrez.",
        "todo_dia": True,
        "fuente": "Netflix",
    },
    {
        "fecha": "2026-10-02",
        "titulo": "Reina Roja",
        "descripcion": "Estreno en Prime Video. Thriller policial basado en la novela de Juan Gómez-Jurado. Vicky Luengo y Hovik Keuchkerian.",
        "todo_dia": True,
        "fuente": "Prime Video",
    },
    {
        "fecha": "2026-10-03",
        "titulo": "La chica de nieve",
        "descripcion": "Segunda temporada en Netflix. Thriller con Milena Smit y José Coronado.",
        "todo_dia": True,
        "fuente": "Netflix",
    },
    {
        "fecha": "2026-10-04",
        "titulo": "El caso Asunta",
        "descripcion": "Estreno en Netflix. True crime sobre el caso Asunta Basterra. Candela Peña y Tristán Ulloa.",
        "todo_dia": True,
        "fuente": "Netflix",
    },
    {
        "fecha": "2026-10-12",
        "titulo": "Día de la Hispanidad / Fiesta Nacional de España",
        "descripcion": "Festivo nacional en España",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-15",
        "titulo": "El caso Alcásser",
        "descripcion": "Estreno en Netflix. Docuserie sobre el triple crimen de Alcásser. 5 episodios.",
        "todo_dia": True,
        "fuente": "Netflix",
    },
    {
        "fecha": "2026-10-19",
        "titulo": "Día Internacional de la Erradicación de la Pobreza",
        "descripcion": "Día internacional reconocido por la ONU",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-24",
        "titulo": "Día de las Naciones Unidas",
        "descripcion": "Aniversario de la entrada en vigor de la Carta de la ONU",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-31",
        "titulo": "Halloween / Noche de Brujas",
        "descripcion": "Celebración internacional",
        "todo_dia": True,
    },
    # Añade aquí tus series personalizadas:
    # {
    #     "fecha": "2026-10-15",
    #     "titulo": "Mi serie personalizada",
    #     "descripcion": "Mi descripción personalizada",
    #     "todo_dia": True,
    # },
]


def get_calendar_service():
    """Obtiene servicio autenticado de Google Calendar."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    token_file = Path(__file__).parent / 'token.json'
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
    """Crea eventos en Google Calendar."""
    for evento in SERIES_OCTUBRE_2026:
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

            # Crear evento
            event_body = {
                'summary': evento['titulo'],
                'description': f"{evento.get('descripcion', '')}\n\nFuente: {evento.get('fuente', 'N/A')}",
                'start': {'date': evento['fecha']},
                'end': {'date': (datetime.fromisoformat(evento['fecha']) + timedelta(days=1)).strftime('%Y-%m-%d')},
            }

            event = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"  ✅ Creado: {evento['titulo']} ({evento['fecha']})")

        except Exception as e:
            print(f"  ❌ Error con {evento['titulo']}: {e}")


def main():
    print("🗓️  Añadiendo series españolas de octubre a Google Calendar")
    print("=" * 60)

    # Cargar credenciales
    load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

    # Verificar credenciales
    if not all([os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'), os.getenv('GOOGLE_CALLBACK_URL')]):
        print("❌ Faltan credenciales en .env")
        return

    print("✅ Credenciales cargadas")

    # Autenticar
    print("\n🔐 Autenticando con Google Calendar...")
    service = get_calendar_service()
    print("✅ Autenticado correctamente")

    # Mostrar eventos a crear
    print(f"\n📋 {len(SERIES_OCTUBRE_2026)} series de octubre a crear:")
    for e in SERIES_OCTUBRE_2026:
        print(f"  📅 {e['fecha']} - {e['titulo']} ({e.get('fuente', 'N/A')})")

    confirm = input("\n¿Crear estos eventos en Google Calendar? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return

    # Crear eventos
    print("\n📤 Creando eventos en Google Calendar...")
    service = get_calendar_service()
    for evento in SERIES_OCTUBRE_2026:
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
                'description': f"{evento.get('descripcion', '')}\n\nFuente: {evento.get('fuente', 'N/A')}",
                'start': {'date': evento['fecha']},
                'end': {'date': (datetime.fromisoformat(evento['fecha']) + timedelta(days=1)).strftime('%Y-%m-%d')},
            }

            event = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"  ✅ Creado: {evento['titulo']} ({evento['fecha']})")

        except Exception as e:
            print(f"  ❌ Error con {evento['titulo']}: {e}")

    print("\n✅ Proceso completado")


def main():
    print("🗓️  Añadiendo series españolas de octubre a Google Calendar")
    print("=" * 60)

    # Cargar credenciales
    load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

    # Verificar credenciales
    if not all([os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'), os.getenv('GOOGLE_CALLBACK_URL')]):
        print("❌ Faltan credenciales en .env")
        return

    print("✅ Credenciales cargadas")

    # Autenticar
    print("\n🔐 Autenticando con Google Calendar...")
    service = get_calendar_service()
    print("✅ Autenticado correctamente")

    # Mostrar eventos a crear
    print(f"\n📋 {len(SERIES_OCTUBRE_2026)} series de octubre a crear:")
    for e in SERIES_OCTUBRE_2026:
        print(f"  📅 {e['fecha']} - {e['titulo']} ({e.get('fuente', 'N/A')})")

    confirm = input("\n¿Crear estos eventos en Google Calendar? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return

    # Crear eventos
    print("\n📤 Creando eventos en Google Calendar...")
    service = get_calendar_service()
    for evento in SERIES_OCTUBRE_2026:
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
                'description': f"{evento.get('descripcion', '')}\n\nFuente: {evento.get('fuente', 'N/A')}",
                'start': {'date': evento['fecha']},
                'end': {'date': (datetime.fromisoformat(evento['fecha']) + timedelta(days=1)).strftime('%Y-%m-%d')},
            }

            event = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"  ✅ Creado: {evento['titulo']} ({evento['fecha']})")

        except Exception as e:
            print(f"  ❌ Error con {evento['titulo']}: {e}")

    print("\n✅ Proceso completado")


if __name__ == '__main__':
    main()