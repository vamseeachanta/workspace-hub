"""Integration tests for docling document parsing library.

Tests DocumentConverter initialization, PDF-to-Markdown conversion,
and structured output extraction.

Issue: #1446
"""

import time
from pathlib import Path
from textwrap import dedent

import pytest

# Skip entire module if docling is not installed
docling = pytest.importorskip("docling", reason="docling not installed")

from docling.document_converter import DocumentConverter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "docling"


@pytest.fixture(scope="module")
def sample_html(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a minimal HTML file for conversion testing."""
    p = tmp_path_factory.mktemp("docling") / "sample.html"
    p.write_text(
        dedent("""\
        <!DOCTYPE html>
        <html><head><title>Test Document</title></head>
        <body>
        <h1>Introduction</h1>
        <p>This is a test document for docling evaluation.</p>
        <h2>Data Table</h2>
        <table>
          <tr><th>Item</th><th>Value</th></tr>
          <tr><td>Alpha</td><td>100</td></tr>
          <tr><td>Beta</td><td>200</td></tr>
        </table>
        <h2>Conclusion</h2>
        <p>End of test document.</p>
        </body></html>
        """),
        encoding="utf-8",
    )
    return p


@pytest.fixture(scope="module")
def converter() -> DocumentConverter:
    """Return a default DocumentConverter instance."""
    return DocumentConverter()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDocumentConverterInit:
    """Verify that DocumentConverter can be instantiated."""

    def test_default_init(self):
        conv = DocumentConverter()
        assert conv is not None

    def test_converter_has_convert_method(self, converter: DocumentConverter):
        assert callable(getattr(converter, "convert", None))


class TestHTMLConversion:
    """Test conversion of a simple HTML document."""

    def test_converts_html_to_markdown(
        self, converter: DocumentConverter, sample_html: Path
    ):
        result = converter.convert(str(sample_html))
        md = result.document.export_to_markdown()
        assert isinstance(md, str)
        assert len(md) > 0

    def test_markdown_contains_headings(
        self, converter: DocumentConverter, sample_html: Path
    ):
        result = converter.convert(str(sample_html))
        md = result.document.export_to_markdown()
        assert "Introduction" in md
        assert "Conclusion" in md

    def test_markdown_contains_table_data(
        self, converter: DocumentConverter, sample_html: Path
    ):
        result = converter.convert(str(sample_html))
        md = result.document.export_to_markdown()
        assert "Alpha" in md
        assert "100" in md

    def test_export_to_dict(
        self, converter: DocumentConverter, sample_html: Path
    ):
        result = converter.convert(str(sample_html))
        doc_dict = result.document.export_to_dict()
        assert isinstance(doc_dict, dict)
        assert "texts" in doc_dict or "body" in doc_dict or "main-text" in doc_dict

    def test_conversion_timing(
        self, converter: DocumentConverter, sample_html: Path
    ):
        """Conversion of a small HTML doc should complete in under 30 seconds."""
        start = time.monotonic()
        converter.convert(str(sample_html))
        elapsed = time.monotonic() - start
        assert elapsed < 30, f"Conversion took {elapsed:.1f}s — too slow"
