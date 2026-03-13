"""Integration tests — full pipeline from file to manifest YAML."""

import yaml

from scripts.data.doc_intelligence.orchestrator import extract_document
from scripts.data.doc_intelligence.schema import manifest_from_dict, write_manifest
from scripts.data.doc_intelligence.utils import generate_doc_ref


class TestEndToEndPdf:
    def test_pdf_roundtrip(self, sample_pdf, tmp_dir):
        out = tmp_dir / "manifest.yaml"
        m = extract_document(str(sample_pdf), domain="naval-architecture", output=str(out))
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        m2 = manifest_from_dict(loaded)
        assert m2.domain == "naval-architecture"
        assert m2.metadata.format == "pdf"
        assert len(m2.sections) > 0


class TestEndToEndDocx:
    def test_docx_roundtrip(self, sample_docx, tmp_dir):
        out = tmp_dir / "manifest.yaml"
        m = extract_document(str(sample_docx), domain="test", output=str(out))
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        m2 = manifest_from_dict(loaded)
        assert m2.metadata.format == "docx"
        assert len(m2.sections) > 0
        assert len(m2.tables) > 0


class TestEndToEndXlsx:
    def test_xlsx_roundtrip(self, sample_xlsx, tmp_dir):
        out = tmp_dir / "manifest.yaml"
        m = extract_document(str(sample_xlsx), domain="test", output=str(out))
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        m2 = manifest_from_dict(loaded)
        assert m2.metadata.format == "xlsx"
        assert len(m2.tables) == 2


class TestDocRefIntegration:
    def test_doc_ref_in_manifest(self, sample_pdf, tmp_dir):
        out = tmp_dir / "manifest.yaml"
        ref = generate_doc_ref(str(sample_pdf))
        m = extract_document(str(sample_pdf), domain="test", output=str(out), doc_ref=ref)
        loaded = yaml.safe_load(out.read_text())
        assert loaded.get("doc_ref") == ref


class TestCorruptFileIntegration:
    def test_corrupt_pdf_still_produces_manifest(self, corrupt_file, tmp_dir):
        out = tmp_dir / "manifest.yaml"
        m = extract_document(str(corrupt_file), domain="test", output=str(out))
        assert out.exists()
        assert len(m.errors) > 0
