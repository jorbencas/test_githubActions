#!/usr/bin/env python3
"""
google_calendar_filmaffinity.py — Gestor de Google Calendar para estrenos de Filmin/Filmaffinity.
Crea eventos en Google Calendar para los estrenos de series españolas en Filmin.

Uso:
    python google_calendar_filmaffinity.py            # Crea eventos para series configuradas
    python google_calendar_filmaffinity.py --dry-run  # Muestra qué eventos crearía
    python google_calendar_filmaffinity.py --test     # Prueba la conexión
"""
import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

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
REPO_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = REPO_DIR / 'config' / 'google_credentials.json'
TOKEN_FILE = REPO_DIR / 'config' / 'google_token.json'

# Series configuradas (mismo que en scrape_filmaffinity_filmaffinity.py)
SERIES_FILMIN_2026 = [
    {
        "nombre": "El tiempo que te doy",
        "director": "Marina Pérez",
        "protagonistas": ["Nadia de Santiago", "Álvaro Cervantes"],
        "estreno_filmaffinity": "2026-01-15",
        "temporadas": 1,
        "capitulos": 10,
        "genero": "Drama romántico",
    },
    {
        "nombre": "El cuerpo en llamas",
        "director": "Jorge Torregrossa",
        "protagonistas": ["Úrsula Corberó", "Quim Gutiérrez"],
        "estreno_filmaffinity": "2026-02-01",
        "temporadas": 1,
        "capitulos": 8,
        "genero": "True crime / Thriller",
    },
    {
        "nombre": "La chica de nieve",
        "director": "David Ulloa",
        "protagonistas": ["Milena Smit", "José Coronado"],
        "estreno_filmaffinity": "2026-03-01",
        "temporadas": 1,
        "capitulos": 6,
        "genero": "Thriller",
    },
    {
        "nombre": "Reina Roja",
        "director": "Koldo Serra",
        "protagonistas": ["Vicky Luengo", "Hovik Keuchkerian"],
        "estreno_filmaffinity": "2026-02-29",
        "temporadas": 1,
        "capitulos": 7,
        "genero": "Thriller policial",
    },
    {
        "nombre": "El caso Asunta",
        "director": "Carlos Sedes",
        "protagonistas": ["Candela Peña", "Tristán Ulloa"],
        "estreno_filmaffinity": "2026-04-15",
        "temporadas": 1,
        "capitulos": 6,
        "genero": "True crime",
    },
    {
        "nombre": "El caso Alcásser",
        "director": "Gerardo Herrero",
        "protagonistas": ["Ana Polvorosa", "Fernando Cayo"],
        "estreno_filmaffinity": "2026-05-01",
        "temporadas": 1,
        "capitulos": 5,
        "genero": "True crime / Documental",
    },
    {
        "nombre": "El fotógrafo de Mauthausen",
        "director": "Mar Targarona",
        "protagonistas": ["Mario Casas", "Macarena Gómez"],
        "estreno_filmaffinity": "2026-03-15",
        "temporadas": 1,
        "capitulos": 4,
        "genero": "Drama histórico",
    },
    {
        "nombre": "El corazón del océano",
        "director": "Pablo Barrera",
        "protagonistas": ["Clara Lago", "Álvaro Morte"],
        "estreno_filmaffinity": "2026-05-01",
        "temporadas": 1,
        "capitulos": 6,
        "genero": "Drama de época",
    },
    {
        "nombre": "Entre tierras",
        "director": "Carlos de Pando",
        "protagonistas": ["Megan Montaner", "Unax Ugalde"],
        "estreno_filmaffinity": "2026-06-01",
        "temporadas": 1,
        "capitulos": 8,
        "genero": "Drama romántico / Época",
    },
    {
        "nombre": "Los ilusos 13+13",
        "director": "Jonás Trueba",
        "protagonistas": ["Aura Garrido", "Francesc Garrido"],
        "estreno_filmaffinity": "2026-09-03",
        "temporadas": 1,
        "capitulos": 1,
        "genero": "Drama / Metacine",
    },
]

# Configuración Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
REPO_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_DIR / 'config'
CREDENTIALS_FILE = CONFIG_DIR / 'google_credentials.json'
TOKEN_FILE = CONFIG_DIR / 'google_token.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

FILMAFFINITY_SEARCH = "https://www.filmaffinity.com/es/search.php?stext="


class GoogleCalendarManager:
    """Gestor de Google Calendar para crear eventos de estrenos."""
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Calendar usando OAuth2."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            print("⚠️  Google Calendar API no disponible")
            print("   Instala: pip install google-auth google-auth-oauthlib google-api-python-client")
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
                    print("   1. Ve a https://console.cloud.google.com/")
                    print("   2. Crea un proyecto y habilita Google Calendar API")
                    print("   3. Crea credenciales OAuth 2.0 (tipo 'Aplicación de escritorio')")
                    print(f"   4. Descarga el JSON y guárdalo como {CREDENTIALS_FILE}")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar autenticado correctamente")
    
    def crear_evento_estreno(self, serie: dict) -> bool:
        """Crea un evento en Google Calendar para el estreno de una serie."""
        if not self.service:
            return False
        
        try:
            fecha_estreno = serie.get('estreno_filmaffinity', '')
            if not fecha_estreno:
                print(f"  ⚠️  {serie['nombre']}: Sin fecha de estreno")
                return False
            
            # Validar fecha
            try:
                datetime.fromisoformat(fecha_estreno)
            except ValueError:
                print(f"  ⚠️  {serie['nombre']}: Fecha inválida '{fecha_estreno}'")
                return False
            
            protagonistas_str = ', '.join(serie.get('protagonistas', []))
            
            evento = {
                'summary': f"🎬 Estreno Filmin: {serie['nombre']}",
                'description': (
                    f"🎬 Estreno en Filmin: {serie['nombre']}\n\n"
                    f"📅 Fecha: {serie.get('estreno_filmaffinity', 'N/A')}\n"
                    f"🎭 Género: {serie.get('genero', 'N/A')}\n"
                    f"🎬 Director: {serie.get('director', 'N/A')}\n"
                    f"👥 Protagonistas: {', '.join(serie.get('protagonistas', ['N/A']))}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n\n"
                    f"🔗 Filmin: https://www.filmaffinity.es\n"
                    f"🎭 Filmaffinity: https://www.filmaffinity.com/es/search.php?stext={serie['nombre'].replace(' ', '+')}\n"
                    f"📺 Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n"
                    f"Género: {serie.get('genero', 'N/A')}"
                ),
                'start': {
                    'date': serie.get('estreno_filmaffinity'),
                    'timeZone': 'Europe/Madrid',
                },
                'end': {
                    'date': (datetime.fromisoformat(serie.get('estreno_filmaffinity')) + timedelta(days=1)).date().isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 día antes
                        {'method': 'popup', 'minutes': 60},       # 1 hora antes
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
            print(f"❌ Error creando evento para {serie['nombre']}: {e}")
            return False
    
    def listar_eventos_proximos(self, dias: int = 30) -> List[Dict]:
        """Lista eventos próximos en el calendario."""
        if not self.service:
            return []
        
        try:
            ahora = datetime.now(timezone.utc).isoformat()
            futuro = (datetime.now(timezone.utc) + timedelta(days=dias)).isoformat()
            
            eventos = self.service.events().list(
                calendarId='primary',
                timeMin=ahora,
                timeMax=futuro,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return eventos.get('items', [])
        except Exception as e:
            print(f"❌ Error listando eventos: {e}")
            return []
    
    def eliminar_eventos_antiguos(self, dias_atras: int = 30) -> int:
        """Elimina eventos pasados más antiguos que X días."""
        if not self.service:
            return 0
        
        try:
            limite = datetime.now(timezone.utc) - timedelta(days=dias_atras)
            limite_iso = limite.isoformat()
            
            eventos = self.service.events().list(
                calendarId='primary',
                timeMax=limite_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            eliminados = 0
            for evento in eventos.get('items', []):
                try:
                    self.service.events().delete(
                        calendarId='primary',
                        eventId=evento['id']
                    ).execute()
                    eliminados += 1
                except Exception:
                    pass
            
            print(f"🗑️ Eliminados {eliminados} eventos antiguos (> {dias_atras} días)")
            return eliminados
        except Exception as e:
            print(f"❌ Error eliminando eventos: {e}")
            return 0


def test_conexion():
    """Prueba la conexión a Google Calendar."""
    print("🔍 Probando conexión a Google Calendar...")
    
    if not GOOGLE_CALENDAR_AVAILABLE:
        print("❌ Librerías de Google Calendar no instaladas")
        print("   Ejecuta: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    
    calendar = GoogleCalendarManager()
    if calendar.service:
        print("✅ Conexión exitosa a Google Calendar")
        
        # Listar próximos eventos
        eventos = calendar.listar_eventos_proximos(7)
        if eventos:
            print(f"\n📅 Próximos eventos (7 días):")
            for evento in eventos[:5]:
                inicio = evento['start'].get('dateTime', evento['start'].get('date'))
                print(f"  📅 {inicio} - {evento.get('summary', 'Sin título')}")
        else:
            print("\n📅 No hay eventos próximos (7 días)")
        return True
    else:
        print("❌ No se pudo autenticar")
        return False


def crear_todos_eventos():
    """Crea eventos para todas las series configuradas."""
    print("🎬 Creando eventos de estrenos de Filmin en Google Calendar...")
    
    calendar = GoogleCalendarManager()
    if not calendar.service:
        return
    
    creados = 0
    for serie in SERIES_FILMIN_2026:
        print(f"  🎬 Procesando: {serie['nombre']}...")
        if calendar.crear_evento_estreno(serie):
            print(f"  ✅ Creado: {serie['nombre']} ({serie.get('estreno_filmaffinity')})")
        else:
            print(f"  ❌ Error: {serie['nombre']}")
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n✅ Creados {creados}/{len(SERIES_FILMIN_2026)} eventos")


def main():
    parser = argparse.ArgumentParser(description="Gestor de Google Calendar para estrenos Filmin")
    parser.add_argument("--dry-run", action="store_true", help="Muestra qué eventos crearía sin crearlos")
    parser.add_argument("--test", action="store_true", help="Prueba la conexión")
    parser.add_argument("--crear-todos", action="store_true", help="Crea todos los eventos configurados")
    parser.add_argument("--listar", type=int, default=7, help="Lista eventos próximos (días)")
    parser.add_argument("--limpiar", type=int, help="Elimina eventos antiguos (días)")
    
    args = parser.parse_args()
    
    if args.test:
        test_conexion()
        return
    
    if args.dry_run:
        print("🔍 DRY RUN - Eventos que se crearían:")
        for serie in SERIES_FILMIN_2026:
            print(f"  📅 {serie['nombre']} - {serie.get('estreno_filmaffinity', 'N/A')} ({serie.get('genero', 'N/A')})")
        return
    
    if args.listar:
        calendar = GoogleCalendarManager()
        if calendar.service:
            eventos = calendar.listar_eventos_proximos(args.listar)
            print(f"📅 Eventos próximos ({args.listar} días):")
            for evento in eventos:
                inicio = evento['start'].get('dateTime', evento['start'].get('date'))
                print(f"  📅 {inicio} - {evento.get('summary', 'Sin título')}")
        return
    
    if args.limpiar:
        calendar = GoogleCalendarManager()
        if calendar.service:
            calendar.eliminar_eventos_antiguos(args.limpiar)
        return
    
    if args.crear_todos:
        crear_todos_eventos()
        return
    
    # Por defecto: test
    test_conexion()


if __name__ == "__main__":
    main()