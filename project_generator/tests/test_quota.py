"""Tests del reparto de cuota de Gemini en project_generator.

La cuota del free tier es por día, proyecto y modelo (20 peticiones para
gemini-2.5-flash) y la comparten todos los workflows del repo, así que el
generador se comía un 429 ajeno. Estos tests fijan el comportamiento
esperado: distinguir el tope diario de un límite de ritmo, no malgastar
peticiones reintentando lo que no se puede recuperar y no tumbar el job.
"""
import asyncio
import os
import sys
import types
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

# Settings exige estas variables al importarse, y solo se leen del entorno.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

import ai_providers as ap  # noqa: E402
from google.genai import errors as ge  # noqa: E402

# Error real devuelto por la API (recortado) en el run que falló.
ERROR_TOPE_DIARIO = (
    "You exceeded your current quota, please check your plan and billing details. "
    "* Quota exceeded for metric: generativelanguage.googleapis.com/"
    "generate_content_free_tier_requests, limit: 20, model: gemini-2.5-flash\n"
    "Please retry in 41.7754725s. "
    "'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier'"
)


def _error_429(mensaje: str) -> ge.ClientError:
    return ge.ClientError(429, {"error": {"message": mensaje, "status": "RESOURCE_EXHAUSTED"}}, None)


class _ClienteFalso:
    """Cliente que cuenta llamadas y siempre lanza la excepción indicada."""

    def __init__(self, excepcion: Exception):
        self.excepcion = excepcion
        self.llamadas = 0
        self.models = types.SimpleNamespace(generate_content=self._responder)

    def _responder(self, **_kwargs):
        self.llamadas += 1
        raise self.excepcion


def _proveedor(cliente) -> ap.GeminiProvider:
    prov = ap.GeminiProvider.__new__(ap.GeminiProvider)
    prov.api_key = "test-key"
    prov.model = "gemini-2.5-flash-lite"
    prov.client = cliente
    return prov


def test_reconoce_el_tope_diario_de_cuota():
    assert ap._es_tope_diario(_error_429(ERROR_TOPE_DIARIO)) is True


def test_un_429_de_ritmo_no_es_tope_diario():
    error = _error_429("Resource has been exhausted. Please retry in 0.05s.")
    assert ap._es_tope_diario(error) is False


def test_extrae_el_RetryInfo_del_servidor():
    assert ap._espera_sugerida_por_la_api(_error_429(ERROR_TOPE_DIARIO)) == pytest.approx(41.78, abs=0.01)


def test_el_tope_diario_no_se_reintenta():
    """Un límite por día no se arregla esperando: una sola llamada y avisar."""
    cliente = _ClienteFalso(_error_429(ERROR_TOPE_DIARIO))
    prov = _proveedor(cliente)

    with pytest.raises(ap.QuotaExhaustedError):
        asyncio.run(prov.generate("prompt", "system"))

    assert cliente.llamadas == 1, "no debe malgastar peticiones reintentando un tope diario"


def test_el_tope_diario_no_pasa_por_el_fallback_determinista():
    """El fallback daría las mismas plantillas de siempre, así que no debe activarse."""
    assert issubclass(ap.QuotaExhaustedError, ap.AIProviderError)
    assert ap._debe_reintentar(ap.QuotaExhaustedError("x")) is False


def test_un_429_de_ritmo_se_reintenta_respetando_la_espera():
    """Aquí sí tiene sentido reintentar, y se espera lo que dice la API."""
    cliente = _ClienteFalso(_error_429("Resource has been exhausted. Please retry in 0.05s."))
    prov = _proveedor(cliente)

    with pytest.raises(ge.ClientError):
        asyncio.run(prov.generate("prompt", "system"))

    # 3 del bucle interno, y tenacity NO debe multiplicar el intento.
    assert cliente.llamadas == 3


def test_un_error_distinto_de_429_si_se_reintenta():
    cliente = _ClienteFalso(ge.ServerError(500, {"error": {"message": "internal"}}, None))
    prov = _proveedor(cliente)

    with pytest.raises(Exception):
        asyncio.run(prov.generate("prompt", "system"))

    assert cliente.llamadas == 3, "un 500 sigue confiando en la reentrada de tenacity"


def test_cmd_generate_no_tumba_el_job_con_el_tope_agotado():
    """La cuota agotada deja el historial intacto y no envía nada a Telegram."""
    import main as main_mod

    enviados = []

    def _falla(*_args, **_kwargs):
        raise ap.QuotaExhaustedError("Cuota diaria agotada.")

    main_mod.ProjectGenerator.generate_projects = _falla
    main_mod.send_to_telegram = lambda *a, **k: enviados.append(1) or True

    args = types.SimpleNamespace(
        count=3, nivel=None, scope=None, lenguaje=None, tipo=None, send_telegram=True
    )
    resultado = asyncio.run(main_mod.cmd_generate(args))

    assert resultado == []
    assert not enviados, "no debe enviar nada a Telegram si no se generó nada"
