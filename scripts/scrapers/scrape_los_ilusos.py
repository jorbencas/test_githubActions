#!/usr/bin/env python3
"""
scrape_los_ilusos.py — Configuración y entry point del buscador de noticias
sobre la película "Los ilusos 13+13" (2026), de Jonás Trueba, con Francesco Carril,
Aura Garrido y Vito Sanz.

El motor genérico (MovieNewsScraper, relevancia, Telegram, etc.) está en
movie_scraper_base.py (SOLID: SRP + OCP + DIP). Este módulo solo define la
configuración específica de "Los ilusos 13+13".

La salida se acumula (deduplicada por URL) en files/los_ilusos.json.

Uso:
    python scripts/scrapers/scrape_los_ilusos.py            # recopila y archiva
    python scripts/scrapers/scrape_los_ilusos.py --dry-run  # muestra sin guardar
    python scripts/scrapers/scrape_los_ilusos.py --enviar   # además envía resumen a Telegram
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

OUTPUT_PATH = REPO_DIR / "files" / "los_ilusos.json"


def _ia_prompt_los_ilusos(numerados: str) -> str:
    return (
        "Eres un experto en cine. De los siguientes titulares, identifica SOLO los que "
        "contengan información sobre la FECHA DE ESTRENO o DISPONIBILIDAD en una "
        "plataforma de streaming o venta digital de la película 'Los ilusos 13+13' (2026) "
        "de Jonás Trueba.\n"
        "NO cuentan: críticas, reseñas, entrevistas, tráilers, festivales, rodaje, "
        "noticias sobre el director, ni nada que no sea una fecha concreta de estreno "
        "en plataforma (Filmin, Netflix, Amazon, Apple TV, etc.).\n"
        "SÍ cuentan: 'se estrena en Filmin el X', 'disponible en Netflix desde X', "
        "'estreno digital el X', ' sale en plataforma X'.\n"
        "Si ningún titular contiene una fecha de estreno en plataforma, responde: NINGUNO\n"
        "Responde SOLO con la lista de números de los titulares que SÍ son relevantes, "
        "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
        f"{numerados}"
    )


LOS_ILUSOS_CONFIG = MovieConfig(
    pelicula="Los ilusos 13+13",
    pelicula_es="Los ilusos 13+13",
    output_path=OUTPUT_PATH,
    queries=[
        "Los ilusos 13+13 estreno plataforma",
        "Los ilusos 13+13 Filmin",
        "Los ilusos 13+13 Netflix",
        "Los ilusos 13+13 Amazon Prime Video",
        "Los ilusos 13+13 Apple TV",
        "Los ilusos 13+13 digital",
        "Los ilusos 13+13 streaming",
        "Los ilusos 13+13 disponible",
    ],
    queries_extra=[
        "Los ilusos 13+13 estreno octubre",
        "Los ilusos 13+13 estreno noviembre",
        "Los ilusos 13+13 venta digital",
        "Los ilusos 13+13 VOD",
    ],
    yt_queries=[
        "Los ilusos 13+13",
        "Los ilusos 13+13 Jonás Trueba",
        "Los ilusos 13+13 tráiler",
    ],
    contraste_queries=[
        "Los ilusos 13+13",
        "Los ilusos Trueba",
    ],
    sitios_resenias=[
        ("decine21.com", "Los ilusos 13+13"),
        ("filmaffinity.com", "Los ilusos 13+13"),
        ("sensacine.com", "Los ilusos 13+13"),
        ("ecartelera.com", "Los ilusos 13+13"),
        ("fotogramas.es", "Los ilusos 13+13"),
        ("espinof.com", "Los ilusos 13+13"),
        ("cinemaldito.com", "Los ilusos 13+13"),
        ("aullidos.com", "Los ilusos 13+13"),
        ("cinemania", "Los ilusos 13+13"),
        ("hipertextual.com", "Los ilusos 13+13"),
        ("cadenaser.com", "Los ilusos 13+13"),
        ("rtve.es", "Los ilusos 13+13"),
        ("elpais.com", "Los ilusos 13+13"),
        ("elmundo.es", "Los ilusos 13+13"),
        ("20minutos.es", "Los ilusos 13+13"),
        ("lavanguardia.com", "Los ilusos 13+13"),
        ("abc.es", "Los ilusos 13+13"),
        ("reddit.com", "Los ilusos 13+13"),
        ("imdb.com", "Los ilusos 13+13"),
        ("themoviedb.org", "Los ilusos 13+13"),
        ("letterboxd.com", "Los ilusos 13+13"),
    ],
    redes_sociales=[
        "Jonás Trueba Los ilusos 13+13",
        "Los Ilusos Films Instagram",
        "Jonás Trueba Instagram Los ilusos",
        "Francesco Carril Los ilusos",
        "Aura Garrido Los ilusos",
    ],
    filmaffinity_queries=[
        "site:filmaffinity.com Los ilusos 13+13",
        "filmaffinity Los ilusos 13+13",
    ],
    fuentes_cine_directas=[
        {"url": "https://www.cinemaldito.com/?s=los+ilusos+13", "selector": "article a[href]", "medio": "Cinemaldito"},
        {"url": "https://www.aullidos.com/?s=los+ilusos+13", "selector": "article a[href]", "medio": "Aullidos"},
        {"url": "https://www.ecartelera.com/buscar/?q=los+ilusos+13", "selector": "a[href*='/peliculas/']", "medio": "ECartelera"},
        {"url": "https://www.sensacine.com/buscar/?q=los+ilusos+13", "selector": "a[href*='/peliculas/']", "medio": "SensaCine"},
        {"url": "https://www.espinof.com/buscar/?s=los+ilusos+13", "selector": "article a[href]", "medio": "Espinof"},
        {"url": "https://www.cinemania.es/?s=los+ilusos+13", "selector": "article a[href]", "medio": "Cinemania"},
    ],
    senales_fuertes=[
        "los ilusos 13", "los ilusos 13+13", "los ilusos Trueba",
        "jonás trueba", "jonas trueba", "francesco carril",
        "aura garrido", "vito sanz", "isabelle stoffel",
        "los ilusos films", "the wishful thinkers",
    ],
    senales_cine=[
        "película", "pelicula", "cine", "film", "estreno", "largometraje",
        "crítica", "critica", "reseña", "resena", "review",
        "fotograma", "rodaje", "pantalla", "cineasta",
        "terror", "thriller", "drama",
    ],
    senales_negativas=[
        "los ilusos 2013", "los ilusos original",
        "la reconquista", "la virgen de agosto", "quién lo impide",
        "tenéis que venir a verla", "volveréis",
        "los exiliados románticos", "los exiliados romanticos",
    ],
    anios_otros=[
        "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017",
        "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",
    ],
    umbral_positivas=2,
    titulos_clave=(
        "los ilusos 13", "los ilusos 13+13", "los ilusos Trueba",
        "jonás trueba", "jonas trueba", "francesco carril",
        "aura garrido", "vito sanz",
    ),
    clasificador=[
        ("trailer", ["tráiler", "trailer", "trailer oficial", "teaser"]),
        ("poster", ["póster", "poster", "cartel"]),
        ("entrevista", ["entrevista", "interview"]),
        ("critica", ["crítica", "critica", "reseña", "review", "críticas"]),
        ("foto", ["foto", "fotograf", "imágenes", "imagenes", "imagen", "fotograma"]),
        ("video", ["vídeo", "video", "clip"]),
        ("noticia", ["estreno", "rodaje", "se anuncia", "festival"]),
    ],
    ia_prompt=_ia_prompt_los_ilusos,
    ia_model="gemini-2.5-flash",
    regla_extra=None,
    filtro_adulto=[],
)


def main():
    parser = argparse.ArgumentParser(description="Recopila info sobre Los ilusos 13+13 (2026)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()

    scraper = MovieNewsScraper(LOS_ILUSOS_CONFIG)
    notifier = TelegramNewsSender()

    ejecutar(scraper, dry_run=args.dry_run, enviar=args.enviar, notifier=notifier)


if __name__ == "__main__":
    main()
