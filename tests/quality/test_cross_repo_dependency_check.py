"""Tests for cross-repo dependency verification script.

Run with:
    uv run pytest tests/quality/test_cross_repo_dependency_check.py -v
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

# Import the module under test
sys_path_entry = str(Path(__file__).resolve().parent.parent.parent / "scripts" / "quality")
import sys

sys.path.insert(0, sys_path_entry)
import importlib

cross_repo = importlib.import_module("cross-repo-dependency-check")


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace with fake tier-1 repos."""
    # Create digitalmodel with src layout
    dm = tmp_path / "digitalmodel"
    dm_src = dm / "src" / "digitalmodel"
    dm_src.mkdir(parents=True)
    (dm_src / "__init__.py").write_text("# digitalmodel\n")
    (dm_src / "core.py").write_text(
        textwrap.dedent("""\
        import assetutilities
        from assetutilities.common import utils
        import os
        """)
    )
    (dm / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "digitalmodel"
        version = "0.1.0"
        dependencies = [
            "assetutilities>=0.0.7",
            "click>=8.0",
        ]
        """)
    )

    # Create assetutilities
    au = tmp_path / "assetutilities"
    au_src = au / "src" / "assetutilities"
    au_src.mkdir(parents=True)
    (au_src / "__init__.py").write_text("# assetutilities\n")
    (au_src / "common.py").write_text("import os\n")
    (au / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "assetutilities"
        version = "0.1.0"
        dependencies = [
            "pyyaml>=6.0",
        ]
        """)
    )

    # Create assethold with undeclared dep on digitalmodel
    ah = tmp_path / "assethold"
    ah_src = ah / "src" / "assethold"
    ah_src.mkdir(parents=True)
    (ah_src / "__init__.py").write_text("# assethold\n")
    (ah_src / "analysis.py").write_text(
        textwrap.dedent("""\
        import digitalmodel
        from assetutilities import common
        """)
    )
    (ah / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "assethold"
        version = "0.1.0"
        dependencies = [
            "assetutilities",
        ]
        """)
    )

    # achantas-data: exists but no cross-repo imports
    ad = tmp_path / "achantas-data"
    ad_src = ad / "src" / "achantas_data"
    ad_src.mkdir(parents=True)
    (ad_src / "__init__.py").write_text("# achantas_data\n")
    (ad / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "achantas-data"
        version = "0.1.0"
        dependencies = [
            "pyyaml>=6.0",
        ]
        """)
    )

    # aceengineer-strategy: exists but NO pyproject.toml
    aes = tmp_path / "aceengineer-strategy"
    aes.mkdir()
    (aes / "README.md").write_text("# Strategy\n")

    return tmp_path


@pytest.fixture
def circular_workspace(tmp_path: Path) -> Path:
    """Workspace with circular dependencies: A->B->A."""
    repo_a = tmp_path / "digitalmodel"
    repo_a_src = repo_a / "src" / "digitalmodel"
    repo_a_src.mkdir(parents=True)
    (repo_a_src / "__init__.py").write_text("import assetutilities\n")
    (repo_a / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "digitalmodel"
        version = "0.1.0"
        dependencies = ["assetutilities"]
        """)
    )

    repo_b = tmp_path / "assetutilities"
    repo_b_src = repo_b / "src" / "assetutilities"
    repo_b_src.mkdir(parents=True)
    (repo_b_src / "__init__.py").write_text("import digitalmodel\n")
    (repo_b / "pyproject.toml").write_text(
        textwrap.dedent("""\
        [project]
        name = "assetutilities"
        version = "0.1.0"
        dependencies = ["digitalmodel"]
        """)
    )

    return tmp_path


# ── Tests ───────────────────────────────────────────────────────────────────


class TestExtractImportsFromFile:
    """Test the AST-based import extraction."""

    def test_simple_import(self, tmp_path: Path) -> None:
        """Test extracting a simple import statement."""
        f = tmp_path / "test.py"
        f.write_text("import os\nimport sys\n")
        imports = cross_repo.extract_imports_from_file(f)
        modules = [i["module"] for i in imports]
        assert "os" in modules
        assert "sys" in modules

    def test_from_import(self, tmp_path: Path) -> None:
        """Test extracting from...import statements."""
        f = tmp_path / "test.py"
        f.write_text("from pathlib import Path\nfrom os.path import join\n")
        imports = cross_repo.extract_imports_from_file(f)
        modules = [i["module"] for i in imports]
        assert "pathlib" in modules
        assert "os.path" in modules
        assert all(i["kind"] == "from" for i in imports)

    def test_syntax_error_file(self, tmp_path: Path) -> None:
        """Test that files with syntax errors return empty list."""
        f = tmp_path / "bad.py"
        f.write_text("def broken(\n")
        imports = cross_repo.extract_imports_from_file(f)
        assert imports == []

    def test_line_numbers(self, tmp_path: Path) -> None:
        """Test that line numbers are correctly captured."""
        f = tmp_path / "test.py"
        f.write_text("# comment\nimport os\nimport sys\n")
        imports = cross_repo.extract_imports_from_file(f)
        assert imports[0]["line"] == 2
        assert imports[1]["line"] == 3


class TestGetTopLevelModule:
    """Test module name extraction."""

    def test_simple(self) -> None:
        assert cross_repo.get_top_level_module("os") == "os"

    def test_dotted(self) -> None:
        assert cross_repo.get_top_level_module("assetutilities.common.utils") == "assetutilities"


class TestNormalizeDeps:
    """Test dependency string normalization."""

    def test_plain_name(self) -> None:
        assert cross_repo.normalize_dep_name("assetutilities") == "assetutilities"

    def test_with_version(self) -> None:
        assert cross_repo.normalize_dep_name("assetutilities>=0.0.7") == "assetutilities"

    def test_with_extras(self) -> None:
        assert cross_repo.normalize_dep_name("package[dev]>=1.0") == "package"

    def test_hyphen_underscore(self) -> None:
        assert cross_repo.normalize_dep_name("achantas-data>=1.0") == "achantas_data"

    def test_with_env_marker(self) -> None:
        assert cross_repo.normalize_dep_name(
            "excel2img; sys_platform=='win32'"
        ) == "excel2img"


class TestFindTier1InDeps:
    """Test finding tier-1 repos in dependency lists."""

    def test_finds_assetutilities(self) -> None:
        deps = ["assetutilities>=0.0.7", "click>=8.0", "pyyaml"]
        found = cross_repo.find_tier1_in_deps(deps, cross_repo.IMPORT_NAME_TO_REPO)
        assert "assetutilities" in found
        assert len(found) == 1

    def test_finds_multiple(self) -> None:
        deps = ["assetutilities", "digitalmodel>=0.1.0"]
        found = cross_repo.find_tier1_in_deps(deps, cross_repo.IMPORT_NAME_TO_REPO)
        assert set(found) == {"assetutilities", "digitalmodel"}

    def test_no_tier1(self) -> None:
        deps = ["click>=8.0", "pyyaml", "requests"]
        found = cross_repo.find_tier1_in_deps(deps, cross_repo.IMPORT_NAME_TO_REPO)
        assert found == []


class TestFindCycles:
    """Test cycle detection."""

    def test_no_cycles(self) -> None:
        graph: dict[str, set[str]] = {
            "a": {"b"},
            "b": {"c"},
            "c": set(),
        }
        cycles = cross_repo.find_cycles(graph)
        assert cycles == []

    def test_simple_cycle(self) -> None:
        graph: dict[str, set[str]] = {
            "a": {"b"},
            "b": {"a"},
        }
        cycles = cross_repo.find_cycles(graph)
        assert len(cycles) >= 1
        # At least one cycle should contain both a and b
        all_nodes = set()
        for c in cycles:
            all_nodes.update(c)
        assert "a" in all_nodes
        assert "b" in all_nodes

    def test_triangle_cycle(self) -> None:
        graph: dict[str, set[str]] = {
            "a": {"b"},
            "b": {"c"},
            "c": {"a"},
        }
        cycles = cross_repo.find_cycles(graph)
        assert len(cycles) >= 1

    def test_empty_graph(self) -> None:
        cycles = cross_repo.find_cycles({})
        assert cycles == []


class TestParseProjectToml:
    """Test pyproject.toml parsing."""

    def test_valid_toml(self, tmp_path: Path) -> None:
        f = tmp_path / "pyproject.toml"
        f.write_text(
            textwrap.dedent("""\
            [project]
            name = "mypackage"
            version = "1.0"
            dependencies = ["requests>=2.0", "click"]
            """)
        )
        name, deps = cross_repo.parse_pyproject_deps(f)
        assert name == "mypackage"
        assert "requests>=2.0" in deps
        assert "click" in deps

    def test_missing_file(self, tmp_path: Path) -> None:
        name, deps = cross_repo.parse_pyproject_deps(tmp_path / "nonexistent.toml")
        assert name == ""
        assert deps == []

    def test_no_dependencies_key(self, tmp_path: Path) -> None:
        f = tmp_path / "pyproject.toml"
        f.write_text(
            textwrap.dedent("""\
            [project]
            name = "mypackage"
            version = "1.0"
            """)
        )
        name, deps = cross_repo.parse_pyproject_deps(f)
        assert name == "mypackage"
        assert deps == []

    def test_merge_conflict_markers(self, tmp_path: Path) -> None:
        """Test that git merge conflict markers are handled."""
        f = tmp_path / "pyproject.toml"
        f.write_text(
            textwrap.dedent("""\
            <<<<<<< Updated upstream
            [project]
            name = "mypackage"
            version = "1.0"
            dependencies = ["requests"]
            =======
            [project]
            name = "mypackage"
            version = "2.0"
            dependencies = ["requests", "click"]
            >>>>>>> Stashed changes
            """)
        )
        # Should not crash — handles conflict markers gracefully
        name, deps = cross_repo.parse_pyproject_deps(f)
        # May parse one side or fail gracefully
        # The important thing is no exception


class TestAnalyzeWorkspace:
    """Integration tests with full workspace analysis."""

    def test_detects_undeclared_dependency(self, tmp_workspace: Path) -> None:
        """assethold imports digitalmodel but doesn't declare it."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        undeclared = [v for v in violations if v.kind == "undeclared"]
        # assethold imports digitalmodel but only declares assetutilities
        undeclared_pairs = [(v.source_repo, v.target_repo) for v in undeclared]
        assert ("assethold", "digitalmodel") in undeclared_pairs

    def test_declared_dependency_no_violation(self, tmp_workspace: Path) -> None:
        """digitalmodel imports assetutilities and declares it — no violation."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        undeclared = [v for v in violations if v.kind == "undeclared"]
        undeclared_pairs = [(v.source_repo, v.target_repo) for v in undeclared]
        assert ("digitalmodel", "assetutilities") not in undeclared_pairs

    def test_missing_repo_skipped(self, tmp_workspace: Path) -> None:
        """Repos not present on disk should be marked as not existing."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        # aceengineer-strategy exists but has no pyproject
        assert repos["aceengineer-strategy"].exists is True
        assert repos["aceengineer-strategy"].has_pyproject is False

    def test_import_graph_built(self, tmp_workspace: Path) -> None:
        """The import graph should have edges for cross-repo imports."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        assert "assetutilities" in repos["digitalmodel"].imported_tier1_deps
        assert "digitalmodel" in repos["assethold"].imported_tier1_deps

    def test_circular_detection(self, circular_workspace: Path) -> None:
        """Should detect circular dependency between digitalmodel and assetutilities."""
        repos, violations, cycles = cross_repo.analyze_workspace(circular_workspace)
        assert len(cycles) >= 1
        circular_violations = [v for v in violations if v.kind == "circular"]
        assert len(circular_violations) >= 1

    def test_python_file_count(self, tmp_workspace: Path) -> None:
        """Should count Python files in each repo."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        # digitalmodel has __init__.py and core.py
        assert repos["digitalmodel"].python_file_count >= 2


class TestOutputGeneration:
    """Test Mermaid and report generation."""

    def test_mermaid_output(self, tmp_workspace: Path) -> None:
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        mermaid = cross_repo.generate_mermaid(repos)
        assert "graph LR" in mermaid
        assert "digitalmodel" in mermaid

    def test_json_report_structure(self, tmp_workspace: Path) -> None:
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        report = cross_repo.generate_report(repos, violations, cycles)
        assert "schema_version" in report
        assert "repos" in report
        assert "violations" in report
        assert "stats" in report
        assert report["stats"]["repos_scanned"] >= 1

    def test_report_json_serializable(self, tmp_workspace: Path) -> None:
        """The report should be JSON-serializable."""
        repos, violations, cycles = cross_repo.analyze_workspace(tmp_workspace)
        report = cross_repo.generate_report(repos, violations, cycles)
        json_str = json.dumps(report, default=str)
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == "1.0"


class TestMainFunction:
    """Test the CLI entry point."""

    def test_main_returns_nonzero_on_violations(self, tmp_workspace: Path) -> None:
        """main() should return 1 when violations are found."""
        ret = cross_repo.main(
            ["--workspace", str(tmp_workspace), "--output-dir", str(tmp_workspace / "out")]
        )
        assert ret == 1  # undeclared dep in assethold

    def test_main_writes_output_files(self, tmp_workspace: Path) -> None:
        """main() should write mermaid and json files."""
        out_dir = tmp_workspace / "output"
        cross_repo.main(
            ["--workspace", str(tmp_workspace), "--output-dir", str(out_dir)]
        )
        assert (out_dir / "dependency-graph.mermaid").exists()
        assert (out_dir / "dependency-report.json").exists()

    def test_main_json_only(self, tmp_workspace: Path, capsys) -> None:
        """--json-only should output JSON to stdout."""
        out_dir = tmp_workspace / "output"
        cross_repo.main(
            [
                "--workspace", str(tmp_workspace),
                "--output-dir", str(out_dir),
                "--json-only",
            ]
        )
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "repos" in data

    def test_main_nonexistent_workspace(self) -> None:
        """main() should return 1 for non-existent workspace."""
        ret = cross_repo.main(["--workspace", "/nonexistent/path"])
        assert ret == 1
