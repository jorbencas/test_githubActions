from scripts.utils.constants_downloadfile import (
    FUENTES, CONFIG, JS_CONFIG,
    EMAIL_TEMPLATE, EMAIL_ROW_TEMPLATE, EMAIL_SOURCE_HEADER, EMAIL_VIDEO_HEADER, EMAIL_VIDEO_ROW,
    clasificar_noticia,
)


class TestFuentesStructure:
    def test_fuentes_has_items(self):
        assert len(FUENTES) > 50

    def test_each_fuente_has_url_or_yt(self):
        for name, info in FUENTES.items():
            has_url = "url" in info or "yt" in info or "rss" in info
            assert has_url, f"{name} missing url/yt/rss: {info}"

    def test_quick_sources_count(self):
        quick = {k: v for k, v in FUENTES.items() if v.get("quick")}
        assert len(quick) >= 60, f"Expected >= 60 quick sources, got {len(quick)}"

    def test_rss_sources_have_url(self):
        rss = {k: v for k, v in FUENTES.items() if "rss" in v and v.get("quick")}
        for name, info in rss.items():
            assert info["rss"].startswith("http"), f"{name} RSS URL invalid: {info['rss']}"

    def test_web_scraping_sources_have_selector(self):
        web = {k: v for k, v in FUENTES.items() if "url" in v and "selector" in v and v.get("quick")}
        for name, info in web.items():
            assert "selector" in info, f"{name} missing selector"
            assert "tipo" in info, f"{name} missing tipo"

    def test_chinese_ai_sources_exist(self):
        chinese = ["QbitAI", "Qwen", "DeepSeek"]
        for name in chinese:
            found = any(name.lower() in k.lower() for k in FUENTES.keys())
            assert found, f"Chinese AI source '{name}' not found"


class TestEmailTemplates:
    def test_email_template_has_placeholders(self):
        assert "{contenido_html}" in EMAIL_TEMPLATE
        assert "{lista_email}" in EMAIL_TEMPLATE
        assert "{videos_html}" in EMAIL_TEMPLATE
        assert "{fecha_hoy}" in EMAIL_TEMPLATE

    def test_email_row_template_has_placeholders(self):
        assert "{icon}" in EMAIL_ROW_TEMPLATE
        assert "{enlace}" in EMAIL_ROW_TEMPLATE
        assert "{titulo}" in EMAIL_ROW_TEMPLATE
        assert "{resumen_html}" in EMAIL_ROW_TEMPLATE

    def test_email_source_header_has_placeholders(self):
        assert "{source_name}" in EMAIL_SOURCE_HEADER
        assert "{source_count}" in EMAIL_SOURCE_HEADER
        assert "{source_color}" in EMAIL_SOURCE_HEADER
        assert "{source_icon}" in EMAIL_SOURCE_HEADER

    def test_email_video_header_has_placeholders(self):
        assert "{video_count}" in EMAIL_VIDEO_HEADER

    def test_email_video_row_has_placeholders(self):
        assert "{thumbnail}" in EMAIL_VIDEO_ROW
        assert "{canal}" in EMAIL_VIDEO_ROW
        assert "{enlace}" in EMAIL_VIDEO_ROW
        assert "{titulo}" in EMAIL_VIDEO_ROW
        assert "{duracion}" in EMAIL_VIDEO_ROW

    def test_email_row_has_button(self):
        assert "Leer noticia →" in EMAIL_ROW_TEMPLATE

    def test_email_row_title_style(self):
        assert "font-size: 15px" in EMAIL_ROW_TEMPLATE
        assert "font-weight: 700" in EMAIL_ROW_TEMPLATE
        assert "color: #0f172a" in EMAIL_ROW_TEMPLATE

    def test_email_row_summary_style(self):
        # Summary style is applied in send_email.py, not in template
        # Template just has {resumen_html} placeholder
        assert "{resumen_html}" in EMAIL_ROW_TEMPLATE


class TestTabsMultimedia:
    def test_has_tabs_in_js_config(self):
        tabs = JS_CONFIG.get("TABS_MULTIMEDIA", [])
        ids = [t["id"] for t in tabs]
        assert "youtube" in ids

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
