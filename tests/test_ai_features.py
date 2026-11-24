import json
from pathlib import Path

import pytest

from scripts.ai_tools_generator import (
    build_gemini_prompt,
    load_categories,
    format_tool_message,
    mix_tools,
    _norm_name,
    _norm_url,
    filtrar_nuevos,
    select_skills_from_db,
    select_tools_from_db,
    select_from_pool,
    load_blog_resources_for_message,
    _validate_promoted,
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
    def test_category_count(self):
        data = json.loads(AI_CATS_PATH.read_text(encoding="utf-8"))
        assert len(data["categorias"]) == 166

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
        assert len(ai_gen.CAT_NAMES) == 166

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
        assert "Workflow" in msg and "A -> B -> C" in msg
        assert "Combina" in msg
        assert "https://openai.com/whisper" in msg
        assert "Limitaciones" in msg and "Requiere GPU." in msg

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


class TestNuncaRepiten:
    """Filtro estricto: nada ya enviado vuelve a salir, ni siquiera en variantes."""

    def test_norm_name_normaliza_variantes(self):
        assert _norm_name("OpenAI Whisper") == _norm_name("openai-whisper!")
        assert _norm_name("  Café   IA ") == _norm_name("cafe ia")
        assert _norm_name("") == ""

    def test_norm_url_quita_www_query_y_slash(self):
        assert _norm_url("https://www.ejemplo.com/ruta/?utm=1#x") == "ejemplo.com/ruta"
        assert _norm_url("HTTP://Ejemplo.com/Ruta/") == _norm_url("https://ejemplo.com/ruta")

    def test_filtrar_nuevos_descarta_nombre_o_url_ya_enviados(self):
        sent_names = {_norm_name("OpenAI Whisper")}
        sent_urls = {_norm_url("https://openai.com/whisper")}
        items = [
            {"tool": "openai-whisper", "url": ""},
            {"tool": "Otra tool", "url": "https://www.openai.com/whisper/"},
            {"tool": "Nueva tool", "url": "https://nueva.dev"},
        ]
        out = filtrar_nuevos(items, sent_names, sent_urls)
        assert [t["tool"] for t in out] == ["Nueva tool"]

    def test_filtrar_nuevos_quita_duplicados_dentro_del_lote(self):
        items = [
            {"tool": "Foo", "url": "https://a.dev"},
            {"tool": "foo!", "url": "https://b.dev"},
            {"tool": "Bar", "url": "https://a.dev"},
        ]
        out = filtrar_nuevos(items, set(), set())
        assert [t["tool"] for t in out] == ["Foo"]

    def test_mix_tools_sin_duplicados_intra_lote(self):
        g = [{"tool": "Whisper", "cat": "a"}]
        d = [{"tool": "whisper!", "cat": "b"}, {"tool": "Otra", "cat": "c"}]
        out = mix_tools(g, d, total=3)
        names = [_norm_name(t["tool"]) for t in out]
        assert len(names) == len(set(names))
        assert len(out) == 2

    def test_select_skills_no_recicla(self):
        skills = [{"titulo": f"Skill {i}"} for i in range(3)]
        assert select_skills_from_db(skills, ["Skill 0", "Skill 1", "Skill 2"], count=2) == []
        out = select_skills_from_db(skills, ["Skill 0"], count=5)
        assert len(out) == 2
        assert all(s["titulo"] != "Skill 0" for s in out)

    def test_select_pool_no_recicla(self):
        pool = [{"tool": f"T{i}", "cat": "img_gen"} for i in range(3)]
        assert select_from_pool(pool, {"sent_titles": ["T0", "T1", "T2"]}, count=5) == []

    def test_select_pool_no_recicla_variantes_de_nombre(self):
        pool = [{"tool": "OpenAI Whisper", "cat": "transcripcion", "url": "https://x.dev"}]
        history = {"sent_titles": ["openai whisper!"], "sent_urls": []}
        assert select_from_pool(pool, history, count=5) == []

    def test_select_db_no_recicla(self):
        database = {"tools": [
            {"tool": "A", "cat": "img_gen"},
            {"tool": "B", "cat": "code_gen"},
        ]}
        history = {"sent_titles": ["A", "B"]}
        assert select_tools_from_db(database, history, count=5) == []

    def test_recursos_blog_no_recicla_los_ya_enviados(self):
        import scripts.ai_tools_generator as ai_gen
        data = json.loads(ai_gen.BLOG_RESOURCES_PATH.read_text(encoding="utf-8"))
        titles = [r.get("titulo", "") for r in data[:20] if r.get("titulo")]
        assert titles
        out = load_blog_resources_for_message(5, titles)
        sent = {_norm_name(t) for t in titles}
        assert len(out) <= 5
        assert all(_norm_name(r.get("titulo", "")) not in sent for r in out)

    def test_validate_promoted_exige_categoria_y_restricciones(self):
        load_categories()
        src = {"enlace": "https://huggingface.co/x", "fuente": "HF"}
        good = {
            "cat": "img_gen", "tool": "X Tool", "body": "Descripción.",
            "workflow": "A -> B", "combinaciones": ["img_gen", "no_existe"],
            "url": "https://x.dev", "restricciones": "Requiere GPU.", "dific": 2,
        }
        v = _validate_promoted(good, src)
        assert v is not None
        assert v["combinaciones"] == ["img_gen"]
        assert _validate_promoted(dict(good, cat="no_existe"), src) is None
        assert _validate_promoted(dict(good, restricciones="  "), src) is None
        assert _validate_promoted(dict(good, url="ftp://mal"), src) is None


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