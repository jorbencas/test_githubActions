"""
test_fechas.py — Tests de utils.fechas: parseo de fechas de publicación y
regla única de recencia ≤24 h aplicada por todos los scrapers y envíos de
noticias (scrape_news, send_telegram, send_email, movie scrapers, FormulaTV).
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from utils.fechas import (MADRID, es_reciente, extraer_fecha_de_texto,
                          parsear_fecha, texto_es_reciente)

REF = datetime(2026, 11, 17, 20, 32, tzinfo=MADRID)


# =============================================================================
# Parseo de formatos
# =============================================================================
def test_parsea_rfc822_rss():
    f = parsear_fecha("Wed, 11 Apr 2026 20:32:00 +0200", ref=REF)
    assert f == datetime(2026, 4, 11, 20, 32, tzinfo=MADRID)


def test_parsea_rfc822_de_hoy():
    f = parsear_fecha("Tue, 17 Nov 2026 08:00:00 +0000", ref=REF)
    assert f == datetime(2026, 11, 17, 9, 0, tzinfo=MADRID)


def test_parsea_iso():
    assert parsear_fecha("2026-04-11T20:32:00", ref=REF) == datetime(2026, 4, 11, 20, 32, tzinfo=MADRID)
    assert parsear_fecha("2026-11-17", ref=REF) == datetime(2026, 11, 17, 0, 0, tzinfo=MADRID)


def test_parsea_espanol():
    assert parsear_fecha("11 abril 2026, 20:32", ref=REF) == datetime(2026, 4, 11, 20, 32, tzinfo=MADRID)
    assert parsear_fecha("11 de abril de 2026", ref=REF) == datetime(2026, 4, 11, 0, 0, tzinfo=MADRID)
    assert parsear_fecha("11/04/2026 20:32", ref=REF) == datetime(2026, 4, 11, 20, 32, tzinfo=MADRID)


def test_parsea_relativo():
    assert parsear_fecha("hace 2 horas", ref=REF) == REF - timedelta(hours=2)
    assert parsear_fecha("hace 3 días", ref=REF) == REF - timedelta(days=3)
    assert parsear_fecha("hace 1 mes", ref=REF) == REF - timedelta(days=30)


def test_sin_fecha_devuelve_none():
    assert parsear_fecha("", ref=REF) is None
    assert parsear_fecha(None, ref=REF) is None
    assert parsear_fecha("Reciente", ref=REF) is None
    assert parsear_fecha("próximamente", ref=REF) is None


# =============================================================================
# Regla de recencia ≤24 h
# =============================================================================
def test_reciente_dentro_de_24h():
    assert texto_es_reciente("Tue, 17 Nov 2026 08:00:00 +0000", ref=REF) is True
    assert texto_es_reciente("hace 2 horas", ref=REF) is True
    assert texto_es_reciente("2026-11-17", ref=REF) is True


def test_no_reciente_mas_de_24h():
    assert texto_es_reciente("Wed, 11 Apr 2026 20:32:00 +0200", ref=REF) is False
    assert texto_es_reciente("11 abril 2026, 20:32", ref=REF) is False
    assert texto_es_reciente("hace 3 días", ref=REF) is False


def test_borde_exacto_24h():
    assert es_reciente(REF - timedelta(hours=24), ref=REF) is True
    assert es_reciente(REF - timedelta(hours=24, minutes=1), ref=REF) is False


def test_fechas_futuras_no_se_descartan():
    """Lo futuro no es «antiguo»: anuncios de estrenos o ruido de zona horaria."""
    assert es_reciente(REF + timedelta(days=30), ref=REF) is True


def test_sin_fecha_devuelve_none_en_texto():
    assert texto_es_reciente("", ref=REF) is None
    assert texto_es_reciente("Reciente", ref=REF) is None


# =============================================================================
# Extracción de fechas dentro de títulos
# =============================================================================
def test_extraer_fecha_de_titulo():
    f = extraer_fecha_de_texto("Noticia actualizada 11 Abril 2026, 20:32", ref=REF)
    assert f == datetime(2026, 4, 11, 20, 32, tzinfo=MADRID)


def test_titulo_sin_fecha_no_parsea_anios_suelos():
    assert extraer_fecha_de_texto("El nido (2026) estreno en cines", ref=REF) is None
    assert extraer_fecha_de_texto("Nueve reinas (2027)", ref=REF) is None
