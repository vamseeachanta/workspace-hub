"""Behavioral regressions for effective Git hooks (issue #3852).

Protocol basis: git-scm.com/docs/githooks, DESCRIPTION and pre-push, accessed
2026-10-22. Expected dispatch is a hand calculation: a wrapper passes each
argument and input byte unchanged, and returns the child's exit status. File
modes use Python's octal permission notation; they are fixture permissions,
not engineering acceptance limits.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INSTALL = ROOT / "scripts/setup/install-all-hooks.sh"
ENFORCE = ROOT / "scripts/enforcement/install-hooks.sh"


@pytest.fixture(autouse=True)
def isolated_git(monkeypatch, tmp_path):
    """Never let a caller's repository bindings or global hooks target live Git."""
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("TMPDIR", str(tmp_path))


def git(repo, *args, input=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args], input=input, text=True,
        capture_output=True, check=True,
    ).stdout.strip()


def make_repo(tmp_path, hooks_path=None, worktree=False):
    repo = tmp_path / "repository with spaces"
    repo.mkdir()
    git(repo, "init", "-q")
    if worktree:
        # An empty tree and parentless commit are independent literal fixtures.
        # hash-object avoids invoking commit hooks or changing Git identity.
        tree = git(repo, "hash-object", "-w", "-t", "tree", "--stdin", input="")
        commit = git(
            repo, "hash-object", "-w", "-t", "commit", "--stdin",
            input=f"tree {tree}\nauthor Fixture <fixture> 0 +0000\n"
                  "committer Fixture <fixture> 0 +0000\n\nfixture\n",
        )
        git(repo, "update-ref", "HEAD", commit)
        target = tmp_path / "linked worktree"
        git(repo, "worktree", "add", "--detach", str(target), "HEAD")
        repo = target
    if hooks_path is not None:
        git(repo, "config", "core.hooksPath", str(hooks_path))
    source = repo / "scripts/hooks"
    source.mkdir(parents=True)
    (source / "pre-push.sh").write_text(
        '#!/usr/bin/env bash\n'
        'printf "%s\\n" "$@" > args.txt\n'
        'cat > refs.txt\n'
        'exit "${FIXTURE_RESULT:-0}"\n'
    )
    (source / "track-skill-patches.sh").write_text("exit 0\n")
    return repo


def hook_dir(repo):
    return Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))


def run(script, repo, *args):
    return subprocess.run(
        ["bash", str(script), *args], cwd=repo, text=True, capture_output=True, check=False,
    )


def snapshot(path):
    return {
        str(p.relative_to(path)): (p.read_bytes(), p.stat().st_mode)
        for p in path.rglob("*") if p.is_file()
    }


@pytest.mark.parametrize("kind", ["default", "relative", "absolute", "worktree", "worktree-relative"])
@pytest.mark.parametrize("child_status", ["0", "1"])
def test_installs_event_at_effective_path_and_git_dispatches(tmp_path, kind, child_status, monkeypatch):
    custom = {"relative": "custom hooks", "absolute": tmp_path / "external hooks",
              "worktree-relative": "custom hooks"}.get(kind)
    repo = make_repo(tmp_path, custom, worktree=kind.startswith("worktree"))
    nested = repo / "nested"
    nested.mkdir()
    result = run(INSTALL, nested)
    assert result.returncode == 0, result.stderr
    installed = hook_dir(repo) / "pre-push"
    assert installed.is_file()
    assert os.access(installed, os.X_OK)
    assert not (hook_dir(repo) / "track-skill-patches.sh").exists()
    before = snapshot(hook_dir(repo))
    assert run(INSTALL, repo, "--quiet").returncode == 0
    assert snapshot(hook_dir(repo)) == before

    # Two synthetic refs, including deletion, come from the pre-push grammar.
    # OID strings are tokens only: this stub never resolves objects.
    refs = "refs/heads/topic a refs/heads/topic b\n(delete) 0 refs/heads/old c\n"
    input_file = tmp_path / "push-input"
    input_file.write_text(refs)
    monkeypatch.setenv("FIXTURE_RESULT", child_status)  # Git: any nonzero status rejects.
    result = subprocess.run(
        ["git", "-C", str(repo), "hook", "run", "--to-stdin", str(input_file),
         "pre-push", "--", "origin", "destination with spaces"],
        capture_output=True, text=True, check=False,
    )
    assert (result.returncode == 0) == (child_status == "0")
    assert (repo / "refs.txt").read_text() == refs
    assert (repo / "args.txt").read_text() == "origin\ndestination with spaces\n"


@pytest.mark.parametrize("existing", ["regular", "symlink", "directory", "managed-lookalike"])
def test_preserves_unknown_existing_hook(tmp_path, existing):
    repo = make_repo(tmp_path)
    target = hook_dir(repo) / "pre-push"
    content = "#!/bin/sh\nexit 1\n"
    if existing == "directory":
        target.mkdir()
    elif existing == "symlink":
        original = tmp_path / "original"
        original.write_text(content)
        target.symlink_to(original)
    else:
        if existing == "managed-lookalike":
            content += "# Managed by install-all-hooks.sh\n"
        target.write_text(content)
    result = run(INSTALL, repo)
    assert result.returncode != 0
    if existing == "directory":
        assert target.is_dir()
    else:
        assert target.read_text() == content
    if existing == "symlink":
        assert target.is_symlink()


def test_dry_run_creates_nothing(tmp_path):
    repo = make_repo(tmp_path, "missing hooks")
    before = snapshot(repo)
    result = run(INSTALL, repo, "--dry-run")
    assert result.returncode == 0, result.stderr
    assert snapshot(repo) == before
    assert not hook_dir(repo).exists()


def test_check_reports_missing_disabled_and_current(tmp_path):
    repo = make_repo(tmp_path)
    assert run(INSTALL, repo, "--check").returncode != 0
    assert run(INSTALL, repo).returncode == 0
    assert run(INSTALL, repo, "--check").returncode == 0
    target = hook_dir(repo) / "pre-push"
    target.chmod(0o644)
    assert run(INSTALL, repo, "--check").returncode != 0
    assert run(INSTALL, repo).returncode == 0
    assert os.access(target, os.X_OK)


def test_missing_source_does_not_install_wrapper(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "scripts/hooks/pre-push.sh").rename(repo / "scripts/hooks/unused.sh")
    assert run(INSTALL, repo).returncode != 0
    assert not (hook_dir(repo) / "pre-push").exists()


@pytest.mark.parametrize("kind", ["relative", "absolute", "worktree"])
def test_enforcement_uses_effective_path(tmp_path, kind):
    custom = {"relative": "custom hooks", "absolute": tmp_path / "external hooks"}.get(kind)
    repo = make_repo(tmp_path, custom, worktree=kind == "worktree")
    hooks = hook_dir(repo)
    hooks.mkdir(exist_ok=True, parents=True)
    (hooks / "pre-push").write_text(
        '#!/usr/bin/env bash\nREPO_ROOT="$(git rev-parse --show-toplevel)"\n'
        'OVERALL_EXIT=0\nPUSH_LINES=()\n'
        '# <<INSTALL_HOOKS_EXTENSION_POINT>>\nexit "$OVERALL_EXIT"\n'
    )
    source = repo / "scripts/enforcement"
    source.mkdir()
    (source / "enforcement-env.sh").write_text("export FIXTURE_ENFORCEMENT=1\n")
    result = run(ENFORCE, repo)
    assert result.returncode == 0, result.stderr
    assert (hooks / "enforcement-env").read_text() == "export FIXTURE_ENFORCEMENT=1\n"
    text = (hooks / "pre-push").read_text()
    assert "--git-path hooks/enforcement-env" in text
    before = snapshot(hooks)
    assert run(ENFORCE, repo).returncode == 0
    assert snapshot(hooks) == before


def test_enforcement_dry_run_preserves_dead_tail_and_modes(tmp_path):
    repo = make_repo(tmp_path)
    hooks = hook_dir(repo)
    (hooks / "pre-push").write_text(
        '#!/usr/bin/env bash\n# <<INSTALL_HOOKS_EXTENSION_POINT>>\nexit 0\n'
        '# enforcement-env stranded below exit\n'
    )
    before = snapshot(hooks)
    result = run(ENFORCE, repo, "--dry-run")
    assert result.returncode == 0, result.stderr
    assert snapshot(hooks) == before


def test_tracked_push_hook_sources_effective_environment(tmp_path):
    repo = make_repo(tmp_path, "custom hooks", worktree=True)
    hooks = hook_dir(repo)
    hooks.mkdir()
    (hooks / "enforcement-env").write_text("export FIXTURE_ENFORCEMENT=present\n")
    source = repo / "scripts/enforcement"
    source.mkdir()
    (source / "require-review-on-push.sh").write_text(
        'test "${FIXTURE_ENFORCEMENT:-}" = present\n'
    )
    shutil.copy2(ROOT / "scripts/hooks/pre-push.sh", repo / "scripts/hooks/pre-push.sh")
    assert run(INSTALL, repo).returncode == 0
    env = os.environ.copy()
    env["PRE_PUSH_CHANGED_FILES"] = "docs/example.md"
    env["REVIEW_GATE_STRICT"] = "1"
    result = subprocess.run(
        ["bash", str(hooks / "pre-push"), "origin", "destination"], cwd=repo,
        input="refs/heads/topic a refs/heads/topic b\n", env=env,
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr


def test_setup_then_enforcement_keeps_managed_wrapper(tmp_path):
    repo = make_repo(tmp_path, "custom hooks")
    source = repo / "scripts/enforcement"
    source.mkdir()
    (source / "enforcement-env.sh").write_text("export FIXTURE_ENFORCEMENT=1\n")
    setup = repo / "scripts/setup"
    setup.mkdir()
    shutil.copy2(INSTALL, setup / INSTALL.name)
    assert run(INSTALL, repo).returncode == 0
    target = hook_dir(repo) / "pre-push"
    before = target.read_bytes()
    result = run(ENFORCE, repo)
    assert result.returncode == 0, result.stderr
    assert target.read_bytes() == before
    assert (hook_dir(repo) / "enforcement-env").exists()


def test_enforcement_dry_run_preserves_nonexecutable_hook(tmp_path):
    repo = make_repo(tmp_path)
    target = hook_dir(repo) / "pre-push"
    target.write_text('#!/bin/bash\n# <<INSTALL_HOOKS_EXTENSION_POINT>>\nexit 0\n')
    target.chmod(0o644)
    before = snapshot(hook_dir(repo))
    assert run(ENFORCE, repo, "--dry-run").returncode == 0
    assert snapshot(hook_dir(repo)) == before
