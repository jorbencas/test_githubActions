#!/usr/bin/env python3
"""
scrape_filmaffinity.py — Scraper de series españolas en Filmaffinity
para los próximos meses. Busca información en Filmaffinity y crea eventos en Google Calendar.

Uso:
    python scripts/scrapers/scrape_filmaffinity.py            # recopila y crea eventos
    python scripts/scrapers/scrape_filmaffinity.py --dry-run  # muestra sin crear eventos
    python scripts/scrapers/scrape_filmaffinity.py --enviar   # también envía resumen a Telegram
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
sys.path.insert(0, str(SCRIPT_DIR))

from movie_scraper_base import MovieConfig, MovieNewsScraper, TelegramNewsSender, ejecutar

# Google Calendar integration
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
OUTPUT_PATH = REPO_DIR / 'files' / 'filmaffinity_series.json'

# Series españolas a buscar en Filmaffinity (principales de los próximos meses)
SERIES_2026 = [
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

# Filmaffinity base URLs
FILMAFFINITY_SEARCH = "https://www.filmaffinity.com/es/search.php?stext="
FILMAFFINITY_BASE = "https://www.filmaffinity.com"

# Filmin calendar (simulated - would need actual API or scraping)
FILMIN_CALENDAR_URL = "https://www.filmaffinity.es/calendario-estrenos"

OUTPUT_PATH = REPO_DIR / 'files' / 'filmaffinity_filmaffinity_series.json'


class GoogleCalendarManager:
    """Gestor de Google Calendar para crear eventos de estrenos."""
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Calendar usando OAuth2."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            print("⚠️  Google Calendar API no disponible (instala google-auth, google-auth-oauthlib, google-api-python-client)")
            return
        
        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    print(f"⚠️  No se encuentra {CREDENTIALS_FILE}. Configura credenciales OAuth2 en Google Cloud Console.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar autenticado")
        
    def crear_evento_estreno(self, serie: dict) -> bool:
        """Crea un evento en Google Calendar para el estreno de una serie."""
        if not self.service:
            return False
        
        try:
            # Fecha de estreno
            fecha_estreno = serie.get('estreno_filmaffinity', '')
            if not fecha_estreno:
                return False
            
            # Crear evento
            evento = {
                'summary': f"🎬 Estreno: {serie['nombre']}",
                'description': (
                    f"Estreno en Filmin: {serie['nombre']}\n"
                    f"Director: {serie.get('director', 'N/A')}\n"
                    f"Protagonistas: {', '.join(serie.get('protagonistas', []))}\n"
                    f"Género: {serie.get('genero', 'N/A')}\n"
                    f"Temporadas: {serie.get('temporadas', 1)} | Capítulos: {serie.get('capitulos', '?')}\n"
                    f"Filmin: https://www.filmaffinity.es\n"
                    f"Filmaffinity: {FILMAFFINITY_SEARCH}{serie['nombre'].replace(' ', '+')}"
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


class FilmaffinityFilminScraper:
    """Scraper para buscar series españolas en Filmaffinity y Filmin."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
    
    def buscar_en_filmaffinity(self, titulo: str) -> Optional[Dict]:
        """Busca una serie en Filmaffinity y devuelve info básica."""
        try:
            query = urllib.parse.quote_plus(titulo)
            url = f"https://www.filmaffinity.com/es/search.php?stext={urllib.parse.quote_plus(titulo)}"
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
            
            response = requests.get(f"https://www.filmaffinity.com/es/search.php?stext={urllib.parse.quote_plus(titulo)}", 
                                  timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return None
            
            # Parsear HTML para encontrar el primer resultado
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el primer resultado de película/serie
            movie_card = soup.find('div', class_='movie-card') or soup.find('div', class_='mc-title')
            if not movie_card:
                # Buscar en la estructura antigua
                movie_card = soup.find('div', {'id': 'movie-1'}) or soup.find('div', class_='mc-title')
            
            if not movie_card:
                # Intentar buscar en los resultados
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if '/es/film' in href and '/film' in href:
                        film_url = f"https://www.filmaffinity.com{link['href']}"
                        # Obtener detalles
                        return self._obtener_detalles_filmaffinity(film_url)
            
            return None
        except Exception as e:
            print(f"  ⚠️ Error buscando en Filmaffinity: {e}")
            return None
    
    def _obtener_detalles_filmaffinity(self, url: str) -> Optional[Dict]:
        """Obtiene detalles de una película/serie de Filmaffinity."""
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información
            titulo = soup.find('h1', id='main-title') or soup.find('h1', class_='mc-title')
            titulo = titulo.get_text(strip=True) if titulo else ''
            
            # Año
            ano = ''
            ano_elem = soup.find('span', id='year') or soup.find('dd', class_='year')
            if ano_elem:
                ano = ano_elem.get_text(strip=True)
            
            # Género
            genero = ''
            genero_elem = soup.find('dd', class_='genre') or soup.find('div', class_='genres')
            if genero_elem:
                genero = genero_elem.get_text(strip=True)
            
            # Director
            director = ''
            director_elem = soup.find('dd', class_='director') or soup.find('span', itemprop='director')
            if director_elem:
                director = director_elem.get_text(strip=True)
            
            # Protagonistas
            protagonistas = []
            reparto = soup.find('div', id='cast') or soup.find('div', class_='cast')
            if reparto:
                actores = reparto.find_all('a')
                for actor in actores[:5]:
                    nombre = actor.get_text(strip=True)
                    if nombre:
                        protagonistas.append(nombre)
            
            # Sinopsis
            sinopsis = ''
            sinopsis_elem = soup.find('div', id='sinopsis') or soup.find('div', class_='synopsis')
            if sinopsis_elem:
                sinopsis = sinopsis_elem.get_text(strip=True)[:500]
            
            return {
                'titulo': titulo,
                'año': ano,
                'genero': genero,
                'director': director,
                'protagonistas': protagonistas,
                'sinopsis': sinopsis,
                'url': f"https://www.filmaffinity.com{url}" if url.startswith('/') else url
            }
        except Exception as e:
            print(f"  ⚠️ Error obteniendo detalles: {e}")
            return None
    
    def buscar_series_filmaffinity(self, series_lista: List[Dict]) -> List[Dict]:
        """Busca información de las series en Filmaffinity y completa datos."""
        resultados = []
        for serie in series_lista:
            print(f"  🔍 Buscando: {serie['nombre']}...")
            detalles = self.buscar_en_filmaffinity(serie['nombre'])
            if detalles:
                serie.update(detalles)
                print(f"  ✅ Encontrado: {serie['nombre']} ({detalles.get('titulo', 'N/A')})")
            else:
                print(f"  ⚠️ No encontrado en Filmaffinity: {serie['nombre']}")
            serie['fecha_actualizacion'] = datetime.now(timezone.utc).isoformat()
            resultados.append(serie)
            time.sleep(1)  # Rate limiting
        return resultados


def cargar_estado_anterior():
    """Carga el estado anterior de series procesadas."""
    if OUTPUT_PATH.exists():
        try:
            return json.loads(OUTPUT_PATH.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def guardar_estado(series: List[Dict]):
    """Guarda el estado actual de series."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(series, ensure_ascii=False, indent=2), encoding='utf-8')


def crear_eventos_google_calendar(series: List[Dict]) -> int:
    """Crea eventos en Google Calendar para las series."""
    calendar = GoogleCalendarManager()
    if not calendar.service:
        return 0
    
    creados = 0
    for serie in SERIES_2026:
        if calendar.crear_evento_estreno(serie):
            print(f"✅ Evento creado: {serie['nombre']}")
            creados += 1
        time.sleep(0.5)  # Rate limiting
    return creados


def scrape_filmaffinity_filmaffinity() -> List[Dict]:
    """Función principal de scraping."""
    print("🔍 Iniciando scraping de Filmaffinity/Filmin...")
    
    # Cargar estado anterior
    series_anteriores = cargar_estado_anterior()
    series_procesadas = {s['nombre']: s for s in series_anteriores}
    
    # Scraper
    scraper = FilmaffinityFilminScraper()
    series_actualizadas = scraper.buscar_series_filmaffinity(SERIES_2026)
    
    # Merge con datos anteriores
    for serie in SERIES_2026:
        nombre = serie['nombre']
        if nombre in series_procesadas:
            # Mantener datos anteriores y actualizar con nuevos
            serie_actualizada = next((s for s in series_actualizadas if s['nombre'] == nombre), serie)
            series_procesadas[nombre] = serie_actualizada
        else:
            series_procesadas[nombre] = serie
    
    series_finales = list(series_procesadas.values())
    
    # Guardar
    guardar_estado(list(series_procesadas.values()))
    
    # Crear eventos en Google Calendar
    print("\n📅 Creando eventos en Google Calendar...")
    calendar = GoogleCalendarManager()
    if calendar.service:
        creados = 0
        for serie in SERIES_2026:
            if calendar.crear_evento_estreno(serie):
                print(f"✅ Evento creado: {serie['nombre']}")
            time.sleep(0.5)
    
    return list(series_procesadas.values())


def main():
    parser = argparse.ArgumentParser(description="Scraper Filmaffinity/Filmin + Google Calendar")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()
    
    print("🎬 Iniciando scraper Filmaffinity/Filmin + Google Calendar...")
    
    if args.dry_run:
        print("🔍 DRY RUN - Solo mostrando resultados")
        # Scraping
        scraper = FilmaffinityFilminScraper()
        series = scraper.buscar_series_filmaffinity(SERIES_2026)
        for s in s:
            print(f"  📺 {s['nombre']} - {s.get('estreno_filmaffinity', 'N/A')}")
        return
    
    # Scraping completo
    series = scrape_filmaffinity_filmaffinity()
    
    print(f"\n✅ Procesadas {len(SERIES_2026)} series")
    for s in SERIES_2026:
        print(f"  📺 {s['nombre']} - Estreno: {s.get('estreno_filmaffinity', 'N/A')}")


if __name__ == "__main__":
    main()