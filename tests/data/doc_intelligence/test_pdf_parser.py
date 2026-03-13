"""Tests for PdfParser — text extraction, tables, figure refs, corrupt files."""

import pytest

from scripts.data.doc_intelligence.parsers.pdf import PdfParser


class TestPdfCanHandle:
    def test_accepts_pdf(self):
        assert PdfParser().can_handle("report.pdf")

    def test_rejects_docx(self):
        assert not PdfParser().can_handle("report.docx")


class TestPdfExtraction:
    def test_extracts_sections(self, sample_pdf):
        m = PdfParser().parse(str(sample_pdf), domain="test")
        assert len(m.sections) > 0
        texts = " ".join(s.text for s in m.sections)
        assert "riser design" in texts.lower()

    def test_extracts_tables(self, sample_pdf):
        m = PdfParser().parse(str(sample_pdf), domain="test")
        assert len(m.tables) > 0
        flat = [cell for t in m.tables for row in t.rows for cell in row]
        assert any("Diameter" in c for c in flat)

    def test_corrupt_file_returns_errors(self, corrupt_file):
        m = PdfParser().parse(str(corrupt_file), domain="test")
        assert len(m.errors) > 0
        assert m.metadata.filename == "corrupt.pdf"
