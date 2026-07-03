from scripts.utils.constants_downloadfile import (
    FUENTES, PLAYWRIGHT_SOURCES, CONFIG, JS_CONFIG,
    clasificar_noticia,
)


class TestFuentesStructure:
    def test_fuentes_has_items(self):
        assert len(FUENTES) > 50

    def test_each_fuente_has_url_or_yt(self):
        for name, info in FUENTES.items():
            has_url = "url" in info or "yt" in info or "rss" in info
            assert has_url, f"{name} missing url/yt/rss: {info}"


class TestPlaywrightSources:
    def test_is_a_set(self):
        assert isinstance(PLAYWRIGHT_SOURCES, set)
        assert len(PLAYWRIGHT_SOURCES) > 0


class TestTabsMultimedia:
    def test_has_tabs_in_js_config(self):
        tabs = JS_CONFIG.get("TABS_MULTIMEDIA", [])
        ids = [t["id"] for t in tabs]
        assert "youtube" in ids
        assert "instagram" in ids

    def test_each_tab_has_id(self):
        tabs = JS_CONFIG.get("TABS_MULTIMEDIA", [])
        for tab in tabs:
            assert "id" in tab, f"tab missing id: {tab}"


class TestConfig:
    def test_has_images_folder(self):
        assert "IMAGES_FOLDER" in CONFIG


class TestClasificarNoticia:
    def test_detects_ai(self):
        assert clasificar_noticia("OpenAI lanza GPT-5") == "🤖 IA"

    def test_detects_security(self):
        result = clasificar_noticia("Nueva vulnerabilidad en Linux")
        assert result == "🔒 Ciberseguridad"

    def test_returns_general_for_unknown(self):
        result = clasificar_noticia("Receta de cocina italiana")
        assert result == "💡 General"
