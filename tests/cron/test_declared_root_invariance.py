"""Declared roots are data, not local filesystem paths.

Policy: issue #3711 requires rendering without filesystem resolution.
Declarations: scripts/cron/cron_render.py::workspace_hub_path/build_context and
scripts/cron/build-cron-identity-inventory.py::_build_machine. The synthetic
schedule comes from tests/cron/test_cron_identity_inventory.py::fixture_paths.
Expected commands are written independently below; inventory expectations are
hand-counted: one Linux target times one selected task gives one unique row,
with no legacy variants, unsupported tasks or collisions.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
from pathlib import Path, PurePosixPath

import pytest
import yaml


@pytest.fixture
def cron_modules(monkeypatch):
    cron_dir = Path(__file__).resolve().parents[2] / "scripts" / "cron"
    monkeypatch.syspath_prepend(str(cron_dir))
    renderer = importlib.import_module("cron_render")
    spec = importlib.util.spec_from_file_location(
        "declared_root_inventory", cron_dir / "build-cron-identity-inventory.py"
    )
    assert spec and spec.loader
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)
    return renderer, inventory


def _registry(root):
    return {"machines": {"target": {
        "os": "linux", "schedule_variant": "full",
        "workspace_root": str(root), "harness_profile": {"roles": []},
    }}}


def _task():
    return {
        "id": "probe", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": '"${WORKSPACE_HUB}/scripts/run.sh" >> "$LOG" 2>&1',
        "machines": ["target"], "roles": [],
    }


def _alias_declared_root(monkeypatch, root, tmp_path):
    """Simulate a platform alias without changing source-file digest lookups."""
    original_resolve = Path.resolve
    alias = tmp_path / "aliased" / root.name
    calls = []

    def resolve(path, *args, **kwargs):
        lexical = PurePosixPath(path.as_posix())
        if lexical == root or root in lexical.parents:
            calls.append(lexical)
            return alias / lexical.relative_to(root)
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    return calls


def test_declared_root_is_lexical_under_aliasing_resolver(
    tmp_path, monkeypatch, cron_modules
):
    renderer, _ = cron_modules
    root = PurePosixPath(tmp_path.as_posix()) / "declared" / "checkout"
    calls = _alias_declared_root(monkeypatch, root, tmp_path)

    hub = renderer.workspace_hub_path(str(root))
    context = renderer.build_context(
        "target", registry=_registry(root), workspace_hub=str(root)
    )
    rendered = renderer.render_task(_task(), context)

    assert isinstance(hub, PurePosixPath)
    assert str(hub) == str(root)
    assert context["workspace_hub"] == str(root)
    assert context["log"] == f"{root}/logs/quality/cron-wrapper.log"
    assert rendered["command"] == (
        f'"{root}/scripts/run.sh" >> "{root}/logs/quality/cron-wrapper.log" 2>&1'
    )
    assert rendered["line"] == (
        f'0 1 * * * "{root}/scripts/run.sh" '
        f'>> "{root}/logs/quality/cron-wrapper.log" 2>&1'
    )
    assert calls == []


def test_spaced_root_rendering_is_platform_invariant(
    tmp_path, monkeypatch, cron_modules
):
    renderer, _ = cron_modules
    root = PurePosixPath(tmp_path.as_posix()) / "declared" / "checkout with spaces"
    calls = _alias_declared_root(monkeypatch, root, tmp_path)

    context = renderer.build_context(
        "target", registry=_registry(root), workspace_hub=str(root)
    )
    rendered = renderer.render_task(_task(), context)

    assert context["workspace_hub"] == str(root)
    assert context["log"] == f"{root}/logs/quality/cron-wrapper.log"
    assert rendered["command"] == (
        f'"{root}/scripts/run.sh" >> "{root}/logs/quality/cron-wrapper.log" 2>&1'
    )
    assert rendered["line"] == (
        f'0 1 * * * "{root}/scripts/run.sh" '
        f'>> "{root}/logs/quality/cron-wrapper.log" 2>&1'
    )
    assert calls == []


@pytest.mark.parametrize("leaf", ["checkout", "checkout with spaces"])
def test_fixture_inventory_uses_declared_root(
    tmp_path, monkeypatch, cron_modules, leaf
):
    _, inventory = cron_modules
    root = PurePosixPath(tmp_path.as_posix()) / "declared" / leaf
    catalog_path = tmp_path / "catalog.yaml"
    registry_path = tmp_path / "registry.yaml"
    classes_path = tmp_path / "classes.yaml"
    for path, document in (
        (catalog_path, {"tasks": [_task()]}),
        (registry_path, _registry(root)),
        (classes_path, {"preserved_external": [], "preserved_local": []}),
    ):
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
    # An unrelated checkout environment must not replace the declared root.
    monkeypatch.setenv("WORKSPACE_HUB", str(tmp_path / "unrelated"))
    calls = _alias_declared_root(monkeypatch, root, tmp_path)

    payload = inventory.build(catalog_path, registry_path, classes_path)

    expected_line = (
        f'0 1 * * * "{root}/scripts/run.sh" '
        f'>> "{root}/logs/quality/cron-wrapper.log" 2>&1'
    )
    machine_key = hashlib.sha256(b"cron-machine:target").hexdigest()[:12]
    assert payload["machines"] == [machine_key]
    assert payload["identities"] == [{
        "canonical_line_sha256": hashlib.sha256(expected_line.encode()).hexdigest(),
        "legacy_variant_ids": [], "machine_id": machine_key,
        "task_id": hashlib.sha256(b"cron-task:probe").hexdigest()[:12], "unique": True,
    }]
    assert payload["unsupported"] == []
    assert payload["collisions"] == []
    assert calls == []
