"""Tests del sondeo de cuota (`python -m src.main quota`).

El free tier no publica sus límites, así que la única fuente fiable es lo que
devuelve la propia API: cabeceras `x-ratelimit-*` y el cuerpo del 429.
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

import quota as q  # noqa: E402

# Cuerpo real del 429 que tumbó el workflow, con las dos formas de comillas:
# el mensaje llega con comillas simples y el details del JSON con dobles.
CUOTA_REAL = {
    "error": {
        "code": 429,
        "message": (
            "You exceeded your current quota... * Quota exceeded for metric: "
            "generativelanguage.googleapis.com/generate_content_free_tier_requests, "
            "limit: 20, model: gemini-2.5-flash\nPlease retry in 41.7s."
        ),
        "status": "RESOURCE_EXHAUSTED",
        "details": [
            {
                "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
                "quotaValue": "20",
            }
        ],
    }
}


class _Respuesta:
    def __init__(self, codigo, cabeceras=None, cuerpo=None, texto=""):
        self.status_code = codigo
        self.headers = cabeceras or {}
        self._cuerpo = cuerpo
        self.text = texto

    def json(self):
        if self._cuerpo is None:
            raise ValueError("sin json")
        return self._cuerpo


class _Cliente:
    def __init__(self, respuestas):
        self.respuestas = respuestas
        self.peticiones = []

    async def post(self, url, json=None, headers=None):
        model = url.split("/models/")[1].split(":")[0]
        self.peticiones.append(model)
        return self.respuestas.get(model, _Respuesta(200, {"x-test": "1"}))


def _sondear(respuestas, model="m"):
    return asyncio.run(q.sondear_modelo(_Cliente(respuestas), "k", model))


def test_lee_el_limite_de_las_cabeceras():
    r = _sondear({"m": _Respuesta(200, {
        "x-ratelimit-limit-requests": "1500",
        "x-ratelimit-remaining-requests": "1497",
    })})
    assert r["estado"] == "disponible"
    assert r["x-ratelimit-limit-requests"] == "1500"
    assert r["x-ratelimit-remaining-requests"] == "1497"


def test_saca_el_limite_diario_del_429():
    """Es el único sitio donde aparece el 20 del log del workflow."""
    r = _sondear({"m": _Respuesta(429, cuerpo=CUOTA_REAL)})
    assert r["estado"] == "429 sin cuota"
    assert r["limite_diario"] == "20"
    assert r["cuota"] == "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
    assert r["modelo_en_el_error"] == "gemini-2.5-flash"


def test_un_429_sin_json_no_revienta():
    r = _sondear({"m": _Respuesta(429, texto="plain text")})
    assert r["estado"] == "429 sin cuota"
    assert "limite_diario" not in r


def test_404_significa_que_el_modelo_no_existe():
    assert _sondear({"m": _Respuesta(404)})["estado"] == "404 no existe"


def test_otro_error_http_se_reporta_con_el_detalle():
    r = _sondear({"m": _Respuesta(400, texto="API key not valid")})
    assert r["estado"] == "http 400"
    assert "API key not valid" in r["detalle"]


def test_solo_interesting_las_cabeceras_de_cuota():
    r = _sondear({"m": _Respuesta(200, {
        "x-ratelimit-limit-requests": "20",
        "content-type": "application/json",
        "server": "scaffolding",
    })})
    assert "server" not in r and "content-type" not in r


def test_un_error_de_red_no_tumba_el_sondeo():
    class _Rojo(_Cliente):
        async def post(self, *a, **k):
            raise OSError("connection reset")

    r = asyncio.run(q.sondear_modelo(_Rojo({}), "k", "m"))
    assert r["estado"] == "error de red"


def test_sondea_en_serie_para_no_gastar_cuota_a_la_vez():
    cliente = _Cliente({})
    original = q.httpx.AsyncClient

    class _Stub:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return cliente

        async def __aexit__(self, *a):
            return False

    q.httpx.AsyncClient = _Stub
    try:
        modelos = ["a", "b", "c"]
        res = asyncio.run(q.sondear_todos("k", modelos))
    finally:
        q.httpx.AsyncClient = original

    assert [r["modelo"] for r in res] == modelos
    assert cliente.peticiones == modelos


def test_la_tabla_incluye_modelo_estado_y_limite():
    texto = q.formatear([
        {"modelo": "gemini-2.5-flash", "estado": "429 sin cuota", "limite_diario": "20",
         "cuota": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"},
        {"modelo": "gemini-2.5-pro", "estado": "404 no existe"},
    ])
    assert "gemini-2.5-flash" in texto
    assert "429 sin cuota" in texto
    assert "20" in texto
    assert "404 no existe" in texto


def test_los_modelos_sugeridos_no_repiten():
    assert len(q.MODELOS_SUGERIDOS) == len(set(q.MODELOS_SUGERIDOS))
