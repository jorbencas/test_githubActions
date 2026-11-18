#!/usr/bin/env python3
"""
test_disponibilidad.py — Tests de utils.disponibilidad: verificación de
enlaces vivos (HEAD/GET, códigos anti-bot) y filtrado de items caídos.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from utils.disponibilidad import filtrar_disponibles, verificar_url


def _resp(status):
    r = MagicMock()
    r.status_code = status
    return r


# =============================================================================
# verificar_url
# =============================================================================
def test_url_vacia_no_vive():
    ok, motivo = verificar_url("")
    assert ok is False
    assert motivo == "sin enlace"


def test_esquema_no_soportado():
    ok, motivo = verificar_url("ftp://example.com/x")
    assert ok is False
    assert motivo == "esquema no soportado"


@patch("utils.disponibilidad.requests.head")
def test_200_es_vivo(mock_head):
    mock_head.return_value = _resp(200)
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is True
    assert motivo == "200"


@patch("utils.disponibilidad.requests.head")
def test_301_es_vivo(mock_head):
    mock_head.return_value = _resp(301)
    ok, _ = verificar_url("https://example.com/a")
    assert ok is True


@patch("utils.disponibilidad.requests.head")
def test_403_anti_bot_es_vivo(mock_head):
    """403/429 = protección anti-bot → el enlace vive para el lector."""
    mock_head.return_value = _resp(403)
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is True
    assert motivo == "403"


@patch("utils.disponibilidad.requests.head")
def test_429_anti_bot_es_vivo(mock_head):
    mock_head.return_value = _resp(429)
    ok, _ = verificar_url("https://example.com/a")
    assert ok is True


@patch("utils.disponibilidad.requests.head")
def test_401_paywall_es_vivo(mock_head):
    """401 = paywall (Reuters/WSJ) → el artículo existe para el lector."""
    mock_head.return_value = _resp(401)
    ok, _ = verificar_url("https://example.com/a")
    assert ok is True


@patch("utils.disponibilidad.requests.head")
def test_999_linkedin_es_vivo(mock_head):
    """999 = código anti-bot de LinkedIn → el enlace vive."""
    mock_head.return_value = _resp(999)
    ok, _ = verificar_url("https://example.com/a")
    assert ok is True


@patch("utils.disponibilidad.requests.head")
def test_404_es_muerto(mock_head):
    mock_head.return_value = _resp(404)
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "HTTP 404"


@patch("utils.disponibilidad.requests.head")
def test_410_es_muerto(mock_head):
    mock_head.return_value = _resp(410)
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "HTTP 410"


@patch("utils.disponibilidad.requests.head")
def test_500_es_muerto(mock_head):
    mock_head.return_value = _resp(503)
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "HTTP 503"


@patch("utils.disponibilidad.requests.head")
def test_405_falla_con_get(mock_head):
    """HEAD rechazado (405) → se reintenta con GET."""
    import requests as rq
    mock_head.return_value = _resp(405)
    with patch("utils.disponibilidad.requests.get") as mock_get:
        mock_get.return_value = _resp(200)
        ok, motivo = verificar_url("https://example.com/a")
        assert ok is True
        assert mock_get.called


@patch("utils.disponibilidad.requests.head")
def test_timeout_es_muerto(mock_head):
    import requests as rq
    mock_head.side_effect = rq.exceptions.Timeout()
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "timeout"


@patch("utils.disponibilidad.requests.head")
def test_ssl_es_muerto(mock_head):
    import requests as rq
    mock_head.side_effect = rq.exceptions.SSLError()
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "SSL"


@patch("utils.disponibilidad.requests.head")
def test_connection_error_es_muerto(mock_head):
    import requests as rq
    mock_head.side_effect = rq.exceptions.ConnectionError()
    ok, motivo = verificar_url("https://example.com/a")
    assert ok is False
    assert motivo == "ConnectionError"


# =============================================================================
# filtrar_disponibles
# =============================================================================
@patch("utils.disponibilidad.verificar_url")
def test_filtrar_separa_vivos_y_muertos(mock_ver):
    def _ver(url, timeout=10):
        if "viva" in url:
            return True, "200"
        if "anti" in url:
            return True, "403"
        return False, "HTTP 404"

    mock_ver.side_effect = _ver
    items = [
        {"titulo": "a", "enlace": "https://x/viva1"},
        {"titulo": "b", "enlace": "https://x/muerta"},
        {"titulo": "c", "enlace": "https://x/anti"},
        {"titulo": "d"},  # sin enlace → se conserva
    ]
    vivos, muertos = filtrar_disponibles(items, campo="enlace")
    assert [i["titulo"] for i in vivos] == ["a", "c", "d"]
    assert len(muertos) == 1
    assert muertos[0][0]["titulo"] == "b"
    assert muertos[0][1] == "HTTP 404"


@patch("utils.disponibilidad.verificar_url")
def test_filtrar_conserva_orden(mock_ver):
    mock_ver.side_effect = lambda url, timeout=10: (True, "200")
    items = [{"enlace": f"https://x/{i}"} for i in range(5)]
    vivos, muertos = filtrar_disponibles(items)
    assert [i["enlace"] for i in vivos] == [i["enlace"] for i in items]
    assert muertos == []


@patch("utils.disponibilidad.verificar_url")
def test_filtrar_campo_url(mock_ver):
    mock_ver.side_effect = lambda url, timeout=10: (
        (True, "200") if "ok" in url else (False, "HTTP 404")
    )
    items = [
        {"titulo": "x", "url": "https://x/ok"},
        {"titulo": "y", "url": "https://x/gone"},
    ]
    vivos, muertos = filtrar_disponibles(items, campo="url")
    assert [i["titulo"] for i in vivos] == ["x"]
    assert muertos[0][0]["titulo"] == "y"


@patch("utils.disponibilidad.verificar_url")
def test_filtrar_lista_vacia(mock_ver):
    vivos, muertos = filtrar_disponibles([])
    assert vivos == []
    assert muertos == []
    mock_ver.assert_not_called()


@patch("utils.disponibilidad.verificar_url")
def test_filtrar_excepcion_no_tumba(mock_ver):
    """Una excepción inesperada en una URL no debe tumbar el filtrado."""
    def _ver(url, timeout=10):
        if "boom" in url:
            raise RuntimeError("inesperado")
        return True, "200"

    mock_ver.side_effect = _ver
    items = [
        {"enlace": "https://x/ok"},
        {"enlace": "https://x/boom"},
    ]
    vivos, muertos = filtrar_disponibles(items)
    assert len(vivos) == 1
    assert len(muertos) == 1
    assert muertos[0][1] == "RuntimeError"
