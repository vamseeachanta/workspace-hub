"""Pinned-snapshot and descriptor-bound renderer tests for issue #3449."""
from __future__ import annotations

import io
from pathlib import Path
import stat
import subprocess
import tarfile

import pytest

from client_llm_wiki.bootstrap_renderer import (
    BootstrapRenderError,
    RenderTokens,
    _validated_archive_members,
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


def _tar_bytes(members: list[tarfile.TarInfo]) -> bytes:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for member in members:
            payload = b"x" if member.isreg() else b""
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload) if payload else None)
    return stream.getvalue()


def test_render_uses_committed_head_and_normalizes_modes(tmp_path):
    repo = _template_repo(tmp_path)
    clone = _empty_clone(tmp_path)
    commit = _git(repo, "rev-parse", "HEAD")
    readme = repo / "templates" / "client-llm-wiki" / "README.md"
    readme.write_text("DIRTY CONTENT\n", encoding="utf-8")
    (readme.parent / "untracked.txt").write_text("ignore me\n", encoding="utf-8")

    manifest = _render(repo, clone)

    assert manifest.template_commit == commit
    assert (clone / "README.md").read_text() == (
        "# example-co\nexample-org/llm-wiki-example-co\n"
    )
    assert not (clone / "untracked.txt").exists()
    assert stat.S_IMODE((clone / "README.md").stat().st_mode) == 0o644
    assert stat.S_IMODE((clone / "verify.sh").stat().st_mode) == 0o755
    assert (clone / ".git" / "sentinel").read_text() == "git metadata\n"


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
        "example-co|EXAMPLE-CO|example-org/llm-wiki-example-co|"
        "not-mounted|false|<PROJECT_SHORT_NAME>\n"
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


@pytest.mark.parametrize(
    ("name", "member_type"),
    [
        ("../escape", tarfile.REGTYPE),
        ("/absolute", tarfile.REGTYPE),
        ("unsafe-link", tarfile.SYMTYPE),
        ("unsafe-fifo", tarfile.FIFOTYPE),
        ("unsafe-device", tarfile.CHRTYPE),
    ],
)
def test_archive_parser_rejects_traversal_links_and_special_files(name, member_type):
    member = tarfile.TarInfo(name)
    member.type = member_type

    with pytest.raises(BootstrapRenderError):
        _validated_archive_members(_tar_bytes([member]), {name: 0o100644})


def test_archive_parser_rejects_duplicate_members():
    first = tarfile.TarInfo("README.md")
    second = tarfile.TarInfo("README.md")

    with pytest.raises(BootstrapRenderError, match="duplicate"):
        _validated_archive_members(
            _tar_bytes([first, second]),
            {"README.md": 0o100644},
        )


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


def test_bind_rejects_symlink_clone(tmp_path):
    real_clone = _empty_clone(tmp_path)
    linked_clone = tmp_path / "linked-clone"
    linked_clone.symlink_to(real_clone, target_is_directory=True)

    with pytest.raises(BootstrapRenderError, match="symlink|no-follow"):
        with bind_empty_clone(linked_clone):
            pass
