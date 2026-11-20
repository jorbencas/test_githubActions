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

from publishers.send_telegram import (
    VOICE_MAX_CHARS_IDIOMA,
    VOICE_MAX_POR_IDIOMA,
    _limitar_oraciones,
    construir_mensaje_noticia,
    hoy_ya_se_envio_voz,
    marcar_voz_enviada,
    obtener_timestamp_ultimo_audio,
)


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


def test_limitar_oraciones_por_numero():
    oraciones = [f"Titular número {i}" for i in range(100)]
    out = _limitar_oraciones(oraciones)
    assert len(out) == VOICE_MAX_POR_IDIOMA
    assert out[0] == oraciones[0]


def test_limitar_oraciones_por_caracteres():
    # Cada título ~100 chars → el tope de chars corta antes que el de nº
    oraciones = ["x" * 100 for _ in range(VOICE_MAX_POR_IDIOMA)]
    out = _limitar_oraciones(oraciones)
    total = sum(len(t) for t in out) + 2 * max(0, len(out) - 1)
    assert total <= VOICE_MAX_CHARS_IDIOMA
    assert len(out) >= 1


def test_limitar_oraciones_vacia():
    assert _limitar_oraciones([]) == []


def test_estado_voz_marcar_y_leer(tmp_path, monkeypatch):
    import publishers.send_telegram as st

    monkeypatch.setattr(st, "VOICE_SENT_LOG", str(tmp_path / "telegram_voice_sent.json"))
    assert hoy_ya_se_envio_voz() is False
    assert obtener_timestamp_ultimo_audio() is None

    marcar_voz_enviada(["Titular A", "Titular B"])
    assert hoy_ya_se_envio_voz() is True
    ts = obtener_timestamp_ultimo_audio()
    assert ts is not None

    # Re-marcar conserva el resto del estado
    marcar_voz_enviada(["Otro"])
    datos = st._leer_estado_voz()
    assert datos["news_count"] == 1
    assert datos["news_titles"] == ["Otro"]
