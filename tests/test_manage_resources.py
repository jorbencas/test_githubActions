from scripts.publishers.manage_resources import (
    domain_from, format_card, count_cards, find_grid_bounds,
    extract_sections_with_depth, extract_category_name,
    generate_frontmatter,
)


class TestDomainFrom:
    def test_strips_www(self):
        assert domain_from("https://www.example.com/page") == "example.com"

    def test_no_www(self):
        assert domain_from("https://example.com") == "example.com"

    def test_subdomain(self):
        assert domain_from("https://sub.example.com") == "sub.example.com"


class TestFormatCard:
    def test_card_has_required_parts(self):
        card = format_card("Test", "https://example.com", "A description")
        assert '<a href="https://example.com"' in card
        assert "Test" in card
        assert "A description" in card
        assert "</a>" in card

    def test_card_without_description(self):
        card = format_card("NoDesc", "https://example.com", "")
        assert "NoDesc" in card
        assert "<p" not in card  # No empty <p>

    def test_card_escapes_html(self):
        card = format_card("<b>X</b>", "https://example.com", 'a & b < c')
        assert "&lt;b&gt;X&lt;/b&gt;" in card
        assert "a &amp; b &lt; c" in card

    def test_favicon_url(self):
        card = format_card("X", "https://example.com/page", "")
        assert "google.com/s2/favicons?domain=example.com" in card


class TestCountCards:
    def test_counts_correctly(self):
        html = (
            '<a href="https://a.com" class="flex items-start gap-4 ..."></a>\n'
            '<a href="https://b.com" class="flex items-start gap-4 ..."></a>\n'
            '<a href="https://c.com" class="flex items-start gap-4 ..."></a>\n'
        )
        assert count_cards(html) == 3

    def test_zero_cards(self):
        assert count_cards("<p>no cards here</p>") == 0

    def test_card_with_long_content(self):
        card = format_card("Long", "https://example.com", "x" * 500)
        assert count_cards(card) == 1


class TestFindGridBounds:
    def test_simple_grid(self):
        html = '<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">\ncard\n</div>'
        start, end = find_grid_bounds(html, 0)
        assert start == 0
        assert html[start:end] == html

    def test_nested_divs(self):
        html = (
            '<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">\n'
            '  <div>inner</div>\n'
            '</div>\n'
            'tail'
        )
        start, end = find_grid_bounds(html, 0)
        assert end == len(html) - 5  # minus "tail"
        assert html[end:] == "\ntail"

    def test_deeply_nested(self):
        html = (
            '<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">\n'
            '  <div><div><p>deep</p></div></div>\n'
            '</div>\n'
        )
        start, end = find_grid_bounds(html, 0)
        assert html[:end] == html.strip()


class TestExtractSections:
    SAMPLE = """---
title: Test
---

<div class="not-prose mt-12 mb-6"><h2 id="cat1">📁 Categoria 1</h2></div>
<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
<a href="https://a.com" class="flex items-start gap-4 ..."></a>
</div>

<div class="not-prose mt-12 mb-6"><h2 id="cat2">📁 Categoria 2</h2></div>
<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
<a href="https://b.com" class="flex items-start gap-4 ..."></a>
</div>
"""

    def test_extracts_two_sections(self):
        parts = extract_sections_with_depth(self.SAMPLE)
        sections = [p for p in parts if p[0] == "section"]
        assert len(sections) == 2

    def test_first_section_content(self):
        parts = extract_sections_with_depth(self.SAMPLE)
        sections = [p for p in parts if p[0] == "section"]
        assert "Categoria 1" in sections[0][1]
        assert "a.com" in sections[0][1]

    def test_preamble_includes_frontmatter(self):
        parts = extract_sections_with_depth(self.SAMPLE)
        preambles = [p for p in parts if p[0] == "preamble"]
        assert any("---" in p[1] for p in preambles)


class TestExtractCategoryName:
    def test_with_emoji(self):
        html = '<h2 class="...">📁 Categoria</h2>'
        assert extract_category_name(html) == "categoria"

    def test_without_emoji(self):
        html = '<h2 class="...">Testing</h2>'
        assert extract_category_name(html) == "testing"

    def test_empty(self):
        assert extract_category_name("<p>no h2</p>") == ""


class TestGenerateFrontmatter:
    def test_first_page(self):
        fm = generate_frontmatter(0, 2, 500)
        assert '"Recursos para desarrolladores"' in fm
        assert 'tags' in fm

    def test_subsequent_page(self):
        fm = generate_frontmatter(1, 2, 300)
        assert 'Página 2' in fm
        assert '300' in fm
