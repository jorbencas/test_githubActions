"""
test_formulatv_estrenos.py — Tests de parsers y filtros de estrenos del día
(scrape_formulatv_telegram.py): fecha de ejecución (Europe/Madrid), blocklist
("Los ilusos 13+13"), dedup y fuentes (FormulaTV, SensaCine, Filmaffinity, TVMaze).
"""
import sys
from datetime import date
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import scrape_formulatv_telegram as ft

HOY = date(2026, 11, 4)
AYER = date(2026, 11, 3)
MANANA = date(2026, 11, 5)


# =============================================================================
# Blocklist
# =============================================================================
def test_excluido_los_ilusos():
    assert ft.excluido("Los ilusos 13+13") is True
    assert ft.excluido("los ILUSOS 13+13 (2026)") is True
    assert ft.excluido("Trailer Los ilusos 13+13") is True


def test_no_excluido_titulo_normal():
    assert ft.excluido("Palomas negras") is False
    assert ft.excluido("El Señor de los Anillos: Los Anillos de Poder") is False


# =============================================================================
# Parseo de fechas en español
# =============================================================================
def test_parse_fecha_es_con_anio():
    assert ft.parse_fecha_es("4 de noviembre de 2026", 2026) == date(2026, 11, 4)
    assert ft.parse_fecha_es("30 de octubre de 2026", 2026) == date(2026, 10, 30)


def test_parse_fecha_es_sin_anio_usa_anio_default():
    assert ft.parse_fecha_es("(4 de noviembre)", 2026) == date(2026, 11, 4)
    assert ft.parse_fecha_es("30oct.", 2026) == date(2026, 10, 30)


def test_parse_fecha_es_invalida():
    assert ft.parse_fecha_es("", 2026) is None
    assert ft.parse_fecha_es("próximamente", 2026) is None
    assert ft.parse_fecha_es("32 de noviembre de 2026", 2026) is None
    assert ft.parse_fecha_es("mesa de centro", 2026) is None


# =============================================================================
# Filtro central: fecha de ejecución + blocklist
# =============================================================================
def _item(titulo, fecha_estreno):
    return {"titulo": titulo, "fecha_estreno": fecha_estreno, "cadena": "X",
            "fuente": "Test", "capitulos": "?", "temporadas": 1}


def test_filtrar_estrenos_solo_fecha_de_ejecucion():
    items = [
        _item("Estreno hoy", "2026-11-04"),
        _item("Estreno ayer", "2026-11-03"),
        _item("Estreno mañana", "2026-11-05"),
        _item("Sin fecha", ""),
    ]
    out = ft.filtrar_estrenos(items, HOY)
    assert [i["titulo"] for i in out] == ["Estreno hoy"]


def test_filtrar_estrenos_aplica_blocklist():
    items = [
        _item("Los ilusos 13+13", "2026-11-04"),
        _item("Serie Normal", "2026-11-04"),
    ]
    out = ft.filtrar_estrenos(items, HOY)
    assert [i["titulo"] for i in out] == ["Serie Normal"]


def test_filtrar_estrenos_falla_si_no_es_hoy_incluso_con_blocklist():
    items = [_item("Los ilusos 13+13", "2026-11-03")]
    assert ft.filtrar_estrenos(items, HOY) == []


# =============================================================================
# Dedup
# =============================================================================
def test_deduplicar_misma_clave():
    items = [
        _item("Serie X", "2026-11-04"),
        _item("Serie X", "2026-11-04"),
        _item("Serie Y", "2026-11-04"),
    ]
    out = ft.deduplicar(items)
    assert len(out) == 2


def test_filtrar_nuevos_vs_enviados():
    items = [
        _item("Serie X", "2026-11-04"),
        _item("Serie Y", "2026-11-04"),
    ]
    enviados = {"Serie X|2026-11-04"}
    out = ft.filtrar_nuevos(items, enviados)
    assert [i["titulo"] for i in out] == ["Serie Y"]


# =============================================================================
# Parser FormulaTV (pills con data-tip)
# =============================================================================
FORMULATV_HTML = """
<html><body>
<a class="cal-pill" href="/series/serie-ejemplo/"
   data-tip-title="Serie Ejemplo" data-tip-date="2026-11-04"
   data-tip-plat="Netflix" data-tip-genre="Drama"
   data-tip-temps="2" data-tip-caps="8">Serie Ejemplo</a>
<a class="cal-pill" href="/series/otra/"
   data-tip-title="Otra Serie" data-tip-date="2026-11-10"
   data-tip-plat="Netflix">Otra Serie</a>
</body></html>
"""


def test_parse_formulatv_solo_fecha_hoy():
    items = ft.parse_formulatv(FORMULATV_HTML, HOY, solo_espanolas=True)
    assert len(items) == 1
    it = items[0]
    assert it["titulo"] == "Serie Ejemplo"
    assert it["fecha_estreno"] == "2026-11-04"
    assert it["cadena"] == "Netflix"
    assert it["url"].startswith("https://www.formulatv.com/")


def test_parse_formulatv_filtro_espanolas():
    # cadenas US tradicionales (Hulu, CBS...) quedan fuera con el filtro;
    # plataformas con originales españoles (Netflix, HBO Max...) sí pasan
    html = """
    <a class="cal-pill" href="/series/x/" data-tip-title="US Show"
       data-tip-date="2026-11-04" data-tip-plat="Hulu">US Show</a>
    """
    assert ft.parse_formulatv(html, HOY, solo_espanolas=True) == []
    assert len(ft.parse_formulatv(html, HOY, solo_espanolas=False)) == 1


# =============================================================================
# Parser SensaCine
# =============================================================================
SENSACINE_HTML = """
<ul>
 <li class="mdl">
  <div class="card entity-card entity-card-list cf">
   <div class="meta">
    <h2 class="meta-title">
     <a class="meta-title-link" href="/peliculas/pelicula-1000005692/">Karateka</a>
    </h2>
    <div class="meta-body">
     <div class="meta-body-item meta-body-info">
      <span class="date">4 de noviembre de 2026</span>
     </div>
    </div>
   </div>
  </div>
 </li>
 <li class="mdl">
  <div class="card entity-card entity-card-list cf">
   <div class="meta">
    <h2 class="meta-title">
     <a class="meta-title-link" href="/peliculas/pelicula-999/">Vieja Peli</a>
    </h2>
    <div class="meta-body">
     <div class="meta-body-item meta-body-info">
      <span class="date">30 de octubre de 2026</span>
     </div>
    </div>
   </div>
  </div>
 </li>
</ul>
"""


def test_parse_sensacine_extrae_titulo_fecha_url():
    items = ft.parse_sensacine(SENSACINE_HTML, HOY)
    assert len(items) == 2
    hoy_item = next(i for i in items if i["titulo"] == "Karateka")
    assert hoy_item["fecha_estreno"] == "2026-11-04"
    assert hoy_item["url"] == "https://www.sensacine.com/peliculas/pelicula-1000005692/"
    assert hoy_item["fuente"] == "SensaCine"


def test_parse_sensacine_filtrado_central_deja_solo_hoy():
    items = ft.filtrar_estrenos(ft.parse_sensacine(SENSACINE_HTML, HOY), HOY)
    assert [i["titulo"] for i in items] == ["Karateka"]


# =============================================================================
# Parser Filmaffinity (main.html, fecha sin año)
# =============================================================================
FILMAFFINITY_HTML = """
<a href="https://www.filmaffinity.com/es/film123456.html">
 <div class="fa-content-card">
  <div class="card-footer">
   <div class="mtitle mb-2">Película Ejemplo</div>
   <div><small>(4 de noviembre)</small></div>
  </div>
 </div>
</a>
<a href="https://www.filmaffinity.com/es/film654321.html">
 <div class="fa-content-card">
  <div class="card-footer">
   <div class="mtitle mb-2">Otra Película</div>
   <div><small>(10 de diciembre)</small></div>
  </div>
 </div>
</a>
"""


def test_parse_filmaffinity_fecha_sin_anio():
    items = ft.parse_filmaffinity(FILMAFFINITY_HTML, HOY)
    assert len(items) == 2
    ej = next(i for i in items if i["titulo"] == "Película Ejemplo")
    assert ej["fecha_estreno"] == "2026-11-04"  # año actual por defecto
    assert ej["url"] == "https://www.filmaffinity.com/es/film123456.html"


def test_parse_filmaffinity_filtrado_central_deja_solo_hoy():
    items = ft.filtrar_estrenos(ft.parse_filmaffinity(FILMAFFINITY_HTML, HOY), HOY)
    assert [i["titulo"] for i in items] == ["Película Ejemplo"]


# =============================================================================
# Parser TVMaze (schedule ES, solo S1E1)
# =============================================================================
TVMAZE_DATA = [
    {"season": 1, "number": 1, "airdate": "2026-11-04",
     "url": "https://www.tvmaze.com/episodes/1/serie-nueva-1x01",
     "summary": "<p>Estreno de la serie</p>",
     "show": {"name": "Serie Nueva", "url": "https://www.tvmaze.com/shows/1/serie-nueva",
              "network": {"name": "La 1"}}},
    {"season": 3, "number": 205, "airdate": "2026-11-04",
     "show": {"name": "Culebrón"}},          # no es S1E1 → fuera
    {"season": 1, "number": 1, "airdate": "2026-11-05",
     "show": {"name": "Otro Estreno"}},       # no es hoy → fuera
]


def test_parse_tvmaze_solo_s1e1_de_hoy():
    items = ft.parse_tvmaze(TVMAZE_DATA, HOY)
    assert len(items) == 1
    it = items[0]
    assert it["titulo"] == "Serie Nueva"
    assert it["fecha_estreno"] == "2026-11-04"
    assert it["cadena"] == "La 1"
    assert it["fuente"] == "TVMaze"


def test_parse_tvmaze_resumen_sin_html():
    items = ft.parse_tvmaze(TVMAZE_DATA, HOY)
    assert items[0]["sinopsis"] == "Estreno de la serie"


def test_parse_tvmaze_lista_vacia():
    assert ft.parse_tvmaze([], HOY) == []
    assert ft.parse_tvmaze(None, HOY) == []


# =============================================================================
# Fecha de ejecución
# =============================================================================
def test_fecha_ejecucion_es_date():
    assert isinstance(ft.fecha_ejecucion(), date)
