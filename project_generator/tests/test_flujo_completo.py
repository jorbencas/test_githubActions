"""Prueba de extremo a extremo: respuesta cortada y qué llega finalmente.

Reproduce el fallo reportado (nada llegó a Telegram) con un provider simulado
que se corta por `MAX_TOKENS`, y comprueba qué proyectos se salvan.
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from ai_providers import ResponseTruncatedError  # noqa: E402
from generator import ProjectGenerator  # noqa: E402


def _proyecto(numero: int) -> dict:
    return {
        "id": f"id{numero:03d}",
        "titulo": f"Proyecto {numero}",
        "descripcion_corta": f"Descripción corta del proyecto {numero}",
        "descripcion_detallada": f"Descripción detallada del proyecto {numero}.",
        "nivel": "semisenior",
        "scope": "proyecto",
        "tipo": ["web"],
        "tech_stack": {
            "lenguaje_principal": "python",
            "frameworks": [],
            "librerias": [],
            "bases_datos": [],
            "infraestructura": [],
            "ia_ml": [],
            "testing": [],
            "otros": [],
        },
        "funcionalidades_clave": ["Hacer cosas"],
        "casos_uso": ["Un caso de uso"],
        "complejidad_estimada": "media",
        "tiempo_estimado_semanas": 4,
        "hash_unicidad": f"hash{numero:03d}",
    }


def _completo(cuantos: int) -> str:
    proyectos = ",".join(json.dumps(_proyecto(i)) for i in range(cuantos))
    return '{"proyectos": [' + proyectos + "]}"


def _cortado() -> str:
    """Dos proyectos enteros y el tercero a medias, como en el log."""
    return _completo(2)[:-1] + ',{"id":"id003","titulo":"Proyecto 3","descripcion_corta":"se corta aquí y sigue escribiendo sin cerrar'


class ProviderSimulado:
    """Se corta la primera vez; si le piden 1 proyecto, responde bien."""

    def __init__(self):
        self.peticiones = 0
        self.primera = True

    def get_model_name(self):
        return "simulado"

    async def generate(self, prompt, system_prompt, temperature=0.7, max_tokens=4000):
        self.peticiones += 1
        cantidad = 1 if "EXACTAMENTE 1 proyectos" in prompt else 3
        if self.primera and cantidad > 1:
            self.primera = False
            raise ResponseTruncatedError("simulado: MAX_TOKENS", texto=_cortado())
        return _completo(cantidad)


def _generador() -> ProjectGenerator:
    g = ProjectGenerator()
    g.data_dir = Path(tempfile.mkdtemp())
    g.history_file = g.data_dir / "hist.json"
    g.history.proyectos = []
    g.history.ultimos_hashes = []
    g._init_provider = lambda: None
    g._get_inspiration_sources = lambda: []
    g._get_external_inspiration = lambda: _sin_espera()
    return g


async def _sin_espera():
    return []


def test_se_salvan_los_dos_proyectos_que_habian_llegado_completos():
    g = _generador()
    g.provider = ProviderSimulado()
    resultado = asyncio.run(g.generate_projects(count=3))
    titulos = [p.proyecto.titulo for p in resultado]
    assert titulos == ["Proyecto 0", "Proyecto 1"]


def test_no_hace_falta_el_segundo_intento_si_rescata_algo():
    g = _generador()
    provider = ProviderSimulado()
    g.provider = provider
    asyncio.run(g.generate_projects(count=3))
    assert provider.peticiones == 1, "rescató 2, no debía pedir otra vez"


def test_si_no_hay_nada_aprovechable_reintenta_con_un_solo_proyecto():
    class SoloInutilizable(ProviderSimulado):
        """Nada aprovechable en la tanda de 3, pero sí si le piden solo 1."""

        async def generate(self, prompt, system_prompt, temperature=0.7, max_tokens=4000):
            self.peticiones += 1
            if "EXACTAMENTE 1 proyectos" in prompt:
                return _completo(1)
            raise ResponseTruncatedError("casi entero", texto='{"proyectos": [{"titulo":')

    g = _generador()
    provider = SoloInutilizable()
    g.provider = provider
    resultado = asyncio.run(g.generate_projects(count=3))
    assert provider.peticiones == 2
    assert len(resultado) == 1, "debe llegar el proyecto del reintento"
    assert resultado[0].proyecto.titulo == "Proyecto 0"


def test_se_guardan_en_el_historial_y_no_se_duplican():
    g = _generador()
    g.provider = ProviderSimulado()
    primero = asyncio.run(g.generate_projects(count=3))
    assert len(primero) == 2
    assert g.history.total_generados == 2
    assert g.history_file.exists()

    # Segunda pasada con el mismo contenido: los hashes ya están, se descartan.
    g2 = _generador()
    g2.history = g.history
    g2.provider = ProviderSimulado()
    segundo = asyncio.run(g2.generate_projects(count=3))
    assert len(segundo) == 0
