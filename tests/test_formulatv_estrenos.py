"""
test_formulatv_estrenos.py — Tests de parsers y filtros de estrenos del día
(scrape_formulatv_telegram.py): fecha de ejecución (Europe/Madrid), blocklist
("Los ilusos 13+13"), dedup y fuentes (FormulaTV, SensaCine, Filmaffinity,
TVMaze, Movistar+, À Punt, RSS de noticias y backfill silencioso).
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


# =============================================================================
# Formato del mensaje (parse_mode HTML: enlaces reales + escapado)
# =============================================================================
def test_formatear_mensaje_link_es_anchor_html():
    items = [ft._item("Serie X", HOY, "SensaCine", "SensaCine",
                      "https://e.com/a?b=1&c=2")]
    msg = ft.formatear_mensaje(items)
    assert '<a href="https://e.com/a?b=1&amp;c=2">Leer artículo</a>' in msg
    assert "Leer artículo (" not in msg


def test_formatear_mensaje_escapa_datos():
    items = [ft._item('Titular <b> & "raro"', HOY, "Cadena & Cia", "Cadena & Cia",
                      "https://e.com/x", sinopsis='Sinopsis <script>alert(1)</script> & más')]
    msg = ft.formatear_mensaje(items)
    assert "<script>" not in msg
    assert "&lt;b&gt;" in msg          # título escapado
    assert "Cadena &amp; Cia" in msg   # cadena escapada
    assert "&lt;script&gt;" in msg     # sinopsis escapada


# =============================================================================
# Fuente 5 — À Punt: noticias de la serie "Bambalina"
# =============================================================================
APUNT_NOTAS_HTML = """
<html><body>
<article class="content text-side" data-cid="1904888">
  <a class="multimedia"
     href="https://www.apuntmedia.es/sala-de-premsa/comenca-rodatge-bambalina_1_1904888.html"
     title="Comença el rodatge de ‘Bambalina’"><picture></picture></a>
  <div class="content-info">28/10/2026</div>
  <div class="content-text"><p>La nova sèrie de ficció pròpia d’À Punt enceta el rodatge.</p></div>
</article>
<article class="content text-side" data-cid="1">
  <a class="multimedia"
     href="https://www.apuntmedia.es/sala-de-premsa/otra-noticia_1_1.html"
     title="Otra noticia sin relación">x</a>
  <div class="content-info">01/11/2026</div>
</article>
</body></html>
"""

APUNT_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Nueva entrega de Bambalina en À Punt</title>
    <link>https://www.apuntmedia.es/noticies/cultura/bambalina-entrega.html</link>
    <pubDate>Wed, 04 Nov 2026 10:00:00 +0100</pubDate>
  </item>
  <item>
    <title>Deportes: resultado del fin de semana</title>
    <link>https://www.apuntmedia.es/esports/futbol.html</link>
    <pubDate>Wed, 04 Nov 2026 11:00:00 +0100</pubDate>
  </item>
</channel></rss>
"""


def test_parse_apunt_notas_filtra_keyword():
    items = ft.parse_apunt_notas(APUNT_NOTAS_HTML)
    assert len(items) == 1
    it = items[0]
    assert "Bambalina" in it["titulo"]
    assert it["fecha_estreno"] == "2026-10-28"
    assert it["cadena"] == "À Punt"
    assert it["fuente"] == "À Punt"
    assert it["capitulos"] is None
    assert "rodatge" in it["sinopsis"]


def test_parse_apunt_rss_filtra_keyword():
    items = ft.parse_apunt_rss(APUNT_RSS_XML)
    assert len(items) == 1
    it = items[0]
    assert "Bambalina" in it["titulo"]
    assert it["fecha_estreno"] == "2026-11-04"
    assert it["url"].endswith("bambalina-entrega.html")
    assert it["capitulos"] is None


def test_parse_apunt_rss_ilegible():
    assert ft.parse_apunt_rss("no es xml <<<") == []


def test_filtrar_noticias_ventana_14_dias():
    nuevo = ft._item("Bambalina reciente", HOY, "À Punt", "À Punt",
                     "https://x/1", capitulos=None)
    limite = ft._item("Bambalina hace 14 días", date(2026, 10, 21), "À Punt",
                      "À Punt", "https://x/2", capitulos=None)
    viejo = ft._item("Bambalina antigua", date(2026, 10, 1), "À Punt",
                     "À Punt", "https://x/3", capitulos=None)
    futuro = ft._item("Bambalina futura", MANANA, "À Punt", "À Punt",
                      "https://x/4", capitulos=None)
    out = ft.filtrar_noticias([nuevo, limite, viejo, futuro], HOY)
    assert [i["titulo"] for i in out] == ["Bambalina reciente", "Bambalina hace 14 días"]


def test_noticias_a_punt_sin_tag_pelicula_y_grupo_propio():
    it = ft._item("Comença el rodatge de Bambalina", HOY, "À Punt", "À Punt",
                  "https://www.apuntmedia.es/sala-de-premsa/bambalina.html",
                  capitulos=None)
    msg = ft.formatear_mensaje([it])
    assert "🎬 Película" not in msg
    assert "📍 <b>À Punt</b>" in msg
    assert '<a href="https://www.apuntmedia.es/sala-de-premsa/bambalina.html">Leer artículo</a>' in msg


# =============================================================================
# Fuente 6 — Movistar+ («Hoy en M+ Estrenos»)
# =============================================================================
MOVISTAR_HTML = """
<html><body>
<section><h2 class="section-header__title">Hoy en M+ Estrenos</h2>
<div class="mplus-collection__content"><ul class="brand-carousel">
  <li><div class="mplus-collection__date">05:05</div>
    <a href="https://www.movistarplus.es/cine/frontera/ficha?tipo=E&id=1" class="mplus-collection__card">
      <div class="mplus-collection__title">Cine</div>
      <div class="mplus-collection__subtitle">Frontera</div></a></li>
  <li><div class="mplus-collection__date">06:44</div>
    <a href="https://www.movistarplus.es/cine/salt/ficha?tipo=E&id=2" class="mplus-collection__card">
      <div class="mplus-collection__title">Cine</div>
      <div class="mplus-collection__subtitle">Salt</div></a></li>
</ul></div></section>
<section><h2 class="section-header__title">Si te gusta M+ Estrenos te gustará…</h2>
<div class="mplus-collection__content"><ul>
  <li><a href="https://www.movistarplus.es/cine/otra/ficha?id=3">
    <div class="mplus-collection__subtitle">Recomendación</div></a></li>
</ul></div></section>
</body></html>
"""


def test_parse_movistar_estrenos_solo_coleccion_hoy():
    items = ft.parse_movistar_estrenos(MOVISTAR_HTML, HOY)
    assert [i["titulo"] for i in items] == ["Frontera", "Salt"]
    assert all(i["fecha_estreno"] == "2026-11-04" for i in items)
    assert all(i["fuente"] == "Movistar+" for i in items)
    assert items[0]["url"].startswith("https://www.movistarplus.es/cine/")


def test_parse_movistar_estrenos_ignora_recomendaciones():
    items = ft.parse_movistar_estrenos(MOVISTAR_HTML, HOY)
    assert "Recomendación" not in [i["titulo"] for i in items]


def test_parse_movistar_estrenos_sin_seccion_hoy():
    assert ft.parse_movistar_estrenos("<html><body><p>nada</p></body></html>", HOY) == []


# =============================================================================
# Fuente 7 — RSS de noticias de series/cine
# =============================================================================
RSS_FORMULATV = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>FormulaTV</title>
  <item>
    <title>La 1 estrena serie nueva</title>
    <link>https://www.formulatv.com/noticias/serie-nueva/</link>
    <pubDate>Wed, 04 Nov 2026 08:00:00 +0100</pubDate>
  </item>
  <item>
    <title>Sin enlace ni fecha</title>
  </item>
  <item>
    <title>Otra noticia</title>
    <link>https://www.formulatv.com/noticias/otra/</link>
    <pubDate>Mon, 02 Nov 2026 10:00:00 +0100</pubDate>
  </item>
</channel></rss>
"""


def test_parse_rss_noticias_extrae_items_completos():
    items = ft.parse_rss_noticias(RSS_FORMULATV, "FormulaTV")
    assert len(items) == 2
    assert items[0]["titulo"] == "La 1 estrena serie nueva"
    assert items[0]["fecha_estreno"] == "2026-11-04"
    assert items[0]["url"] == "https://www.formulatv.com/noticias/serie-nueva/"
    assert items[0]["cadena"] == "FormulaTV"
    assert items[0]["capitulos"] is None


def test_parse_rss_noticias_acepta_fecha_iso():
    rss = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
      <entry><title>Atom item</title><link href="https://x/1"/>
      <updated>2026-11-03T12:00:00Z</updated></entry></feed>"""
    items = ft.parse_rss_noticias(rss, "Fotogramas")
    assert len(items) == 1
    assert items[0]["fecha_estreno"] == "2026-11-03"


def test_parse_rss_noticias_ilegible():
    assert ft.parse_rss_noticias("esto no es xml <<<", "SensaCine") == []


# =============================================================================
# Rutas del repo (regresión: REPO_DIR sobraba un nivel y files/ caía fuera)
# =============================================================================
def test_repo_dir_y_sent_file_dentro_del_repo():
    repo = Path(__file__).resolve().parent.parent
    assert ft.REPO_DIR == repo
    assert ft.SENT_FILE == repo / 'files' / 'formulatv_sent.json'
    assert (ft.REPO_DIR / 'scripts' / 'scrape_formulatv_telegram.py').exists()


# =============================================================================
# Backfill silencioso (noticias antiguas se marcan sin enviar)
# =============================================================================
def test_partir_backfill_noticias_viejas_no_se_envian():
    vieja = dict(ft._item("Noticia de hace 10 días", date(2026, 10, 25),
                          "Fotogramas", "Fotogramas", "https://x/1", capitulos=None),
                 noticia=True)
    reciente = dict(ft._item("Noticia de ayer", date(2026, 11, 3),
                             "Fotogramas", "Fotogramas", "https://x/2", capitulos=None),
                    noticia=True)
    estreno = ft._item("Estreno de hoy", HOY, "SensaCine", "SensaCine", "https://x/3")
    enviar, backfill = ft.partir_backfill([vieja, reciente, estreno], HOY)
    assert [i["titulo"] for i in enviar] == ["Noticia de ayer", "Estreno de hoy"]
    assert [i["titulo"] for i in backfill] == ["Noticia de hace 10 días"]


def test_partir_backfill_estrenos_nunca_son_backfill():
    estreno = ft._item("Estreno", HOY, "FormulaTV", "La 1", "https://x/1")
    enviar, backfill = ft.partir_backfill([estreno], HOY)
    assert len(enviar) == 1 and backfill == []


# =============================================================================
# TVMaze: estrenos de temporada (episodio 1 de cualquier temporada)
# =============================================================================
def test_parse_tvmaze_acepta_estrenos_de_temporada():
    data = [
        {"season": 2, "number": 1, "airdate": "2026-11-04",
         "show": {"name": "Segunda Temporada", "network": {"name": "Movistar+"}}},
        {"season": 2, "number": 2, "airdate": "2026-11-04",
         "show": {"name": "Segunda Temporada"}},
    ]
    items = ft.parse_tvmaze(data, HOY)
    assert [i["titulo"] for i in items] == ["Segunda Temporada"]
