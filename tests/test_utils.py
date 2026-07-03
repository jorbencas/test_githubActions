import json, tempfile, os
from scripts.utils.common import load_json, save_json, normalizar_url, deduplicar_items


class TestLoadSaveJson:
    def test_save_and_load(self):
        data = [{"a": 1}, {"b": 2}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_json(path, data)
            loaded = load_json(path)
            assert loaded == data
        finally:
            os.unlink(path)

    def test_load_missing(self):
        assert load_json("/tmp/nonexistent_test.json") == []


class TestNormalizarUrl:
    def test_removes_trailing_slash(self):
        assert normalizar_url("https://example.com/") == "https://example.com"

    def test_keeps_www(self):
        assert normalizar_url("https://www.example.com") == "https://www.example.com"

    def test_removes_utm(self):
        assert normalizar_url("https://example.com?utm_source=twitter") == "https://example.com"

    def test_removes_fragment(self):
        assert normalizar_url("https://example.com#section") == "https://example.com"


class TestDeduplicarItems:
    def test_exact_duplicates_short_titles(self):
        items = [{"titulo": "hola"}, {"titulo": "hola"}]
        # Titles under 10 chars skip prefix dedup, so both kept
        assert len(deduplicar_items(items)) == 2

    def test_exact_duplicates_long_titles(self):
        items = [
            {"titulo": "noticia muy importante de tecnologia"},
            {"titulo": "noticia muy importante de tecnologia"},
            {"enlace": "https://example.com/1"},
            {"enlace": "https://example.com/1"},
        ]
        # First two: same long title → dedup
        # Last two: same URL → dedup
        assert len(deduplicar_items(items)) == 2

    def test_duplicate_by_url(self):
        items = [
            {"titulo": "A", "enlace": "https://example.com/a"},
            {"titulo": "B", "enlace": "https://example.com/a"},
        ]
        assert len(deduplicar_items(items)) == 1

    def test_no_duplicates(self):
        items = [{"titulo": "hola"}, {"titulo": "adiós"}]
        assert len(deduplicar_items(items)) == 2

    def test_empty_list(self):
        assert deduplicar_items([]) == []

    def test_similar_titles(self):
        items = [
            {"titulo": "Python 3.13 released with new features"},
            {"titulo": "Python 3.13 released with new features finally"},
        ]
        assert len(deduplicar_items(items)) == 1
