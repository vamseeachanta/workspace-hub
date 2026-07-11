"""SHA-256 integration and fail-closed GitHub API finalizer coverage."""
import subprocess
from pathlib import Path

import pytest
import yaml

from client_llm_wiki import bootstrap_contract, bootstrap_finalizer, bootstrap_remote
from client_llm_wiki.bootstrap_manifest import persist_render_manifest
from client_llm_wiki.bootstrap_renderer import RenderTokens, bind_empty_clone, render_committed_template


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
    ).stdout.strip()


def fixture(tmp_path: Path, object_format: str):
    workspace = tmp_path / "ecosystem" / "workspace-hub"
    template = workspace / "templates" / "client-llm-wiki"
    (template / ".claude").mkdir(parents=True)
    (template / ".gitignore").write_text("private-output/\n")
    (template / ".claude" / "CLAUDE.md").write_text("private\n")
    (template / "README.md").write_text("# <CLIENT_SHORT_NAME>\n")
    subprocess.run(["git", "init", str(workspace)], check=True, capture_output=True)
    git(workspace, "config", "user.name", "Fixture")
    git(workspace, "config", "user.email", "fixture@example.test")
    git(workspace, "add", ".")
    git(workspace, "commit", "-m", "test: template")
    clone = workspace.parent / "llm-wiki-client"
    subprocess.run(
        ["git", "init", "-b", "main", f"--object-format={object_format}", str(clone)],
        check=True, capture_output=True,
    )
    repo = "org/llm-wiki-client"
    git(clone, "remote", "add", "origin", f"https://github.com/{repo}.git")
    manifest = tmp_path / "evidence" / "render.json"
    manifest.parent.mkdir()
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


@pytest.mark.parametrize(("repo_status", "branch_status", "sha", "expected"), [
    (200, 404, None, "absent"), (200, 200, "d" * 40, "equal"),
    (200, 200, "e" * 40, "different"), (401, 404, None, "unknown"),
    (403, 404, None, "unknown"), (404, 404, None, "unknown"),
    (200, 500, None, "unknown"), (200, 200, "malformed", "unknown"),
])
def test_remote_state_mapping_is_fail_closed(
    monkeypatch, repo_status, branch_status, sha, expected,
):
    repo = {"name": "llm-wiki-client", "owner": {"login": "org"},
            "private": True, "archived": False}
    replies = iter(((repo_status, repo), (branch_status, {"object": {"sha": sha}})))
    monkeypatch.setattr(bootstrap_remote, "github_api", lambda *_args: next(replies))
    assert bootstrap_remote.remote_state("org/llm-wiki-client", "d" * 40)[0] == expected


def test_github_api_uses_literal_host_and_isolated_hostile_config(monkeypatch, tmp_path):
    hostile = tmp_path / "gh"
    hostile.mkdir()
    (hostile / "hosts.yml").write_text("attacker.invalid:\n  oauth_token: hostile\n")
    seen = {}

    def run(command):
        seen.update(command=command, env=bootstrap_remote.isolated_env())
        return subprocess.CompletedProcess(command, 1, b"", b"failed")

    monkeypatch.setenv("GH_HOST", "attacker.invalid")
    monkeypatch.setenv("GH_CONFIG_DIR", str(hostile))
    monkeypatch.setenv("GIT_CONFIG", "/tmp/hostile")
    monkeypatch.setattr(bootstrap_remote, "_run", run)
    assert bootstrap_remote.github_api("repos/org/llm-wiki-client") == (0, {})
    assert seen["command"][0:5] == ["gh", "api", "--hostname", "github.com", "--include"]
    assert "GH_HOST" not in seen["env"]
    assert seen["env"]["GIT_CONFIG"] == "/dev/null"
    assert seen["env"]["GH_CONFIG_DIR"] == str(hostile)


@pytest.mark.parametrize("repo_payload", [
    {"name": "wrong", "owner": {"login": "org"}, "private": True, "archived": False},
    {"name": "llm-wiki-client", "owner": {"login": "wrong"}, "private": True, "archived": False},
    {"name": "llm-wiki-client", "owner": {"login": "org"}, "private": False, "archived": False},
    {"name": "llm-wiki-client", "owner": {"login": "org"}, "private": True, "archived": True},
])
def test_remote_rejects_wrong_identity_public_and_archived(monkeypatch, repo_payload):
    monkeypatch.setattr(bootstrap_remote, "github_api", lambda *_args: (200, repo_payload))
    assert bootstrap_remote.remote_state("org/llm-wiki-client", "d" * 40) == ("unknown", None)


@pytest.mark.parametrize("outcome", ["malformed", "timeout", "exception"])
def test_github_api_failures_are_unknown(monkeypatch, outcome):
    def run(command):
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(command, 15)
        if outcome == "exception":
            raise OSError("lookup failed")
        return subprocess.CompletedProcess(command, 0, b"not-json", b"")
    monkeypatch.setattr(bootstrap_remote, "_run", run)
    expected_status = 200 if outcome == "malformed" else 0
    assert bootstrap_remote.github_api("repos/org/llm-wiki-client") == (expected_status, {})
    assert bootstrap_remote.remote_state("org/llm-wiki-client", "d" * 40) == ("unknown", None)


def test_sha256_repository_finalizes_exact_blob_tree_root_and_cas(tmp_path, monkeypatch):
    probe = subprocess.run(
        ["git", "init", "--object-format=sha256", str(tmp_path / "probe")],
        check=False, capture_output=True,
    )
    if probe.returncode:
        pytest.skip("installed Git lacks SHA-256 repository support")
    workspace, clone, registry, manifest = fixture(tmp_path / "case", "sha256")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    states = iter((("absent", None), ("absent", None), ("equal", None)))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")
    result = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)
    assert len(result["commit_oid"]) == len(result["tree_oid"]) == 64
    assert git(clone, "rev-parse", "refs/heads/main") == result["commit_oid"]
    assert git(clone, "write-tree") == result["tree_oid"]
    assert git(clone, "hash-object", "README.md") in git(clone, "ls-tree", "-r", "HEAD")
    assert git(clone, "rev-list", "--parents", "-1", "HEAD").split() == [result["commit_oid"]]
