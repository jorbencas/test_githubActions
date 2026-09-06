import subprocess
from pathlib import Path

from scripts.tools.bump_updated_dates import (
    parse_date,
    fmt_date,
    frontmatter_block,
)

FM = "---\ntitle: X\npubDate: \"2026/09/04\"\ndescription: Y\n---\n# Body"


class TestParsing:
    def test_frontmatter_block(self):
        assert "pubDate" in frontmatter_block(FM)
        assert frontmatter_block("no fm") is None

    def test_parse_date_slash_and_dash(self):
        assert parse_date("\"2026/09/04\"") == (2026, 9, 4)
        assert parse_date("2026-06-28") == (2026, 6, 28)
        assert parse_date("nada") is None

    def test_fmt_date_respects_separator_and_padding(self):
        assert fmt_date((2026, 9, 4), "/") == "2026/09/04"
        assert fmt_date((2026, 6, 28), "-") == "2026-06-28"