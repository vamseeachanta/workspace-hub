"""Tests for DocxParser — headings, body, tables, hierarchy, corrupt files."""

import pytest

from scripts.data.doc_intelligence.parsers.docx_parser import DocxParser


class TestDocxCanHandle:
    def test_accepts_docx(self):
        assert DocxParser().can_handle("report.docx")

    def test_rejects_pdf(self):
        assert not DocxParser().can_handle("report.pdf")


class TestDocxExtraction:
    def test_extracts_headings_and_body(self, sample_docx):
        m = DocxParser().parse(str(sample_docx), domain="test")
        headings = [s for s in m.sections if s.level > 0]
        body = [s for s in m.sections if s.level == 0]
        assert len(headings) >= 2
        assert len(body) >= 1

    def test_heading_hierarchy(self, sample_docx):
        m = DocxParser().parse(str(sample_docx), domain="test")
        levels = [s.level for s in m.sections if s.level > 0]
        assert 1 in levels
        assert 2 in levels

    def test_extracts_tables(self, sample_docx):
        m = DocxParser().parse(str(sample_docx), domain="test")
        assert len(m.tables) >= 1
        cols = m.tables[0].columns
        assert "Item" in cols or "Status" in cols

    def test_corrupt_file_returns_errors(self, tmp_dir):
        bad = tmp_dir / "bad.docx"
        bad.write_bytes(b"NOT A DOCX FILE")
        m = DocxParser().parse(str(bad), domain="test")
        assert len(m.errors) > 0
