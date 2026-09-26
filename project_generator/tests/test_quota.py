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


def _proveedor(cliente, models="gemini-2.5-flash-lite") -> ap.GeminiProvider:
    prov = ap.GeminiProvider.__new__(ap.GeminiProvider)
    prov.api_key = "test-key"
    prov.models = [m.strip() for m in models.split(",") if m.strip()]
    prov.model = prov.models[0]
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


# ── Cadena de modelos ────────────────────────────────────────────────────────

class _ClientePorModelo:
    """Responde solo a los modelos de `disponibles`; el resto da 404."""

    def __init__(self, disponibles, error=404):
        self.disponibles = disponibles
        self.error = error
        self.llamadas = []

    def _responder(self, model=None, **_kwargs):
        self.llamadas.append(model)
        if model not in self.disponibles:
            if self.error == 404:
                raise ge.ClientError(
                    404, {"error": {"message": "models/x is not found", "status": "NOT_FOUND"}}, None
                )
            raise self.error
        return types.SimpleNamespace(text='{"proyectos": []}')

    @property
    def models(self):
        return types.SimpleNamespace(generate_content=self._responder)


def test_la_lista_de_modelos_se_prueba_en_orden():
    prov = ap.GeminiProvider.__new__(ap.GeminiProvider)
    prov.models = [m.strip() for m in "a, b ,c".split(",") if m.strip()]
    assert prov.models == ["a", "b", "c"]


def test_si_el_primer_modelo_no_existe_pasa_al_siguiente():
    """Es el caso que motivó el fallback: flash-lite sin 404 disponible."""
    cliente = _ClientePorModelo({"gemini-2.5-flash"})
    prov = _proveedor(cliente, "gemini-2.5-flash-lite,gemini-2.5-flash")

    respuesta = asyncio.run(prov.generate("p", "s"))

    assert respuesta == '{"proyectos": []}'
    assert cliente.llamadas == ["gemini-2.5-flash-lite", "gemini-2.5-flash"]


def test_si_el_primer_modelo_no_tiene_cuota_pasa_al_siguiente():
    """El cupo es por modelo, así que el siguiente puede seguir teniendo."""
    cliente = _ClientePorModelo(
        {"gemini-2.5-flash"},
        error=_error_429(ERROR_TOPE_DIARIO),
    )
    prov = _proveedor(cliente, "gemini-2.5-flash-lite,gemini-2.5-flash")

    respuesta = asyncio.run(prov.generate("p", "s"))

    assert respuesta == '{"proyectos": []}'
    assert cliente.llamadas == ["gemini-2.5-flash-lite", "gemini-2.5-flash"]


def test_si_ningun_modelo_sirve_el_ultimo_error_propaga():
    """Con un solo modelo, un 404 debe seguir siendo un fallo ruidoso."""
    cliente = _ClientePorModelo(set())
    prov = _proveedor(cliente, "gemini-2.5-flash-lite")

    with pytest.raises(ap.ModelNotAvailableError):
        asyncio.run(prov.generate("p", "s"))


def test_el_nombre_del_modelo_refleja_toda_la_cadena():
    prov = ap.GeminiProvider.__new__(ap.GeminiProvider)
    prov.models = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
    prov.model = prov.models[0]
    assert prov.get_model_name() == "gemini:gemini-2.5-flash-lite > gemini-2.5-flash"
