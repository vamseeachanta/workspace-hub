"""Tests for repo-architecture-scanner.py — TDD: written before implementation.

Tests cover:
  - Package discovery from a repo with src/ layout
  - Package discovery from a repo without src/ layout (root packages)
  - Class counting (lines starting with 'class ')
  - Function counting (lines starting with 'def ')
  - __all__ export detection
  - Test directory detection
  - Markdown output format (table, top-10, entry points, mermaid)
"""

import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# Add scripts/analysis to path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "analysis"))


@pytest.fixture
def sample_repo(tmp_path):
    """Create a minimal repo structure with src/ layout for testing."""
    src = tmp_path / "src" / "mypackage"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("")

    # Package alpha: 3 files, 2 classes, 3 functions, has __all__, has tests
    alpha = src / "alpha"
    alpha.mkdir(parents=True)
    (alpha / "__init__.py").write_text('__all__ = ["AlphaEngine", "run_alpha"]\n')
    (alpha / "engine.py").write_text(textwrap.dedent("""\
        \"\"\"Alpha engine module.\"\"\"

        class AlphaEngine:
            def run(self):
                pass

        class AlphaHelper:
            pass

        def run_alpha():
            pass
    """))
    (alpha / "utils.py").write_text(textwrap.dedent("""\
        def helper_one():
            pass

        def helper_two():
            pass
    """))

    # Package beta: 1 file, 0 classes, 1 function, no __all__, no tests
    beta = src / "beta"
    beta.mkdir(parents=True)
    (beta / "__init__.py").write_text("")
    (beta / "core.py").write_text(textwrap.dedent("""\
        def beta_main():
            pass
    """))

    # Package gamma: empty (GAP) — only __init__.py
    gamma = src / "gamma"
    gamma.mkdir(parents=True)
    (gamma / "__init__.py").write_text("")

    # Tests for alpha only
    tests_dir = tmp_path / "tests" / "alpha"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_engine.py").write_text("def test_alpha(): pass\n")

    # Entry points — __main__.py inside the top-level namespace package
    (src / "__main__.py").write_text("print('hello')\n")

    # Scripts directory
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run_pipeline.py").write_text("#!/usr/bin/env python\n")

    return tmp_path


@pytest.fixture
def sample_repo_no_src(tmp_path):
    """Create a repo without src/ layout — packages at root."""
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('__all__ = ["Thing"]\n')
    (pkg / "thing.py").write_text("class Thing:\n    pass\n")
    return tmp_path


class TestPackageDiscovery:
    """Test that discover_packages finds all top-level packages."""

    def test_discovers_packages_under_src(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        names = {p["name"] for p in packages}
        assert "alpha" in names
        assert "beta" in names
        assert "gamma" in names

    def test_discovers_packages_without_src(self, sample_repo_no_src):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo_no_src)
        names = {p["name"] for p in packages}
        assert "mypkg" in names

    def test_package_has_required_keys(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        required_keys = {"name", "path", "py_files", "classes", "functions", "has_all", "has_tests"}
        for pkg in packages:
            assert required_keys.issubset(pkg.keys()), f"Package {pkg.get('name')} missing keys"


class TestCounting:
    """Test class and function counting logic."""

    def test_count_classes(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        assert alpha["classes"] == 2  # AlphaEngine, AlphaHelper

    def test_count_functions(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # run_alpha + helper_one + helper_two + run (method) = 4 top-level defs
        # BUT spec says "^def " so methods indented won't match
        # engine.py: run_alpha (top-level def) -> 1
        # utils.py: helper_one, helper_two -> 2
        # __init__.py: 0
        # Total top-level: 3
        assert alpha["functions"] == 3

    def test_count_functions_beta(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        beta = next(p for p in packages if p["name"] == "beta")
        assert beta["functions"] == 1  # beta_main
        assert beta["classes"] == 0

    def test_empty_package_counts(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        gamma = next(p for p in packages if p["name"] == "gamma")
        assert gamma["classes"] == 0
        assert gamma["functions"] == 0


class TestExportsAndTests:
    """Test __all__ detection and test directory matching."""

    def test_has_all_true(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        assert alpha["has_all"] is True

    def test_has_all_false(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        beta = next(p for p in packages if p["name"] == "beta")
        assert beta["has_all"] is False

    def test_has_tests_true(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        assert alpha["has_tests"] is True

    def test_has_tests_false(self, sample_repo):
        from repo_architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        beta = next(p for p in packages if p["name"] == "beta")
        assert beta["has_tests"] is False


class TestMarkdownOutput:
    """Test the generated markdown report format."""

    def test_markdown_contains_table(self, sample_repo):
        from repo_architecture_scanner import generate_markdown

        packages = [
            {"name": "alpha", "path": "/x/alpha", "py_files": 3, "classes": 2,
             "functions": 3, "has_all": True, "has_tests": True},
        ]
        md = generate_markdown("testrepo", packages, [], [])
        assert "| Package" in md
        assert "| alpha" in md

    def test_markdown_contains_mermaid(self, sample_repo):
        from repo_architecture_scanner import generate_markdown

        packages = [
            {"name": "alpha", "path": "/x/alpha", "py_files": 3, "classes": 2,
             "functions": 3, "has_all": True, "has_tests": True},
        ]
        md = generate_markdown("testrepo", packages, [], [])
        assert "```mermaid" in md
        assert "graph" in md

    def test_markdown_contains_top10(self, sample_repo):
        from repo_architecture_scanner import generate_markdown

        # Create 12 packages to verify top-10 listing
        packages = [
            {"name": f"pkg{i:02d}", "path": f"/x/pkg{i:02d}", "py_files": 20 - i,
             "classes": i, "functions": i * 2, "has_all": False, "has_tests": False}
            for i in range(12)
        ]
        md = generate_markdown("testrepo", packages, [], [])
        assert "Top 10" in md or "top 10" in md.lower() or "Largest" in md

    def test_markdown_contains_entry_points(self, sample_repo):
        from repo_architecture_scanner import generate_markdown

        packages = []
        entry_points = ["/repo/__main__.py", "/repo/scripts/run.py"]
        md = generate_markdown("testrepo", packages, entry_points, [])
        assert "__main__.py" in md
        assert "run.py" in md


class TestEntryPointDiscovery:
    """Test finding __main__.py, scripts/, CLI commands."""

    def test_finds_main_py(self, sample_repo):
        from repo_architecture_scanner import find_entry_points

        entry_points = find_entry_points(sample_repo)
        main_files = [e for e in entry_points if "__main__.py" in e]
        assert len(main_files) >= 1

    def test_finds_scripts(self, sample_repo):
        from repo_architecture_scanner import find_entry_points

        entry_points = find_entry_points(sample_repo)
        script_files = [e for e in entry_points if "scripts" in e.lower() or "run_pipeline" in e]
        assert len(script_files) >= 1
