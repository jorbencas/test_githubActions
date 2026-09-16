#!/usr/bin/env python3
"""
scrape_el_nido.py — Configuración y entry point del buscador de noticias/info
sobre la película "El nido" (2026), thriller psicológico/terror de Hugo Stuven
(Filmax) con Michelle Jenner (estreno en cines: 11/09/2026).

El motor genérico (MovieNewsScraper, relevancia, Telegram, etc.) está en
movie_scraper_base.py (SOLID: SRP + OCP + DIP). Este módulo solo define la
configuración específica de "El nido": búsquedas, señales de relevancia,
anti-falsos-positivos y el prompt de validación IA (con sesgo a desnudez/sexo).

Añade búsquedas específicas sobre desnudez/sexo/tetas/guía parental y vigila
sitios de reseñas/spoilers para avisar de contenido adulto en la película.

La salida se acumula (deduplicada por URL) en files/el_nido_pelicula.json.

Uso:
    python scripts/scrapers/scrape_el_nido.py            # recopila y archiva
    python scripts/scrapers/scrape_el_nido.py --dry-run  # muestra sin guardar
    python scripts/scrapers/scrape_el_nido.py --enviar   # además envía resumen a Telegram
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

# =============================================================================
# Configuración específica de "El nido" (2026)
# =============================================================================

OUTPUT_PATH = REPO_DIR / "files" / "el_nido_pelicula.json"


def _ia_prompt_el_nido(numerados: str) -> str:
    return (
        "Eres un experto en cine. Determina cuáles de los siguientes titulares se refieren "
        "EXCLUSIVAMENTE a la película española 'El nido' (2026), un thriller/terror psicológico "
        "dirigido por Hugo Stuven, producido por Filmax y protagonizado por Michelle Jenner, "
        "estrenada en cines el 11 de septiembre de 2026, sobre una madre sobreprotectora que "
        "encierra a su familia en casa.\n"
        "NO cuentan: noticias de nidos de pájaros o naturaleza, ni otras películas llamadas "
        "'El nido' (u 'The Nest'), ni series.\n"
        "SÍ cuentan también los artículos que comenten desnudos, sexo, tetas o calificación "
        "de contenido de esta película.\n"
        "Responde SOLO con la lista de números de los titulares que SÍ son sobre esta película, "
        "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
        f"{numerados}"
    )


EL_NIDO_CONFIG = MovieConfig(
    pelicula="El nido",
    pelicula_es="El nido",
    output_path=OUTPUT_PATH,
    queries=[
        "El nido Hugo Stuven",
        "El nido película desnudos",
        "El nido película sexo",
        "El nido desnudez",
        "El nido escenas de sexo",
        "El nido Michelle Jenner desnudos",
        "El nido desnudo",
        "El nido tetas",
        "El nido guía parental",
        "El nido parental guide IMDb",
        "El nido spoilers final explicado",
        "El nido spoilers",
        "El nido escenaHot",
        "El nido escena hot",
        "El nido escena bañera",
        "El nido escena baño",
        "El nido bañera",
        "El nido baño",
        "The Nest 2026 movie nudity",
        "The Nest 2026 movie sex scene",
        "The Nest 2026 film naked",
        "The Nest Hugo Stuven nudity",
        "The Nest 2026 parental guide",
        "The Nest 2026 spoilers",
        "The Nest 2026 nude scenes",
        "The Nest 2026 sex scenes",
        "The Nest 2026 Michelle Jenner nude",
        "The Nest 2026 review nudity",
        "The Nest 2026 bathtub scene",
        "The Nest 2026 bath scene",
    ],
    queries_extra=[
        "El nido escenas sexo desnudo rating",
        "El nido final spoilers reseña",
        "El nido spoilernet",
        "El nido escena desnudo Michelle Jenner",
        "El nido violación",
        "El nido sexual",
        "El nido escena bañera Michelle Jenner",
        "El nido bañera desnudo",
        "The Nest 2026 naked scenes",
        "The Nest 2026 erotic scenes",
        "The Nest 2026 sex scene Michelle Jenner",
        "The Nest 2026 nude spoiler",
        "The Nest movie 2026 nudity",
        "The Nest film 2026 sex",
        "The Nest 2026 bathtub nude",
        "The Nest 2026 bath naked",
    ],
    yt_queries=[
        "el nido película desnudos",
        "el nido escenas sexo",
        "el nido spoilers",
        "The Nest 2026 nudity",
        "The Nest 2026 sex scene",
    ],
    contraste_queries=[
        "el nido",
        "el nido 2026",
        "el nido hugo stuven",
    ],
    sitios_resenias=[
        ("decine21.com", "el nido"),
        ("decine21.com", "el nido sexo"),
        ("filmaffinity.com", "el nido"),
        ("filmaffinity.com", "el nido 2026"),
        ("sensacine.com", "el nido"),
        ("ecartelera.com", "el nido"),
        ("fotogramas.es", "el nido"),
        ("espinof.com", "el nido"),
        ("cinemaldito.com", "el nido"),
        ("aullidos.com", "el nido"),
        ("cinemania", "el nido"),
        ("elcineenlauva.com", "el nido"),
        ("labutaca.net", "el nido"),
        ("cineuropa.org", "el nido"),
        ("dirigido.es", "el nido"),
        ("title-magazine.com", "el nido"),
        ("contraste.info", "el nido"),
        ("hipertextual.com", "el nido"),
        ("eldiario.es", "el nido"),
        ("cadenaser.com", "el nido"),
        ("rtve.es", "el nido"),
        ("europapress.es", "el nido"),
        ("efeservices.com", "el nido"),
        ("elcomercio.es", "el nido"),
        ("elpais.com", "el nido"),
        ("elmundo.es", "el nido"),
        ("20minutos.es", "el nido"),
        ("lavanguardia.com", "el nido"),
        ("abc.es", "el nido"),
        ("larazon.es", "el nido"),
        ("elperiodico.com", "el nido"),
        ("laverdad.es", "el nido"),
        ("levante-emv.com", "el nido"),
        ("letterboxd.com", "el nido"),
        ("reddit.com", "el nido spoilers"),
        ("imdb.com", "el nido"),
        ("imdb.com", "el nido parents guide"),
        ("themoviedb.org", "el nido"),
        ("kids-in-mind.com", "el nido"),
        ("screenit.com", "el nido"),
    ],
    redes_sociales=[
        "filmax el nido instagram",
        "filmax el nido twitter",
        "filmax el nido x.com",
        "hugo stuven el nido instagram",
        "hugo stuven el nido twitter",
        "michelle jenner el nido instagram",
        "michelle jenner el nido twitter",
        "dylan radley el nido instagram",
        "el nido película instagram",
    ],
    filmaffinity_queries=[
        "site:filmaffinity.com el nido",
        "site:filmaffinity.com el nido 2026",
        "filmaffinity el nido crítica",
        "filmaffinity el nido reseña",
    ],
    fuentes_cine_directas=[
        {"url": "https://www.cinemaldito.com/?s=el+nido", "selector": "article a[href]", "medio": "Cinemaldito"},
        {"url": "https://www.aullidos.com/?s=el+nido", "selector": "article a[href]", "medio": "Aullidos"},
        {"url": "https://www.ecartelera.com/buscar/?q=el+nido", "selector": "a[href*='/peliculas/']", "medio": "ECartelera"},
        {"url": "https://www.sensacine.com/buscar/?q=el+nido", "selector": "a[href*='/peliculas/']", "medio": "SensaCine"},
        {"url": "https://www.cineuropa.org/es/?s=el+nido", "selector": "article a[href]", "medio": "Cineuropa"},
        {"url": "https://www.labutaca.net/buscar/?s=el+nido", "selector": "article a[href]", "medio": "La Butaca"},
        {"url": "https://www.espinof.com/buscar/?s=el+nido", "selector": "article a[href]", "medio": "Espinof"},
        {"url": "https://www.cinemania.es/?s=el+nido", "selector": "article a[href]", "medio": "Cinemania"},
    ],
    senales_fuertes=[
        "hugo stuven", "michelle jenner", "luisa gavasa", "pablo derqui",
        "dylan radley", "filmax", "velasco", "santiago lallana",
        "césar de nicolás", "cesar de nicolas", "el nido 2026",
        "11 de septiembre", "septiembre de 2026",
        "encierra a su familia", "encierro", "madre sobreprotectora",
        "the nest 2026", "the nest hugo stuven", "the nest filmax",
        "the nest michelle jenner", "the nest movie",
    ],
    senales_cine=[
        "desnudo", "desnudos", "desnudez", "sexo", "erótic", "erotico",
        "escenas de sexo", "tetas", "topless", "desnudo parcial",
        "guía parental", "guia parental", "parental guide", "mpaa",
        "no recomendada para menores", "no apta para menores",
        "spoiler", "spoilers", "espóiler", "espoiler", "final explicado",
        "nudity", "nude", "naked", "sex scene", "nude scene", "erotic",
        "topless", "parental guide", "mpaa", "rated", "rating",
        "uncensored", "explicit", "adult content", "mature",
        "bañera", "baño", "escena de baño", "escena de bañera",
        "bathtub", "bath scene", "bathtub scene",
        "película", "pelicula", "cine", "film", "estreno", "largometraje",
        "tráiler", "trailer", "reparto", "director", "dirección", "direccion",
        "crítica", "critica", "reseña", "resena", "review", "cartel", "póster",
        "poster", "fotograma", "rodaje", "taquilla", "pantalla", "cineasta",
        "industria del cine", "actores", "actriz", "guion", "banda sonora",
        "terror", "thriller", "suspense", "drama",
    ],
    senales_negativas=[
        "pájaro", "pájaros", "pajaros", "ave de", "aves", "águila", "aguila",
        "halcón", "halcon", "búho", "buho", "lechuza", "cuervo", "cuervos",
        "gorrión", "golondrina", "herrerillo", "nidos de", "nido de pájaros",
        "bird", "birds", "birdhouse",
        "sean durkin", "nido vacío", "nido vacio", "nido de amor",
        "novela", "teatro de", "cea",
        "fertilidad", "embarazo", "bebé", "bebe",
        "the nest 2020", "the nest 2019", "the nest 2018", "the nest 2017",
        "the nest jamie dornan", "the nest carrie coon",
    ],
    anios_otros=[
        "1980", "2003", "2005", "2007", "2012", "2013", "2014", "2016", "2017",
        "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",
        "2027", "2028", "2029",
    ],
    umbral_positivas=2,
    titulos_clave=(
        "el nido", "hugo stuven", "michelle jenner", "filmax",
        "luisa gavasa", "pablo derqui", "dylan radley", "velasco",
        "santiago lallana", "césar de nicolás", "cesar de nicolas",
    ),
    clasificador=[
        ("sexo", ["desnud", "sexo", "erótic", "erotico", "tetas", "topless",
                  "guía parental", "guia parental", "parental guide", "mpaa"]),
        ("trailer", ["tráiler", "trailer", "trailer oficial", "teaser"]),
        ("poster", ["póster", "poster", "cartel"]),
        ("entrevista", ["entrevista", "interview"]),
        ("critica", ["crítica", "critica", "reseña", "review", "críticas"]),
        ("forograma", ["fotograma", "frame"]),
        ("foto", ["foto", "fotograf", "imágenes", "imagenes", "imagen", "imágenes"]),
        ("video", ["vídeo", "video", "clip"]),
        ("noticia", ["estreno", "primeras imágenes", "primera imagen", "rodaje", "se anuncia"]),
    ],
    ia_prompt=_ia_prompt_el_nido,
    ia_model="gemini-2.5-flash",
    regla_extra=None,
    filtro_adulto=[
        "desnud", "sexo", "erótic", "erotico", "tetas", "topless",
        "guía parental", "guia parental", "parental guide", "mpaa",
        "escenas de sexo", "contenido sexual", "nudity", "sex scene",
        "nude", "naked", "nude scene", "sex scenes", "erotic",
        "bañera", "baño", "escena de baño", "escena de bañera",
        "bathtub", "bath scene", "bathtub scene",
        "no recomendada para menores", "no apta para menores",
        "+18", "xxx", "calificación", "calificacion", "rating",
        "spoiler", "spoilers", "final explicado",
        "explicit", "uncensored", "mature", "adult content",
    ],
)


def main():
    parser = argparse.ArgumentParser(description="Recopila info sobre la película El nido (2026)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()

    scraper = MovieNewsScraper(EL_NIDO_CONFIG)
    notifier = TelegramNewsSender()

    ejecutar(scraper, dry_run=args.dry_run, enviar=args.enviar, notifier=notifier)


if __name__ == "__main__":
    main()