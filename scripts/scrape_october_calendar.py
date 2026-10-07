#!/usr/bin/env python3
"""
Scraper de eventos de octubre para Google Calendar
Extrae eventos de octubre desde events.json (Tech Timeline) y los añade a Google Calendar.
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

# Cargar variables de entorno del proyecto mecano_prueba_web
load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')

# Configuración
SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
EVENTS_FILE = REPO_DIR / 'public' / 'data' / 'events.json'
TOKEN_FILE = Path(__file__).parent / 'token.json'

# Scopes para Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_credentials():
    """Obtiene credenciales OAuth2 de Google Calendar."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    callback_url = os.getenv('GOOGLE_CALLBACK_URL')
    
    if not all([client_id, client_secret, callback_url]):
        raise ValueError("Faltan credenciales de Google en .env")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "redirect_uris": [callback_url],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    
    return flow

def get_calendar_service():
    """Obtiene servicio autenticado de Google Calendar."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    # Intentar cargar token guardado
    token_file = Path(__file__).parent / 'token.json'
    creds = None
    
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), ['https://www.googleapis.com/auth/calendar'])
    
    # Si no hay credenciales válidas, hacer flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_config(
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
            flow.redirect_uri = os.getenv('GOOGLE_CALLBACK_URL')
            creds = flow.run_local_server(port=0)
            
            # Guardar token
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def load_october_events():
    """Carga eventos de octubre desde events.json."""
    events_file = Path(__file__).parent.parent / 'public' / 'data' / 'events.json'
    
    if not Path(EVENTS_FILE).exists():
        raise FileNotFoundError(f"No se encuentra {EVENTS_FILE}")
    
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        all_events = json.load(f)
    
    # Filtrar eventos de octubre (mes 10) de cualquier año
    october_events = []
    for event in all_events:
        try:
            # El campo de fecha puede variar, probar varios campos
            date_str = event.get('date') or event.get('date_start') or event.get('start_date') or ''
            if not date_str:
                continue
            
            # Parsear fecha (formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            date_part = date_str.split('T')[0]
            event_date = datetime.fromisoformat(date_part)
            
            if event_date.month == 10:  # Octubre
                event_data = {
                    'summary': event.get('title', 'Evento sin título'),
                    'description': event.get('description', ''),
                    'start': {'date': event_date.date().isoformat()},
                    'end': {'date': (event_date + timedelta(days=1)).date().isoformat()},
                }
                
                # Añadir ubicación si existe
                if event.get('location'):
                    event_data['location'] = event['location']
                
                # Añadir URL si existe
                if event.get('url') or event.get('link'):
                    event_data['description'] = f"{event_data['description']}\n\nMás info: {event.get('url') or event.get('link')}"
                
                october_events.append(event_data)
        except (ValueError, TypeError) as e:
            print(f"⚠️  Evento con fecha inválida: {event.get('title', 'Sin título')} - {e}")
            continue
    
    return october_events

def create_events_in_calendar(service, events, calendar_id='primary'):
    """Crea eventos en Google Calendar."""
    created = 0
    skipped = 0
    errors = 0
    
    for event in events:
        try:
            # Verificar si ya existe (buscar por título y fecha)
            existing = service.events().list(
                calendarId='primary',
                timeMin=event['start']['date'] + 'T00:00:00Z',
                timeMax=event['start']['date'] + 'T23:59:59Z',
                q=event['summary'],
                singleEvents=True
            ).execute()
            
            existing_events = existing.get('items', [])
            event_exists = False
            
            for existing_event in existing_events:
                if (existing_event.get('summary') == event['summary'] and 
                    existing_event.get('start', {}).get('date') == event['start']['date']):
                    event_exists = True
                    break
            
            if event_exists:
                print(f"  ⏭️  Ya existe: {event['summary']} ({event['start']['date']})")
                continue
            
            # Crear evento
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"  ✅ Creado: {event['summary']} ({event['start']['date']})")
            
        except HttpError as e:
            print(f"  ❌ Error creando '{event.get('summary', 'Sin título')}': {e}")
        except Exception as e:
            print(f"  ❌ Error inesperado: {e}")

def main():
    print("🗓️  Scraper de eventos de octubre para Google Calendar")
    print("=" * 60)
    
    # 1. Cargar credenciales
    load_dotenv('/home/jorge/dev/mecano_prueba_web/.env')
    
    # Verificar credenciales
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_CALLBACK_URL']
    missing = [var for var in ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_CALLBACK_URL'] if not os.getenv(var)]
    if missing:
        print(f"❌ Faltan variables en .env: {missing}")
        return
    
    print("✅ Credenciales cargadas")
    
    # 2. Obtener servicio de Calendar
    try:
        print("\n🔐 Autenticando con Google Calendar...")
        service = get_calendar_service()
        print("✅ Autenticado correctamente")
    except Exception as e:
        print(f"❌ Error autenticando: {e}")
        print("\n💡 Si es la primera vez, ejecuta: python scripts/calendar_setup.py --auth")
        return
    
    # 3. Cargar eventos de octubre
    print("\n📅 Cargando eventos de octubre...")
    october_events = load_october_events()
    print(f"📋 Encontrados {len(october_events)} eventos de octubre")
    
    if not october_events:
        print("⚠️  No hay eventos de octubre en events.json")
        return
    
    # Mostrar eventos a crear
    print("\n📋 Eventos a crear:")
    for event in october_events:
        print(f"  📅 {event['start']['date']} - {event['summary']}")
    
    # Confirmar
    confirm = input("\n¿Crear estos eventos en Google Calendar? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # 4. Crear eventos
    print("\n📤 Creando eventos en Google Calendar...")
    create_events_in_calendar(service, october_events)
    
    print("\n✅ Proceso completado")

if __name__ == '__main__':
    main()