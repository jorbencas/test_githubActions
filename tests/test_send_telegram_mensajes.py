"""
test_send_telegram_mensajes.py — Formato del reporte tech (send_telegram.py):

Los mensajes usan parse_mode HTML: el título va en <b> y la noticia es un
<a href> azul clicable (nunca «Abrir noticia(url)» en crudo). Variante en
texto plano como fallback si Telegram rechaza el HTML.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from publishers.send_telegram import construir_mensaje_noticia


def test_mensaje_noticia_es_anchor_html():
    html, _plano = construir_mensaje_noticia(
        "OpenAI lanza GPT-6", "https://example.com/news")
    assert '<b>OpenAI lanza GPT-6</b>' in html
    assert '<a href="https://example.com/news">Abrir noticia</a>' in html
    assert "Abrir noticia (" not in html
    assert "](https://" not in html  # sin sintaxis Markdown


def test_mensaje_noticia_escapa_titulo_y_url():
    html, _plano = construir_mensaje_noticia(
        'Titular <b> & "comillas"', "https://e.com/?a=1&b=2")
    assert "&lt;b&gt;" in html
    assert "<b> &amp;" not in html          # el <b> interno NO queda crudo
    assert "&amp;b=2" in html               # & de la URL escapado en href
    assert '"comillas"' not in html         # comillas escapadas


def test_mensaje_noticia_variante_plano():
    _html, plano = construir_mensaje_noticia("Título", "https://e.com/x")
    assert plano == "💻 Título\n\nhttps://e.com/x"
    assert "<" not in plano


def test_mensaje_noticia_titulo_vacio():
    html, plano = construir_mensaje_noticia("", "https://e.com/x")
    assert 'href="https://e.com/x"' in html
    assert plano.endswith("https://e.com/x")
