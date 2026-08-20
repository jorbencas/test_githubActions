import json
from pathlib import Path

import pytest

from scripts.ai_tools_generator import (
    build_gemini_prompt,
    load_categories,
    format_tool_message,
    mix_tools,
)
import scripts.ai_tools_generator as ai_gen
from scripts.saludo_imagen import (
    CONFIG,
    load_config,
    _greeting_for_hour,
    _build_prompt,
)

SCRIPT_DIR = Path(__file__).resolve().parent.parent
AI_CATS_PATH = SCRIPT_DIR / "scripts" / "utils" / "ai_categories.json"
AI_DB_PATH = SCRIPT_DIR / "scripts" / "utils" / "ai_tools_database.json"
SALUDO_CONFIG = SCRIPT_DIR / "scripts" / "utils" / "saludos_config.json"


class TestAiCategories:
    def test_150_categories(self):
        data = json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))
        assert len(data["categorias"]) == 150

    def test_all_categories_have_emoji_and_nombre(self):
        data = json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))
        for key, val in data["categorias"].items():
            assert "emoji" in val, f"{key} missing emoji"
            assert "nombre" in val, f"{key} missing nombre"

    def test_unique_keys(self):
        data = json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))
        keys = list(data["categorias"].keys())
        assert len(keys) == len(set(keys))

    def test_covers_main_areas(self):
        data = json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))
        cats = set(data["categorias"].keys())
        # multimedia
        assert {"video_gen", "img_gen", "audio_tts"} <= cats
        # unión de conceptos
        assert {"unir_conceptos", "mindmap", "second_brain"} <= cats
        # automatizaciones
        assert {"automatizaciones", "n8n_ai", "workflow_gen", "agentes"} <= cats
        # estudiar
        assert {"estudiar", "flashcards_ai", "tutor_ai"} <= cats
        # generación
        assert {"texto_gen", "code_gen", "img_gen"} <= cats


class TestAiToolsDatabase:
    def test_db_records_valid(self):
        data = json.loads(AI_DB_PATH.read_text(encoding="utf-8"))
        cats = set(json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))["categorias"].keys())
        ids = []
        for tool in data["tools"]:
            assert tool["cat"] in cats, f"{tool['tool']} cat inválido: {tool['cat']}"
            assert "body" in tool and "dific" in tool
            assert "workflow" in tool and "combinaciones" in tool
            assert tool.get("url", "").startswith("http"), f"{tool['tool']} sin url válida"
            ids.append(tool["id"])
        assert len(ids) == len(set(ids)), "ids duplicados"

    def test_combinaciones_referencian_categorias_validas(self):
        data = json.loads(AI_DB_PATH.read_text(encoding="utf-8"))
        cats = set(json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))["categorias"].keys())
        for tool in data["tools"]:
            for combo in tool.get("combinaciones", []):
                assert combo in cats, f"{tool['tool']} combina con cat inválida: {combo}"


class TestAiToolsGenerator:
    def test_load_categories_pobla_mapas(self):
        load_categories()
        assert len(ai_gen.CAT_NAMES) == 150

    def test_format_tool_message_incluye_flujo_y_combinaciones(self):
        tool = {
            "cat": "transcripcion",
            "tool": "Whisper",
            "body": "Transcribe.",
            "workflow": "A -> B -> C",
            "combinaciones": ["second_brain", "video_edit"],
            "url": "https://openai.com/whisper",
            "restricciones": "Requiere GPU.",
        }
        msg = format_tool_message(tool, 1)
        assert "Whisper" in msg
        assert "Flujo" in msg and "A -> B -> C" in msg
        assert "Combina" in msg
        assert "https://openai.com/whisper" in msg
        assert "Ojo" in msg and "Requiere GPU." in msg

    def test_format_tool_message_sin_url_omite_enlace(self):
        tool = {
            "cat": "transcripcion",
            "tool": "Whisper",
            "body": "Transcribe.",
            "workflow": "A -> B",
            "combinaciones": [],
        }
        msg = format_tool_message(tool, 1)
        assert "🔗" not in msg

    def test_build_prompt_estricto(self):
        prompt = build_gemini_prompt(["transcripcion", "img_gen"], ["ya env"], [], [])
        assert "EXACTAMENTE" in prompt
        assert "transcripcion" in prompt
        assert "ya env" in prompt
        assert "restricciones" in prompt

    def test_database_tools_tienen_restricciones(self):
        db = json.loads(AI_DB_PATH.read_text(encoding="utf-8"))
        for tool in db["tools"]:
            assert tool.get("restricciones", "").strip(), f"{tool['tool']} sin restricciones"

    def test_mix_tools_respeta_total(self):
        g = [{"tool": f"g{i}", "cat": "x"} for i in range(3)]
        d = [{"tool": f"d{i}", "cat": "y"} for i in range(3)]
        assert len(mix_tools(g, d, total=5)) == 5
        assert len(mix_tools(None, d, total=3)) == 3


class TestSaludoConfig:
    def test_config_valida(self):
        data = json.loads(SALUDO_CONFIG.read_text(encoding="utf-8"))
        for seccion in ("estilos", "publicos", "emociones", "materias", "festivos", "temporadas"):
            assert seccion in data and len(data[seccion]) > 0

    def test_solo_dias_y_noches(self):
        data = json.loads(SALUDO_CONFIG.read_text(encoding="utf-8"))
        saludos = data["meta"]["saludos"]
        assert "Buenos días" in saludos
        assert "Buenas noches" in saludos
        assert "Buenas tardes" not in saludos


class TestSaludoImagen:
    def test_greeting_por_hora(self):
        assert _greeting_for_hour(6) == "Buenos días"
        assert _greeting_for_hour(11) == "Buenos días"
        assert _greeting_for_hour(12) == "Buenas noches"
        assert _greeting_for_hour(15) == "Buenas noches"
        assert _greeting_for_hour(22) == "Buenas noches"
        assert _greeting_for_hour(1) == "Buenas noches"

    def test_build_prompt_sin_terror(self):
        load_config()
        from datetime import datetime

        prompt = _build_prompt(
            "Buenos días", "Eres la luz que ilumina el día", datetime(2026, 12, 25), "Navidad", "añevin, regalos",
            "acuarela", "niños", "alegre", "la mañana", "invierno festivo",
        )
        assert "Navidad" in prompt
        assert "buenos días" in prompt
        # el prompt ya NO incrusta la frase: el texto se superpone luego por PIL
        assert "Eres la luz que ilumina el día" not in prompt
        # el prompt debe prohibir texto en la imagen y contenido de terror
        assert "NO incluyas NINGÚN texto" in prompt
        assert "NO terror" in prompt
        assert "horror" in prompt.lower()

    def test_build_prompt_festivo_usa_tema(self):
        load_config()
        from datetime import datetime

        p = _build_prompt("Buenas noches", "Eres la luz que ilumina mi noche", datetime(2026, 12, 25), "Navidad",
                          "árbol navideño", "cartoon", "mixto", "tierno", "navidad", "invierno")
        assert "árbol navideño" in p
        # la frase ya no va en el prompt (se superpone por PIL después)
        assert "Eres la luz que ilumina mi noche" not in p


class TestSaludoFallback:
    def test_fallback_pil_genera_png(self):
        from scripts.saludo_imagen import fallback_pil

        data = fallback_pil("Buenos días", "amigo")
        assert data is not None
        # PNG magic number
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_superponer_texto_preserva_proporciones(self):
        from scripts.saludo_imagen import fallback_pil, _superponer_texto

        raw = fallback_pil("Buenas noches", "amigo")
        out = _superponer_texto(raw, "Eres la luz que ilumina mi noche", "Buenas noches")
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(out))
        assert abs(img.width / img.height - 1.0) < 0.01  # cuadrada, sin apaisar
        assert img.width >= 256

    def test_fallback_pollinations_url_valida(self):
        import requests as _r
        from scripts.saludo_imagen import fallback_pollinations

        data = fallback_pollinations("Buenos días", "amigo", "cafe")
        # puede fallar por red, pero si devuelve algo debe ser JPEG
        if data is not None:
            assert data[:2] == b"\xff\xd8"