"""Tests del rescuata de respuestas cortadas por falta de tokens.

El workflow falló con `Unterminated string starting at: line 531 column 9
(char 32666)`: el modelo llenó los 8000 tokens de salida y el JSON quedó a
medias, así que no salió ni un proyecto y a Telegram no llegó nada. Estos tests
fijan el comportamiento que evita eso.
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

import ai_providers  # noqa: E402
from ai_providers import (  # noqa: E402
    GeminiProvider,
    ResponseTruncatedError,
    _tope_salida,
)
from prompts import recuperar_proyectos, validate_project_json  # noqa: E402


# --- La respuesta truncada del log ---------------------------------------------

TRUNCADO = (
    '{"proyectos": [\n'
    '  {"id":"e4a0b2d1c3","titulo":"Generador de Documentación Técnica con IA",'
    '"descripcion_corta":"Genera READMEs y diagramas desde código.",'
    '"descripcion_detallada":"App fullstack que sube código y genera documentación.",'
    '"nivel":"semisenior","scope":"proyecto","tipo":["web"],'
    '"tech_stack":{"lenguaje_principal":"python","frameworks":[]},'
    '"funcionalidades_clave":["Subir código"],"casos_uso":["Documentar una API"],'
    '"complejidad_estimada":"media","tiempo_estimado_semanas":4,'
    '"hash_unicidad":"aaa111"},\n'
    '  {"id":"b7c3d9e2f1","titulo":"Buscador Semántico de Documentos",'
    '"descripcion_corta":"Encuentra documentos por significado.",'
    '"descripcion_detallada":"Indexa PDFs con embeddings y busca por similitud.",'
    '"nivel":"semisenior","scope":"proyecto","tipo":["ia_ml"],'
    '"tech_stack":{"lenguaje_principal":"python"},'
    '"funcionalidades_clave":["Indexar"],"casos_uso":["Buscar"],'
    '"complejidad_estimada":"media","tiempo_estimado_semanas":5,'
    '"hash_unicidad":"bbb222"},\n'
    '  {"id":"c9d1e4f7a3","titulo":"Traductor de Aulas",'
    '"descripcion_corta":"Traduce grabaciones de clase.",'
    '"descripcion_detallada":"Sube un audio, lo transcribe y lo traduce al español, la respuesta se corta aquí y el RUN se interrumpe a mitad de la cadena sin cerrarla'
)


def test_el_json_truncado_no_parsea_como_json_normal():
    """El síntoma que se vio en el log."""
    import json
    with pytest.raises(json.JSONDecodeError):
        json.loads(TRUNCADO)


def test_se_rescatan_los_dos_proyectos_completos():
    """El punto del ejercicio: no perder los que sí llegaron enteros."""
    rescatados = recuperar_proyectos(TRUNCADO)
    assert [p["titulo"] for p in rescatados] == [
        "Generador de Documentación Técnica con IA",
        "Buscador Semántico de Documentos",
    ]


def test_el_proyecto_a_medias_se_descarta():
    assert all(p["id"] != "c9d1e4f7a3" for p in recuperar_proyectos(TRUNCADO))


def test_lo_rescatado_sigue_siendo_validable():
    """Rescatar no vale de nada si luego no se puede construir el modelo."""
    from models import Proyecto
    validados = validate_project_json({"proyectos": recuperar_proyectos(TRUNCADO)})
    assert len(validados) == 2
    for datos in validados:
        assert Proyecto(**datos).hash_unicidad


# --- Casos límite del escáner --------------------------------------------------

def test_una_llave_dentro_de_un_string_no_cuenta():
    """Un `{` o `}` en un texto no debe desbalancear el conteo."""
    texto = ('{"proyectos":[{"titulo":"Genera {JSON} desde un template",'
             '"notas":"cierra } y abre { aqui","hash_unicidad":"x1"}]}')
    assert len(recuperar_proyectos(texto)) == 1


def test_escapes_de_comilla_no_abren_cadena():
    texto = r'{"proyectos":[{"titulo":"Dice \"hola\" y sigue","hash_unicidad":"x2"}]}'
    assert recuperar_proyectos(texto)[0]["titulo"] == 'Dice "hola" y sigue'


def test_objeto_incompleto_al_final_se_ignora_sin_quejarse():
    texto = '{"proyectos":[{"titulo":"Completo","hash_unicidad":"a"},{"titulo":"Roto'
    assert len(recuperar_proyectos(texto)) == 1


def test_texto_sin_la_clave_proyectos_devuelve_lista_vacia():
    assert recuperar_proyectos("Hola, soy un modelo y no devuelvo JSON") == []
    assert recuperar_proyectos("") == []
    assert recuperar_proyectos(None) == []


def test_json_completo_no_pierde_ninguno():
    texto = '{"proyectos":[' + ",".join(
        f'{{"titulo":"P{i}","hash_unicidad":"h{i}"}}' for i in range(5)
    ) + ']}'
    assert len(recuperar_proyectos(texto)) == 5


# --- Detección del corte en el proveedor ---------------------------------------

class _Respuesta:
    def __init__(self, texto, finish_reason=None, tokens=None):
        self.text = texto
        self.finish_reason = finish_reason
        self.usage_metadata = None
        if tokens is not None:
            self.usage_metadata = type("Uso", (), {"candidates_token_count": tokens})()


class _Cliente:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.models = type("M", (), {"generate_content": staticmethod(self._responder)})

    def _responder(self, *a, **k):
        return self.respuesta


def _proveedor(respuesta):
    p = GeminiProvider.__new__(GeminiProvider)
    p.api_key = "k"
    p.models = ["gemini-2.5-flash"]
    p.model = "gemini-2.5-flash"
    p.client = _Cliente(respuesta)
    return p


def test_finish_reason_max_tokens_avisa_en_vez_de_pasarse():
    """Antes esto pasaba por respuesta buena y el error salía 20 líneas más abajo."""
    p = _proveedor(_Respuesta(TRUNCADO, "MAX_TOKENS", tokens=8000))
    with pytest.raises(ResponseTruncatedError) as exc:
        asyncio.run(p.generate("prompt", "system"))
    assert "MAX_TOKENS" in str(exc.value)
    assert "8000" in str(exc.value)


def test_el_error_lleva_el_texto_para_poder_rescatar():
    p = _proveedor(_Respuesta(TRUNCADO, "MAX_TOKENS"))
    with pytest.raises(ResponseTruncatedError) as exc:
        asyncio.run(p.generate("prompt", "system"))
    assert len(recuperar_proyectos(exc.value.texto)) == 2


def test_una_respuesta_completa_no_dispara_el_error():
    completo = '{"proyectos":[{"titulo":"P","hash_unicidad":"h"}]}'
    p = _proveedor(_Respuesta(completo, "STOP"))
    assert asyncio.run(p.generate("prompt", "system")) == completo


def test_tenacity_no_reintenta_un_corte():
    """Reintentar un corte es gastar cuota a sabiendas: siempre acaba igual."""
    assert ai_providers._debe_reintentar(ResponseTruncatedError("cortada")) is False


# --- Topes por modelo ----------------------------------------------------------

@pytest.mark.parametrize("modelo,tope", [
    ("gemini-2.5-flash", 32768),
    ("gemini-2.5-flash-lite", 32768),
    ("gemini-2.5-pro", 32768),
    ("gemini-2.0-flash-lite", 8192),
    ("gemini-2.0-flash", 8192),
    ("gemini-1.5-flash", 8192),
    ("modelo-inventado", 8192),
])
def test_tope_de_salida_por_modelo(modelo, tope):
    assert _tope_salida(modelo) == tope


def test_se_recorta_la_peticion_para_no_recibir_un_400():
    """Pedir 16384 a un 2.0-flash es un 400 y tiraba la generación."""
    p = GeminiProvider.__new__(GeminiProvider)
    _, config = p._preparar_contenidos(
        "gemini-2.0-flash-lite", "prompt", "system", {"max_output_tokens": 16384}
    )
    assert config["max_output_tokens"] == 8192


def test_un_25_acepta_el_tope_alto():
    p = GeminiProvider.__new__(GeminiProvider)
    _, config = p._preparar_contenidos(
        "gemini-2.5-flash", "prompt", "system", {"max_output_tokens": 16384}
    )
    assert config["max_output_tokens"] == 16384


def test_el_thinking_se_desactiva_para_que_el_json_no_se_quede_sin_sitio():
    p = GeminiProvider.__new__(GeminiProvider)
    _, config = p._preparar_contenidos("gemini-2.5-flash", "p", "s", {})
    assert config["thinking_config"] == {"thinking_budget": 0}


def test_el_20_no_recibe_thinking_config():
    """En 2.0 `thinking_config` es un 400."""
    p = GeminiProvider.__new__(GeminiProvider)
    _, config = p._preparar_contenidos("gemini-2.0-flash", "p", "s", {})
    assert "thinking_config" not in config
