"""Pinned-snapshot and descriptor-bound renderer tests for issue #3449."""

from __future__ import annotations

import inspect
import json
import os
from pathlib import Path
import stat
import subprocess

import pytest
from client_llm_wiki import bootstrap_renderer
from client_llm_wiki.bootstrap_renderer import (
    BootstrapRenderError,
    RenderTokens,
    bind_empty_clone,
    render_committed_template,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _template_repo(tmp_path: Path, readme: str | None = None) -> Path:
    repo = tmp_path / "workspace-hub"
    root = repo / "templates" / "client-llm-wiki"
    (root / ".claude").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / ".gitignore").write_text("private-output/\n", encoding="utf-8")
    (root / ".claude" / "CLAUDE.md").write_text("private only\n", encoding="utf-8")
    (root / "README.md").write_text(
        readme or "# <CLIENT_SHORT_NAME>\n<CLIENT_PRIVATE_REPO>\n",
        encoding="utf-8",
    )
    (root / "docs" / "note.md").write_text(
        "<CLIENT_SHORT_NAME_UPPER> / <PROJECT_SHORT_NAME>\n",
        encoding="utf-8",
    )
    script = root / "verify.sh"
    script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "core.hooksPath", "/dev/null")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test Operator")
    _git(repo, "add", "templates/client-llm-wiki")
    _git(repo, "commit", "-m", "test: add generic template")
    return repo


def _empty_clone(tmp_path: Path) -> Path:
    clone = tmp_path / "llm-wiki-example-co"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "sentinel").write_text("git metadata\n", encoding="utf-8")
    return clone


def _tokens() -> RenderTokens:
    return RenderTokens(
        short_name="example-co",
        short_name_upper="EXAMPLE-CO",
        repo_slug="example-org/llm-wiki-example-co",
        raw_source_status="not-mounted",
        ingestion_enabled=False,
    )


def _render(repo: Path, clone: Path, failpoint=None):
    with bind_empty_clone(clone) as bound:
        if failpoint is None:
            return render_committed_template(bound, repo, _tokens())
        return bootstrap_renderer._render_committed_template_for_test(
            bound, repo, _tokens(), failpoint=failpoint,
        )


def test_public_renderer_has_no_injection_or_callback_boundary():
    signature = inspect.signature(render_committed_template)
    assert tuple(signature.parameters) == ("clone", "template_worktree", "tokens")
    with pytest.raises(TypeError):
        render_committed_template(None, None, None, failpoint="write")
    with pytest.raises(TypeError):
        render_committed_template(None, None, None, callback=lambda: None)


def test_render_uses_committed_head_and_normalizes_modes(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    commit = _git(repo, "rev-parse", "HEAD")
    readme = repo / "templates" / "client-llm-wiki" / "README.md"
    readme.write_text("DIRTY CONTENT\n", encoding="utf-8")
    (readme.parent / "untracked.txt").write_text("ignore me\n", encoding="utf-8")

    manifest = _render(repo, clone)

    assert manifest.template_commit == commit
    assert (clone / "README.md").read_text() == ("# example-co\nexample-org/llm-wiki-example-co\n")
    assert not (clone / "untracked.txt").exists()
    assert stat.S_IMODE((clone / "README.md").stat().st_mode) == 0o644
    assert stat.S_IMODE((clone / "verify.sh").stat().st_mode) == 0o755
    assert (clone / ".git" / "sentinel").read_text() == "git metadata\n"


def test_render_consumes_exact_snapshot_without_archive(tmp_path, monkeypatch):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    dotfile = repo / "templates/client-llm-wiki/.hidden"
    dotfile.write_bytes(b"committed dotfile\n")
    _git(repo, "add", str(dotfile.relative_to(repo)))
    _git(repo, "commit", "-m", "test: add dotfile")
    dotfile.write_bytes(b"dirty dotfile\n")
    commands: list[tuple[str, ...]] = []
    original = subprocess.run

    def record(command, *args, **kwargs):
        commands.append(tuple(str(part) for part in command))
        return original(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", record)
    _render(repo, clone)

    assert (clone / ".hidden").read_bytes() == b"committed dotfile\n"
    assert not any("archive" in command for command in commands)


def test_render_has_no_rehearsal_or_staging_tree(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    _render(repo, clone)
    assert not hasattr(bootstrap_renderer, "_bound_stage")
    assert not list(tmp_path.glob(".client-wiki-stage-*"))


def test_template_snapshot_ignores_hostile_ambient_git_environment(tmp_path, monkeypatch):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    decoy = tmp_path / "decoy"
    subprocess.run(["git", "init", str(decoy)], check=True, capture_output=True)
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(decoy))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")

    _render(repo, clone)

    assert (clone / "README.md").read_text().startswith("# example-co")


def test_allowlisted_tokens_resolve_and_project_token_survives(tmp_path):
    repo = _template_repo(
        tmp_path,
        "<CLIENT_SHORT_NAME>|<CLIENT_SHORT_NAME_UPPER>|"
        "<CLIENT_PRIVATE_REPO>|<RAW_SOURCE_STATUS>|"
        "<INGESTION_ENABLED>|<PROJECT_SHORT_NAME>\n",
    )
    clone = _empty_clone(tmp_path)

    _render(repo, clone)

    assert (clone / "README.md").read_text() == (
        "example-co|EXAMPLE-CO|example-org/llm-wiki-example-co|not-mounted|false|<PROJECT_SHORT_NAME>\n"
    )


def test_unknown_client_token_fails_before_clone_writes(tmp_path):
    repo = _template_repo(tmp_path, "<CLIENT_RAW_ROOT>\n")
    clone = _empty_clone(tmp_path)

    with pytest.raises(BootstrapRenderError, match="CLIENT_RAW_ROOT"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]


def test_git_symlink_is_rejected_before_clone_writes(tmp_path):
    repo = _template_repo(tmp_path)
    root = repo / "templates" / "client-llm-wiki"
    (root / "unsafe-link").symlink_to("README.md")
    _git(repo, "add", "templates/client-llm-wiki/unsafe-link")
    _git(repo, "commit", "-m", "test: add unsafe link")
    clone = _empty_clone(tmp_path)

    with pytest.raises(BootstrapRenderError, match="symlink|mode"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]


def test_missing_privacy_firewall_is_rejected_before_clone_writes(tmp_path):
    repo = _template_repo(tmp_path)
    firewall = repo / "templates" / "client-llm-wiki" / ".gitignore"
    firewall.unlink()
    _git(repo, "add", "templates/client-llm-wiki/.gitignore")
    _git(repo, "commit", "-m", "test: remove required firewall")
    clone = _empty_clone(tmp_path)

    with pytest.raises(BootstrapRenderError, match="firewall"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]


@pytest.mark.parametrize(
    ("required_path", "replacement"),
    [(path, kind) for path in (".gitignore", ".claude/CLAUDE.md") for kind in ("directory", "executable")],
)
def test_privacy_firewall_requires_regular_non_executable_blobs(tmp_path, required_path, replacement):
    repo = _template_repo(tmp_path)
    firewall = repo / "templates/client-llm-wiki" / required_path
    if replacement == "directory":
        firewall.unlink()
        firewall.mkdir()
        (firewall / "child").write_text("not a firewall\n", encoding="utf-8")
    else:
        firewall.chmod(0o755)
    _git(repo, "add", "-A", "templates/client-llm-wiki")
    _git(repo, "commit", "-m", f"test: invalid {required_path}")
    clone = _empty_clone(tmp_path)

    with pytest.raises(BootstrapRenderError, match="privacy firewall"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]


@pytest.mark.parametrize("stage", ["create", "bind", "record", "write", "chmod", "final_validation"])
def test_failure_preserves_bounded_structured_residue(tmp_path, monkeypatch, stage):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    forbidden = ("unlink", "rmdir", "rename", "truncate", "ftruncate")
    for name in forbidden:
        monkeypatch.setattr(bootstrap_renderer.os, name, lambda *_a, _name=name, **_k: pytest.fail(_name))

    with pytest.raises(BootstrapRenderError) as raised:
        _render(repo, clone, stage)

    residue = raised.value.residue
    assert residue is not None
    assert (residue.clone_device, residue.clone_inode) == (clone.stat().st_dev, clone.stat().st_ino)
    assert len(residue.completed_members) <= bootstrap_renderer._RESIDUE_MEMBER_LIMIT
    assert residue.failure_stage == stage
    assert residue.template_commit == _git(repo, "rev-parse", "HEAD")
    assert residue.residue_policy == "preserved"
    assert "Do not retry" in residue.instruction
    assert sorted(path.name for path in clone.iterdir()) != [".git"]
    if stage == "final_validation":
        expected = {
            str(path.relative_to(clone))
            for path in clone.rglob("*")
            if path != clone / ".git" and clone / ".git" not in path.parents
        }
        assert set(residue.completed_members) == expected


@pytest.mark.parametrize(
    ("primitive", "stage"),
    [
        ("mkdir", "create"),
        ("open", "create"),
        ("fstat", "bind"),
        ("record", "record"),
        ("write", "write"),
        ("fchmod", "chmod"),
    ],
)
def test_real_primitive_failure_reports_exact_stage(tmp_path, monkeypatch, primitive, stage):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def fail(*_args, **_kwargs):
        raise OSError("primitive failure")

    if primitive == "record":
        monkeypatch.setattr(bootstrap_renderer, "_record_artifact", fail)
    elif primitive == "open":
        real_open = bootstrap_renderer.os.open

        def fail_created_file(name, *args, **kwargs):
            if name == ".gitignore":
                raise OSError("primitive failure")
            return real_open(name, *args, **kwargs)

        monkeypatch.setattr(bootstrap_renderer.os, "open", fail_created_file)
    elif primitive == "fstat":
        real_fstat = bootstrap_renderer.os.fstat

        def fail_created_descriptor(descriptor):
            if os.readlink(f"/proc/self/fd/{descriptor}").endswith(("/.claude", "/docs")):
                raise OSError("primitive failure")
            return real_fstat(descriptor)

        monkeypatch.setattr(bootstrap_renderer.os, "fstat", fail_created_descriptor)
    else:
        monkeypatch.setattr(bootstrap_renderer.os, primitive, fail)

    with pytest.raises(BootstrapRenderError) as raised:
        _render(repo, clone)

    assert raised.value.residue.failure_stage == stage


@pytest.mark.parametrize("failure", [RuntimeError("stop"), KeyboardInterrupt("stop"), SystemExit(9)])
def test_bound_directory_fd_closes_for_each_base_exception(tmp_path, monkeypatch, failure):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    opened: list[int] = []
    real_open = bootstrap_renderer.os.open
    real_fstat = bootstrap_renderer.os.fstat

    def recording_open(*args, **kwargs):
        descriptor = real_open(*args, **kwargs)
        if args and args[0] in {".claude", "docs"}:
            opened.append(descriptor)
        return descriptor

    def interrupt_fstat(descriptor):
        if descriptor in opened:
            raise failure
        return real_fstat(descriptor)

    monkeypatch.setattr(bootstrap_renderer.os, "open", recording_open)
    monkeypatch.setattr(bootstrap_renderer.os, "fstat", interrupt_fstat)
    with pytest.raises(BootstrapRenderError):
        _render(repo, clone)

    assert opened
    for descriptor in opened:
        with pytest.raises(OSError):
            real_fstat(descriptor)


def test_exception_payload_is_not_exposed_and_residue_json_is_bounded(tmp_path, monkeypatch):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    payload = "secret-ish\x00\n" + "x" * 10_000
    def fail_write(_descriptor, _data):
        raise RuntimeError(payload)

    monkeypatch.setattr(bootstrap_renderer, "_write_all", fail_write)
    with pytest.raises(BootstrapRenderError) as raised:
        _render(repo, clone)

    assert "secret-ish" not in str(raised.value)
    assert len(str(raised.value)) < 100
    encoded = json.dumps(raised.value.residue.__dict__ if hasattr(raised.value.residue, "__dict__") else {
        "template_commit": raised.value.residue.template_commit,
        "residue_policy": raised.value.residue.residue_policy,
        "failure_stage": raised.value.residue.failure_stage,
    })
    assert "\\u0000" not in encoded and "secret-ish" not in encoded
    with pytest.raises(BootstrapRenderError, match="only a real .git"):
        _render(repo, clone)


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(9)])
def test_base_exception_preserves_residue(tmp_path, monkeypatch, signal):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def interrupt(_descriptor, _mode):
        raise signal

    monkeypatch.setattr(bootstrap_renderer.os, "fchmod", interrupt)
    with pytest.raises(BootstrapRenderError) as raised:
        _render(repo, clone)
    assert raised.value.residue is not None
    assert raised.value.residue.uncertain_member
    assert sorted(path.name for path in clone.iterdir()) != [".git"]


def test_directory_modes_are_normalized_despite_umask(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    previous = os.umask(0o077)
    try:
        _render(repo, clone)
    finally:
        os.umask(previous)

    assert stat.S_IMODE((clone / "docs").stat().st_mode) == 0o755


def test_bind_rejects_symlink_clone(tmp_path):
    real_clone = _empty_clone(tmp_path)
    linked_clone = tmp_path / "linked-clone"
    linked_clone.symlink_to(real_clone, target_is_directory=True)

    with pytest.raises(BootstrapRenderError, match="symlink|no-follow"):
        with bind_empty_clone(linked_clone):
            pass
