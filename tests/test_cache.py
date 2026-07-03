import tempfile, os, json
from datetime import datetime, timedelta
from scripts.utils.cache import FileCache, CacheManager, _default_key


class TestDefaultKey:
    def test_uses_enlace(self):
        assert _default_key({"enlace": "https://x.com"}) == "https://x.com"

    def test_fallback_empty(self):
        assert _default_key({"otro": "x"}) == ""

    def test_strips_and_lowers(self):
        assert _default_key({"enlace": "  HTTPS://X.COM/ "}) == "https://x.com"


class TestFileCache:
    def test_load_empty_if_not_exists(self):
        with tempfile.TemporaryDirectory() as d:
            c = FileCache(os.path.join(d, "cache.json"))
            assert c.load() == {}

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cache.json")
            c = FileCache(path)
            c.save({"k1": "v1"})
            c2 = FileCache(path)
            assert c2.load() == {"k1": "v1"}

    def test_load_list_converts_to_dict(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cache.json")
            with open(path, "w") as f:
                json.dump(
                    [{"enlace": "https://a.com"}, {"enlace": "https://b.com"}], f
                )
            c = FileCache(path)
            data = c.load()
            assert "https://a.com" in data
            assert "https://b.com" in data

    def test_cache_in_memory(self):
        with tempfile.TemporaryDirectory() as d:
            c = FileCache(os.path.join(d, "cache.json"))
            assert c.load() == {}
            # Second call returns cached
            assert c.load() == {}


class TestCacheManager:
    def test_is_new_returns_true_for_missing(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(FileCache(os.path.join(d, "cache.json")))
            assert cm.is_new("unknown_key")

    def test_mark_sent_and_is_new(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(FileCache(os.path.join(d, "cache.json")))
            cm.mark_sent("k1")
            assert not cm.is_new("k1")

    def test_mark_sent_with_dict(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(FileCache(os.path.join(d, "cache.json")))
            cm.mark_sent({"enlace": "https://example.com"})
            assert not cm.is_new({"enlace": "https://example.com"})

    def test_ttl_expiry(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(
                FileCache(os.path.join(d, "cache.json")), ttl_hours=1
            )
            cm.mark_sent("k1")
            assert not cm.is_new("k1")
            # Force entry to be old
            cm._data["k1"] = {
                "ts": (datetime.now() - timedelta(hours=2)).timestamp()
            }
            assert cm.is_new("k1")

    def test_flush_persists(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cache.json")
            cm = CacheManager(FileCache(path))
            cm.mark_sent("persisted_key")
            cm.flush()
            cm2 = CacheManager(FileCache(path))
            assert not cm2.is_new("persisted_key")

    def test_size(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(FileCache(os.path.join(d, "cache.json")))
            assert cm.size() == 0
            cm.mark_sent("a")
            cm.mark_sent("b")
            assert cm.size() == 2

    def test_clear(self):
        with tempfile.TemporaryDirectory() as d:
            cm = CacheManager(FileCache(os.path.join(d, "cache.json")))
            cm.mark_sent("k")
            cm.clear()
            assert cm.size() == 0
