"""Adversarial authorization and cleanup tests for the bootstrap contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

from client_llm_wiki import bootstrap_contract
from client_llm_wiki.bootstrap_contract import (
    BootstrapContractError,
    derive_workspace_layout,
    execute_render,
    verify_unborn_clone,
)


REPO_SLUG = "example-org/llm-wiki-example-co"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _workspace(tmp_path: Path) -> Path:
    repo = tmp_path / "ecosystem" / "workspace-hub"
    template = repo / "templates" / "client-llm-wiki"
    (template / ".claude").mkdir(parents=True)
    (template / ".gitignore").write_text("private-output/\n", encoding="utf-8")
    (template / ".claude" / "CLAUDE.md").write_text("private\n", encoding="utf-8")
    (template / "README.md").write_text("# <CLIENT_SHORT_NAME>\n", encoding="utf-8")
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "core.hooksPath", "/dev/null")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test Operator")
    _git(repo, "add", "templates/client-llm-wiki")
    _git(repo, "commit", "-m", "test: add template")
    return repo


def _entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "short_name": "example-co",
        "repo": REPO_SLUG,
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
        "raw_source_status": "not-mounted",
        "ingestion_enabled": False,
    }
    entry.update(overrides)
    return entry


def _registry_file(tmp_path: Path, entry: dict[str, object] | None = None) -> Path:
    path = tmp_path / "registry.yml"
    path.write_text(
        yaml.safe_dump(
            {"registry_version": "0.2", "wikis": [entry or _entry()]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _init_target(path: Path, origin: str | None = None) -> Path:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    _git(path, "config", "core.hooksPath", "/dev/null")
    if origin is not None:
        _git(path, "remote", "add", "origin", origin)
    return path


class RecordingRunner:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, args, **_kwargs):
        self.calls.append(list(args))
        payload = {
            "nameWithOwner": REPO_SLUG,
            "visibility": "PRIVATE",
            "isArchived": False,
        }
        return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")


def test_layout_ignores_cwd_and_hostile_git_environment(tmp_path, monkeypatch):
    workspace = _workspace(tmp_path)
    decoy = tmp_path / "decoy"
    subprocess.run(["git", "init", str(decoy)], check=True, capture_output=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLIENT_WIKI_DESTINATION", str(tmp_path / "attacker"))
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(decoy))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")

    layout = derive_workspace_layout(workspace, REPO_SLUG)

    assert layout.target == workspace.parent / "llm-wiki-example-co"
    with pytest.raises(SystemExit):
        bootstrap_contract.main(
            ["classify", "--registry", "unused", "--destination", "/tmp/elsewhere"]
        )


def test_layout_rejects_symlinked_common_git_directory(tmp_path):
    workspace = _workspace(tmp_path)
    real_git = workspace / ".git-real"
    (workspace / ".git").rename(real_git)
    (workspace / ".git").symlink_to(real_git, target_is_directory=True)

    with pytest.raises(BootstrapContractError, match="non-symlink|real .git"):
        derive_workspace_layout(workspace, REPO_SLUG)


@pytest.mark.parametrize("rewrite", ["pushurl", "instead-of"])
def test_clone_rejects_effective_push_or_fetch_rewrites(tmp_path, rewrite):
    clone = _init_target(tmp_path / "clone", f"https://github.com/{REPO_SLUG}.git")
    if rewrite == "pushurl":
        _git(clone, "config", "remote.origin.pushurl", "https://example.invalid/other")
    else:
        _git(
            clone,
            "config",
            "url.https://example.invalid/.insteadOf",
            "https://github.com/",
        )

    with pytest.raises(BootstrapContractError, match="origin"):
        verify_unborn_clone(clone, REPO_SLUG)


def test_execute_render_exposes_no_template_or_destination_override():
    with pytest.raises(TypeError):
        execute_render(
            Path("registry.yml"),
            "example-co",
            template_worktree=Path("attacker-workspace"),
        )


def test_failed_final_origin_validation_preserves_created_tree(tmp_path, monkeypatch):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    real_render = bootstrap_contract.render_committed_template

    def mutate_before_final_validation(clone, template, tokens):
        manifest = real_render(clone, template, tokens)
        _git(target, "remote", "set-url", "origin", "https://example.invalid/other")
        return manifest

    monkeypatch.setattr(
        bootstrap_contract, "render_committed_template", mutate_before_final_validation
    )
    with pytest.raises(
        BootstrapContractError, match="render final validation failed"
    ) as raised:
        execute_render(registry, "example-co", runner=RecordingRunner())

    assert raised.value.residue is not None
    assert raised.value.residue.failure_stage == "final_validation"
    assert (target / "README.md").is_file()


@pytest.mark.parametrize(
    "failure",
    [
        KeyboardInterrupt("secret-ish\x00\n" + "x" * 10_000),
        SystemExit("secret-ish\x00\n" + "x" * 10_000),
        OSError("secret-ish\x00\n" + "x" * 10_000),
        BootstrapContractError("secret-ish\x00\n" + "x" * 10_000),
    ],
)
def test_final_validation_base_exception_has_fixed_complete_residue(
    tmp_path,
    monkeypatch,
    failure,
):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    real_verify = bootstrap_contract._verify_bound_clone
    calls = 0
    descriptors: tuple[int, ...] = ()

    def fail_second_verify(clone, repo_slug, **kwargs):
        nonlocal calls, descriptors
        calls += 1
        if calls == 2:
            descriptors = (clone.parent_fd, clone.root_fd, clone.git_fd)
            raise failure
        return real_verify(clone, repo_slug, **kwargs)

    monkeypatch.setattr(bootstrap_contract, "_verify_bound_clone", fail_second_verify)
    with pytest.raises(BootstrapContractError) as raised:
        execute_render(registry, "example-co", runner=RecordingRunner())

    residue = raised.value.residue
    expected = {".claude", ".claude/CLAUDE.md", ".gitignore", "README.md"}
    assert str(raised.value) == "render final validation failed"
    assert "secret-ish" not in str(raised.value)
    assert residue.template_commit == _git(workspace, "rev-parse", "HEAD")
    assert residue.residue_policy == "preserved"
    assert set(residue.completed_members) == expected
    assert residue.uncertain_member is None
    assert residue.failure_stage == "final_validation"
    for descriptor in descriptors:
        with pytest.raises(OSError):
            os.fstat(descriptor)


def test_final_validation_rejects_post_bind_git_directory_swap(tmp_path, monkeypatch):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    real_render = bootstrap_contract.render_committed_template

    def swap_before_final_validation(clone, template, tokens):
        manifest = real_render(clone, template, tokens)
        (target / ".git").rename(target / ".git-held")
        subprocess.run(["git", "init", str(target)], check=True, capture_output=True)
        _git(target, "remote", "add", "origin", f"https://github.com/{REPO_SLUG}.git")
        return manifest

    monkeypatch.setattr(
        bootstrap_contract, "render_committed_template", swap_before_final_validation
    )
    with pytest.raises(BootstrapContractError, match="render final validation failed"):
        execute_render(registry, "example-co", runner=RecordingRunner())

    assert (target / "README.md").exists()
    assert (target / ".git").is_dir() and (target / ".git-held").is_dir()


def test_source_registered_render_never_touches_raw_root_contents(
    tmp_path, monkeypatch
):
    workspace = _workspace(tmp_path)
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    raw_root = tmp_path / "authorized-raw"
    raw_root.mkdir()
    sentinel = raw_root / "sentinel.bin"
    sentinel.write_bytes(b"private sentinel")
    before = (sentinel.stat().st_ino, hashlib.sha256(sentinel.read_bytes()).hexdigest())
    registry = _registry_file(
        tmp_path,
        _entry(raw_roots=[str(raw_root)], raw_source_status="mounted"),
    )
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    originals = (os.open, os.stat, os.lstat, os.scandir)

    def guarded(callable_):
        def wrapper(path, *args, **kwargs):
            if isinstance(path, (str, os.PathLike)):
                candidate = Path(path)
                if candidate == raw_root or raw_root in candidate.parents:
                    raise AssertionError("raw root filesystem access")
            return callable_(path, *args, **kwargs)

        return wrapper

    with pytest.MonkeyPatch.context() as guard:
        for name, original in zip(
            ("open", "stat", "lstat", "scandir"), originals, strict=True
        ):
            guard.setattr(os, name, guarded(original))
        execute_render(registry, "example-co", runner=RecordingRunner())

    after = (sentinel.stat().st_ino, hashlib.sha256(sentinel.read_bytes()).hexdigest())
    assert after == before


def test_cli_render_persists_explicit_external_manifest(tmp_path, monkeypatch, capsys):
    workspace = _workspace(tmp_path)
    registry = _registry_file(tmp_path)
    target = workspace.parent / "llm-wiki-example-co"
    _init_target(target, f"https://github.com/{REPO_SLUG}.git")
    _git(target, "config", "--unset", "core.hooksPath")
    _git(target, "symbolic-ref", "HEAD", "refs/heads/main")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    manifest_path = evidence / "render.json"
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    monkeypatch.setattr(
        bootstrap_contract, "verify_private_repo", lambda *_a, **_k: None
    )

    result = bootstrap_contract.main(
        [
            "render",
            "--registry",
            str(registry),
            "--short-name",
            "example-co",
            "--manifest",
            str(manifest_path),
        ]
    )

    evidence_json = json.loads(capsys.readouterr().out.splitlines()[-1])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result == 0
    assert manifest["template"]["commit"] == _git(workspace, "rev-parse", "HEAD")
    assert evidence_json["manifest"] == str(manifest_path)
    assert evidence_json["backing_name"] == manifest["backing_name"]
    assert (target / ".gitignore").is_file()


@pytest.mark.parametrize("option", ["--failpoint", "--callback"])
def test_public_cli_rejects_injection_authority(option):
    with pytest.raises(SystemExit):
        bootstrap_contract.main(
            [
                "render",
                "--registry",
                "registry.yml",
                "--short-name",
                "example-co",
                "--manifest",
                "manifest.json",
                option,
                "write",
            ]
        )


def test_execute_render_rejects_failpoint_authority():
    with pytest.raises(TypeError):
        execute_render(Path("registry.yml"), "example-co", failpoint="write")


def test_cli_residue_json_uses_fixed_error_and_policy(monkeypatch, capsys):
    residue = bootstrap_contract.RenderResidue(
        "a" * 40,
        1,
        2,
        ("README.md",),
        None,
        "write",
    )

    def fail_execute(*_args, **_kwargs):
        raise BootstrapContractError("secret-ish\x00\n" + "x" * 10_000, residue=residue)

    monkeypatch.setattr(bootstrap_contract, "execute_render", fail_execute)
    result = bootstrap_contract.main(
        [
            "render",
            "--registry",
            "registry.yml",
            "--short-name",
            "example-co",
            "--manifest",
            "manifest.json",
        ]
    )
    payload = json.loads(capsys.readouterr().err)

    assert result == 1
    assert payload["error"] == "render_failed"
    assert payload["residue"]["template_commit"] == "a" * 40
    assert payload["residue"]["residue_policy"] == "preserved"
