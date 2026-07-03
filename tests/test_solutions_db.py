import re
from scripts.solutions.solutions_db import lookup, generate_generic, LANG_GENERATORS


class TestNormalizeKey:
    def test_basic_slug(self):
        from scripts.solutions.solutions_db import _normalize_key
        assert _normalize_key("Suma de Dígitos") == "suma-de-digitos"

    def test_accented(self):
        from scripts.solutions.solutions_db import _normalize_key
        assert _normalize_key("Par o Ímpar") == "par-o-impar"

    def test_special_chars(self):
        from scripts.solutions.solutions_db import _normalize_key
        assert _normalize_key("Cifrado César (simple)") == "cifrado-cesar-simple"

    def test_extra_spaces(self):
        from scripts.solutions.solutions_db import _normalize_key
        assert _normalize_key("  Hola   Mundo  ") == "hola-mundo"


class TestLookup:
    def test_known_title_returns_solution(self):
        result = lookup("suma-de-digitos", "python")
        assert result is not None
        assert "codigo" in result
        assert "paso1" in result
        assert "descripcion" in result

    def test_known_curated_returns_data(self):
        result = lookup("fibonacci-recursivo", "javascript")
        assert result is not None
        assert result["big_o_time"] == "O(2^n) (O(n) con memoización/iterativo)"

    def test_unknown_title_returns_none(self):
        result = lookup("xyz-nonexistent-challenge-12345", "python")
        assert result is None

    def test_with_spaces_and_accents(self):
        result = lookup("Detector de Palíndromos", "python")
        assert result is not None
        assert result["codigo"] != ""

    def test_all_languages_have_generators(self):
        for lang_id in ["python", "javascript", "typescript", "go", "rust",
                        "java", "csharp", "kotlin", "swift", "php", "ruby", "dart"]:
            result = lookup("suma-de-digitos", lang_id)
            assert result is not None, f"Failed for {lang_id}"
            assert result["codigo"] != "", f"Empty code for {lang_id}"


class TestGenerateGeneric:
    def test_generates_python_code(self):
        result = generate_generic("Test Challenge", "python")
        assert "codigo" in result
        assert result["descripcion"] != ""
        assert result["dificultad"] == "Intermedio"

    def test_generates_js_code(self):
        result = generate_generic("Test Challenge", "javascript")
        assert "function" in result["codigo"]

    def test_unknown_lang_falls_back_to_python(self):
        result = generate_generic("Test", "nonexistent")
        assert result is not None


class TestAllLangGenerators:
    def test_all_generators_produce_code(self):
        for lang_id, gen_func in LANG_GENERATORS.items():
            code = gen_func("Test", "A description")
            assert len(code) > 20, f"Too short for {lang_id}"
