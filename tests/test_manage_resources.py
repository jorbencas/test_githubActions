from scripts.publishers.manage_resources import (
    domain_from, format_card, count_cards, find_section_bounds, SECTION_OPEN_RE,
    extract_sections, extract_category_name,
    generate_frontmatter, has_imports, ensure_imports, convert_legacy_section,
    fix_malformed_cards, deduplicate_all_files,
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
        assert '<ResourceCard' in card
        assert 'href="https://example.com"' in card
        assert 'title="Test"' in card
        assert 'description="A description"' in card
        assert '/>' in card

    def test_card_without_description(self):
        card = format_card("NoDesc", "https://example.com", "")
        assert 'description=""' in card

    def test_card_escapes_quotes(self):
        card = format_card('Test "Name"', "https://example.com", 'desc "with" quotes')
        assert "&quot;" in card

    def test_card_ampersand_not_escaped(self):
        card = format_card("Test", "https://example.com", "a & b")
        assert "a & b" in card

    def test_no_favicon_reference(self):
        card = format_card("X", "https://example.com/page", "")
        assert "google.com/s2/favicons" not in card

    def test_card_escapes_angle_brackets(self):
        card = format_card("Test", "https://example.com", "Less than <250 or >100 items")
        assert "&lt;" in card
        assert "&gt;" in card
        assert "<250" not in card
        assert ">100" not in card


class TestCountCards:
    def test_counts_correctly(self):
        text = (
            '<ResourceCard\n'
            '  href="https://a.com"\n'
            '  title="A"\n'
            '  description="a"\n'
            '/>\n'
            '<ResourceCard\n'
            '  href="https://b.com"\n'
            '  title="B"\n'
            '  description="b"\n'
            '/>\n'
        )
        assert count_cards(text) == 2

    def test_zero_cards(self):
        assert count_cards("<p>no cards here</p>") == 0


class TestFindSectionBounds:
    def test_simple_section(self):
        text = '<ResourceCategory id="test" title="Test">\n\ncard\n\n</ResourceCategory>'
        start, end = find_section_bounds(text, 0)
        assert start == 0
        assert text[start:end] == text

    def test_nested_sections_not_nested(self):
        text = (
            '<ResourceCategory id="a" title="A">\n'
            '<ResourceCard\n'
            '  href="https://x.com"\n'
            '  title="X"\n'
            '  description="x"\n'
            '/>\n'
            '</ResourceCategory>\n'
            '<ResourceCategory id="b" title="B">\n'
            'card\n'
            '</ResourceCategory>\n'
            'tail'
        )
        start, end = find_section_bounds(text, 0)
        # Should stop at first </ResourceCategory> (section "a")
        section_a = text[start:end]
        assert 'id="a"' in section_a
        assert 'id="b"' not in section_a
        assert section_a.endswith('</ResourceCategory>')

    def test_end_of_content(self):
        text = '<ResourceCategory id="x" title="X">\ncard\n'
        start, end = find_section_bounds(text, 0)
        assert text[start:end] == text


class TestExtractSections:
    SAMPLE = """---
title: Test
---

preamble text

<ResourceCategory id="cat1" title="📁 Categoria 1">

<ResourceCard
  href="https://a.com"
  title="A"
  description="a"
/>

</ResourceCategory>

<ResourceCategory id="cat2" title="📁 Categoria 2">

<ResourceCard
  href="https://b.com"
  title="B"
  description="b"
/>

</ResourceCategory>

footer
"""

    def test_extracts_two_sections(self):
        parts = extract_sections(self.SAMPLE)
        sections = [p for p in parts if p[0] == "section"]
        assert len(sections) == 2

    def test_first_section_content(self):
        parts = extract_sections(self.SAMPLE)
        sections = [p for p in parts if p[0] == "section"]
        assert "cat1" in sections[0][1]
        assert "Categoria 1" in sections[0][1]
        assert "a.com" in sections[0][1]

    def test_preamble_includes_frontmatter(self):
        parts = extract_sections(self.SAMPLE)
        preambles = [p for p in parts if p[0] == "preamble"]
        assert any("---" in p[1] for p in preambles)

    def test_footer_is_preamble(self):
        parts = extract_sections(self.SAMPLE)
        preambles = [p for p in parts if p[0] == "preamble"]
        assert any("footer" in p[1] for p in preambles)


class TestExtractCategoryName:
    def test_with_emoji(self):
        text = '<ResourceCategory id="x" title="📁 Categoria">\ncard\n</ResourceCategory>'
        assert extract_category_name(text) == "categoria"

    def test_without_emoji(self):
        text = '<ResourceCategory id="x" title="Testing">\ncard\n</ResourceCategory>'
        assert extract_category_name(text) == "testing"

    def test_empty(self):
        assert extract_category_name("<p>no section</p>") == ""


class TestGenerateFrontmatter:
    def test_first_page(self):
        fm = generate_frontmatter(0, 500)
        assert '"Recursos para desarrolladores"' in fm
        assert 'tags' in fm

    def test_subsequent_page(self):
        fm = generate_frontmatter(1, 300)
        assert 'Página 2' in fm
        assert '300' in fm


class TestHasImports:
    def test_has_imports(self):
        assert has_imports("import ResourceCard from '@components/ResourceCard.astro';")

    def test_no_imports(self):
        assert not has_imports("---\ntitle: Test\n---\n\ncontent")


class TestEnsureImports:
    def test_adds_imports_after_frontmatter(self):
        text = "---\ntitle: Test\n---\n\ncontent"
        result = ensure_imports(text)
        assert "import ResourceCard from" in result
        assert "import ResourceCategory from" in result
        assert "content" in result
        assert result.index("import") > result.index("---")

    def test_does_not_duplicate(self):
        text = "---\ntitle: Test\n---\n\nimport ResourceCard from '@components/ResourceCard.astro';\nimport ResourceCategory from '@components/ResourceCategory.astro';\n\ncontent"
        result = ensure_imports(text)
        assert result.count("import ResourceCard") == 1


class TestConvertLegacySection:
    def test_converts_html_section(self):
        html = '''<div class="not-prose mt-12 mb-6"><h2 class="..." id="test-id">🔧 Test Title</h2></div>
<div class="not-prose grid grid-cols-1 md:grid-cols-2 gap-4 my-6">

<a href="https://example.com" class="flex items-start gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-cyan-400 dark:hover:border-cyan-400 hover:shadow-xl hover:-translate-y-1 transition-all no-underline group">
  <img src="https://www.google.com/s2/favicons?domain=example.com&sz=32" width="20" height="20" class="mt-1 shrink-0 rounded bg-slate-100 dark:bg-slate-800 p-0.5" alt="Test" loading="lazy" />
  <div>
    <span class="font-bold text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">Test Tool</span>
    <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5 leading-snug">A description with &amp; ampersand</p>
  </div>
</a>

</div>'''
        result = convert_legacy_section(html)
        assert '<ResourceCategory id="test-id" title="🔧 Test Title">' in result
        assert '<ResourceCard' in result
        assert 'href="https://example.com"' in result
        assert 'title="Test Tool"' in result
        assert 'description="A description with & ampersand"' in result
        assert '</ResourceCategory>' in result

    def test_returns_original_if_no_h2(self):
        assert convert_legacy_section("<p>no section</p>") == "<p>no section</p>"


class TestFixMalformedCards:
    def test_fixes_missing_closing_angle(self):
        content = '''<ResourceCard
  href="https://example.com"
  title="Test"
  description="Desc"
/>
'''
        result = fix_malformed_cards(content)
        assert '/>' in result
        assert 'href="https://example.com"' in result

    def test_fixes_slash_without_angle(self):
        content = '''<ResourceCard
  href="https://example.com"
  title="Test"
  description="Desc"
/>
'''
        result = fix_malformed_cards(content)
        assert '/>' in result

    def test_leaves_valid_cards_unchanged(self):
        content = '''<ResourceCard
  href="https://example.com"
  title="Test"
  description="Desc"
/>
'''
        result = fix_malformed_cards(content)
        assert result == content

    def test_fixes_multiple_malformed_cards(self):
        content = '''<ResourceCard
  href="https://a.com"
  title="A"
  description="Desc A"
/>

<ResourceCard
  href="https://b.com"
  title="B"
  description="Desc B"
/>
'''
        result = fix_malformed_cards(content)
        assert result.count('/>') == 2


class TestDeduplicateAllFiles:
    def test_deduplicates_across_files(self, tmp_path):
        """Test that same URL in different files/categories is deduplicated."""
        # Create two resource files with overlapping URLs
        file1 = tmp_path / "resources.mdx"
        file1.write_text('''---
draft: false
title: "Recursos para desarrolladores"
---

<ResourceCategory id="ai" title="AI Tools">

<ResourceCard
  href="https://example.com/tool1"
  title="Tool1"
  description="AI tool"
/>

</ResourceCategory>
''')

        file2 = tmp_path / "resources2.mdx"
        file2.write_text('''---
draft: false
title: "Recursos para desarrolladores (Página 2)"
---

<ResourceCategory id="devtools" title="Dev Tools">

<ResourceCard
  href="https://example.com/tool1"
  title="Tool1"
  description="Same tool in different category"
/>

<ResourceCard
  href="https://example.com/tool2"
  title="Tool2"
  description="Unique tool"
/>

</ResourceCategory>
''')

        removed = deduplicate_all_files(tmp_path)
        assert removed == 1  # One duplicate removed

        # Verify file2 no longer has the duplicate
        content2 = file2.read_text()
        assert content2.count('https://example.com/tool1') == 0
        assert 'https://example.com/tool2' in content2
