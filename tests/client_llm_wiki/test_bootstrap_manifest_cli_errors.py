"""Fail-closed CLI translation for render-manifest publication failures."""

import json

import pytest

from client_llm_wiki import bootstrap_contract
from client_llm_wiki.bootstrap_attestation import BootstrapManifestError
from tests.client_llm_wiki.test_bootstrap_contract_security import (
    REPO_SLUG,
    _git,
    _init_target,
    _registry_file,
    _workspace,
)


def _authorized_render(tmp_path, monkeypatch):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    _git(target, "config", "--unset", "core.hooksPath")
    _git(target, "symbolic-ref", "HEAD", "refs/heads/main")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    monkeypatch.setattr(
        bootstrap_contract, "verify_private_repo", lambda *_a, **_k: None
    )
    return registry


def _render_args(registry, manifest):
    return [
        "render",
        "--registry",
        str(registry),
        "--short-name",
        "example-co",
        "--manifest",
        str(manifest),
    ]


def test_occupied_manifest_returns_fixed_bounded_json(tmp_path, monkeypatch, capsys):
    registry = _authorized_render(tmp_path, monkeypatch)
    manifest = tmp_path / "occupied.json"
    manifest.write_text("victim", encoding="utf-8")

    result = bootstrap_contract.main(_render_args(registry, manifest))

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    assert captured.err == (
        '{"error":"manifest_persistence_failed","residue":'
        '{"backing_name":null,"residue_policy":"preserved"}}\n'
    )
    assert manifest.read_text(encoding="utf-8") == "victim"


@pytest.mark.parametrize(
    ("backing", "expected"),
    [(".render.json.backing-safe", ".render.json.backing-safe"), ("x" * 1000, None)],
)
def test_injected_failure_never_exposes_exception(
    tmp_path, monkeypatch, capsys, backing, expected
):
    registry = _authorized_render(tmp_path, monkeypatch)
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    def fail_persistence(*_args, **_kwargs):
        raise BootstrapManifestError("secret\x00" + "z" * 10_000, backing_name=backing)

    monkeypatch.setattr(bootstrap_contract, "persist_render_manifest", fail_persistence)
    result = bootstrap_contract.main(_render_args(registry, evidence / "render.json"))

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "error": "manifest_persistence_failed",
        "residue": {"backing_name": expected, "residue_policy": "preserved"},
    }
    assert "secret" not in captured.err
