#!/usr/bin/env python3
"""
scrape_eixam.py — Configuración y entry point de la recopilación de información
sobre la película "Eixam" (Enjambre, 2026), thriller rural de Óscar Bernàcer.

El motor genérico (MovieNewsScraper, relevancia, Telegram, etc.) está en
movie_scraper_base.py (SOLID: SRP + OCP + DIP). Este módulo solo define la
configuración específica de Eixam, la regla extra de relevancia (doble título)
y el flujo main que añade la vigilancia de IMDb Parental.

La salida se acumula (deduplicada por URL) en files/eixam_pelicula.json.

Uso:
    python scripts/scrapers/scrape_eixam.py                 # recopila y archiva
    python scripts/scrapers/scrape_eixam.py --dry-run       # muestra sin guardar
    python scripts/scrapers/scrape_eixam.py --enviar        # además envía resumen a Telegram

    Con --enviar también se vigilan las 2 fichas de Guía Parental de IMDb
    (tt39163611 / tt37076898) y se envía 1 mensaje si cambia su texto.
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
from imdb_parental import IMDBParentalMonitor

# =============================================================================
# Configuración específica de "Eixam" (Enjambre, 2026)
# =============================================================================

OUTPUT_PATH = REPO_DIR / "files" / "eixam_pelicula.json"
IMDB_PARENTAL_PATH = REPO_DIR / "files" / "eixam_imdb_parental.json"
IMDB_PARENTAL_URLS = [
    "https://www.imdb.com/es-es/title/tt39163611/parentalguide/?ref_=tt_stry_pg",
    "https://www.imdb.com/es-es/title/tt37076898/parentalguide/?ref_=tt_stry_pg",
]


def _regla_extra_eixam(texto: str, punt: int):
    """Regla especial de Eixam (OCP hook en MovieConfig.regla_extra):
    Si el titular contiene AMBOS títulos (eixam + enjambre), basta un solo
    refuerzo de cine (punt >= 1). Si contiene "eixam" pero punt==0 y no hay
    ninguna señal de cine (nombre propio en ciencia: 'enjambre de Eixam'), rechazar."""
    if "eixam" in texto and "enjambre" in texto:
        return punt >= 1
    if "eixam" in texto and punt == 0 and not any(c in texto for c in EIXAM_CONFIG.senales_cine):
        return False
    return None


def _ia_prompt_eixam(numerados: str) -> str:
    return (
        "Eres un experto en cine. Determina cuáles de los siguientes titulares se refieren "
        "EXCLUSIVAMENTE a la película española 'Eixam' (Enjambre, 2026), un thriller rural "
        "dirigido por Óscar Bernàcer con Pablo Molinero y Cristina Fernández Pintado, cuya "
        "historia transcurre en la aldea de Malpàs.\n"
        "NO cuentan: otras películas/series llamadas 'Enjambre' (ej. Swarm de Donald Glover, "
        "Hypnotic, series de abejas/apicultura, ciencia, aviación).\n"
        "Responde SOLO con la lista de números de los titulares que SÍ son sobre esta película, "
        "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
        f"{numerados}"
    )


EIXAM_CONFIG = MovieConfig(
    pelicula="Eixam",
    pelicula_es="Enjambre",
    output_path=OUTPUT_PATH,
    queries=[
        "Eixam Óscar Bernàcer",
        "Eixam película",
        "Eixam Enjambre 2026",
        "Enjambre película Óscar Bernàcer",
        "Enjambre 2026 película",
        "Enjambre óscar bernacer estreno",
        "Eixam crítica",
        "Enjambre crítica reseña",
        "Eixam tráiler trailer",
        "Enjambre tráiler oficial",
        "Eixam Pablo Molinero",
        "eixam Cristina Fernández Pintado",
        "eixam Malpàs",
        "eixam Bejís rodaje",
        "Eixam película española",
        "Eixam thriller rural",
        "Eixam estreno cines",
        "Enjambre película española",
        "Enjambre thriller rural",
        "Enjambre estreno cines",
        "Eixam reparto actores",
        "Enjambre reparto actores",
        "Eixam Pablo Derqui",
        "Enjambre Pablo Derqui",
        "Eixam Marta Belenguer",
        "Enjambre Marta Belenguer",
        "Eixam Atlàntida Mallorca",
        "Enjambre Atlàntida Mallorca",
        "Eixam Nakamura Films",
        "Enjambre Nakamura Films",
        "Eixam A Contracorriente Films",
        "Enjambre A Contracorriente Films",
    ],
    queries_extra=[
        "enjambre película 2026",
        "enjambre bernàcer",
        "enjambre película valenciana",
        "enjambre thriller rural",
        "enjambre reseña crítica",
        "enjambre película española",
        "enjambre estreno cines",
        "enjambre reparto actores",
        "enjambre Pablo Derqui",
        "enjambre Marta Belenguer",
        "enjambre Atlàntida Mallorca",
        "enjambre Nakamura Films",
        "enjambre A Contracorriente Films",
        "eixam película española",
        "eixam thriller rural",
        "eixam estreno cines",
        "eixam reparto actores",
        "eixam Pablo Derqui",
        "eixam Marta Belenguer",
        "eixam Atlàntida Mallorca",
        "eixam Nakamura Films",
        "eixam A Contracorriente Films",
    ],
    yt_queries=[
        "eixam película",
        "eixam enjambre tráiler",
        "eixam óscar bernàcer",
        "enjambre eixam estreno 2026",
        "eixam thriller rural",
    ],
    contraste_queries=[
        "eixam enjambre",
        "enjambre eixam",
        "eixam bernàcer",
    ],
    sitios_resenias=[
        ("decine21.com", "eixam"),
        ("decine21.com", "enjambre 2026"),
        ("contraste.info", "eixam"),
        ("contraste.info", "enjambre bernàcer"),
        ("butacaancha", "eixam"),
        ("fotogramas.es", "eixam"),
        ("cinemaldito.com", "eixam"),
        ("aullidos.com", "eixam"),
        ("ecartelera", "eixam"),
        ("sensa cine", "eixam"),
        ("filmaffinity", "eixam"),
        ("cineuropa.org", "eixam"),
        ("labutaca.net", "eixam"),
        ("dirigido.es", "eixam"),
        ("espinof.com", "eixam"),
        ("title-magazine.com", "eixam"),
        ("elcineenlauva.com", "eixam"),
        ("cinemanía", "eixam"),
        ("elcomercio.es", "eixam"),
        ("elpais.com", "eixam"),
        ("elmundo.es", "eixam"),
        ("laregion.es", "eixam"),
        ("20minutos.es", "eixam"),
        ("buzzfeed.com", "eixam"),
        ("timeout.com", "eixam"),
        ("indiewire.com", "eixam"),
        ("variety.com", "eixam"),
        ("hollywoodreporter.com", "eixam"),
        ("cadenaser.com", "eixam"),
        ("rtve.es", "eixam"),
        ("europapress.es", "eixam"),
        ("efeservices.com", "eixam"),
        ("laverdad.es", "eixam"),
        ("levante-emv.com", "eixam"),
        ("informacion.es", "eixam"),
        ("diarioinformacion.com", "eixam"),
        ("abc.es", "eixam"),
        ("larazon.es", "eixam"),
        ("elperiodico.com", "eixam"),
        ("nius.es", "eixam"),
        ("lasprovincias.es", "eixam"),
        ("superfilmes.es", "eixam"),
        ("cineuropa.org", "enjambre 2026"),
        ("imdb.com", "eixam"),
        ("themoviedb.org", "eixam"),
    ],
    redes_sociales=[
        "acontracorrientefilms eixam instagram",
        "acontracorrientefilms enjambre instagram",
        "atlantidamallorca eixam instagram",
        "atlantidamallorca enjambre instagram",
        "acontracorrientefilms eixam twitter",
        "acontracorrientefilms enjambre twitter",
        "atlantidamallorca eixam twitter",
        "atlantidamallorca enjambre twitter",
        "acontracorrientefilms eixam x.com",
        "atlantidamallorca eixam x.com",
        "nakamura films eixam instagram",
        "nakamura films enjambre instagram",
        "nakamura films eixam twitter",
        "nakamura films enjambre twitter",
        "nakamura films eixam x.com",
    ],
    filmaffinity_queries=[
        "site:filmaffinity.com eixam",
        "site:filmaffinity.com enjambre 2026",
        "filmaffinity eixam crítica",
        "filmaffinity enjambre reseña",
    ],
    fuentes_cine_directas=[
        {"url": "https://www.cinemaldito.com/?s=eixam", "selector": "article a[href]", "medio": "Cinemaldito"},
        {"url": "https://www.aullidos.com/?s=eixam", "selector": "article a[href]", "medio": "Aullidos"},
        {"url": "https://www.ecartelera.com/buscar/?q=eixam", "selector": "a[href*='/peliculas/']", "medio": "ECartelera"},
        {"url": "https://www.sensacine.com/buscar/?q=eixam", "selector": "a[href*='/peliculas/']", "medio": "SensaCine"},
        {"url": "https://www.cineuropa.org/es/?s=eixam", "selector": "article a[href]", "medio": "Cineuropa"},
        {"url": "https://www.labutaca.net/buscar/?s=eixam", "selector": "article a[href]", "medio": "La Butaca"},
        {"url": "https://www.espinof.com/buscar/?s=eixam", "selector": "article a[href]", "medio": "Espinof"},
        {"url": "https://www.cinemania.es/?s=eixam", "selector": "article a[href]", "medio": "Cinemania"},
    ],
    senales_fuertes=[
        "óscar bernàcer", "oscar bernacer", "bernàcer", "pablo molinero",
        "cristina fernández pintado", "cristina fernandez pintado",
        "maría maroto", "maria maroto", "pablo derqui", "marta belenguer",
        "jordi aguilar", "glòria march", "gloria march", "àngel fígols",
        "àngel fígols", "malpàs", "bejís", "bejis", "a contracorriente",
        "nadal", "lluc", "silvia", "alba", "comunidad valenciana",
        "atlàntida mallorca", "atlantida mallorca", "corte y confección",
        "nakamura films", "primer largometraje de ficción",
    ],
    senales_cine=[
        "película", "pelicula", "cine", "film", "estreno", "largometraje",
        "tráiler", "trailer", "reparto", "director", "dirección", "direccion",
        "crítica", "critica", "reseña", "resena", "review", "cartel", "póster",
        "poster", "fotograma", "rodaje", "taquilla", "pantalla", "cineasta",
        "industria del cine", "actores", "actriz", "guion", "banda sonora",
    ],
    senales_negativas=[
        "abeja", "abejas", "apicultura", "colmena", "drones", "apiario",
        "miel", "polinización", "polinizacion",
        "donald glover", "swarm", "prime video series", "serie de prime video",
        "hipnotic", "laurent bouzereau", "el exterminador", "exterminador",
        "battle fish", "thor", "marvel", "avengers", "avispas", "machos enjambre",
        "avispa", "jugador", "torneo", "ciencia", "investigación", "investigacion",
        "genética", "genetica", "ordenador", "computadora", "apple", "ios",
        "teléfono", "telefono", "avión", "avion", "helicóptero", "helicoptero",
        "la nueva serie", "serie de la semana", "recomendada", "recomienda",
    ],
    anios_otros=["2020", "2003", "2005", "2014", "2021", "2019", "2022", "2013", "2025"],
    umbral_positivas=2,
    titulos_clave=("eixam", "enjambre", "bernàcer", "oscar bernacer", "óscar bernàcer"),
    clasificador=[
        ("trailer", ["tráiler", "trailer", "trailer oficial", "teaser"]),
        ("poster", ["póster", "poster", "cartel"]),
        ("entrevista", ["entrevista", "interview"]),
        ("critica", ["crítica", "critica", "reseña", "review", "críticas"]),
        ("forograma", ["fotograma", "frame"]),
        ("foto", ["foto", "fotograf", "imágenes", "imagenes", "imagen", "imágenes"]),
        ("video", ["vídeo", "video", "clip"]),
        ("noticia", ["estreno", "primeras imágenes", "primera imagen", "rodaje", "se anuncia"]),
    ],
    ia_prompt=_ia_prompt_eixam,
    ia_model="gemini-2.5-flash",
    regla_extra=_regla_extra_eixam,
)


def main():
    parser = argparse.ArgumentParser(description="Recopila info sobre la película Eixam (Enjambre)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()

    scraper = MovieNewsScraper(EIXAM_CONFIG)
    notifier = TelegramNewsSender()

    ejecutar(scraper, dry_run=args.dry_run, enviar=args.enviar, notifier=notifier)

    if args.enviar:
        print("\n🛡️ Comprobando Guía Parental de IMDb...")
        parental = IMDBParentalMonitor(
            urls=IMDB_PARENTAL_URLS,
            path=IMDB_PARENTAL_PATH,
        )
        parental.comprobar(dry_run=args.dry_run)


if __name__ == "__main__":
    main()