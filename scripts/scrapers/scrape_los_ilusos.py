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
        "Eres un experto en cine. Determina cuáles de los siguientes titulares se refieren "
        "EXCLUSIVAMENTE a la película 'Los ilusos 13+13' (2026), de Jonás Trueba, "
        "una revisión/reworked de su película 'Los ilusos' (2013), con Francesco Carril, "
        "Aura Garrido y Vito Sanz.\n"
        "NO cuentan: la película original 'Los ilusos' (2013) ni otras películas del director "
        "Jonás Trueba (La reconquista, La virgen de agosto, etc.).\n"
        "SÍ cuentan: noticias sobre la película 'Los ilusos 13+13', estreno, crítica, "
        "entrevistas, festivales, distribución.\n"
        "Responde SOLO con la lista de números de los titulares que SÍ son sobre esta película, "
        "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
        f"{numerados}"
    )


LOS_ILUSOS_CONFIG = MovieConfig(
    pelicula="Los ilusos 13+13",
    pelicula_es="Los ilusos 13+13",
    output_path=OUTPUT_PATH,
    queries=[
        "Los ilusos 13+13 película",
        "Los ilusos 13+13 Jonás Trueba",
        "Los ilusos 13+13 2026",
        "Los ilusos 13+13 Francesco Carril",
        "Los ilusos 13+13 Aura Garrido",
        "Los ilusos 13+13 Vito Sanz",
        "Los ilusos 13+13 estreno",
        "Los ilusos 13+13 crítica",
        "Los ilusos 13+13 reseña",
        "Los ilusos 13+13 trailer",
        "Los ilusos 13+13 cinemaldito",
        "Los ilusos 13+13 fotogramas",
        "Los ilusos 13+13 filmaffinity",
        "The Wishful Thinkers 13+13",
        "Los ilusos Trueba 2026",
    ],
    queries_extra=[
        "Los ilusos 13+13 Jonás Trueba estreno",
        "Los ilusos 13+13 Jonás Trueba crítica",
        "Los ilusos 13+13 Madrid cine",
        "Los ilusos 13+13 Golem Madrid",
        "Los ilusos 13+13 Los Ilusos Films",
        "Los ilusos 13+13 revised reworked",
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
