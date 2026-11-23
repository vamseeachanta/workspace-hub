"""Tests for XlsxParser — sheets as tables, multi-sheet, skip-empty, corrupt."""

import pytest

from scripts.data.doc_intelligence.parsers.xlsx import XlsxParser


class TestXlsxCanHandle:
    def test_accepts_xlsx(self):
        assert XlsxParser().can_handle("data.xlsx")

    def test_rejects_pdf(self):
        assert not XlsxParser().can_handle("data.pdf")


class TestXlsxExtraction:
    def test_sheet_becomes_table(self, sample_xlsx):
        m = XlsxParser().parse(str(sample_xlsx), domain="test")
        assert len(m.tables) >= 1
        t = m.tables[0]
        assert "Name" in t.columns or "Value" in t.columns

    def test_multi_sheet(self, sample_xlsx):
        m = XlsxParser().parse(str(sample_xlsx), domain="test")
        assert len(m.tables) == 2
        sheet_names = {t.source.sheet for t in m.tables}
        assert "Parameters" in sheet_names
        assert "Summary" in sheet_names

    def test_skips_empty_rows(self, sample_xlsx):
        m = XlsxParser().parse(str(sample_xlsx), domain="test")
        summary_table = [t for t in m.tables if t.source.sheet == "Summary"][0]
        for row in summary_table.rows:
            assert any(cell.strip() for cell in row)

    def test_corrupt_file_returns_errors(self, tmp_dir):
        bad = tmp_dir / "bad.xlsx"
        bad.write_bytes(b"NOT AN XLSX")
        m = XlsxParser().parse(str(bad), domain="test")
        assert len(m.errors) > 0
