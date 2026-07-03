from scripts.utils.constants_retos import CONFIG, WEBS_RETOS, RETO_MD_TEMPLATE, PROMPT_IMAGEN_TEMPLATE_RETO


class TestConfig:
    def test_has_required_keys(self):
        assert "GEMINI_KEY" in CONFIG
        assert "AI_MODELS" in CONFIG
        assert "CHALLENGES_DIR" in CONFIG
        assert isinstance(CONFIG["AI_MODELS"], list)
        assert len(CONFIG["AI_MODELS"]) > 0


class TestWebsRetos:
    def test_has_websites(self):
        assert len(WEBS_RETOS) > 0

    def test_each_has_url_and_selector(self):
        for name, cfg in WEBS_RETOS.items():
            assert "url" in cfg, f"{name} missing url"
            assert "selector" in cfg, f"{name} missing selector"
            assert cfg["url"].startswith("http"), f"{name} invalid url"


class TestRetoMdTemplate:
    def test_has_all_placeholders(self):
        required = [
            "{titulo}", "{resumen_corto}", "{fecha_pub}", "{tags_seo}",
            "{slug_name}", "{ruta_imagen}", "{dificultad}",
            "{descripcion_ia}", "{tabla_casos}",
            "{paso_1}", "{paso_2}", "{paso_3}",
            "{big_o_time}", "{big_o_space}",
            "{python_code}", "{javascript_code}", "{java_code}", "{typescript_code}",
        ]
        for placeholder in required:
            assert placeholder in RETO_MD_TEMPLATE, f"Missing placeholder: {placeholder}"


class TestPromptImagen:
    def test_has_titulo_placeholder(self):
        assert "{titulo_post}" in PROMPT_IMAGEN_TEMPLATE_RETO
