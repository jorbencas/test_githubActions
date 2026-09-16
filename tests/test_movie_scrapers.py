"""
test_movie_scrapers.py — Tests para los scrapers de películas/series
usando el motor genérico SOLID (movie_scraper_base.py).
"""
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts" / "scrapers"
sys.path.insert(0, str(SCRIPT_DIR))

from movie_scraper_base import MovieConfig, MovieNewsScraper, RelevanceFilter, MovieClassifier


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def el_nido_config():
    """Config de El nido para tests."""
    from scrape_el_nido import EL_NIDO_CONFIG
    return EL_NIDO_CONFIG


@pytest.fixture
def nueve_reinas_config():
    """Config de Nueve reinas para tests."""
    from scrape_nueve_reinas import NUEVE_REINAS_CONFIG
    return NUEVE_REINAS_CONFIG


@pytest.fixture
def los_ilusos_config():
    """Config de Los ilusos 13+13 para tests."""
    from scrape_los_ilusos import LOS_ILUSOS_CONFIG
    return LOS_ILUSOS_CONFIG


# =============================================================================
# Tests de configuración
# =============================================================================

class TestMovieConfigs:
    """Tests de que las configs están bien formadas."""

    def test_el_nido_config_has_required_fields(self, el_nido_config):
        assert el_nido_config.pelicula
        assert el_nido_config.pelicula_es
        assert el_nido_config.output_path.suffix == ".json"
        assert len(el_nido_config.queries) > 0
        assert len(el_nido_config.senales_fuertes) > 0
        assert len(el_nido_config.senales_negativas) > 0
        assert len(el_nido_config.titulos_clave) > 0
        assert el_nido_config.ia_prompt is not None

    def test_nueve_reinas_config_has_required_fields(self, nueve_reinas_config):
        assert nueve_reinas_config.pelicula
        assert nueve_reinas_config.pelicula_es
        assert nueve_reinas_config.output_path.suffix == ".json"
        assert len(nueve_reinas_config.queries) > 0
        assert len(nueve_reinas_config.senales_fuertes) > 0
        assert len(nueve_reinas_config.senales_negativas) > 0
        assert len(nueve_reinas_config.titulos_clave) > 0
        assert nueve_reinas_config.ia_prompt is not None

    def test_los_ilusos_config_has_required_fields(self, los_ilusos_config):
        assert los_ilusos_config.pelicula
        assert los_ilusos_config.pelicula_es
        assert los_ilusos_config.output_path.suffix == ".json"
        assert len(los_ilusos_config.queries) > 0
        assert len(los_ilusos_config.senales_fuertes) > 0
        assert len(los_ilusos_config.senales_negativas) > 0
        assert len(los_ilusos_config.titulos_clave) > 0
        assert los_ilusos_config.ia_prompt is not None

    def test_el_nido_no_false_positives_birds(self, el_nido_config):
        """El nido no debe confundirse con nidos de pájaros."""
        filtro = RelevanceFilter(el_nido_config)
        # Titulares de pájaros/naturaleza
        assert not filtro.es_relevante("Cómo construir un nido para pájaros")
        assert not filtro.es_relevante("Los nidos de las águilas en peligro")
        assert not filtro.es_relevante("Bird nesting habits in spring")

    def test_nueve_reinas_no_false_positives_original(self, nueve_reinas_config):
        """Nueve reinas no debe confundirse con la película original."""
        filtro = RelevanceFilter(nueve_reinas_config)
        # Película original argentina
        assert not filtro.es_relevante("Nueve reinas: la película de Ricardo Darín del 2000")
        assert not filtro.es_relevante("Criminal 2004 con John C. Reilly")
        assert not filtro.es_relevante("Bluffmaster 2005 película india")

    def test_los_ilusos_no_false_positives_original(self, los_ilusos_config):
        """Los ilusos 13+13 no debe confundirse con la película original."""
        filtro = RelevanceFilter(los_ilusos_config)
        # Película original
        assert not filtro.es_relevante("Los ilusos 2013 de Jonás Trueba")
        assert not filtro.es_relevante("La reconquista de Jonás Trueba")
        assert not filtro.es_relevante("La virgen de agosto de Jonás Trueba")


# =============================================================================
# Tests de relevancia
# =============================================================================

class TestRelevanceFilter:
    """Tests del filtro de relevancia."""

    def test_el_nido_relevante_with_strong_signals(self, el_nido_config):
        filtro = RelevanceFilter(el_nido_config)
        assert filtro.es_relevante("El nido Michelle Jenner desnudos")
        assert filtro.es_relevante("El nido Hugo Stuven spoilers")
        assert filtro.es_relevante("El nido escenas de sexo en bañera")

    def test_nueve_reinas_relevante_with_strong_signals(self, nueve_reinas_config):
        filtro = RelevanceFilter(nueve_reinas_config)
        assert filtro.es_relevante("Nueve reinas Netflix Álvaro Morte")
        assert filtro.es_relevante("Nueve reinas Netflix estreno")
        assert filtro.es_relevante("Nueve reinas Patrick Criado rodaje")

    def test_los_ilusos_relevante_with_strong_signals(self, los_ilusos_config):
        filtro = RelevanceFilter(los_ilusos_config)
        assert filtro.es_relevante("Los ilusos 13+13 Jonás Trueba estreno")
        assert filtro.es_relevante("Los ilusos 13+13 Aura Garrido")
        assert filtro.es_relevante("Los ilusos 13+13 crítica cinema")


# =============================================================================
# Tests de clasificador
# =============================================================================

class TestMovieClassifier:
    """Tests del clasificador de tipos de contenido."""

    def test_el_nido_clasificador(self, el_nido_config):
        clasificador = MovieClassifier(el_nido_config.clasificador)
        assert clasificador.clasificar("El nido tráiler oficial") == "trailer"
        assert clasificador.clasificar("El nido póster nuevo") == "poster"
        assert clasificador.clasificar("El nido entrevista con Michelle Jenner") == "entrevista"
        assert clasificador.clasificar("El nido crítica de cine") == "critica"
        assert clasificador.clasificar("El nido estreno en cines") == "noticia"

    def test_nueve_reinas_clasificador(self, nueve_reinas_config):
        clasificador = MovieClassifier(nueve_reinas_config.clasificador)
        assert clasificador.clasificar("Nueve reinas tráiler Netflix") == "trailer"
        assert clasificador.clasificar("Nueve reinas entrevista Álvaro Morte") == "entrevista"
        assert clasificador.clasificar("Nueve reinas rodaje Madrid") == "noticia"

    def test_los_ilusos_clasificador(self, los_ilusos_config):
        clasificador = MovieClassifier(los_ilusos_config.clasificador)
        assert clasificador.clasificar("Los ilusos 13+13 tráiler") == "trailer"
        assert clasificador.clasificar("Los ilusos 13+13 crítica") == "critica"
        assert clasificador.clasificar("Los ilusos 13+13 estreno") == "noticia"


# =============================================================================
# Tests de IA prompt
# =============================================================================

class TestIAPrompts:
    """Tests de que los prompts de IA están bien formados."""

    def test_el_nido_prompt_format(self, el_nido_config):
        prompt = el_nido_config.ia_prompt("1. Titular de prueba\n2. Otro titular")
        assert "El nido" in prompt
        assert "1. Titular de prueba" in prompt
        assert "2. Otro titular" in prompt
        assert "Responde SOLO" in prompt

    def test_nueve_reinas_prompt_format(self, nueve_reinas_config):
        prompt = nueve_reinas_config.ia_prompt("1. Titular de prueba")
        assert "Nueve reinas" in prompt
        assert "1. Titular de prueba" in prompt
        assert "Responde SOLO" in prompt

    def test_los_ilusos_prompt_format(self, los_ilusos_config):
        prompt = los_ilusos_config.ia_prompt("1. Titular de prueba")
        assert "Los ilusos" in prompt
        assert "1. Titular de prueba" in prompt
        assert "Responde SOLO" in prompt
