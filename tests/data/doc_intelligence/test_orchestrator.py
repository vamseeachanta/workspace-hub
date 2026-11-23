"""Tests for orchestrator — format detection, dispatch, manifest write."""

import yaml
from pathlib import Path

from scripts.data.doc_intelligence.orchestrator import extract_document


class TestFormatDetection:
    def test_pdf_dispatches_to_pdf_parser(self, sample_pdf):
        m = extract_document(str(sample_pdf), domain="test")
        assert m.metadata.format == "pdf"

    def test_docx_dispatches_to_docx_parser(self, sample_docx):
        m = extract_document(str(sample_docx), domain="test")
        assert m.metadata.format == "docx"


class TestManifestWrite:
    def test_writes_manifest_to_output(self, sample_pdf, tmp_dir):
        out = tmp_dir / "result.manifest.yaml"
        m = extract_document(str(sample_pdf), domain="test", output=str(out))
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        assert loaded["domain"] == "test"
        assert loaded["extraction_stats"]["sections"] > 0


class TestUnsupported:
    def test_unsupported_format_returns_error(self, tmp_dir):
        txt = tmp_dir / "readme.txt"
        txt.write_text("hello")
        m = extract_document(str(txt), domain="test")
        assert len(m.errors) > 0
        assert "unsupported" in m.errors[0].lower()
