#!/usr/bin/env python3
"""
scrape_nueve_reinas.py — Configuración y entry point del buscador de noticias
sobre la serie "Nueve reinas" (Netflix, 2027), adaptación de la película argentina
de Fabián Bielinsky, con Álvaro Morte, Patrick Criado y Aura Garrido.

El motor genérico (MovieNewsScraper, relevancia, Telegram, etc.) está en
movie_scraper_base.py (SOLID: SRP + OCP + DIP). Este módulo solo define la
configuración específica de "Nueve reinas".

La salida se acumula (deduplicada por URL) en files/nueve_reinas.json.

Uso:
    python scripts/scrapers/scrape_nueve_reinas.py            # recopila y archiva
    python scripts/scrapers/scrape_nueve_reinas.py --dry-run  # muestra sin guardar
    python scripts/scrapers/scrape_nueve_reinas.py --enviar   # además envía resumen a Telegram
"""
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from movie_scraper_base import (
    MovieConfig, MovieNewsScraper, TelegramNewsSender, ejecutar,
)

OUTPUT_PATH = REPO_DIR / "files" / "nueve_reinas.json"


def _ia_prompt_nueve_reinas(numerados: str) -> str:
    return (
        "Eres un experto en cine/series. Determina cuáles de los siguientes titulares se refieren "
        "EXCLUSIVAMENTE a la serie de Netflix 'Nueve reinas' (2027), adaptación de la película "
        "argentina de Fabián Bielinsky (2000), con Álvaro Morte y Patrick Criado, ambientada "
        "en el Madrid de 2012.\n"
        "NO cuentan: la película original argentina del 2000, la remake estadounidense 'Criminal' "
        "(2004), la versión india 'Bluffmaster' (2005), ni otros proyectos no relacionados.\n"
        "SÍ cuentan: noticias sobre el rodaje, casting, estreno, tráiler, críticas, entrevistas, "
        "fotografías de rodaje,Avances de la serie.\n"
        "Responde SOLO con la lista de números de los titulares que SÍ son sobre esta serie, "
        "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
        f"{numerados}"
    )


NUEVE_REINAS_CONFIG = MovieConfig(
    pelicula="Nueve reinas",
    pelicula_es="Nueve reinas",
    output_path=OUTPUT_PATH,
    queries=[
        "Nueve reinas Netflix serie",
        "Nueve reinas Netflix 2027",
        "Nueve reinas Álvaro Morte",
        "Nueve reinas Patrick Criado",
        "Nueve reinas Aura Garrido",
        "Nueve reinas José Coronado",
        "Nueve reinas Netflix rodaje",
        "Nueve reinas Netflix estreno",
        "Nueve reinas serie argentina Netflix",
        "Nueve reinas adaptación Netflix",
        "Nueve reinas Madrid Netflix",
        "Nueve reinas Netflix tráiler",
        "Nueve reinas Netflix crítica",
        "Nine Queens Netflix series",
        "Nine Queens Netflix 2027",
    ],
    queries_extra=[
        "Nueve reinas Netflix reparto",
        "Nueve reinas Netflix guion",
        "Nueve reinas Netflix productora LAZONA",
        "Nueve reinas Netflix Xosé Morais",
        "Nueve reinas Netflix Álex Rodrigo",
        "Nueve reinas Netflix Jorge Saavedra",
        "Nueve reinas sellos falsificados Netflix",
        "Nueve reinas estafadores Netflix",
        "Nueve reinas crisis económica Netflix",
    ],
    yt_queries=[
        "Nueve reinas Netflix",
        "Nueve reinas serie Netflix",
        "Nueve reinas Álvaro Morte Netflix",
    ],
    contraste_queries=[
        "Nueve reinas",
        "Nueve reinas Netflix",
    ],
    sitios_resenias=[
        ("decine21.com", "Nueve reinas Netflix"),
        ("filmaffinity.com", "Nueve reinas Netflix"),
        ("sensacine.com", "Nueve reinas Netflix"),
        ("ecartelera.com", "Nueve reinas Netflix"),
        ("fotogramas.es", "Nueve reinas Netflix"),
        ("espinof.com", "Nueve reinas Netflix"),
        ("cinemaldito.com", "Nueve reinas Netflix"),
        ("aullidos.com", "Nueve reinas Netflix"),
        ("cinemania", "Nueve reinas Netflix"),
        ("hipertextual.com", "Nueve reinas Netflix"),
        ("eldiario.es", "Nueve reinas Netflix"),
        ("rtve.es", "Nueve reinas Netflix"),
        ("europapress.es", "Nueve reinas Netflix"),
        ("elpais.com", "Nueve reinas Netflix"),
        ("elmundo.es", "Nueve reinas Netflix"),
        ("20minutos.es", "Nueve reinas Netflix"),
        ("lavanguardia.com", "Nueve reinas Netflix"),
        ("abc.es", "Nueve reinas Netflix"),
        ("reddit.com", "Nueve reinas Netflix"),
        ("imdb.com", "Nueve reinas Netflix"),
        ("themoviedb.org", "Nueve reinas Netflix"),
    ],
    redes_sociales=[
        "Netflix España Nueve reinas",
        "Netflix Nueve reinas Instagram",
        "Netflix Nueve reinas Twitter",
        "Álvaro Morte Nueve reinas",
        "Patrick Criado Nueve reinas",
        "Aura Garrido Nueve reinas",
    ],
    filmaffinity_queries=[
        "site:filmaffinity.com Nueve reinas Netflix",
        "filmaffinity Nueve reinas Netflix serie",
    ],
    fuentes_cine_directas=[
        {"url": "https://www.cinemaldito.com/?s=nueve+reinas+netflix", "selector": "article a[href]", "medio": "Cinemaldito"},
        {"url": "https://www.aullidos.com/?s=nueve+reinas+netflix", "selector": "article a[href]", "medio": "Aullidos"},
        {"url": "https://www.ecartelera.com/buscar/?q=nueve+reinas+netflix", "selector": "a[href*='/peliculas/']", "medio": "ECartelera"},
        {"url": "https://www.sensacine.com/buscar/?q=nueve+reinas+netflix", "selector": "a[href*='/peliculas/']", "medio": "SensaCine"},
        {"url": "https://www.espinof.com/buscar/?s=nueve+reinas+netflix", "selector": "article a[href]", "medio": "Espinof"},
        {"url": "https://www.cinemania.es/?s=nueve+reinas+netflix", "selector": "article a[href]", "medio": "Cinemania"},
    ],
    senales_fuertes=[
        "nueve reinas", "nine queens", "netflix", "álvaro morte", "alvaro morte",
        "patrick criado", "aura garrido", "josé coronado", "jose coronado",
        "lazona", "xosé morais", "victor sierra", "álex Rodrigo", "jorge saavedra",
        "sellos falsificados", "estafadores", "madrid 2012", "crisis económica",
        "fabian bielinsky", "bielinsky",
    ],
    senales_cine=[
        "serie", "series", "netflix", "estreno", "rodaje", "filmando",
        "tráiler", "trailer", "reparto", "director", "dirección",
        "crítica", "critica", "reseña", "review", "capítulo", "episodio",
        "temporada", "showrunner", "guion", "producción",
    ],
    senales_negativas=[
        "película original", "pelicula original", "ricardo darín", "ricardo darin",
        "gastón pauls", "gaston pauls", "leticia brédice", "leticia bredice",
        "criminal 2004", "bluffmaster 2005", "john c. reilly", "diego luna",
        "fabián bielinsky muerte", "fallecimiento bielinsky",
        "remake argentino", "versión original",
    ],
    anios_otros=[
        "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007",
        "2008", "2009", "2010", "2011", "2013", "2014", "2015", "2016",
        "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",
    ],
    umbral_positivas=2,
    titulos_clave=(
        "nueve reinas", "nine queens", "álvaro morte", "alvaro morte",
        "patrick criado", "aura garrido", "josé coronado", "jose coronado",
        "netflix", "lazona",
    ),
    clasificador=[
        ("trailer", ["tráiler", "trailer", "trailer oficial", "teaser"]),
        ("poster", ["póster", "poster", "cartel"]),
        ("entrevista", ["entrevista", "interview"]),
        ("critica", ["crítica", "critica", "reseña", "review", "críticas"]),
        ("foto", ["foto", "fotograf", "imágenes", "imagenes", "imagen", "fotograma"]),
        ("video", ["vídeo", "video", "clip"]),
        ("noticia", ["estreno", "rodaje", "se anuncia", "producción", "casting"]),
    ],
    ia_prompt=_ia_prompt_nueve_reinas,
    ia_model="gemini-2.5-flash",
    regla_extra=None,
    filtro_adulto=[],
)


def main():
    parser = argparse.ArgumentParser(description="Recopila info sobre la serie Nueve reinas (Netflix)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()

    scraper = MovieNewsScraper(NUEVE_REINAS_CONFIG)
    notifier = TelegramNewsSender()

    ejecutar(scraper, dry_run=args.dry_run, enviar=args.enviar, notifier=notifier)


if __name__ == "__main__":
    main()
