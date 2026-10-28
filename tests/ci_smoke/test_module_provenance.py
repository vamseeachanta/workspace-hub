"""Loaded-module provenance for source imports and a synthetic installed layout.

The real smoke exercises the resolver from src. The external environment is
synthetic: no wheel is built or installed. Lazy modules are inspected only after
import. Namespace packages have no concrete file to check (PEP 420).
"""
from __future__ import annotations

import importlib
import sys
import sysconfig
from pathlib import Path
from types import ModuleType

import pytest

SRC_ROOT = Path(__file__).resolve().parent.parent.parent / "src"
EXAMPLE = "provenance_example"


def _assert_module_provenance(prefix: str, expected_root: Path) -> dict[str, Path]:
    """Inspect already-loaded modules without importing or clearing the namespace."""
    root = expected_root.resolve()
    resolved = {}
    violations = {}
    for name, module in sorted(sys.modules.copy().items()):
        if name != prefix and not name.startswith(prefix + "."):
            continue
        file = getattr(module, "__file__", None)
        if file is None:
            spec = getattr(module, "__spec__", None)
            if (
                spec is not None
                and spec.origin is None
                and spec.submodule_search_locations is not None
            ):
                continue  # PEP 420 namespace packages have no concrete file.
            violations[name] = "no file and not a namespace package"
            continue
        path = Path(file).resolve()
        resolved[name] = path
        if not path.is_relative_to(root):
            violations[name] = str(path)

    assert not violations, (
        f"Module provenance outside expected root {root}:\n"
        + "\n".join(f"  {name}: {reason}" for name, reason in violations.items())
    )
    assert resolved, f"No concrete modules loaded for {prefix}"
    return resolved


def _inject_module(monkeypatch, name, path):
    module = ModuleType(name)
    if path is not None:
        module.__file__ = str(path)
    monkeypatch.setitem(sys.modules, name, module)
    return module


@pytest.fixture
def load_example(monkeypatch):
    """Import real fixture files, then restore only this synthetic namespace."""
    previous = {
        name: module for name, module in sys.modules.copy().items()
        if name == EXAMPLE or name.startswith(EXAMPLE + ".")
    }
    for name in previous:
        monkeypatch.delitem(sys.modules, name)

    def load(root, *, namespace=True):
        package = root / EXAMPLE
        package.mkdir(parents=True)
        (package / "entry.py").write_text("from . import nested\n", encoding="utf-8")
        (package / "nested.py").write_text("VALUE = 'loaded'\n", encoding="utf-8")
        (package / "lazy.py").write_text("VALUE = 'lazy'\n", encoding="utf-8")
        if not namespace:
            (package / "__init__.py").write_text("", encoding="utf-8")
        monkeypatch.syspath_prepend(str(root))
        importlib.import_module(EXAMPLE + ".entry")
        expected = {
            EXAMPLE + ".entry": (package / "entry.py").resolve(),
            EXAMPLE + ".nested": (package / "nested.py").resolve(),
        }
        if not namespace:
            expected[EXAMPLE] = (package / "__init__.py").resolve()
        return expected

    yield load

    for name in list(sys.modules):
        if name == EXAMPLE or name.startswith(EXAMPLE + "."):
            del sys.modules[name]
    sys.modules.update(previous)


def test_all_loaded_project_modules_have_expected_provenance():
    """Real coverage is limited to modules loaded by the source resolver smoke."""
    resolver = importlib.import_module("workspace_hub.workstations.resolver")
    assert resolver.WorkstationPathResolver is not None
    resolved = _assert_module_provenance("workspace_hub", SRC_ROOT)
    expected = {
        "workspace_hub.workstations":
            (SRC_ROOT / "workspace_hub/workstations/__init__.py").resolve(),
        "workspace_hub.workstations.resolver":
            (SRC_ROOT / "workspace_hub/workstations/resolver.py").resolve(),
    }
    assert resolved.items() >= expected.items()


def test_outside_submodule_is_rejected(tmp_path, monkeypatch):
    importlib.import_module("workspace_hub.workstations.resolver")
    outside = tmp_path / "outside.py"
    outside.write_text("", encoding="utf-8")
    name = "workspace_hub.outside"
    injected = _inject_module(monkeypatch, name, outside)
    with pytest.raises(AssertionError, match=r"workspace_hub\.outside") as failure:
        _assert_module_provenance("workspace_hub", SRC_ROOT)
    assert str(outside.resolve()) in str(failure.value)
    assert sys.modules[name] is injected


def test_namespace_packages_and_all_concrete_modules(tmp_path, load_example):
    expected = load_example(tmp_path / "source")
    namespace = sys.modules[EXAMPLE]
    assert namespace.__spec__.origin is None
    assert namespace.__spec__.submodule_search_locations is not None
    assert getattr(namespace, "__file__", None) is None
    assert _assert_module_provenance(EXAMPLE, tmp_path / "source") == expected
    assert sys.modules[EXAMPLE] is namespace


@pytest.mark.parametrize("suffix", ["_extra", "_extra.plugin"])
def test_sibling_prefix_collision_is_ignored(tmp_path, monkeypatch, load_example, suffix):
    root = tmp_path / "source"
    expected = load_example(root)
    _inject_module(monkeypatch, EXAMPLE + suffix, tmp_path / "outside.py")
    assert _assert_module_provenance(EXAMPLE, root) == expected


def test_prefix_lookalike_is_rejected(tmp_path, monkeypatch, load_example):
    root = tmp_path / "source"
    load_example(root)
    lookalike = tmp_path / "source-extra" / "outside.py"
    lookalike.parent.mkdir()
    lookalike.write_text("", encoding="utf-8")
    _inject_module(monkeypatch, EXAMPLE + ".lookalike", lookalike)
    with pytest.raises(AssertionError, match=r"provenance_example\.lookalike") as failure:
        _assert_module_provenance(EXAMPLE, root)
    assert str(lookalike.resolve()) in str(failure.value)


def test_symlink_escape_is_rejected(tmp_path, monkeypatch, load_example):
    root = tmp_path / "source"
    load_example(root)
    outside = tmp_path / "outside.py"
    outside.write_text("", encoding="utf-8")
    link = root / "escape.py"
    link.symlink_to(outside)
    _inject_module(monkeypatch, EXAMPLE + ".escape", link)
    with pytest.raises(AssertionError, match=r"provenance_example\.escape") as failure:
        _assert_module_provenance(EXAMPLE, root)
    assert str(outside.resolve()) in str(failure.value)


def test_expected_root_is_resolved(tmp_path, load_example):
    root = tmp_path / "source"
    expected = load_example(root)
    alias = tmp_path / "source-link"
    alias.symlink_to(root, target_is_directory=True)
    assert _assert_module_provenance(EXAMPLE, alias) == expected


def test_concrete_module_without_file_is_rejected(tmp_path, monkeypatch, load_example):
    root = tmp_path / "source"
    load_example(root)
    _inject_module(monkeypatch, EXAMPLE + ".missing_file", None)
    with pytest.raises(AssertionError, match=r"provenance_example\.missing_file"):
        _assert_module_provenance(EXAMPLE, root)


def test_concrete_top_level_module_is_rejected(tmp_path, monkeypatch):
    outside = tmp_path / "outside.py"
    outside.write_text("", encoding="utf-8")
    _inject_module(monkeypatch, "provenance_concrete", outside)
    with pytest.raises(AssertionError, match="provenance_concrete") as failure:
        _assert_module_provenance("provenance_concrete", tmp_path / "expected")
    assert str(outside.resolve()) in str(failure.value)


def test_namespace_without_concrete_modules_is_rejected(tmp_path, monkeypatch, load_example):
    root = tmp_path / "source"
    expected = load_example(root)
    for name in expected:
        monkeypatch.delitem(sys.modules, name)
    with pytest.raises(AssertionError, match="No concrete modules"):
        _assert_module_provenance(EXAMPLE, root)


def test_empty_namespace_is_rejected(tmp_path):
    with pytest.raises(AssertionError, match="No concrete modules"):
        _assert_module_provenance("unloaded_provenance_example", tmp_path)


def _external_purelib(tmp_path):
    """Use the running interpreter's install scheme under a temporary prefix."""
    environment = tmp_path / "external-environment"
    root = Path(sysconfig.get_path(
        "purelib", vars={"base": str(environment), "platbase": str(environment)},
    ))
    assert root.is_relative_to(environment)
    assert not root.is_relative_to(SRC_ROOT.resolve())
    return root


@pytest.mark.parametrize("namespace", [True, False], ids=["namespace", "regular"])
def test_synthetic_installed_layout(tmp_path, load_example, namespace):
    root = _external_purelib(tmp_path)
    expected = load_example(root, namespace=namespace)
    assert _assert_module_provenance(EXAMPLE, root) == expected
    assert all(not path.is_relative_to(SRC_ROOT.resolve()) for path in expected.values())
    assert EXAMPLE + ".lazy" not in sys.modules
    importlib.import_module(EXAMPLE + ".lazy")
    expected[EXAMPLE + ".lazy"] = (root / EXAMPLE / "lazy.py").resolve()
    assert _assert_module_provenance(EXAMPLE, root) == expected


def test_synthetic_installed_layout_rejects_editable_checkout(
    tmp_path, monkeypatch, load_example,
):
    root = _external_purelib(tmp_path)
    expected = load_example(root)
    checkout = tmp_path / "editable-checkout"
    package = checkout / EXAMPLE
    package.mkdir(parents=True)
    shadow = package / "shadow.py"
    shadow.write_text("VALUE = 'checkout'\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(checkout))
    assert _assert_module_provenance(EXAMPLE, root) == expected
    imported = importlib.import_module(EXAMPLE + ".shadow")
    assert Path(imported.__file__).resolve() == shadow.resolve()
    with pytest.raises(AssertionError, match=r"provenance_example\.shadow") as failure:
        _assert_module_provenance(EXAMPLE, root)
    assert str(shadow.resolve()) in str(failure.value)
