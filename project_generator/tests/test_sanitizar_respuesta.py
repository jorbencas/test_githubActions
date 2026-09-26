"""Tests del saneado de la respuesta de la IA antes de construir los modelos.

Reproduce el fallo que tumbó el workflow: el modelo devolvió
`tech_stack.ia_ml[0].url_docs = "N/A"` y Pydantic, que exige HttpUrl, abortó
el run entero, tirando también los otros proyectos que sí eran válidos.
"""
import os
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from models import Proyecto  # noqa: E402
from prompts import limpiar_tech_stack, validate_project_json, _url_es_valida  # noqa: E402


def _proyecto(url_docs, titulo="Comparador de PDFs"):
    """Proyecto mínimo válido, con una herramienta que lleva el url_docs."""
    return {
        "titulo": titulo,
        "descripcion_corta": "Compara dos PDFs y saca las diferencias",
        "descripcion_detallada": "Sube dos PDFs, extrae el texto y genera un informe de diferencias.",
        "nivel": "semisenior",
        "scope": "proyecto",
        "tipo": ["web"],
        "tech_stack": {
            "lenguaje_principal": "python",
            "frameworks": [],
            "librerias": [],
            "bases_datos": [],
            "infraestructura": [],
            "ia_ml": [{
                "nombre": "difflib",
                "categoria": "lib",
                "descripcion": "Diffs línea a línea",
                "url_docs": url_docs,
            }],
            "testing": [],
            "otros": [],
        },
        "funcionalidades_clave": ["Subir PDFs", "Comparar texto"],
        "casos_uso": ["Revisar contratos"],
        "complejidad_estimada": "media",
        "tiempo_estimado_semanas": 4,
        "hash_unicidad": "abc123",
    }


# --- El caso exacto del log ----------------------------------------------------

def test_el_na_del_log_ya_no_revierte_nada():
    """Si esto falla, el workflow vuelve a caer."""
    for valor in ["N/A", "n/a", "-", "none", "N/D", "No disponible", "", "   "]:
        limpio = limpiar_tech_stack(_proyecto(valor)["tech_stack"])
        assert limpio["ia_ml"][0]["url_docs"] is None, valor
        # Y debe construir el modelo sin problema
        p = _proyecto(valor)
        limpiar_tech_stack(p["tech_stack"])
        assert Proyecto(**p).tech_stack.ia_ml[0].url_docs is None


def test_una_url_buena_se_respeta():
    ts = _proyecto("https://docs.python.org/3/library/difflib.html")["tech_stack"]
    assert limpiar_tech_stack(ts)["ia_ml"][0]["url_docs"] == \
        "https://docs.python.org/3/library/difflib.html"


def test_url_mal_formada_se_neutra_en_vez_de_matar():
    ts = _proyecto("docs.python.org/difflib")["tech_stack"]
    assert limpiar_tech_stack(ts)["ia_ml"][0]["url_docs"] is None


# --- El saneado completo -------------------------------------------------------

@pytest.mark.parametrize("valor,es_valida", [
    ("https://a.com", True),
    ("http://a.com/x?y=1", True),
    ("N/A", False),
    ("-", False),
    ("", False),
    ("n/d", False),
    ("a.com", False),
    (None, False),
    (123, False),
])
def test_clasificacion_de_urls(valor, es_valida):
    assert _url_es_valida(valor) is es_valida


def test_recorre_las_siete_listas_de_herramientas():
    ts = {lista: [{"nombre": "x", "categoria": "lib", "url_docs": "N/A"}]
          for lista in ["frameworks", "librerias", "bases_datos", "infraestructura",
                        "ia_ml", "testing", "otros"]}
    limpio = limpiar_tech_stack(ts)
    for lista, items in limpio.items():
        assert items[0]["url_docs"] is None, lista


def test_descarta_lo_que_no_puede_ser_una_herramienta():
    ts = {
        "frameworks": [
            "FastAPI",                                  # string suelto
            {"categoria": "lib"},                        # sin nombre
            {"nombre": "x"},                             # sin categoria
            {"nombre": "ok", "categoria": "lib"},        # este se queda
        ],
        "ia_ml": "no es una lista",
    }
    limpio = limpiar_tech_stack(ts)
    # sobrevive solo la herramienta completa, y se le pone url_docs=None
    assert limpio["frameworks"] == [
        {"nombre": "ok", "categoria": "lib", "url_docs": None}
    ]
    assert limpio["ia_ml"] == []


# --- Integración con validate_project_json --------------------------------------

def test_validate_project_json_deja_construir_el_proyecto():
    """El contrato que se rompió: validaba, pero no daba un Proyecto construible."""
    data = {"proyectos": [_proyecto("N/A")]}
    validados = validate_project_json(data)
    assert len(validados) == 1
    assert Proyecto(**validados[0]).titulo == "Comparador de PDFs"


def test_una_url_buena_llega_intacta_a_traves_de_validate():
    url = "https://docs.python.org/3/library/difflib.html"
    validados = validate_project_json({"proyectos": [_proyecto(url)]})
    assert str(validados[0]["tech_stack"]["ia_ml"][0]["url_docs"]) == url


def test_un_proyecto_roto_no_arrastra_a_los_demas():
    """El bug de fondo: un item malo descartaba toda la tanda."""
    bueno = _proyecto("https://a.com", titulo="Bueno")
    roto = _proyecto("N/A", titulo="Roto")
    roto["complejidad_estimada"] = "inventada"  # enum que no existe
    validados = validate_project_json({"proyectos": [roto, bueno]})
    construidos = []
    for p in validados:
        try:
            construidos.append(Proyecto(**p))
        except Exception:
            pass
    assert [p.titulo for p in construidos] == ["Bueno"]
