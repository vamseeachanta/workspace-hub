"""Tests for LOC-weighted scoring and trend tracking in module_status_matrix.py.

TDD: written before implementation.

Tests cover:
  - LOC-weighted quality score calculation
  - Test-to-source ratio metric
  - Trend comparison (current vs previous JSON snapshot)
  - Edge cases (zero LOC, zero tests, zero files)
  - Score consistency (higher tests → higher score)
  - JSON snapshot round-trip for trend tracking
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# Import the module (underscore filename — standard import)
_script_path = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "analysis"
    / "module_status_matrix.py"
)
_spec = importlib.util.spec_from_file_location("module_status_matrix", _script_path)
module_status_matrix = importlib.util.module_from_spec(_spec)
sys.modules["module_status_matrix"] = module_status_matrix
_spec.loader.exec_module(module_status_matrix)


# ── Fixtures ──


@pytest.fixture
def sample_packages():
    """Sample package data for scoring tests."""
    return [
        {
            "name": "alpha",
            "status": "PRODUCTION",
            "file_count": 10,
            "test_count": 8,
            "key_classes": ["AlphaEngine"],
            "docstring_pct": 80,
            "loc": 2000,
        },
        {
            "name": "beta",
            "status": "DEVELOPMENT",
            "file_count": 5,
            "test_count": 2,
            "key_classes": ["BetaHandler"],
            "docstring_pct": 40,
            "loc": 500,
        },
        {
            "name": "gamma",
            "status": "SKELETON",
            "file_count": 2,
            "test_count": 0,
            "key_classes": [],
            "docstring_pct": 0,
            "loc": 30,
        },
        {
            "name": "delta",
            "status": "GAP",
            "file_count": 1,
            "test_count": 0,
            "key_classes": [],
            "docstring_pct": 0,
            "loc": 5,
        },
    ]


@pytest.fixture
def previous_snapshot():
    """Previous JSON snapshot for trend comparison."""
    return {
        "packages": [
            {
                "name": "alpha",
                "status": "PRODUCTION",
                "file_count": 10,
                "test_count": 6,
                "key_classes": ["AlphaEngine"],
                "docstring_pct": 70,
                "loc": 1800,
                "quality_score": 30.0,
            },
            {
                "name": "beta",
                "status": "SKELETON",
                "file_count": 4,
                "test_count": 0,
                "key_classes": ["BetaHandler"],
                "docstring_pct": 20,
                "loc": 400,
                "quality_score": 0.0,
            },
            {
                "name": "gamma",
                "status": "SKELETON",
                "file_count": 2,
                "test_count": 0,
                "key_classes": [],
                "docstring_pct": 0,
                "loc": 30,
                "quality_score": 0.0,
            },
        ],
        "summary": {
            "total": 3,
            "PRODUCTION": 1,
            "DEVELOPMENT": 0,
            "SKELETON": 2,
            "GAP": 0,
        },
    }


# ── Test LOC-weighted quality score ──


class TestQualityScore:
    """Test LOC-weighted quality score calculation."""

    def test_quality_score_returns_float(self):
        from module_status_matrix import compute_quality_score

        score = compute_quality_score(test_count=5, file_count=10, loc=1000)
        assert isinstance(score, float)

    def test_quality_score_formula(self):
        """Score = tests * files / total_loc * 100."""
        from module_status_matrix import compute_quality_score

        # 5 tests * 10 files / 1000 LOC * 100 = 5.0
        score = compute_quality_score(test_count=5, file_count=10, loc=1000)
        assert score == pytest.approx(5.0)

    def test_quality_score_zero_loc(self):
        """Zero LOC should return 0.0, not raise."""
        from module_status_matrix import compute_quality_score

        score = compute_quality_score(test_count=5, file_count=10, loc=0)
        assert score == 0.0

    def test_quality_score_zero_tests(self):
        from module_status_matrix import compute_quality_score

        score = compute_quality_score(test_count=0, file_count=10, loc=1000)
        assert score == 0.0

    def test_higher_tests_higher_score(self):
        from module_status_matrix import compute_quality_score

        low = compute_quality_score(test_count=2, file_count=10, loc=1000)
        high = compute_quality_score(test_count=8, file_count=10, loc=1000)
        assert high > low


# ── Test test-to-source ratio ──


class TestSourceRatio:
    """Test test-to-source ratio metric."""

    def test_ratio_returns_float(self):
        from module_status_matrix import compute_test_source_ratio

        ratio = compute_test_source_ratio(test_count=5, file_count=10)
        assert isinstance(ratio, float)

    def test_ratio_calculation(self):
        """Ratio = test_count / file_count."""
        from module_status_matrix import compute_test_source_ratio

        ratio = compute_test_source_ratio(test_count=5, file_count=10)
        assert ratio == pytest.approx(0.5)

    def test_ratio_zero_files(self):
        """Zero source files should return 0.0, not raise."""
        from module_status_matrix import compute_test_source_ratio

        ratio = compute_test_source_ratio(test_count=5, file_count=0)
        assert ratio == 0.0


# ── Test trend comparison ──


class TestTrendComparison:
    """Test trend detection comparing current vs previous snapshot."""

    def test_trend_up_when_score_increases(self, previous_snapshot):
        from module_status_matrix import compute_trend

        # alpha had quality_score 30.0 previously, now higher
        trend = compute_trend("alpha", 40.0, previous_snapshot)
        assert trend == "↑"

    def test_trend_down_when_score_decreases(self, previous_snapshot):
        from module_status_matrix import compute_trend

        trend = compute_trend("alpha", 20.0, previous_snapshot)
        assert trend == "↓"

    def test_trend_steady_when_score_same(self, previous_snapshot):
        from module_status_matrix import compute_trend

        trend = compute_trend("alpha", 30.0, previous_snapshot)
        assert trend == "→"

    def test_trend_new_package(self, previous_snapshot):
        """New package not in previous snapshot should show 'NEW'."""
        from module_status_matrix import compute_trend

        trend = compute_trend("new_pkg", 10.0, previous_snapshot)
        assert trend == "NEW"

    def test_trend_no_previous(self):
        """No previous snapshot should return '—'."""
        from module_status_matrix import compute_trend

        trend = compute_trend("alpha", 10.0, None)
        assert trend == "—"
