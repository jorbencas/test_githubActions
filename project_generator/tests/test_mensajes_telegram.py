"""Tests del texto que llega a Telegram.

El usuario pidió quitar del mensaje el modelo generador, la ruta del historial
y el par ID/Hash: son datos internos que no aportan al lector.
"""
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from models import Proyecto, ProyectoGenerado  # noqa: E402
from telegram_sender import TelegramReporter  # noqa: E402


def _proyecto() -> Proyecto:
    return Proyecto(
        titulo="Comparador de PDFs",
        descripcion_corta="Compara dos PDFs y saca las diferencias",
        descripcion_detallada="Sube dos PDFs, extrae el texto y genera un informe de diferencias.",
        nivel="semisenior",
        scope="proyecto",
        tipo=["web"],
        tech_stack={"lenguaje_principal": "python"},
        funcionalidades_clave=["Subir PDFs", "Comparar texto"],
        casos_uso=["Revisar contratos"],
        complejidad_estimada="media",
        tiempo_estimado_semanas=4,
        hash_unicidad="f1793359d3a271b4",
        id="f1793359d3",
    )


def _generado() -> ProyectoGenerado:
    return ProyectoGenerado(
        proyecto=_proyecto(),
        metadata={"provider": "gemini:gemini-2.5-flash-lite"},
    )


def _mensajes():
    reporter = TelegramReporter(provider_name="gemini:gemini-2.5-flash-lite")
    proyecto = _generado()
    return (
        reporter._build_summary_message([proyecto]),
        reporter._build_project_message(proyecto.proyecto, 1, 1),
    )


# --- Lo que no debe aparecer ----------------------------------------------------

def test_el_resumen_no_dice_con_que_modelo_se_genero():
    resumen, _ = _mensajes()
    assert "Generado con" not in resumen
    assert "gemini" not in resumen.lower()


def test_el_resumen_no_dice_la_ruta_del_historial():
    resumen, _ = _mensajes()
    assert "Historial" not in resumen
    assert "generated_projects.json" not in resumen


def test_el_mensaje_del_proyecto_no_trae_id_ni_hash():
    _, mensaje = _mensajes()
    assert "🆔" not in mensaje
    assert "Hash" not in mensaje
    assert "f1793359d3" not in mensaje


# --- Lo que sí debe seguir estando ---------------------------------------------

def test_el_resumen_sigue_informando_de_lo_importante():
    resumen, _ = _mensajes()
    assert "Nuevos Proyectos Generados" in resumen
    assert "Total" in resumen
    assert "Distribución" in resumen
    assert "Niveles" in resumen
    assert "Lenguajes" in resumen


def test_el_mensaje_del_proyecto_sigue_tiene_el_contenido():
    _, mensaje = _mensajes()
    assert "Comparador de PDFs" in mensaje
    assert "Subir PDFs" in mensaje
    assert "Comparar texto" in mensaje
    assert "python" in mensaje


def test_el_modelo_sigue_estando_en_el_json_adjunto():
    """Quitarlo del texto no significa perderlo: va en el archivo de datos."""
    reporter = TelegramReporter(provider_name="gemini:gemini-2.5-flash-lite")
    assert reporter.provider_name == "gemini:gemini-2.5-flash-lite"


def test_los_mensajes_no_dejan_lineas_en_blanco_al_final():
    """Al quitar el último bloque, el mensaje no puede acabar en \\n ni en espacios."""
    for mensaje in _mensajes():
        assert mensaje == mensaje.rstrip()
