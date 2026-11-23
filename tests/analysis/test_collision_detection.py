"""Tests for cross-package API name collision detection.

TDD: written before implementation.

Tests cover:
  - Reverse index building (symbol → list of packages)
  - Collision detection with mock package data
  - Deduplication logic (same symbol in same package counted once)
  - Report formatting (markdown section)
  - Top-N most-common colliding symbols
  - No-collision scenario (all symbols unique)
  - Case sensitivity (Config vs config are separate)
  - Integration with existing scanner pipeline
"""

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

# Import architecture scanner (hyphenated filename)
_script_path = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "analysis"
    / "architecture-scanner.py"
)
_spec = importlib.util.spec_from_file_location("architecture_scanner", _script_path)
architecture_scanner = importlib.util.module_from_spec(_spec)
sys.modules["architecture_scanner"] = architecture_scanner
_spec.loader.exec_module(architecture_scanner)


# ── Fixtures ──


@pytest.fixture
def packages_with_collisions():
    """Mock package data with known collisions."""
    return [
        {
            "name": "alpha",
            "path": "/fake/alpha",
            "modules": 3,
            "classes": 2,
            "functions": 2,
            "loc": 100,
            "public_classes": ["Config", "Engine", "Base"],
            "public_functions": ["run", "setup"],
            "has_all": True,
            "has_tests": True,
        },
        {
            "name": "beta",
            "path": "/fake/beta",
            "modules": 2,
            "classes": 1,
            "functions": 1,
            "loc": 80,
            "public_classes": ["Config", "Handler"],
            "public_functions": ["run", "process"],
            "has_all": False,
            "has_tests": False,
        },
        {
            "name": "gamma",
            "path": "/fake/gamma",
            "modules": 1,
            "classes": 1,
            "functions": 0,
            "loc": 30,
            "public_classes": ["Config"],
            "public_functions": ["validate"],
            "has_all": False,
            "has_tests": True,
        },
        {
            "name": "delta",
            "path": "/fake/delta",
            "modules": 2,
            "classes": 1,
            "functions": 1,
            "loc": 50,
            "public_classes": ["UniqueClass"],
            "public_functions": ["unique_func"],
            "has_all": False,
            "has_tests": False,
        },
    ]


@pytest.fixture
def packages_no_collisions():
    """Mock package data with NO collisions — all symbols unique."""
    return [
        {
            "name": "pkg_a",
            "path": "/fake/pkg_a",
            "modules": 2,
            "classes": 1,
            "functions": 1,
            "loc": 50,
            "public_classes": ["AlphaModel"],
            "public_functions": ["alpha_run"],
            "has_all": False,
            "has_tests": True,
        },
        {
            "name": "pkg_b",
            "path": "/fake/pkg_b",
            "modules": 2,
            "classes": 1,
            "functions": 1,
            "loc": 50,
            "public_classes": ["BetaModel"],
            "public_functions": ["beta_run"],
            "has_all": False,
            "has_tests": True,
        },
    ]


# ── Test reverse index building ──


class TestBuildReverseIndex:
    """Test building symbol → [packages] reverse index."""

    def test_reverse_index_contains_all_symbols(self, packages_with_collisions):
        from architecture_scanner import build_reverse_index

        idx = build_reverse_index(packages_with_collisions)
        # All symbols should be present
        assert "Config" in idx
        assert "Engine" in idx
        assert "run" in idx
        assert "UniqueClass" in idx
        assert "unique_func" in idx

    def test_reverse_index_maps_colliding_symbol_to_multiple_packages(
        self, packages_with_collisions
    ):
        from architecture_scanner import build_reverse_index

        idx = build_reverse_index(packages_with_collisions)
        # Config is in alpha, beta, gamma
        assert set(idx["Config"]) == {"alpha", "beta", "gamma"}
        # run is in alpha and beta
        assert set(idx["run"]) == {"alpha", "beta"}


# ── Test collision detection ──


class TestDetectCollisions:
    """Test that collisions are correctly identified."""

    def test_detect_collisions_returns_dict(self, packages_with_collisions):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_with_collisions)
        assert isinstance(collisions, dict)

    def test_detect_collisions_finds_known_collisions(
        self, packages_with_collisions
    ):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_with_collisions)
        # Config collides across 3 packages
        assert "Config" in collisions
        assert len(collisions["Config"]) == 3
        # run collides across 2 packages
        assert "run" in collisions
        assert len(collisions["run"]) == 2

    def test_detect_collisions_excludes_unique_symbols(
        self, packages_with_collisions
    ):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_with_collisions)
        # UniqueClass is only in delta — should NOT be in collisions
        assert "UniqueClass" not in collisions
        assert "unique_func" not in collisions

    def test_no_collisions_returns_empty(self, packages_no_collisions):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_no_collisions)
        assert len(collisions) == 0


# ── Test deduplication ──


class TestDeduplication:
    """Test that the same symbol in the same package is counted once."""

    def test_duplicate_symbol_in_same_package_counted_once(self):
        """If a symbol appears in both public_classes and public_functions
        within the same package, the package should appear only once."""
        from architecture_scanner import build_reverse_index

        packages = [
            {
                "name": "pkg_x",
                "public_classes": ["Transform"],
                "public_functions": ["Transform"],
            },
            {
                "name": "pkg_y",
                "public_classes": [],
                "public_functions": ["Transform"],
            },
        ]
        idx = build_reverse_index(packages)
        # pkg_x should appear only once for Transform
        assert idx["Transform"].count("pkg_x") == 1
        # But Transform should still show up in both packages
        assert set(idx["Transform"]) == {"pkg_x", "pkg_y"}


# ── Test report formatting ──


class TestCollisionReport:
    """Test markdown report section for collisions."""

    def test_collision_report_is_markdown(self, packages_with_collisions):
        from architecture_scanner import generate_collision_report

        report = generate_collision_report(packages_with_collisions)
        assert isinstance(report, str)
        assert "## " in report or "# " in report

    def test_collision_report_lists_colliding_symbols(
        self, packages_with_collisions
    ):
        from architecture_scanner import generate_collision_report

        report = generate_collision_report(packages_with_collisions)
        assert "Config" in report
        assert "run" in report

    def test_collision_report_shows_packages(self, packages_with_collisions):
        from architecture_scanner import generate_collision_report

        report = generate_collision_report(packages_with_collisions)
        assert "alpha" in report
        assert "beta" in report
        assert "gamma" in report

    def test_collision_report_empty_when_no_collisions(
        self, packages_no_collisions
    ):
        from architecture_scanner import generate_collision_report

        report = generate_collision_report(packages_no_collisions)
        # Should still return something but indicate no collisions
        assert "no" in report.lower() or "0" in report or "none" in report.lower()


# ── Test top-N colliding symbols ──


class TestTopCollisions:
    """Test extraction of top-N most common colliding symbols."""

    def test_top_collisions_sorted_by_count(self, packages_with_collisions):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_with_collisions)
        # Sort by number of packages
        sorted_collisions = sorted(
            collisions.items(), key=lambda x: len(x[1]), reverse=True
        )
        # Config (3 packages) should come before run (2 packages)
        names = [name for name, _ in sorted_collisions]
        assert names.index("Config") < names.index("run")

    def test_top_n_limits_results(self, packages_with_collisions):
        from architecture_scanner import detect_collisions

        collisions = detect_collisions(packages_with_collisions)
        sorted_collisions = sorted(
            collisions.items(), key=lambda x: len(x[1]), reverse=True
        )[:1]
        # Only top 1
        assert len(sorted_collisions) == 1
        assert sorted_collisions[0][0] == "Config"


# ── Test case sensitivity ──


class TestCaseSensitivity:
    """Test that symbol names are case-sensitive."""

    def test_config_vs_CONFIG_are_different(self):
        from architecture_scanner import build_reverse_index

        packages = [
            {
                "name": "pkg_a",
                "public_classes": ["Config"],
                "public_functions": [],
            },
            {
                "name": "pkg_b",
                "public_classes": ["config"],
                "public_functions": [],
            },
        ]
        idx = build_reverse_index(packages)
        # These are different symbols
        assert "Config" in idx
        assert "config" in idx
        assert len(idx["Config"]) == 1
        assert len(idx["config"]) == 1
