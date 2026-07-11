"""Pinned-snapshot and descriptor-bound renderer tests for issue #3449."""

from __future__ import annotations

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
        return render_committed_template(
            bound,
            repo,
            _tokens(),
            _failpoint=failpoint,
        )


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


def test_post_bind_clone_replacement_cannot_redirect_writes(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    held_clone = tmp_path / "held-clone"

    def replace_clone(event, _relative_path, _fd):
        if event != "clone_bound":
            return
        clone.rename(held_clone)
        (clone / ".git").mkdir(parents=True)
        (clone / ".git" / "victim").write_text("untouched\n", encoding="utf-8")

    with pytest.raises(BootstrapRenderError, match="identity"):
        _render(repo, clone, replace_clone)

    assert (clone / ".git" / "victim").read_text() == "untouched\n"
    assert sorted(path.name for path in clone.iterdir()) == [".git"]
    assert sorted(path.name for path in held_clone.iterdir()) == [".git"]


def test_forced_failure_removes_only_matching_created_entries(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    bound_count = 0

    def fail_after_two(event, _relative_path, _fd):
        nonlocal bound_count
        if event == "target_member_bound":
            bound_count += 1
            if bound_count == 2:
                raise RuntimeError("injected install failure")

    with pytest.raises(BootstrapRenderError, match="injected install failure"):
        _render(repo, clone, fail_after_two)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]


def test_stage_bound_failure_removes_the_bound_stage(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def fail_stage(event, _relative_path, _fd):
        if event == "stage_bound":
            raise RuntimeError("stage bind failure")

    with pytest.raises(BootstrapRenderError, match="stage bind failure"):
        _render(repo, clone, fail_stage)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]
    assert not list(tmp_path.glob(".client-wiki-stage-*"))


def test_partial_write_failure_is_removed_from_the_ledger(tmp_path, monkeypatch):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def fail_after_partial_write(descriptor, data):
        os.write(descriptor, data[:1])
        raise OSError("simulated disk full")

    monkeypatch.setattr(bootstrap_renderer, "_write_all", fail_after_partial_write)
    with pytest.raises(BootstrapRenderError, match="simulated disk full"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]
    assert not list(tmp_path.glob(".client-wiki-stage-*"))


def test_directory_chmod_failure_is_removed_from_the_ledger(tmp_path, monkeypatch):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    real_fchmod = os.fchmod
    failed = False

    def fail_first_directory(descriptor, mode):
        nonlocal failed
        if not failed and stat.S_ISDIR(os.fstat(descriptor).st_mode):
            failed = True
            raise OSError("simulated chmod failure")
        real_fchmod(descriptor, mode)

    monkeypatch.setattr(bootstrap_renderer.os, "fchmod", fail_first_directory)
    with pytest.raises(BootstrapRenderError, match="simulated chmod failure"):
        _render(repo, clone)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]
    assert not list(tmp_path.glob(".client-wiki-stage-*"))


def test_stage_interference_aborts_before_target_install(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def add_foreign_stage_child(event, relative_path, descriptor):
        if event != "stage_member_bound" or relative_path != "docs":
            return
        child = os.open("foreign", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=descriptor)
        os.close(child)

    with pytest.raises(BootstrapRenderError, match="stage cleanup"):
        _render(repo, clone, add_foreign_stage_child)

    assert sorted(path.name for path in clone.iterdir()) == [".git"]
    residue = list(tmp_path.glob(".client-wiki-stage-*"))
    assert len(residue) == 1
    assert (residue[0] / "docs" / "foreign").exists()


def test_replaced_bound_file_and_victim_are_never_deleted(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    moved = clone / "rendered-readme-moved"

    def replace_file(event, relative_path, _fd):
        if event != "target_member_bound" or relative_path != "README.md":
            return
        (clone / "README.md").rename(moved)
        (clone / "README.md").write_text("victim sentinel\n", encoding="utf-8")
        raise RuntimeError("replace bound file")

    with pytest.raises(BootstrapRenderError, match="replace bound file"):
        _render(repo, clone, replace_file)

    assert (clone / "README.md").read_text() == "victim sentinel\n"
    assert moved.read_text().startswith("# example-co")
    assert (clone / ".git" / "sentinel").read_text() == "git metadata\n"


def test_nonempty_created_directory_is_left_as_bounded_residue(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def make_nonempty(event, relative_path, _fd):
        if event != "target_member_bound" or relative_path != "docs":
            return
        (clone / "docs" / "intruder").write_text("foreign\n", encoding="utf-8")
        raise RuntimeError("foreign child")

    with pytest.raises(BootstrapRenderError, match="foreign child"):
        _render(repo, clone, make_nonempty)

    assert (clone / "docs" / "intruder").read_text() == "foreign\n"
    assert (clone / ".git" / "sentinel").read_text() == "git metadata\n"


def test_unexpected_post_bind_member_causes_final_inventory_failure(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)

    def add_unexpected(event, _relative_path, _fd):
        if event == "before_final_revalidation":
            (clone / "unexpected").write_text("foreign\n", encoding="utf-8")

    with pytest.raises(BootstrapRenderError, match="inventory"):
        _render(repo, clone, add_unexpected)

    assert (clone / "unexpected").read_text() == "foreign\n"
    assert (clone / ".git" / "sentinel").read_text() == "git metadata\n"


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
