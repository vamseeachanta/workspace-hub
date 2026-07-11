"""Descriptor-bound finalization and recovery for issue #3449."""

from __future__ import annotations

import inspect
from pathlib import Path
import subprocess

import yaml

from client_llm_wiki import bootstrap_contract, bootstrap_finalizer
from client_llm_wiki.bootstrap_manifest import persist_render_manifest
from client_llm_wiki.bootstrap_renderer import RenderTokens, bind_empty_clone, render_committed_template


def test_public_finalizer_has_only_trusted_inputs():
    assert tuple(inspect.signature(bootstrap_finalizer.finalize_scaffold).parameters) == (
        "registry_path",
        "short_name",
        "manifest_path",
    )


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
    ).stdout.strip()


def _fixture(tmp_path: Path):
    workspace = tmp_path / "ecosystem" / "workspace-hub"
    template = workspace / "templates" / "client-llm-wiki"
    (template / ".claude").mkdir(parents=True)
    (template / ".gitignore").write_text("private-output/\n")
    (template / ".claude" / "CLAUDE.md").write_text("private\n")
    (template / "README.md").write_text("# <CLIENT_SHORT_NAME>\n")
    subprocess.run(["git", "init", str(workspace)], check=True, capture_output=True)
    _git(workspace, "config", "user.name", "Fixture")
    _git(workspace, "config", "user.email", "fixture@example.test")
    _git(workspace, "add", ".")
    _git(workspace, "commit", "-m", "test: template")
    clone = workspace.parent / "llm-wiki-client"
    subprocess.run(["git", "init", "-b", "main", str(clone)], check=True, capture_output=True)
    repo = "org/llm-wiki-client"
    _git(clone, "remote", "add", "origin", f"https://github.com/{repo}.git")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    manifest = evidence / "render.json"
    with bind_empty_clone(clone) as bound:
        rendered = render_committed_template(
            bound, workspace, RenderTokens("client", "CLIENT", repo, "not-mounted", False),
        )
        persist_render_manifest(
            bound, manifest, registered_repo=repo,
            allowed_origins=(f"git@github.com:{repo}.git", f"https://github.com/{repo}.git"),
            template_commit=rendered.template_commit, template_tree=rendered.template_tree,
        )
    registry = tmp_path / "registry.yml"
    registry.write_text(yaml.safe_dump({"registry_version": "0.2", "wikis": [{
        "short_name": "client", "repo": repo, "visibility": "PRIVATE",
        "posture": "client-private", "status": "planned", "raw_roots": [],
        "raw_source_status": "not-mounted", "ingestion_enabled": False,
    }]}))
    return workspace, clone, registry, manifest


def test_initial_success_constructs_exact_root_commit_and_index(tmp_path, monkeypatch):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    states = iter((("absent", None), ("equal", "unused"), ("equal", "unused")))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")

    result = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)

    assert result["status"] == "finalized"
    assert _git(clone, "rev-list", "--parents", "-1", "HEAD").split() == [result["commit_oid"]]
    assert _git(clone, "write-tree") == result["tree_oid"]
    raw = subprocess.run(
        ["git", "-C", str(clone), "cat-file", "commit", result["commit_oid"]],
        check=True, capture_output=True,
    ).stdout
    assert raw.endswith(b"\n\nchore: initialize metadata-only client wiki\n")


def test_cli_exposes_exact_finalize_arguments():
    args = bootstrap_contract.build_parser().parse_args([
        "finalize-scaffold", "--registry", "registry.yml", "--short-name", "client",
        "--manifest", "render.json",
    ])
    assert str(args.registry) == "registry.yml"
    assert str(args.manifest) == "render.json"
