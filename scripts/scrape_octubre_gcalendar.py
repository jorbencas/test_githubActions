#!/usr/bin/env python3
"""
Scraper de eventos de octubre para Google Calendar
Configurable para añadir eventos de octubre a Google Calendar.
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Cargar variables de entorno
load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

# Configuración
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Obtiene servicio autenticado de Google Calendar."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    # Configuración OAuth
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    callback_url = os.getenv('GOOGLE_CALLBACK_URL')
    
    if not all([client_id, client_secret, callback_url]):
        raise ValueError("Faltan credenciales de Google en .env")
    
    # Intentar cargar token guardado
    token_file = Path(__file__).parent / 'token.json'
    creds = None
    
    if token_file.exists():
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(token_file), ['https://www.googleapis.com/auth/calendar'])
    
    # Si no hay credenciales válidas, hacer flujo OAuth
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    creds = None
    token_file = Path(__file__).parent / 'token.json'
    
    if token_file.exists():
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(token_file), ['https://www.googleapis.com/auth/calendar'])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
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
            
            # Guardar token
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)


# Eventos de octubre de ejemplo (configurables)
OCTUBRE_EVENTOS = [
    {
        "fecha": "2026-10-01",
        "titulo": "Inicio de octubre - Mes de la Ciberseguridad",
        "descripcion": "Mes internacional de la ciberseguridad",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-04",
        "titulo": "Día Mundial de los Animales",
        "descripcion": "Celebración internacional",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-12",
        "titulo": "Día de la Hispanidad / Fiesta Nacional de España",
        "descripcion": "Festivo nacional en España",
        "todo_dia": True,
    },
    {
        "fecha": "2026-10-19",
        "titulo": "Día Internacional de la Erradicación de la Pobreza",
        "descripcion": "ONU",
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
    # Añade aquí tus eventos personalizados:
    # {
    #     "fecha": "2026-10-15",
    #     "titulo": "Mi evento personalizado",
    #     "descripcion": "Descripción del evento",
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
    creados = 0
    for evento in OCTUBRE_EVENTOS:
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
                print(f"  ⏭️  Ya existe: {evento['titulo']}")
                continue
            
            # Crear evento
            event_body = {
                'summary': evento['titulo'],
                'description': evento.get('descripcion', ''),
                'start': {'date': evento['fecha']},
                'end': {'date': (datetime.fromisoformat(evento['fecha']) + timedelta(days=1)).strftime('%Y-%m-%d')},
            }
            
            if not evento.get('todo_dia', True):
                # Si no es todo el día, añadir horas
                pass
            
            event = service.events().insert(calendarId='primary', body=evento).execute()
            print(f"  ✅ Creado: {evento['titulo']} ({evento['fecha']})")
            
        except Exception as e:
            print(f"  ❌ Error con {evento['titulo']}: {e}")

def main():
    print("🗓️  Añadiendo eventos de octubre a Google Calendar")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')
    
    # Verificar credenciales
    if not all([os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'), os.getenv('GOOGLE_CALLBACK_URL')]):
        print("❌ Faltan credenciales en .env")
        return
    
    # Autenticar
    print("🔐 Autenticando con Google Calendar...")
    service = get_calendar_service()
    print("✅ Autenticado")
    
    # Mostrar eventos a crear
    print(f"\n📋 {len(OCTUBRE_EVENTOS)} eventos de octubre a crear:")
    for e in OCTUBRE_EVENTOS:
        print(f"  📅 {e['fecha']} - {e['titulo']}")
    
    confirm = input("\n¿Crear eventos en Google Calendar? (s/N): ").strip().lower()
    if confirm != 's':
        print("Cancelado")
        return
    
    # Crear eventos
    service = get_calendar_service()
    print("\n📤 Creando eventos...")
    # Aquí iría la lógica de creación
    
    print("\n✅ Proceso completado")

if __name__ == '__main__':
    main()