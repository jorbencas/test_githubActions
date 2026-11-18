"""Tests de anti-duplicados: hash normalizado + similitud de título."""
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from dedup import (  # noqa: E402
    filtrar_nuevos,
    hash_unicidad,
    normalizar_texto,
    similitud_jaccard,
    titulo_mas_similar,
    tokens_titulo,
)
from prompts import build_user_prompt, validate_project_json  # noqa: E402


# ── normalización / hash ─────────────────────────────────────────────

def test_normalizar_quita_acentos_y_mayusculas():
    assert normalizar_texto("  Gestión de Tareas  ") == "gestion de tareas"


def test_hash_es_estable_con_acentos_y_mayusculas():
    a = hash_unicidad("Gestión de Tareas", "python", "API de gestión")
    b = hash_unicidad("gestion de tareas", "Python", "api de gestion")
    assert a == b
    assert len(a) == 16


def test_hash_distinto_para_titulos_distintos():
    a = hash_unicidad("Gestor de tareas", "python", "desc")
    b = hash_unicidad("Gestor de notas", "python", "desc")
    assert a != b


# ── similitud ────────────────────────────────────────────────────────

def test_titulos_identicos_tienen_similitud_1():
    assert titulo_mas_similar("Gestor de tareas", ["Gestor de tareas"]) == "Gestor de tareas"


def test_titulos_casi_iguales_se_detectan():
    # mismo producto, otro nombre de stack → debe saltar
    found = titulo_mas_similar(
        "Gestor de tareas FastAPI",
        ["Gestor de tareas Python FastAPI"],
    )
    assert found == "Gestor de tareas Python FastAPI"


def test_titulos_distintos_no_se_filtran():
    assert titulo_mas_similar(
        "Gestor de tareas FastAPI",
        ["Chat en tiempo real WebSockets", "Compilador de grammars"],
    ) is None


def test_jaccard_conjuntos_vacios_es_0():
    assert similitud_jaccard(frozenset(), frozenset({"a"})) == 0.0


def test_numeros_son_tokens():
    # «Proyecto 0» y «Proyecto 1» no deben considerarse el mismo
    assert titulo_mas_similar("Proyecto 0", ["Proyecto 1"]) is None


# ── filtrar_nuevos (hash + similitud + intra-lote) ───────────────────

def _p(titulo: str, h: str = "") -> dict:
    return {"titulo": titulo, "hash_unicidad": h or hash_unicidad(titulo, "py", "d")}


def test_filtra_por_hash_exacto():
    existente = hash_unicidad("Gestor de tareas", "py", "d")
    aceptados, descartados = filtrar_nuevos(
        [_p("Gestor de tareas", existente)], [existente], []
    )
    assert aceptados == []
    assert descartados[0][1] == "hash duplicado"


def test_filtra_por_similitud_aunque_hash_distinto():
    viejo = "Gestor de tareas FastAPI"
    nuevo = _p("Gestor de tareas con FastAPI")  # hash distinto
    aceptados, descartados = filtrar_nuevos(
        [nuevo], [hash_unicidad(viejo, "py", "d")], [viejo]
    )
    assert aceptados == []
    assert "similar a" in descartados[0][1]


def test_dedup_intra_lote():
    a = _p("API de pagos con Stripe")
    b = _p("API de pagos Stripe")  # casi idéntico, mismo lote
    aceptados, descartados = filtrar_nuevos([a, b], [], [])
    assert len(aceptados) == 1
    assert aceptados[0] is a
    assert len(descartados) == 1


def test_acepta_proyectos_distintos():
    a = _p("Gestor de tareas FastAPI")
    b = _p("Chat en tiempo real WebSockets")
    aceptados, descartados = filtrar_nuevos([a, b], [], [])
    assert len(aceptados) == 2
    assert descartados == []


# ── validate_project_json: hash SIEMPRE recalculado ──────────────────

def _raw(titulo: str, hash_malo: str) -> dict:
    return {
        "id": "id001",
        "titulo": titulo,
        "descripcion_corta": "desc",
        "descripcion_detallada": "desc detallada",
        "nivel": "semisenior",
        "scope": "proyecto",
        "tipo": ["web"],
        "tech_stack": {
            "lenguaje_principal": "python",
            "frameworks": [], "librerias": [], "bases_datos": [],
            "infraestructura": [], "ia_ml": [], "testing": [], "otros": [],
        },
        "funcionalidades_clave": ["x"],
        "casos_uso": ["y"],
        "complejidad_estimada": "media",
        "tiempo_estimado_semanas": 4,
        "hash_unicidad": hash_malo,
    }


def test_validate_recalcula_hash_ignorando_al_modelo():
    validado = validate_project_json({"proyectos": [_raw("Mi Proyecto", "aaaaaaaaaaaaaaaa")]})
    esperado = hash_unicidad("Mi Proyecto", "python", "desc")
    assert validado[0]["hash_unicidad"] == esperado
    assert validado[0]["hash_unicidad"] != "aaaaaaaaaaaaaaaa"


# ── prompt: títulos reales recientes ────────────────────────────────

def test_prompt_incluye_titulos_recientes():
    prompt = build_user_prompt(
        count=2,
        existing_hashes=["aaa", "bbb"],
        inspiration_sources=[],
        recent_projects=[
            "Gestor de tareas (python, web)",
            "Chat WebSockets (nodejs, web)",
        ],
    )
    assert "Gestor de tareas (python, web)" in prompt
    assert "Chat WebSockets (nodejs, web)" in prompt
    assert "NO repitas el tema" in prompt


def test_prompt_sin_titulos_usa_hashes():
    prompt = build_user_prompt(
        count=2, existing_hashes=["aaa", "bbb"], inspiration_sources=[]
    )
    assert "Hashes recientes" in prompt
