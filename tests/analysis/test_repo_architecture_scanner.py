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

import ast
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
    (src / "__init__.py").write_text("", encoding="utf-8", newline="\n")

    # Package alpha: 3 files, 2 classes, 3 functions, has __all__, has tests
    alpha = src / "alpha"
    alpha.mkdir(parents=True)
    (alpha / "__init__.py").write_text('__all__ = ["AlphaEngine", "run_alpha"]\n', encoding="utf-8", newline="\n")
    (alpha / "engine.py").write_text(textwrap.dedent("""\
        \"\"\"Alpha engine module.\"\"\"

        class AlphaEngine:
            def run(self):
                pass

        class AlphaHelper:
            pass

        def run_alpha():
            pass
    """), encoding="utf-8", newline="\n")
    (alpha / "utils.py").write_text(textwrap.dedent("""\
        def helper_one():
            pass

        def helper_two():
            pass
    """), encoding="utf-8", newline="\n")

    # Package beta: 1 file, 0 classes, 1 function, no __all__, no tests
    beta = src / "beta"
    beta.mkdir(parents=True)
    (beta / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (beta / "core.py").write_text(textwrap.dedent("""\
        def beta_main():
            pass
    """), encoding="utf-8", newline="\n")

    # Package gamma: empty (GAP) — only __init__.py
    gamma = src / "gamma"
    gamma.mkdir(parents=True)
    (gamma / "__init__.py").write_text("", encoding="utf-8", newline="\n")

    # Tests for alpha only
    tests_dir = tmp_path / "tests" / "alpha"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_engine.py").write_text("def test_alpha(): pass\n", encoding="utf-8", newline="\n")

    # Entry points — __main__.py inside the top-level namespace package
    (src / "__main__.py").write_text("print('hello')\n", encoding="utf-8", newline="\n")

    # Scripts directory
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run_pipeline.py").write_text("#!/usr/bin/env python\n", encoding="utf-8", newline="\n")

    return tmp_path


@pytest.fixture
def sample_repo_no_src(tmp_path):
    """Create a repo without src/ layout — packages at root."""
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('__all__ = ["Thing"]\n', encoding="utf-8", newline="\n")
    (pkg / "thing.py").write_text("class Thing:\n    pass\n", encoding="utf-8", newline="\n")
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


# Handwritten expectations below follow the fixture source and Python's import
# statement reference: __all__ names may be defined or imported, including private
# names. The scanner's default is deliberately limited to top-level definitions.
# https://docs.python.org/3/reference/simple_stmts.html#the-import-statement
@pytest.fixture
def api_repo(tmp_path):
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text(textwrap.dedent('''\
        from .definitions import Widget as PublicWidget, _private
        import collections as utilities
        __all__ = ["utilities", "_private", "PublicWidget", "PublicWidget"]
    '''), encoding="utf-8", newline="\n")
    (package / "definitions.py").write_text(textwrap.dedent('''\
        from collections import Counter
        CONSTANT = "not a definition"

        class Widget:
            def method(self):
                pass

        class _Hidden:
            pass

        async def fetch():
            pass

        def build():
            def nested():
                pass

        def _private():
            pass
    '''), encoding="utf-8", newline="\n")
    (package / "empty.py").write_text('__all__ = []\ndef hidden(): pass\n', encoding="utf-8", newline="\n")
    (package / "tuple_exports.py").write_text(
        '__all__: tuple = ("_kept", "Visible")\n'
        'class Visible: pass\ndef _kept(): pass\ndef omitted(): pass\n',
        encoding="utf-8", newline="\n",
    )
    return tmp_path


def api_by_path(repo):
    from repo_architecture_scanner import discover_packages

    package, = discover_packages(repo)
    return {module["path"]: module for module in package["api"]}


def test_literal_exports(api_repo):
    modules = api_by_path(api_repo)
    assert modules["example/__init__.py"] == {
        "path": "example/__init__.py",
        "exports": ["PublicWidget", "_private", "utilities"],
        "status": "literal",
        "reason": None,
    }
    assert modules["example/empty.py"]["exports"] == []
    assert modules["example/empty.py"]["status"] == "literal"
    assert modules["example/tuple_exports.py"]["exports"] == ["Visible", "_kept"]


def test_default_public_definitions(api_repo):
    module = api_by_path(api_repo)["example/definitions.py"]
    assert module == {
        "path": "example/definitions.py",
        "exports": ["Widget", "build", "fetch"],
        "status": "default",
        "reason": None,
    }


@pytest.mark.parametrize("source", [
    '__all__ = make_exports()',
    '__all__ = [name for name in ("Visible",)]',
    '__all__ = ["Visible"] + ["Other"]',
    '__all__ = ["Visible"]\n__all__.append("Other")',
    '__all__ = ["Visible"]\n__all__ += ["Other"]',
    '__all__ = ["Visible"]\n__all__[0] = "Other"',
    '__all__ = ["Visible"]\nexports = __all__\nexports.clear()',
    'if enabled:\n    __all__ = ["Visible"]',
    'from elsewhere import __all__',
    '__all__ = ["Visible"]\ndel __all__',
    '__all__ = ["Visible", None]',
    '__all__ = "Visible"',
    '__all__: list',
    '__all__ = ["Visible"]\nclass Mutator:\n    __all__.append("Other")',
    '__all__ = ["Visible"]\ndef mutate():\n    __all__.append("Other")\nmutate()',
    '__all__ = ["Visible"]\ndef mutate():\n    global __all__\n    __all__ = compute()\nmutate()',
])
def test_dynamic_exports_unresolved(tmp_path, source):
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text(source + '\nclass Visible: pass\n', encoding="utf-8", newline="\n")
    module = api_by_path(tmp_path)["example/__init__.py"]
    assert module["status"] == "unresolved"
    assert module["exports"] is None
    assert module["reason"] == "dynamic __all__"


def test_invalid_source_unresolved(api_repo):
    (api_repo / "example" / "broken.py").write_text('def broken(:\n', encoding="utf-8", newline="\n")
    modules = api_by_path(api_repo)
    assert modules["example/broken.py"] == {
        "path": "example/broken.py",
        "exports": None,
        "status": "unresolved",
        "reason": "syntax error",
    }
    assert modules["example/definitions.py"]["exports"] == ["Widget", "build", "fetch"]


def test_scan_does_not_import(api_repo):
    from repo_architecture_scanner import scan_repo

    sentinel = api_repo / "executed"
    (api_repo / "example" / "sentinel.py").write_text(textwrap.dedent('''\
        from pathlib import Path
        Path(__file__).parents[1].joinpath("executed").write_text("imported", encoding="utf-8", newline="\\n")
        raise RuntimeError("scanned code must not execute")
        __all__ = ["safe"]
        def safe(): pass
    '''), encoding="utf-8", newline="\n")
    report = scan_repo(api_repo)
    assert "`safe`" in report
    assert not sentinel.exists()


def test_api_order_and_report_are_deterministic(api_repo):
    from repo_architecture_scanner import discover_packages, scan_repo

    (api_repo / "example" / "z_dynamic.py").write_text('__all__ = compute()\n', encoding="utf-8", newline="\n")
    first = discover_packages(api_repo)
    assert first == discover_packages(api_repo)
    package, = first
    assert [module["path"] for module in package["api"]] == [
        "example/__init__.py", "example/definitions.py", "example/empty.py",
        "example/tuple_exports.py", "example/z_dynamic.py",
    ]
    report = scan_repo(api_repo)
    assert report == scan_repo(api_repo)
    assert "## Public API" in report
    assert "`PublicWidget`, `_private`, `utilities`" in report
    assert "`Widget`, `build`, `fetch`" in report
    assert "unresolved: dynamic __all__" in report
    assert "No exports" in report


def test_scan_excludes_linked_sources(tmp_path):
    from repo_architecture_scanner import discover_packages, scan_repo

    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "other"
    outside.mkdir()
    (outside / "__init__.py").write_text('class Outside: pass\n', encoding="utf-8", newline="\n")
    package = repo / "example"
    package.mkdir()
    (package / "__init__.py").write_text('class Local: pass\n', encoding="utf-8", newline="\n")
    (package / "linked.py").symlink_to(outside / "__init__.py")
    (repo / "linked").symlink_to(outside, target_is_directory=True)
    packages = discover_packages(repo)
    assert [package["name"] for package in packages] == ["example"]
    assert api_by_path(repo)["example/__init__.py"]["exports"] == ["Local"]
    assert list(api_by_path(repo)) == ["example/__init__.py"]
    assert "Outside" not in scan_repo(repo)


def test_api_paths_under_src(sample_repo):
    from repo_architecture_scanner import discover_packages

    alpha = next(package for package in discover_packages(sample_repo)
                 if package["name"] == "alpha")
    assert [module["path"] for module in alpha["api"]] == [
        "src/mypackage/alpha/__init__.py",
        "src/mypackage/alpha/engine.py",
        "src/mypackage/alpha/utils.py",
    ]
    assert alpha["api"][0]["exports"] == ["AlphaEngine", "run_alpha"]


def test_legacy_counts_are_preserved(api_repo):
    from repo_architecture_scanner import discover_packages

    package, = discover_packages(api_repo)
    # Hand count from api_repo: Widget, _Hidden, Visible are classes;
    # build, _private, hidden, _kept, omitted are synchronous top-level defs.
    # fetch remains excluded from the legacy regex count, but appears in the API.
    assert package["classes"] == 3
    assert package["functions"] == 5


def test_last_literal_assignment_wins(api_repo):
    (api_repo / "example" / "__init__.py").write_text(
        '__all__ = ["old"]\n__all__ = ("current",)\n',
        encoding="utf-8", newline="\n",
    )
    module = api_by_path(api_repo)["example/__init__.py"]
    assert module["status"] == "literal"
    assert module["exports"] == ["current"]


def test_comments_and_nested_bindings_do_not_declare_exports(api_repo):
    (api_repo / "example" / "__init__.py").write_text(textwrap.dedent('''\
        # __all__ = ["not_executed"]
        def visible():
            __all__ = ["local_only"]
        class Container:
            __all__ = ["class_only"]
    '''), encoding="utf-8", newline="\n")
    module = api_by_path(api_repo)["example/__init__.py"]
    assert module["status"] == "default"
    assert module["exports"] == ["Container", "visible"]


def test_unreadable_source_unresolved(api_repo, monkeypatch):
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        if path.name == "definitions.py":
            raise OSError("synthetic read failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    module = api_by_path(api_repo)["example/definitions.py"]
    assert module["status"] == "unresolved"
    assert module["exports"] is None
    assert module["reason"] == "unreadable source"


@pytest.mark.parametrize("git_marker", ["file", "directory"])
def test_nested_checkouts_are_not_scanned(api_repo, git_marker):
    from repo_architecture_scanner import scan_repo

    nested = api_repo / "example" / "other_checkout"
    nested.mkdir()
    marker = nested / ".git"
    if git_marker == "file":
        marker.write_text("synthetic checkout marker", encoding="utf-8", newline="\n")
    else:
        marker.mkdir()
    (nested / "__init__.py").write_text('class Outside: pass\n', encoding="utf-8", newline="\n")
    (nested / "__main__.py").write_text('raise RuntimeError("not executed")\n', encoding="utf-8", newline="\n")
    assert "Outside" not in scan_repo(api_repo)
    assert "other_checkout" not in scan_repo(api_repo)


def test_linked_src_is_not_scanned(api_repo, tmp_path):
    from repo_architecture_scanner import discover_packages

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").symlink_to(api_repo / "example", target_is_directory=True)
    assert discover_packages(repo) == []


@pytest.mark.parametrize("root_name", ["src", "scripts"])
def test_special_roots_do_not_enter_nested_checkouts(tmp_path, root_name):
    from repo_architecture_scanner import discover_packages, scan_repo

    root = tmp_path / root_name
    package = root / "example"
    package.mkdir(parents=True)
    (root / ".git").write_text("synthetic checkout marker", encoding="utf-8", newline="\n")
    (root / "run.py").write_text("raise RuntimeError('not executed')\n", encoding="utf-8", newline="\n")
    (package / "__init__.py").write_text("class Outside: pass\n", encoding="utf-8", newline="\n")
    other = root / "another"
    other.mkdir()
    (other / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    assert discover_packages(tmp_path) == []
    assert "run.py" not in scan_repo(tmp_path)


STRING_BINDINGS = [
    'try:\n    pass\nexcept ValueError as __all__:\n    pass',
    'match value:\n    case __all__:\n        pass',
    'match value:\n    case [*__all__]:\n        pass',
    'match value:\n    case {"key": item, **__all__}:\n        pass',
    'match value:\n    case [item] as __all__:\n        pass',
]


@pytest.mark.parametrize("binding", STRING_BINDINGS)
@pytest.mark.parametrize("prefix", ['', '__all__ = ["Visible"]\n'])
def test_string_export_bindings_unresolved(tmp_path, binding, prefix):
    from repo_architecture_scanner import _public_api

    assert _public_api(prefix + binding, "example.py") == {
        "path": "example.py", "exports": None,
        "status": "unresolved", "reason": "dynamic __all__",
    }


@pytest.mark.parametrize("binding", STRING_BINDINGS)
@pytest.mark.parametrize("scope", ['def local():', 'async def local():', 'class Local:'])
def test_local_string_bindings_preserve_module_exports(binding, scope):
    from repo_architecture_scanner import _public_api

    source = '__all__ = ["Visible"]\n' + scope + '\n' + textwrap.indent(binding, '    ')
    assert _public_api(source, "example.py") == {
        "path": "example.py", "exports": ["Visible"],
        "status": "literal", "reason": None,
    }


@pytest.mark.parametrize("relative", ["src", "scripts", "example", "example/nested"])
def test_directory_junctions_are_excluded(tmp_path, monkeypatch, relative):
    from repo_architecture_scanner import scan_repo

    target = tmp_path / relative
    target.mkdir(parents=True)
    (target / "__init__.py").write_text("class JunctionOnly: pass\n", encoding="utf-8", newline="\n")
    (target / "__main__.py").write_text("", encoding="utf-8", newline="\n")
    if relative == "example/nested":
        (target.parent / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    monkeypatch.setattr(Path, "is_junction", lambda path: path == target, raising=False)
    report = scan_repo(tmp_path)
    assert "JunctionOnly" not in report
    assert relative + "/__main__.py" not in report


def test_text_io_explicit_utf8_and_lf():
    import repo_architecture_scanner as scanner

    for path in (Path(scanner.__file__), Path(__file__)):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        for call in calls:
            if not isinstance(call.func, ast.Attribute):
                continue
            if call.func.attr not in {"read_text", "write_text"}:
                continue
            keywords = {kw.arg: kw.value for kw in call.keywords}
            assert ast.literal_eval(keywords["encoding"]) == "utf-8"
            if call.func.attr == "write_text":
                assert ast.literal_eval(keywords["newline"]) == "\n"


def test_report_written_as_utf8_lf(tmp_path):
    from repo_architecture_scanner import scan_repo

    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text('class Café: pass\n', encoding="utf-8", newline="\n")
    output = tmp_path / "reports"
    report = scan_repo(tmp_path, output)
    payload = (output / (tmp_path.name + "-architecture.md")).read_bytes()
    assert payload == report.encode("utf-8")
    assert b"\r\n" not in payload
    assert "Café" in report
