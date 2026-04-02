"""Tests for architecture-scanner.py — TDD: written before implementation.

Tests cover:
  - Package discovery from a repo with src/ layout
  - Per-package metrics: modules, classes, functions, LOC
  - Public API surface detection (non-_ prefixed)
  - Import dependency graph between packages
  - YAML report output
  - Markdown output with dependency mermaid graph
  - End-to-end scan_repo pipeline
"""

import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# Import the module (hyphenated filename requires importlib)
import importlib.util

_script_path = Path(__file__).resolve().parents[2] / "scripts" / "analysis" / "architecture-scanner.py"
_spec = importlib.util.spec_from_file_location("architecture_scanner", _script_path)
architecture_scanner = importlib.util.module_from_spec(_spec)
sys.modules["architecture_scanner"] = architecture_scanner
_spec.loader.exec_module(architecture_scanner)


@pytest.fixture
def sample_repo(tmp_path):
    """Create a minimal repo structure with src/ layout for testing."""
    src = tmp_path / "src" / "mypackage"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("")

    # Package alpha: 3 files, 2 public classes, 1 private class,
    # 3 public functions, 1 private function
    alpha = src / "alpha"
    alpha.mkdir(parents=True)
    (alpha / "__init__.py").write_text('__all__ = ["AlphaEngine", "run_alpha"]\n')
    (alpha / "engine.py").write_text(textwrap.dedent("""\
        \"\"\"Alpha engine module.\"\"\"

        from mypackage.beta import beta_main

        class AlphaEngine:
            def run(self):
                pass

        class _AlphaInternal:
            pass

        class AlphaHelper:
            pass

        def run_alpha():
            pass

        def _private_helper():
            pass
    """))
    (alpha / "utils.py").write_text(textwrap.dedent("""\
        from mypackage.gamma import something

        def helper_one():
            pass

        def helper_two():
            pass
    """))

    # Package beta: 2 files, 0 classes, 1 function, imports alpha
    beta = src / "beta"
    beta.mkdir(parents=True)
    (beta / "__init__.py").write_text("")
    (beta / "core.py").write_text(textwrap.dedent("""\
        from mypackage.alpha.engine import AlphaEngine

        def beta_main():
            pass
    """))

    # Package gamma: only __init__.py (empty/stub package)
    gamma = src / "gamma"
    gamma.mkdir(parents=True)
    (gamma / "__init__.py").write_text("something = 42\n")

    # Package delta: imports external only (no inter-package deps)
    delta = src / "delta"
    delta.mkdir(parents=True)
    (delta / "__init__.py").write_text("")
    (delta / "main.py").write_text(textwrap.dedent("""\
        import os
        import json
        from pathlib import Path

        def delta_func():
            pass
    """))

    # Tests for alpha only
    tests_dir = tmp_path / "tests" / "alpha"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_engine.py").write_text("def test_alpha(): pass\n")

    return tmp_path


# ── Package discovery ──


class TestPackageDiscovery:
    """Test that discover_packages finds all top-level packages."""

    def test_discovers_all_packages(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        names = {p["name"] for p in packages}
        assert names == {"alpha", "beta", "gamma", "delta"}

    def test_package_has_required_keys(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        required_keys = {
            "name", "path", "modules", "classes", "functions",
            "loc", "public_classes", "public_functions",
            "has_all", "has_tests",
        }
        for pkg in packages:
            assert required_keys.issubset(pkg.keys()), (
                f"Package {pkg.get('name')} missing keys: "
                f"{required_keys - set(pkg.keys())}"
            )


# ── Per-package metrics ──


class TestMetrics:
    """Test counting: modules, classes, functions, LOC."""

    def test_module_count(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # __init__.py, engine.py, utils.py
        assert alpha["modules"] == 3

    def test_class_count_includes_all(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # AlphaEngine, _AlphaInternal, AlphaHelper
        assert alpha["classes"] == 3

    def test_function_count_top_level_only(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # run_alpha, _private_helper, helper_one, helper_two
        assert alpha["functions"] == 4

    def test_loc_positive(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        assert alpha["loc"] > 0

    def test_empty_package_metrics(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        gamma = next(p for p in packages if p["name"] == "gamma")
        assert gamma["modules"] == 1  # just __init__.py
        assert gamma["classes"] == 0
        assert gamma["functions"] == 0


# ── Public API surface ──


class TestPublicAPISurface:
    """Test detection of public (non-_ prefixed) classes and functions."""

    def test_public_classes(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # AlphaEngine, AlphaHelper (NOT _AlphaInternal)
        assert set(alpha["public_classes"]) == {"AlphaEngine", "AlphaHelper"}

    def test_public_functions(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        alpha = next(p for p in packages if p["name"] == "alpha")
        # run_alpha, helper_one, helper_two (NOT _private_helper)
        assert set(alpha["public_functions"]) == {
            "run_alpha", "helper_one", "helper_two"
        }

    def test_no_public_api_gamma(self, sample_repo):
        from architecture_scanner import discover_packages

        packages = discover_packages(sample_repo)
        gamma = next(p for p in packages if p["name"] == "gamma")
        assert gamma["public_classes"] == []
        assert gamma["public_functions"] == []


# ── Import dependency graph ──


class TestImportDependencyGraph:
    """Test building of inter-package import dependency graph."""

    def test_build_dependency_graph(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        # graph is dict[str, set[str]] — source -> targets

        # alpha imports beta and gamma
        assert "beta" in graph.get("alpha", set())
        assert "gamma" in graph.get("alpha", set())

        # beta imports alpha
        assert "alpha" in graph.get("beta", set())

    def test_no_external_deps_in_graph(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        # delta imports only stdlib — should have empty or no entry
        assert len(graph.get("delta", set())) == 0

    def test_graph_keys_are_package_names(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph

        packages = discover_packages(sample_repo)
        pkg_names = {p["name"] for p in packages}
        graph = build_dependency_graph(sample_repo, packages)
        for source, targets in graph.items():
            assert source in pkg_names
            for t in targets:
                assert t in pkg_names


# ── YAML output ──


class TestYAMLOutput:
    """Test structured YAML report generation."""

    def test_yaml_output_valid(self, sample_repo):
        import yaml
        from architecture_scanner import discover_packages, build_dependency_graph, generate_yaml_report

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        yaml_str = generate_yaml_report(packages, graph)

        data = yaml.safe_load(yaml_str)
        assert "packages" in data
        assert "dependency_graph" in data
        assert "summary" in data

    def test_yaml_has_all_packages(self, sample_repo):
        import yaml
        from architecture_scanner import discover_packages, build_dependency_graph, generate_yaml_report

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        yaml_str = generate_yaml_report(packages, graph)

        data = yaml.safe_load(yaml_str)
        names = {p["name"] for p in data["packages"]}
        assert names == {"alpha", "beta", "gamma", "delta"}


# ── Markdown output ──


class TestMarkdownOutput:
    """Test generated markdown with API surface table and dependency graph."""

    def test_markdown_has_package_table(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph, generate_markdown

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        md = generate_markdown("testrepo", packages, graph)

        assert "| Package" in md
        assert "| alpha" in md
        assert "LOC" in md or "Lines" in md

    def test_markdown_has_dependency_mermaid(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph, generate_markdown

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        md = generate_markdown("testrepo", packages, graph)

        assert "```mermaid" in md
        assert "-->" in md  # dependency edges

    def test_markdown_has_public_api_section(self, sample_repo):
        from architecture_scanner import discover_packages, build_dependency_graph, generate_markdown

        packages = discover_packages(sample_repo)
        graph = build_dependency_graph(sample_repo, packages)
        md = generate_markdown("testrepo", packages, graph)

        assert "API" in md or "api" in md.lower() or "Public" in md


# ── End-to-end ──


class TestEndToEnd:
    """Test the full scan_repo pipeline."""

    def test_scan_repo_produces_files(self, sample_repo, tmp_path):
        from architecture_scanner import scan_repo

        output_dir = tmp_path / "output"
        scan_repo(sample_repo, output_dir)

        md_file = output_dir / "api-surface-map.md"
        yaml_file = output_dir / "api-surface-map.yaml"

        assert md_file.exists()
        assert yaml_file.exists()
        assert md_file.read_text().startswith("# ")
