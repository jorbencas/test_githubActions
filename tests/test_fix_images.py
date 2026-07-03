from pathlib import Path
from io import BytesIO
from PIL import Image

from scripts.tools.fix_images import (
    compute_ssim, _channel_stats, strip_metadata, constrain_size,
    clean_query, slugify, build_srcset, generate_placeholder,
)

SIZES = [480, 768, 1200]


def _make_test_image(mode="RGB", size=(100, 100)):
    return Image.new(mode, size)


class TestSsim:
    def test_identical_returns_one(self):
        img = _make_test_image()
        assert compute_ssim(img, img) >= 0.99

    def test_black_vs_white(self):
        black = Image.new("L", (160, 160), 0)
        white = Image.new("L", (160, 160), 255)
        ssim = compute_ssim(black, white)
        assert ssim < 0.5


class TestChannelStats:
    def test_uniform_image(self):
        img = Image.new("L", (10, 10), 128)
        pixels = list(img.tobytes())
        m_a, m_b, v_a, v_b, c_ab = _channel_stats(pixels, pixels, 10, 10)
        assert m_a == 128.0
        assert m_b == 128.0
        assert c_ab >= 0

    def test_empty_returns_zero(self):
        m_a, m_b, v_a, v_b, c_ab = _channel_stats([], [], 0, 0)
        assert m_a == 0.0
        assert v_a == 0.0


class TestStripMetadata:
    def test_non_empty_result(self):
        img = _make_test_image()
        clean = strip_metadata(img)
        assert clean.size == img.size
        assert clean.mode == img.mode

    def test_preserves_pixels(self):
        img = Image.new("RGB", (10, 10), (255, 0, 0))
        clean = strip_metadata(img)
        assert clean.getpixel((0, 0)) == (255, 0, 0)


class TestConstrainSize:
    def test_shrinks_wide_image(self):
        img = Image.new("RGB", (2000, 1000))
        resized = constrain_size(img, max_width=1200)
        assert resized.width == 1200

    def test_small_image_unchanged(self):
        img = Image.new("RGB", (800, 600))
        resized = constrain_size(img, max_width=1200)
        assert resized.width == 800


class TestCleanQuery:
    def test_removes_stop_words(self):
        # clean_query splits by _ and filters stop words
        assert "guia" not in clean_query("guia_de_Python_para_testing")
        assert "Python" in clean_query("guia_de_Python_para_testing")

    def test_handles_slashes(self):
        # "tutorial" is a stop word, so it's filtered out
        result = clean_query("astro/tutorial")
        assert result == "astro"


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello_world"

    def test_accents(self):
        assert slugify("Día de la Programación") == "dia_de_la_programacion"

    def test_special_chars(self):
        assert slugify("test@#$file") == "test_file"


class TestBuildSrcset:
    def test_correct_format(self):
        images = [("img1-480.webp", 480), ("img1-768.webp", 768)]
        result = build_srcset(images, "/img/test")
        assert "/img/test/img1-480.webp 480w" in result
        assert "/img/test/img1-768.webp 768w" in result

    def test_single_entry(self):
        images = [("img.webp", 1200)]
        result = build_srcset(images, "/img")
        assert result == "/img/img.webp 1200w"


class TestGeneratePlaceholder:
    def test_returns_string(self):
        img = _make_test_image()
        placeholder = generate_placeholder(img)
        assert isinstance(placeholder, str)
        assert len(placeholder) > 20
