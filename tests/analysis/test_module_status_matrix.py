"""Tests for module-status-matrix.py — TDD: written before implementation.

Tests cover:
  - Package scanning (discovers top-level packages under src/digitalmodel/)
  - Maturity classification (PRODUCTION, DEVELOPMENT, SKELETON, GAP)
  - Markdown output format (table, summary, gap highlights)
  - JSON output format (structured data)
  - Docstring percentage calculation
  - Top-5 gap highlighting logic

Related: GitHub issue #1570
"""

import json
import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/analysis to path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "analysis"))


@pytest.fixture
def sample_dm_repo(tmp_path):
    """Create a minimal digitalmodel-like repo structure for testing.

    Layout:
        src/digitalmodel/
            production_pkg/   -- >5 test files, >3 source files, >50% docstrings
            development_pkg/  -- source files, 1-5 test files
            skeleton_pkg/     -- source files, 0 test files
            gap_pkg/          -- only __init__.py (empty)
            tiny_pkg/         -- all files <20 lines -> SKELETON
    """
    dm = tmp_path / "src" / "digitalmodel"
    dm.mkdir(parents=True)
    (dm / "__init__.py").write_text('"""digitalmodel root."""\n')

    # --- PRODUCTION package: >5 test files, >3 source files, >50% docstrings ---
    prod = dm / "production_pkg"
    prod.mkdir()
    (prod / "__init__.py").write_text('"""Production package."""\n__all__ = ["Engine"]\n')
    for i in range(5):
        (prod / f"module_{i}.py").write_text(textwrap.dedent(f'''\
            """Module {i} docstring."""

            class Handler{i}:
                """Handler class."""
                def process(self):
                    pass

            def helper_{i}():
                """Helper function."""
                return {i}
        '''))

    # Tests for production_pkg: 6 test files
    tests_dir = tmp_path / "tests" / "production_pkg"
    tests_dir.mkdir(parents=True)
    for i in range(6):
        (tests_dir / f"test_module_{i}.py").write_text(
            f"def test_handler_{i}(): pass\n"
        )

    # --- DEVELOPMENT package: has source, 1-5 test files ---
    dev = dm / "development_pkg"
    dev.mkdir()
    (dev / "__init__.py").write_text('"""Dev package."""\n')
    for i in range(4):
        # Each file needs >20 non-blank lines to avoid tiny-file SKELETON
        filler = "\n".join(f"    attr_{j} = {j}" for j in range(20))
        (dev / f"core_{i}.py").write_text(textwrap.dedent(f'''\
            """Core {i} module with implementation."""

            class Core{i}:
                """Core handler {i}."""
            {filler}

                def process(self):
                    """Process data."""
                    return {i}

                def validate(self):
                    """Validate input."""
                    return True

            def setup_{i}():
                """Setup function."""
                return Core{i}()

            def teardown_{i}():
                """Teardown function."""
                pass
        '''))

    tests_dev = tmp_path / "tests" / "development_pkg"
    tests_dev.mkdir(parents=True)
    for i in range(3):
        (tests_dev / f"test_core_{i}.py").write_text(
            f"def test_core_{i}(): pass\n"
        )

    # --- SKELETON package: source files but 0 tests ---
    skel = dm / "skeleton_pkg"
    skel.mkdir()
    (skel / "__init__.py").write_text("")
    for i in range(3):
        (skel / f"stub_{i}.py").write_text(textwrap.dedent(f'''\
            class Stub{i}:
                pass

            def do_thing_{i}():
                pass
        '''))

    # --- GAP package: only __init__.py ---
    gap = dm / "gap_pkg"
    gap.mkdir()
    (gap / "__init__.py").write_text("")

    # --- TINY package: all files <20 lines -> SKELETON ---
    tiny = dm / "tiny_pkg"
    tiny.mkdir()
    (tiny / "__init__.py").write_text("")
    (tiny / "small.py").write_text("x = 1\n")

    # Tests for tiny_pkg
    tests_tiny = tmp_path / "tests" / "tiny_pkg"
    tests_tiny.mkdir(parents=True)
    (tests_tiny / "test_small.py").write_text("def test_x(): pass\n")

    return tmp_path


class TestPackageScanning:
    """Test that scan_packages discovers all top-level packages."""

    def test_discovers_all_packages(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        names = {p["name"] for p in packages}
        assert "production_pkg" in names
        assert "development_pkg" in names
        assert "skeleton_pkg" in names
        assert "gap_pkg" in names
        assert "tiny_pkg" in names

    def test_package_has_required_keys(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        required_keys = {
            "name", "status", "file_count", "test_count",
            "key_classes", "docstring_pct",
        }
        for pkg in packages:
            assert required_keys.issubset(pkg.keys()), (
                f"Package {pkg.get('name')} missing keys: "
                f"{required_keys - set(pkg.keys())}"
            )

    def test_file_count_accuracy(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        # 5 module files + __init__.py = 6
        assert prod["file_count"] == 6

    def test_test_count_accuracy(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["test_count"] == 6


class TestMaturityClassification:
    """Test the maturity classification logic."""

    def test_production_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["status"] == "PRODUCTION"

    def test_development_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        dev = next(p for p in packages if p["name"] == "development_pkg")
        assert dev["status"] == "DEVELOPMENT"

    def test_skeleton_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        skel = next(p for p in packages if p["name"] == "skeleton_pkg")
        assert skel["status"] == "SKELETON"

    def test_gap_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        gap = next(p for p in packages if p["name"] == "gap_pkg")
        assert gap["status"] == "GAP"

    def test_tiny_files_classified_skeleton(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        tiny = next(p for p in packages if p["name"] == "tiny_pkg")
        # Has tests but all files <20 lines -> SKELETON
        assert tiny["status"] == "SKELETON"


class TestDocstringPercentage:
    """Test docstring detection in source files."""

    def test_production_high_docstring_pct(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        # All 6 files have docstrings -> 100%
        assert prod["docstring_pct"] == 100

    def test_skeleton_zero_docstring_pct(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        skel = next(p for p in packages if p["name"] == "skeleton_pkg")
        # __init__.py is empty (no docstring), stubs have no docstrings
        assert skel["docstring_pct"] == 0


class TestKeyClasses:
    """Test extraction of key class names."""

    def test_key_classes_found(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        # Should find Handler0..Handler4
        assert len(prod["key_classes"]) >= 3

    def test_gap_has_no_classes(self, sample_dm_repo):
        from module_status_matrix import scan_packages

        packages = scan_packages(sample_dm_repo)
        gap = next(p for p in packages if p["name"] == "gap_pkg")
        assert len(gap["key_classes"]) == 0


class TestMarkdownOutput:
    """Test the generated markdown report format."""

    def test_contains_table(self, sample_dm_repo):
        from module_status_matrix import generate_markdown

        packages = [
            {"name": "alpha", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": ["AlphaEngine"], "docstring_pct": 80},
        ]
        md = generate_markdown(packages)
        assert "| Package" in md
        assert "| alpha" in md
        assert "PRODUCTION" in md

    def test_contains_summary(self, sample_dm_repo):
        from module_status_matrix import generate_markdown

        packages = [
            {"name": "a", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": [], "docstring_pct": 80},
            {"name": "b", "status": "DEVELOPMENT", "file_count": 5,
             "test_count": 2, "key_classes": [], "docstring_pct": 40},
            {"name": "c", "status": "SKELETON", "file_count": 3,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
            {"name": "d", "status": "GAP", "file_count": 1,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
        ]
        md = generate_markdown(packages)
        assert "1 PRODUCTION" in md
        assert "1 DEVELOPMENT" in md
        assert "1 SKELETON" in md
        assert "1 GAP" in md

    def test_highlights_top_gaps(self, sample_dm_repo):
        from module_status_matrix import generate_markdown

        packages = [
            {"name": f"gap_{i}", "status": "SKELETON", "file_count": 20 - i,
             "test_count": 0, "key_classes": [], "docstring_pct": 0}
            for i in range(7)
        ]
        md = generate_markdown(packages)
        # Should mention top 5 gaps
        assert "gap_0" in md  # largest
        assert "Top" in md or "gap" in md.lower()


class TestJSONOutput:
    """Test the structured JSON output."""

    def test_json_is_valid(self, sample_dm_repo):
        from module_status_matrix import generate_json_output

        packages = [
            {"name": "alpha", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": ["AlphaEngine"], "docstring_pct": 80},
        ]
        json_str = generate_json_output(packages)
        data = json.loads(json_str)
        assert "packages" in data
        assert "summary" in data
        assert len(data["packages"]) == 1

    def test_json_summary_counts(self, sample_dm_repo):
        from module_status_matrix import generate_json_output

        packages = [
            {"name": "a", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": [], "docstring_pct": 80},
            {"name": "b", "status": "GAP", "file_count": 1,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
        ]
        json_str = generate_json_output(packages)
        data = json.loads(json_str)
        assert data["summary"]["PRODUCTION"] == 1
        assert data["summary"]["GAP"] == 1
