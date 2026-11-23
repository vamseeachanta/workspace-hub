# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "pytest"]
# ///
"""Tests for validate_confidence.py — TDD first."""

import sys
import os

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validate_confidence import compute_confidence, validate_manifest, validate_directory


def test_compute_confidence_high_quality():
    manifest = {
        "metadata": {"filename": "good.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "x" * 200, "source": {}}],
        "tables": [{"title": "T", "columns": ["a"], "rows": [["b"]], "source": {}}],
        "figure_refs": [{"caption": "Fig 1", "figure_id": "1", "source": {}}],
        "errors": [],
    }
    result = compute_confidence(manifest)
    assert result["score"] == pytest.approx(1.0)
    assert result["verdict"] == "pass"


def test_compute_confidence_empty_manifest():
    manifest = {
        "metadata": {"filename": "empty.pdf", "format": "pdf", "size_bytes": 0},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "errors": ["Unsupported format"],
    }
    result = compute_confidence(manifest)
    assert result["score"] == pytest.approx(0.0)
    assert result["verdict"] == "fail"


def test_compute_confidence_partial():
    manifest = {
        "metadata": {"filename": "partial.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "short", "source": {}}],
        "tables": [],
        "figure_refs": [],
        "errors": [],
    }
    result = compute_confidence(manifest)
    assert 0.3 <= result["score"] <= 0.7
    assert result["verdict"] == "pass"  # 0.3 (section) + 0.2 (no errors) = 0.5


def test_compute_confidence_returns_factors():
    manifest = {
        "metadata": {"filename": "x.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "x" * 200, "source": {}}],
        "tables": [],
        "figure_refs": [],
        "errors": [],
    }
    result = compute_confidence(manifest)
    assert "factors" in result
    assert isinstance(result["factors"], dict)
    assert "has_sections" in result["factors"]
    assert "has_tables" in result["factors"]
    assert "no_errors" in result["factors"]
    assert "avg_text_length" in result["factors"]
    assert "has_figure_refs" in result["factors"]


def test_validate_directory(tmp_path):
    good = {
        "metadata": {"filename": "g.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "x" * 200, "source": {}}],
        "tables": [{"title": "T", "columns": ["a"], "rows": [["b"]], "source": {}}],
        "figure_refs": [],
        "errors": [],
    }
    bad = {
        "metadata": {"filename": "b.pdf", "format": "pdf", "size_bytes": 0},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "errors": ["fail"],
    }
    (tmp_path / "good.manifest.yaml").write_text(yaml.dump(good))
    (tmp_path / "bad.manifest.yaml").write_text(yaml.dump(bad))
    result = validate_directory(str(tmp_path))
    assert result["total"] == 2
    assert result["passed"] == 1
    assert result["failed"] == 1


def test_custom_min_score():
    manifest = {
        "metadata": {"filename": "x.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "short", "source": {}}],
        "tables": [],
        "figure_refs": [],
        "errors": [],
    }
    result = validate_manifest(manifest, min_score=0.8)
    assert result["verdict"] == "fail"
    result2 = validate_manifest(manifest, min_score=0.3)
    assert result2["verdict"] == "pass"


def test_validate_manifest_returns_expected_keys():
    manifest = {
        "metadata": {"filename": "test.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "errors": [],
    }
    result = validate_manifest(manifest)
    assert "filename" in result
    assert "score" in result
    assert "verdict" in result
    assert "factors" in result
    assert result["filename"] == "test.pdf"


def test_validate_directory_results_list(tmp_path):
    manifest = {
        "metadata": {"filename": "a.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "errors": [],
    }
    (tmp_path / "a.manifest.yaml").write_text(yaml.dump(manifest))
    result = validate_directory(str(tmp_path))
    assert "results" in result
    assert len(result["results"]) == 1


def test_validate_directory_empty(tmp_path):
    result = validate_directory(str(tmp_path))
    assert result["total"] == 0
    assert result["passed"] == 0
    assert result["failed"] == 0
    assert result["results"] == []
