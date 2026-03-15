#!/usr/bin/env python3
# ABOUTME: TDD tests for Phase B checkpoint/reporting script (WRK-1188 Phase 0b)
# ABOUTME: Validates discipline distribution, error rate, method breakdown output

"""Tests for phase-b-checkpoint.py — batch checkpoint reporting."""

import json
import yaml
from pathlib import Path

import pytest

import sys
sys.path.insert(
    0, str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
)


# ── Helper: create test summaries ────────────────────────────────────────────


def _make_summary(
    tmp_path, sha, discipline="materials", source="og_standards",
    org="ASTM", method="astm_deterministic",
):
    data = {
        "sha256": sha,
        "discipline": discipline,
        "source": source,
        "org": org,
        "extraction_method": method,
        "summary": f"Test doc {sha}",
        "keywords": [],
    }
    (tmp_path / f"{sha}.json").write_text(json.dumps(data))
    return data


# ── Discipline distribution ──────────────────────────────────────────────────


class TestDisciplineDistribution:
    """Checkpoint reports discipline counts."""

    def test_counts_by_discipline(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", discipline="materials")
        _make_summary(tmp_path, "h2", discipline="materials")
        _make_summary(tmp_path, "h3", discipline="cathodic-protection")
        _make_summary(tmp_path, "h4", discipline="other")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        dist = report["discipline_distribution"]
        assert dist["materials"] == 2
        assert dist["cathodic-protection"] == 1
        assert dist["other"] == 1

    def test_empty_dir_produces_zero_counts(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        assert report["total"] == 0
        assert report["discipline_distribution"] == {}


# ── Error/other rate ─────────────────────────────────────────────────────────


class TestErrorRate:
    """Checkpoint computes 'other' discipline rate as error proxy."""

    def test_other_rate_calculation(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", discipline="materials")
        _make_summary(tmp_path, "h2", discipline="materials")
        _make_summary(tmp_path, "h3", discipline="other")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        # 1 out of 3 is "other" → 33.3%
        assert abs(report["other_rate_pct"] - 33.3) < 1.0

    def test_zero_other_rate(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", discipline="materials")
        _make_summary(tmp_path, "h2", discipline="pipeline")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        assert report["other_rate_pct"] == 0.0


# ── Extraction method breakdown ──────────────────────────────────────────────


class TestMethodBreakdown:
    """Checkpoint reports extraction method counts."""

    def test_method_counts(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", method="astm_deterministic")
        _make_summary(tmp_path, "h2", method="astm_deterministic")
        _make_summary(tmp_path, "h3", method="claude-haiku-cli")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        methods = report["method_breakdown"]
        assert methods["astm_deterministic"] == 2
        assert methods["claude-haiku-cli"] == 1


# ── Source filtering ─────────────────────────────────────────────────────────


class TestSourceFilter:
    """Checkpoint filters by source field."""

    def test_filters_to_og_standards_only(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", source="og_standards")
        _make_summary(tmp_path, "h2", source="ace_standards")
        _make_summary(tmp_path, "h3", source="og_standards")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        assert report["total"] == 2

    def test_no_filter_counts_all(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", source="og_standards")
        _make_summary(tmp_path, "h2", source="ace_standards")

        report = compute_checkpoint(tmp_path, source_filter=None)
        assert report["total"] == 2


# ── Org breakdown ────────────────────────────────────────────────────────────


class TestOrgBreakdown:
    """Checkpoint reports per-organization counts."""

    def test_org_counts(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint
        _make_summary(tmp_path, "h1", org="ASTM")
        _make_summary(tmp_path, "h2", org="ASTM")
        _make_summary(tmp_path, "h3", org="API")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        assert report["org_breakdown"]["ASTM"] == 2
        assert report["org_breakdown"]["API"] == 1


# ── YAML output ──────────────────────────────────────────────────────────────


class TestYAMLOutput:
    """Checkpoint writes valid YAML report."""

    def test_write_checkpoint_yaml(self, tmp_path):
        from phase_b_checkpoint import compute_checkpoint, write_checkpoint
        _make_summary(tmp_path, "h1", discipline="materials")

        report = compute_checkpoint(tmp_path, source_filter="og_standards")
        out_dir = tmp_path / "checkpoints"
        write_checkpoint(report, checkpoints_dir=out_dir, label="test-batch")

        files = list(out_dir.glob("*.yaml"))
        assert len(files) == 1
        data = yaml.safe_load(files[0].read_text())
        assert data["total"] == 1
        assert "generated_at" in data
        assert data["label"] == "test-batch"
