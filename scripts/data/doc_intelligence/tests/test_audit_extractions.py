# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "pytest"]
# ///
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml
import pytest

from audit_extractions import audit_directory, audit_manifest, format_report


def test_audit_counts_manifests(tmp_path):
    for name in ["a.manifest.yaml", "b.manifest.yaml"]:
        (tmp_path / name).write_text(yaml.dump({
            "version": "1.0.0", "tool": "test", "domain": "test",
            "metadata": {"filename": name, "format": "pdf", "size_bytes": 100},
            "sections": [{"heading": "X", "level": 1, "text": "t", "source": {"document": "x"}}],
            "tables": [], "figure_refs": [],
            "extraction_stats": {"sections": 1, "tables": 0, "figure_refs": 0},
            "errors": [],
        }))
    report = audit_directory(str(tmp_path))
    assert report["total_manifests"] == 2
    assert report["total_sections"] == 2


def test_audit_empty_directory(tmp_path):
    report = audit_directory(str(tmp_path))
    assert report["total_manifests"] == 0
    assert report["avg_sections_per_doc"] == 0.0


def test_audit_manifest_single():
    manifest = {
        "metadata": {"filename": "test.pdf", "format": "pdf", "size_bytes": 100},
        "domain": "structural",
        "sections": [{"heading": "A", "level": 1, "text": "t", "source": {}}],
        "tables": [{"title": "T1", "columns": ["a"], "rows": [["b"]], "source": {}}],
        "figure_refs": [],
        "errors": ["warning: missing page"],
    }
    stats = audit_manifest(manifest)
    assert stats["section_count"] == 1
    assert stats["table_count"] == 1
    assert stats["error_count"] == 1
    assert stats["format"] == "pdf"


def test_audit_tracks_errors(tmp_path):
    (tmp_path / "bad.manifest.yaml").write_text(yaml.dump({
        "version": "1.0.0", "tool": "test", "domain": "test",
        "metadata": {"filename": "bad.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [], "tables": [], "figure_refs": [],
        "extraction_stats": {},
        "errors": ["error1", "error2"],
    }))
    report = audit_directory(str(tmp_path))
    assert report["error_rate"] == 1.0
    assert len(report["manifests_with_errors"]) == 1


def test_format_breakdown(tmp_path):
    for name, fmt in [("a.manifest.yaml", "pdf"), ("b.manifest.yaml", "docx")]:
        (tmp_path / name).write_text(yaml.dump({
            "version": "1.0.0", "tool": "test", "domain": "test",
            "metadata": {"filename": name, "format": fmt, "size_bytes": 100},
            "sections": [], "tables": [], "figure_refs": [],
            "extraction_stats": {},
            "errors": [],
        }))
    report = audit_directory(str(tmp_path))
    assert report["format_breakdown"]["pdf"] == 1
    assert report["format_breakdown"]["docx"] == 1


def test_domain_breakdown(tmp_path):
    for name, domain in [("a.manifest.yaml", "structural"), ("b.manifest.yaml", "pipeline")]:
        (tmp_path / name).write_text(yaml.dump({
            "version": "1.0.0", "tool": "test", "domain": domain,
            "metadata": {"filename": name, "format": "pdf", "size_bytes": 100},
            "sections": [], "tables": [], "figure_refs": [],
            "extraction_stats": {},
            "errors": [],
        }))
    report = audit_directory(str(tmp_path))
    assert report["domain_breakdown"]["structural"] == 1
    assert report["domain_breakdown"]["pipeline"] == 1


def test_format_report_returns_string(tmp_path):
    report = audit_directory(str(tmp_path))
    text = format_report(report)
    assert isinstance(text, str)
    assert "total_manifests" in text


def test_avg_tables_per_doc(tmp_path):
    (tmp_path / "a.manifest.yaml").write_text(yaml.dump({
        "version": "1.0.0", "tool": "test", "domain": "test",
        "metadata": {"filename": "a.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [],
        "tables": [
            {"title": "T1", "columns": ["a"], "rows": [["b"]], "source": {}},
            {"title": "T2", "columns": ["a"], "rows": [["b"]], "source": {}},
        ],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }))
    report = audit_directory(str(tmp_path))
    assert report["avg_tables_per_doc"] == 2.0
