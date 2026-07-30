"""Integration rejection matrix for every pre-mutation finalizer mismatch."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess

import pytest
import yaml

from client_llm_wiki import bootstrap_contract, bootstrap_finalizer
from client_llm_wiki.bootstrap_manifest import persist_render_manifest
from client_llm_wiki.bootstrap_renderer import RenderTokens, bind_empty_clone, render_committed_template


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True, text=True,
    )
    return result.stdout.strip()


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


def _files(root: Path, *, exclude_git: bool = False) -> dict[str, tuple[int, bytes]]:
    values = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if exclude_git and (relative == ".git" or relative.startswith(".git/")):
            continue
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            values[relative] = (stat.S_IMODE(info.st_mode), path.read_bytes())
        elif stat.S_ISLNK(info.st_mode):
            values[relative] = (stat.S_IFLNK, os.readlink(path).encode())
    return values


def _state(clone: Path, registry: Path) -> dict[str, object]:
    git = clone / ".git"
    return {
        "objects": _files(git / "objects"),
        "refs": _files(git / "refs"),
        "head": (git / "HEAD").read_bytes() if (git / "HEAD").is_file() else None,
        "index": (git / "index").read_bytes() if (git / "index").exists() else None,
        "worktree": _files(clone, exclude_git=True),
        "registry": registry.read_bytes(),
    }


def _rewrite_manifest(manifest: Path, callback) -> None:
    claims = json.loads(manifest.read_bytes())
    callback(claims)
    data = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    backing = manifest.parent / claims["backing_name"]
    manifest.unlink()
    backing.unlink()
    backing.write_bytes(data)
    backing.chmod(0o600)
    os.link(backing, manifest)


def _commit(clone: Path, *, message="chore: initialize metadata-only client wiki",
            name="Client Wiki Bot", email="client-wiki@example.com") -> str:
    env = os.environ | {
        "GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email,
    }
    subprocess.run(["git", "-C", str(clone), "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", str(clone), "commit", "-m", message], check=True,
                   capture_output=True, env=env)
    return _git(clone, "rev-parse", "HEAD")


def _mutate_unborn(case: str, clone: Path, manifest: Path) -> None:
    git = clone / ".git"
    if case == "wrong-symbolic-head":
        (git / "HEAD").write_text("ref: refs/heads/other\n")
    elif case == "substituted-symbolic-head":
        (git / "HEAD").unlink()
        (git / "HEAD").symlink_to("refs/heads/main")
    elif case == "unexpected-index":
        _git(clone, "add", "README.md")
    elif case == "worktree-bytes":
        (clone / "README.md").write_text("# altered\n")
    elif case == "worktree-mode":
        (clone / "README.md").chmod(0o755)
    elif case == "worktree-member":
        (clone / "unexpected.txt").write_text("unexpected\n")
    elif case in {"parent-identity", "root-identity", "git-identity", "config-identity"}:
        key = case.removesuffix("-identity")
        _rewrite_manifest(manifest, lambda claims: claims["identities"][key].update(inode=-1))
    elif case == "config-content":
        with (git / "config").open("a") as stream:
            stream.write("[gc]\n\tauto = 0\n")
    elif case == "origin-content":
        _git(clone, "remote", "set-url", "origin", "https://github.com/org/wrong.git")


UNBORN_CASES = (
    "wrong-symbolic-head", "substituted-symbolic-head", "unexpected-index",
    "worktree-bytes", "worktree-mode", "worktree-member", "parent-identity",
    "root-identity", "git-identity", "config-identity", "config-content", "origin-content",
)


@pytest.mark.parametrize("case", UNBORN_CASES, ids=UNBORN_CASES)
def test_each_unborn_mismatch_rejects_without_any_mutation(tmp_path, monkeypatch, case):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    _mutate_unborn(case, clone, manifest)
    _assert_rejected_without_mutation(workspace, clone, registry, manifest, monkeypatch)


COMMIT_CASES = (
    "detached-head", "wrong-tree", "wrong-message", "wrong-author", "wrong-committer",
    "parent-commit", "wrong-shape",
)


def _mutate_commit(case: str, clone: Path) -> None:
    if case == "wrong-tree":
        (clone / "README.md").write_text("# wrong tree\n")
    if case == "wrong-message":
        _commit(clone, message="wrong message")
    elif case == "wrong-author":
        _commit(clone, name="Wrong Author")
    elif case == "wrong-committer":
        oid = _commit(clone)
        raw = subprocess.run(
            ["git", "-C", str(clone), "cat-file", "commit", oid], check=True,
            capture_output=True,
        ).stdout.replace(b"committer Client Wiki Bot", b"committer Wrong Committer")
        forged = subprocess.run(
            ["git", "-C", str(clone), "hash-object", "--literally", "-t", "commit",
             "-w", "--stdin"],
            input=raw, check=True, capture_output=True,
        ).stdout.strip().decode()
        _git(clone, "update-ref", "refs/heads/main", forged)
    elif case == "wrong-shape":
        tree = _git(clone, "write-tree")
        raw = f"tree {tree}\nencoding UTF-8\n\nchore: initialize metadata-only client wiki\n"
        forged = subprocess.run(
            ["git", "-C", str(clone), "hash-object", "--literally", "-t", "commit",
             "-w", "--stdin"],
            input=raw.encode(), check=True, capture_output=True,
        ).stdout.strip().decode()
        _git(clone, "update-ref", "refs/heads/main", forged)
    else:
        _commit(clone)
    if case == "parent-commit":
        (clone / "README.md").write_text("# second\n")
        _commit(clone)
    elif case == "detached-head":
        _git(clone, "checkout", "--detach")


@pytest.mark.parametrize("case", COMMIT_CASES, ids=COMMIT_CASES)
def test_each_commit_mismatch_rejects_without_any_mutation(tmp_path, monkeypatch, case):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    _mutate_commit(case, clone)
    _assert_rejected_without_mutation(workspace, clone, registry, manifest, monkeypatch)


REMOTE_CASES = ("existing-equal", "existing-different", "unknown")


@pytest.mark.parametrize("case", REMOTE_CASES, ids=REMOTE_CASES)
def test_each_unborn_remote_sha_state_rejects_without_mutation(tmp_path, monkeypatch, case):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    state = "unknown" if case == "unknown" else ("equal" if case == "existing-equal" else "different")
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: (state, "d" * 40))
    _assert_rejected_without_mutation(
        workspace, clone, registry, manifest, monkeypatch, patch_remote=False,
    )


def _assert_rejected_without_mutation(
    workspace, clone, registry, manifest, monkeypatch, *, patch_remote=True,
) -> None:
    pushes, registry_actions = [], []
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    if patch_remote:
        monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: ("absent", None))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: pushes.append(_args))
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")
    before = _state(clone, registry)
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError):
        bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)
    assert _state(clone, registry) == before
    assert pushes == []
    assert registry_actions == []
