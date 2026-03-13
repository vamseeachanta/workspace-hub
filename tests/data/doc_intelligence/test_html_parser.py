"""Tests for HtmlParser — headings, paragraphs, tables from HTML."""

import pytest

from scripts.data.doc_intelligence.parsers.html import HtmlParser


SAMPLE_HTML = """\
<!DOCTYPE html>
<html>
<head><title>Marine Hydrodynamics Lecture 1</title></head>
<body>
<h1>Introduction to Marine Hydrodynamics</h1>
<p>This lecture covers the fundamentals of fluid mechanics applied to ships.</p>
<h2>1.1 Scope</h2>
<p>Topics include wave theory, resistance, and propulsion.</p>
<h3>1.1.1 Wave Theory</h3>
<p>Linear wave theory describes small-amplitude waves.</p>
<table>
<tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>
<tr><td>Wavelength</td><td>150</td><td>m</td></tr>
<tr><td>Period</td><td>10</td><td>s</td></tr>
</table>
<div>Some additional notes in a div.</div>
</body>
</html>
"""


@pytest.fixture
def sample_html_file(tmp_dir):
    f = tmp_dir / "lecture.html"
    f.write_text(SAMPLE_HTML)
    return f


@pytest.fixture
def minimal_html_file(tmp_dir):
    f = tmp_dir / "minimal.htm"
    f.write_text("<html><body><p>Just a paragraph.</p></body></html>")
    return f


class TestHtmlCanHandle:
    def test_accepts_html(self):
        assert HtmlParser().can_handle("page.html")

    def test_accepts_htm(self):
        assert HtmlParser().can_handle("page.htm")

    def test_rejects_pdf(self):
        assert not HtmlParser().can_handle("doc.pdf")

    def test_case_insensitive(self):
        assert HtmlParser().can_handle("PAGE.HTML")


class TestHtmlExtractSections:
    def test_extracts_headings(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        headings = [s for s in m.sections if s.level > 0]
        assert len(headings) == 3
        assert headings[0].level == 1
        assert "marine hydrodynamics" in headings[0].text.lower()
        assert headings[1].level == 2
        assert headings[2].level == 3

    def test_extracts_paragraphs(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        paragraphs = [s for s in m.sections if s.level == 0]
        assert len(paragraphs) >= 3
        texts = " ".join(p.text for p in paragraphs)
        assert "fluid mechanics" in texts.lower()

    def test_extracts_div_text(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        texts = " ".join(s.text for s in m.sections)
        assert "additional notes" in texts.lower()


class TestHtmlExtractTables:
    def test_extracts_table(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        assert len(m.tables) == 1
        t = m.tables[0]
        assert t.columns == ["Parameter", "Value", "Unit"]
        assert len(t.rows) == 2
        assert t.rows[0] == ["Wavelength", "150", "m"]

    def test_no_table_in_minimal(self, minimal_html_file):
        m = HtmlParser().parse(str(minimal_html_file), domain="test")
        assert len(m.tables) == 0


class TestHtmlMetadata:
    def test_format_is_html(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        assert m.metadata.format == "html"

    def test_domain_is_set(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="naval-architecture")
        assert m.domain == "naval-architecture"

    def test_source_document_is_filename(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        assert m.sections[0].source.document == "lecture.html"

    def test_extraction_stats(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        assert m.extraction_stats["sections"] > 0
        assert m.extraction_stats["tables"] == 1

    def test_checksum_populated(self, sample_html_file):
        m = HtmlParser().parse(str(sample_html_file), domain="test")
        assert m.metadata.checksum is not None
        assert len(m.metadata.checksum) == 64  # SHA256 hex


class TestHtmlNestedDivs:
    def test_nested_divs_no_duplication(self, tmp_dir):
        """Container divs should not duplicate descendant text."""
        html = """\
<html><body>
<div class="container">
  <div class="inner">Inner content only</div>
</div>
</body></html>"""
        f = tmp_dir / "nested.html"
        f.write_text(html)
        m = HtmlParser().parse(str(f), domain="test")
        texts = [s.text for s in m.sections if s.level == 0]
        # Should have "Inner content only" exactly once
        assert texts.count("Inner content only") == 1

    def test_inline_tags_preserve_whitespace(self, tmp_dir):
        """Inline markup should not collapse word boundaries."""
        html = "<html><body><p>A <b>bold</b> word</p></body></html>"
        f = tmp_dir / "inline.html"
        f.write_text(html)
        m = HtmlParser().parse(str(f), domain="test")
        texts = [s.text for s in m.sections if s.level == 0]
        assert any("A bold word" in t for t in texts)


class TestHtmlParserSourceOverride:
    def test_source_document_override(self, sample_html_file):
        m = HtmlParser().parse(
            str(sample_html_file),
            domain="test",
            source_url="https://example.com/lecture.html",
        )
        assert m.sections[0].source.document == "https://example.com/lecture.html"
