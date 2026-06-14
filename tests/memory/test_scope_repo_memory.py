"""TDD for scope-repo-memory.sh (epic #3084 context-flow scaffolder)."""
from __future__ import annotations
import pathlib
import subprocess

import pytest

HUB = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = HUB / "scripts" / "memory" / "scope-repo-memory.sh"
TEMPLATE = HUB / ".claude" / "memory" / "_template-repo-memory" / "MEMORY.md"


def _git_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    repo = tmp_path / "myrepo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def _run(repo: pathlib.Path, *flags: str):
    return subprocess.run(
        ["bash", str(SCRIPT), str(repo), *flags],
        capture_output=True, text=True,
        env={"SCOPE_TEMPLATE": str(TEMPLATE), "PATH": "/usr/bin:/bin"},
    )


def test_creates_skeleton(tmp_path):
    repo = _git_repo(tmp_path)
    r = _run(repo)
    assert r.returncode == 0, r.stderr
    mem = repo / ".claude" / "memory" / "MEMORY.md"
    assert mem.exists()
    assert "myrepo" in mem.read_text()  # template substitution


def test_idempotent_no_clobber(tmp_path):
    repo = _git_repo(tmp_path)
    mem = repo / ".claude" / "memory"
    mem.mkdir(parents=True)
    (mem / "MEMORY.md").write_text("SENTINEL — do not overwrite\n")
    r = _run(repo)
    assert r.returncode == 0
    assert (mem / "MEMORY.md").read_text() == "SENTINEL — do not overwrite\n"


def test_gitignore_negation_added(tmp_path):
    repo = _git_repo(tmp_path)
    (repo / ".gitignore").write_text("node_modules/\nmemory/\n")
    _run(repo)
    gi = (repo / ".gitignore").read_text()
    assert "!.claude/memory/" in gi


def test_gitignore_no_false_add(tmp_path):
    repo = _git_repo(tmp_path)
    (repo / ".gitignore").write_text("node_modules/\n*.log\n")
    _run(repo)
    gi = (repo / ".gitignore").read_text()
    assert "!.claude/memory/" not in gi  # no blanket memory/ rule → no negation


def test_claude_md_created_when_missing(tmp_path):
    repo = _git_repo(tmp_path)
    assert not (repo / "CLAUDE.md").exists()
    _run(repo)
    cm = repo / "CLAUDE.md"
    assert cm.exists()
    text = cm.read_text()
    assert "Memory: read THIS repo" in text
    assert "Inherits workspace-hub" in text
    assert len(text.splitlines()) <= 20  # within harness cap


def test_claude_md_precedence_added(tmp_path):
    repo = _git_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("# My Repo\n> some rules\n")
    _run(repo)
    cm = (repo / "CLAUDE.md").read_text()
    assert "Memory: read THIS repo" in cm


def test_claude_md_cap_respected(tmp_path):
    repo = _git_repo(tmp_path)
    body = "\n".join(f"line {i}" for i in range(20)) + "\n"  # 20 lines, no headroom
    (repo / "CLAUDE.md").write_text(body)
    _run(repo)
    cm = (repo / "CLAUDE.md").read_text()
    assert "Memory: read THIS repo" not in cm  # cap respected, not appended
    assert cm == body  # unchanged


def test_dry_run_writes_nothing(tmp_path):
    repo = _git_repo(tmp_path)
    (repo / ".gitignore").write_text("memory/\n")
    (repo / "CLAUDE.md").write_text("# R\n")
    r = _run(repo, "--dry-run")
    assert r.returncode == 0
    assert not (repo / ".claude" / "memory" / "MEMORY.md").exists()
    assert "!.claude/memory/" not in (repo / ".gitignore").read_text()
    assert "Memory: read THIS repo" not in (repo / "CLAUDE.md").read_text()


def test_rejects_non_git(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    r = _run(plain)
    assert r.returncode == 3


def test_repo_name_from_origin_not_dirname(tmp_path):
    # Simulates running against a worktree dir whose basename != repo name.
    repo = tmp_path / "wt-something"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/acme/realrepo.git"],
        cwd=repo, check=True,
    )
    _run(repo)
    mem = (repo / ".claude" / "memory" / "MEMORY.md").read_text()
    assert "realrepo" in mem
    assert "wt-something" not in mem
