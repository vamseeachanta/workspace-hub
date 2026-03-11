"""Unit tests for scripts/quality/api-audit.py (WRK-1059)."""

import ast
import importlib.util
import tempfile
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[2] / "scripts" / "quality" / "api-audit.py"
_spec = importlib.util.spec_from_file_location("api_audit", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
audit_path = _mod.audit_path
collect_symbols = _mod.collect_symbols
has_docstring = _mod.has_docstring


# ---------------------------------------------------------------------------
# has_docstring
# ---------------------------------------------------------------------------

def test_has_docstring_present():
    src = 'def f():\n    """Docstring."""\n    pass\n'
    node = ast.parse(src).body[0]
    assert has_docstring(node) is True


def test_has_docstring_absent():
    src = "def f():\n    pass\n"
    node = ast.parse(src).body[0]
    assert has_docstring(node) is False


def test_has_docstring_comment_not_counted():
    src = "def f():\n    # not a docstring\n    pass\n"
    node = ast.parse(src).body[0]
    assert has_docstring(node) is False


# ---------------------------------------------------------------------------
# collect_symbols — scope contract
# ---------------------------------------------------------------------------

def test_collect_symbols_module_level_only():
    src = "def pub(): pass\ndef _priv(): pass\n"
    tree = ast.parse(src)
    names = [n for n, _ in collect_symbols(tree)]
    assert "pub" in names
    assert "_priv" not in names


def test_collect_symbols_excludes_nested_functions():
    """Nested inner functions must NOT inflate coverage count."""
    src = (
        "def outer():\n"
        "    def inner(): pass\n"
        "    pass\n"
    )
    tree = ast.parse(src)
    names = [n for n, _ in collect_symbols(tree)]
    assert "outer" in names
    assert "inner" not in names


def test_collect_symbols_class_methods_included():
    src = (
        "class MyClass:\n"
        "    def public_method(self): pass\n"
        "    def _private(self): pass\n"
    )
    tree = ast.parse(src)
    names = [n for n, _ in collect_symbols(tree)]
    assert "MyClass" in names
    assert "public_method" in names
    assert "_private" not in names


def test_collect_symbols_async_function():
    src = "async def fetch(): pass\n"
    tree = ast.parse(src)
    names = [n for n, _ in collect_symbols(tree)]
    assert "fetch" in names


def test_collect_symbols_empty_module():
    tree = ast.parse("")
    assert collect_symbols(tree) == []


# ---------------------------------------------------------------------------
# audit_path — file handling
# ---------------------------------------------------------------------------

def test_audit_path_counts_correctly():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "a.py").write_text('def foo():\n    """Doc."""\n    pass\n')
        (p / "b.py").write_text("def bar(): pass\n")
        total, with_doc = audit_path(p)
    assert total == 2
    assert with_doc == 1


def test_audit_path_skips_syntax_error():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "bad.py").write_text("def (broken syntax")
        (p / "good.py").write_text('def ok():\n    """Doc."""\n    pass\n')
        total, with_doc = audit_path(p)
    assert total == 1
    assert with_doc == 1


def test_audit_path_skips_non_utf8():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "binary.py").write_bytes(b"\xff\xfe invalid utf-8 \x80")
        (p / "ok.py").write_text("def foo(): pass\n")
        total, with_doc = audit_path(p)
    assert total == 1
    assert with_doc == 0


def test_audit_path_zero_symbols():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "empty.py").write_text("# just a comment\n")
        total, with_doc = audit_path(p)
    assert total == 0
    assert with_doc == 0
