from pathlib import Path

from scripts.tips_generator import (
    build_concepts_gemini_prompt,
    build_gemini_prompt,
    build_daily_message,
    format_tip_message,
    load_concepts_database,
    select_concepts_from_db,
)
from scripts.tools.migrate_concepts_es import (
    apply_migration,
    build_migrate_prompt,
    parse_json,
)

SCRIPT_DIR = Path(__file__).resolve().parent.parent
CONCEPTS_PATH = SCRIPT_DIR / "scripts" / "utils" / "concepts_database.json"


def _concepto(id_concepto="cX1", summary="Resumen de ejemplo.", title=None):
    return {
        "id": id_concepto,
        "type": "concepto",
        "cat": "programming",
        "title": title or "Búsqueda binaria (Binary Search)",
        "summary": summary,
        "explanation": (
            "Primer párrafo con la idea general.\n\n"
            "Segundo párrafo con el detalle de cómo funciona.\n\n"
            "Tercer párrafo con cuándo usarlo y errores comunes."
        ),
        "code_example": "def buscar(x):\n    return x",
        "language": "python",
        "use_cases": ["Búsquedas", "Índices"],
        "difficulty": 2,
        "interview_relevant": True,
        "interview_question": "¿Complejidad?",
        "interview_answer": "O(log n)",
    }


def _tip():
    return {
        "type": "trick",
        "cat": "postgresql",
        "title": "Explicar un query SQL lento",
        "body": "EXPLAIN ANALYZE muestra el plan de ejecución real.",
        "mala": "SELECT sin plan.",
        "buena": "EXPLAIN ANALYZE SELECT ...",
    }


class TestFormatTipMessage:
    def test_tip_incluye_body_y_contraste(self):
        msg = format_tip_message(_tip(), 1)
        assert msg.startswith("1. ⚡ Trick 🐘 *PostgreSQL*: Explicar un query SQL lento")
        assert "EXPLAIN ANALYZE muestra el plan de ejecución real." in msg
        assert "❌ _Mala práct.:_" in msg and "✅ _Buena práct.:_" in msg

    def test_concepto_con_summary_no_duplica_titulo_en_cabecera(self):
        msg = format_tip_message(_concepto(), 2)
        assert msg.startswith("2. 📘 Concepto 💻 *Programación*")
        assert ": Búsqueda binaria" not in msg.split("\n")[0]
        assert "▶️ *Búsqueda binaria (Binary Search)* — Resumen de ejemplo." in msg

    def test_concepto_parrafos_indentados(self):
        msg = format_tip_message(_concepto(), 1)
        assert "📖 *Explicación:*" in msg
        assert "   Primer párrafo con la idea general." in msg
        assert "   Segundo párrafo con el detalle de cómo funciona." in msg
        assert "   Tercer párrafo con cuándo usarlo y errores comunes." in msg

    def test_concepto_sin_summary_titulo_en_cabecera(self):
        c = _concepto()
        c["summary"] = ""
        msg = format_tip_message(c, 1)
        assert ": Búsqueda binaria (Binary Search)" in msg.split("\n")[0]

    def test_concepto_code_block_con_lenguaje(self):
        msg = format_tip_message(_concepto(), 1)
        assert "```python" in msg
        assert "   def buscar(x):" in msg
        assert "```" in msg

    def test_concepto_pregunta_entrevista(self):
        msg = format_tip_message(_concepto(), 1)
        assert "🎤 *Entrevista:* ¿Complejidad?" in msg
        assert "💬 *Respuesta:* O(log n)" in msg


class TestBuildDailyMessage:
    def test_mezcla_tips_y_conceptos(self):
        msg = build_daily_message([_tip(), _concepto()])
        assert "📘 *CONCEPTOS DE PROGRAMACIÓN*" in msg
        assert "1. ⚡ Trick" in msg
        assert "2. 📘 Concepto" in msg
        assert "Total: 2" in msg

    def test_sin_conceptos_no_hay_seccion(self):
        msg = build_daily_message([_tip()])
        assert "CONCEPTOS DE PROGRAMACIÓN" not in msg
        assert "Total: 1" in msg

    def test_header_con_saludo_y_fecha(self):
        msg = build_daily_message([_tip()])
        assert msg.startswith("*Buenas ") or "—" in msg.split("\n")[0]

    def test_footer_cuenta_tipos(self):
        msg = build_daily_message([_tip(), _tip(), _concepto()])
        assert "⚡ 2 tricks" in msg
        assert "📘 1 conceptos" in msg


class TestBuildConceptsGeminiPrompt:
    def test_exige_castellano(self):
        prompt = build_concepts_gemini_prompt(["programming"], ["ya enviado"])
        assert "CASTELLANO" in prompt
        assert "comentarios del code_example" in prompt

    def test_titulos_siempre_en_espanol(self):
        prompt = build_concepts_gemini_prompt(["programming"], [])
        assert "títulos van SIEMPRE en español" in prompt
        assert "entre paréntesis la primera vez" in prompt

    def test_explicacion_didactica_extensa(self):
        prompt = build_concepts_gemini_prompt(["programming"], [])
        assert "DIDÁCTICA" in prompt
        assert "3-5 párrafos" in prompt
        assert "analogía o ejemplo cotidiano" in prompt
        assert "malentendidos comunes" in prompt

    def test_no_usa_emojis(self):
        prompt = build_concepts_gemini_prompt(["programming"], [])
        assert "NUNCA uses emojis" in prompt

    def test_incluye_enviados_y_categorias(self):
        prompt = build_concepts_gemini_prompt(["kafka", "entrevistas"], ["Concepto Viejo"])
        assert "kafka, entrevistas" in prompt
        assert "Concepto Viejo" in prompt


class TestBuildGeminiPrompt:
    def test_todo_en_castellano(self):
        prompt = build_gemini_prompt(["python", "docker"], ["tip viejo"], ["noticia"], ["tool"])
        assert "TODO en CASTELLANO" in prompt
        assert "Ningún término en inglés sin su traducción" in prompt
        assert "entre paréntesis la primera vez" in prompt

    def test_sin_titulos_en_ingles(self):
        prompt = build_gemini_prompt(["linux"], [], [], [])
        assert "arranque en frío (cold start)" in prompt

    def test_incluye_contexto(self):
        prompt = build_gemini_prompt(["python"], ["tip viejo"], ["noticia tech"], ["tool x"])
        assert "python" in prompt
        assert "tip viejo" in prompt
        assert "noticia tech" in prompt
        assert "tool x" in prompt

    def test_no_usa_emojis(self):
        prompt = build_gemini_prompt(["python"], [], [], [])
        assert "NUNCA uses emojis" in prompt


class TestSelectConceptsFromDb:
    def test_no_repite_enviados_y_respeta_count(self):
        db = {"meta": {}, "concepts": [
            _concepto("a", title="Concepto A"),
            _concepto("b", title="Concepto B"),
            _concepto("c", title="Búsqueda binaria (Binary Search)"),
        ]}
        selected = select_concepts_from_db(db, ["Búsqueda binaria (Binary Search)"], [], count=2)
        assert len(selected) == 2
        assert all(c["title"] != "Búsqueda binaria (Binary Search)" for c in selected)

    def test_prefiere_categorias_del_batch(self):
        db = {"meta": {}, "concepts": [
            {**_concepto("a"), "cat": "kafka"},
            {**_concepto("b"), "cat": "entrevistas"},
            {**_concepto("c"), "cat": "linux"},
        ]}
        selected = select_concepts_from_db(db, [], ["entrevistas"], count=1)
        assert selected[0]["cat"] == "entrevistas"

    def test_vacio_si_no_hay_conceptos(self):
        assert select_concepts_from_db({"meta": {}, "concepts": []}, [], [], count=5) == []


class TestLoadConceptsDatabase:
    def test_lee_archivo_real(self):
        data = load_concepts_database()
        concepts = data.get("concepts", [])
        assert len(concepts) > 0
        required = {"title", "summary", "explanation"}
        assert required <= set(concepts[0].keys())

    def test_archivo_inexistente_devuelve_vacio(self, monkeypatch):
        monkeypatch.setattr("scripts.tips_generator.CONCEPTS_PATH", CONCEPTS_PATH.parent / "no_existe.json")
        assert load_concepts_database() == {"meta": {}, "concepts": []}


class TestMigrateConceptsEs:
    def test_parse_json_quita_fences(self):
        text = '```json\n[{"id": "a", "title": "T"}]\n```'
        assert parse_json(text) == [{"id": "a", "title": "T"}]
        assert parse_json('[{"id": "a"}]') == [{"id": "a"}]

    def test_prompt_pide_castellano_y_conserva_id(self):
        prompt = build_migrate_prompt([_concepto("cX1")], only_language=False)
        assert "CASTELLANO" in prompt
        assert "cX1" in prompt
        assert "3-5 párrafos" in prompt

    def test_apply_migration_conserva_id_y_cat(self):
        c = _concepto("cX1")
        result = {
            "id": "cX1",
            "title": "Título traducido",
            "summary": "Nuevo resumen",
            "explanation": "Nueva explicación extensa de verdad para el test.",
        }
        out = apply_migration(c, result)
        assert out["id"] == "cX1"
        assert out["cat"] == "programming"
        assert out["type"] == "concepto"
        assert out["title"] == "Título traducido"

    def test_apply_migration_no_pisa_con_vacios(self):
        c = _concepto("cX1")
        out = apply_migration(c, {"id": "cX1", "title": "", "language": ""})
        assert out["title"] == "Búsqueda binaria (Binary Search)"