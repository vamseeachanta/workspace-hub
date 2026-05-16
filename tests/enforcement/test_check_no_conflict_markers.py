"""Tests for scripts/enforcement/check-no-conflict-markers.sh (#2722).

26 cases derived from docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md
TDD: tests written before implementation; expected to FAIL initially.

Fixture strategy: each test builds a hermetic git repo under tmp_path,
stages content, and invokes the script via subprocess. Hermeticity ensures
no cross-test contamination and no dependence on the host workspace-hub state.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DETECTION_SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-no-conflict-markers.sh"
INSTALLER_SCRIPT = REPO_ROOT / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
DRIFT_SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-pre-commit-hook-drift.sh"
MANIFEST = REPO_ROOT / "scripts" / "agents" / "tier1-repos.sh"


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """A hermetic git repo with an initial commit on `main`."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "commit.gpgsign", "false"], check=True
    )
    (tmp_path / "README.md").write_text("# init\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "README.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-q", "-m", "init", "--no-verify"],
        check=True,
    )
    return tmp_path


def _stage(repo: Path, path: str, content: str) -> None:
    """Write content to repo/path and `git add` it."""
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    subprocess.run(["git", "-C", str(repo), "add", "--", path], check=True)


def _run_check(repo: Path, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke the detection script with cwd=repo."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(DETECTION_SCRIPT)],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
    )


# ── Detection-script tests (16 cases) ─────────────────────────────────────


def test_clean_file_passes(tmp_repo: Path) -> None:
    _stage(tmp_repo, "ok.py", "def foo():\n    return 1\n")
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_canonical_markers_fail(tmp_repo: Path) -> None:
    body = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> branch\n"
    _stage(tmp_repo, "conflict.py", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout
    assert "conflict.py" in (r.stdout + r.stderr)


def test_lt_anchor_no_trailing_space_fails(tmp_repo: Path) -> None:
    # diff3/recursive merge-driver style: no trailing space after the anchor
    body = "<<<<<<<\nours\n=======\ntheirs\n>>>>>>>\n"
    _stage(tmp_repo, "conflict.txt", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout


def test_setext_heading_passes(tmp_repo: Path) -> None:
    # markdown setext H1 underline with no <<<<<<< or >>>>>>> co-occurs
    body = "Title\n=======\nbody text\n"
    _stage(tmp_repo, "doc.md", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_shell_banner_passes(tmp_repo: Path) -> None:
    body = "#!/usr/bin/env bash\n# =====================\n# Section header\n# =====================\n"
    _stage(tmp_repo, "script.sh", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_stage_aware_during_merge_clean_passes(tmp_repo: Path) -> None:
    # Simulate an active merge by creating .git/MERGE_MSG
    git_dir = subprocess.run(
        ["git", "-C", str(tmp_repo), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (tmp_repo / git_dir / "MERGE_MSG").write_text("Merge branch 'feature'\n")
    _stage(tmp_repo, "resolved.py", "def ok():\n    return 1\n")
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_stage_aware_during_merge_marker_fails(tmp_repo: Path) -> None:
    # During merge, staged content with markers must still FAIL — this is the r3 fix
    git_dir = subprocess.run(
        ["git", "-C", str(tmp_repo), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (tmp_repo / git_dir / "MERGE_MSG").write_text("Merge branch 'feature'\n")
    body = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> branch\n"
    _stage(tmp_repo, "half-resolved.py", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout


def test_per_line_sentinel_exempts_line(tmp_repo: Path) -> None:
    body = (
        "echo before\n"
        "echo '<<<<<<< HEAD' # CONFLICT_MARKER_FORENSIC_OK\n"
        "echo middle\n"
        "echo '>>>>>>> branch' # CONFLICT_MARKER_FORENSIC_OK\n"
        "echo after\n"
    )
    _stage(tmp_repo, "doc-marker.sh", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_per_line_sentinel_no_blanket_exempt(tmp_repo: Path) -> None:
    # Sentinel on one line does NOT exempt a real marker on another line
    body = (
        "echo '<<<<<<< x' # CONFLICT_MARKER_FORENSIC_OK\n"
        "<<<<<<< HEAD\n"  # real marker — NO sentinel
        "ours\n"
        "=======\n"
        "theirs\n"
        ">>>>>>> branch\n"
    )
    _stage(tmp_repo, "mixed.sh", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout


def test_sentinel_must_be_staged_not_working_tree(tmp_repo: Path) -> None:
    # Stage marker content WITHOUT sentinel; then add sentinel to working tree only
    body = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> branch\n"
    _stage(tmp_repo, "bypass.txt", body)
    # Now write sentinel to working tree but DON'T re-stage
    (tmp_repo / "bypass.txt").write_text(body + "# CONFLICT_MARKER_FORENSIC_OK\n")
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout + r.stderr


def test_unstaged_marker_ignored(tmp_repo: Path) -> None:
    # File with markers in working tree but never staged
    (tmp_repo / "wt.txt").write_text("<<<<<<< x\n=======\n>>>>>>> y\n")
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_multiple_violations_all_cited(tmp_repo: Path) -> None:
    body = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> branch\n"
    _stage(tmp_repo, "a.py", body)
    _stage(tmp_repo, "b.py", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout
    combined = r.stdout + r.stderr
    assert "a.py" in combined and "b.py" in combined


def test_deleted_file_skipped(tmp_repo: Path) -> None:
    # Add and commit a marker-containing file, then stage its deletion
    body = "<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> z\n"
    (tmp_repo / "to-delete.txt").write_text(body)
    subprocess.run(["git", "-C", str(tmp_repo), "add", "to-delete.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_repo), "commit", "-q", "-m", "add file", "--no-verify"],
        check=True,
    )
    subprocess.run(["git", "-C", str(tmp_repo), "rm", "to-delete.txt"], check=True)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_renamed_file_checked(tmp_repo: Path) -> None:
    body = "<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> z\n"
    (tmp_repo / "old.txt").write_text(body)
    subprocess.run(["git", "-C", str(tmp_repo), "add", "old.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_repo), "commit", "-q", "-m", "add", "--no-verify"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_repo), "mv", "old.txt", "new.txt"], check=True
    )
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout
    assert "new.txt" in (r.stdout + r.stderr)


# ── r4 (Gemini-driven) tests ──────────────────────────────────────────────


def test_markdown_blockquote_passes(tmp_repo: Path) -> None:
    # 7-level nested blockquote `>>>>>>>` at column 0 — no <<<<<<< co-occurrence
    body = ">>>>>>> deeply nested blockquote\nmore text\n"
    _stage(tmp_repo, "post.md", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_co_occurrence_required(tmp_repo: Path) -> None:
    # <<<<<<< alone (no >>>>>>>) — debatable false-negative per plan §Risks; documented
    body = "<<<<<<< HEAD\nbut no closing marker\n"
    _stage(tmp_repo, "lonely.txt", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_filename_with_space_handled(tmp_repo: Path) -> None:
    # NUL-delimited iteration handles filenames with spaces (Gemini r2 #8)
    body = "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> branch\n"
    _stage(tmp_repo, "my file.py", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "my file.py" in (r.stdout + r.stderr)


def test_per_file_sentinel_restricted_path(tmp_repo: Path) -> None:
    # docs/plans/ is a restricted-path; per-file sentinel honored there
    body = (
        "<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->\n"
        "\n"
        "# Plan example\n"
        "\n"
        "```\n"
        "<<<<<<< HEAD\n"
        "example marker\n"
        "=======\n"
        "theirs\n"
        ">>>>>>> branch\n"
        "```\n"
    )
    _stage(tmp_repo, "docs/plans/example.md", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 0, r.stderr + r.stdout


def test_per_file_sentinel_arbitrary_path_rejected(tmp_repo: Path) -> None:
    # Same sentinel in src/main.py — NOT a restricted path → no exemption
    body = (
        "# <!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->\n"
        "<<<<<<< HEAD\n"
        "ours\n"
        "=======\n"
        "theirs\n"
        ">>>>>>> branch\n"
    )
    _stage(tmp_repo, "src/main.py", body)
    r = _run_check(tmp_repo)
    assert r.returncode == 1, r.stdout


# ── Installer tests (5 cases) ─────────────────────────────────────────────


@pytest.fixture
def tmp_workspace_with_sibling(tmp_path: Path) -> tuple[Path, Path]:
    """Create a mock workspace-hub-like structure with one sibling repo.

    Returns (ws_root, sibling_root). The installer's canonical path resolution
    is `$WS_ROOT/../$repo` so we lay them out as siblings.
    """
    parent = tmp_path / "parent"
    parent.mkdir()
    ws_root = parent / "workspace-hub"
    sibling = parent / "digitalmodel"
    for repo in (ws_root, sibling):
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@e.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "T"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True
        )
        (repo / "README.md").write_text("# init\n")
        subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "-m", "init", "--no-verify"],
            check=True,
        )
    # Vendor the canonical detection script + a minimal manifest into ws_root
    enf_dir = ws_root / "scripts" / "enforcement"
    enf_dir.mkdir(parents=True)
    shutil.copy(DETECTION_SCRIPT, enf_dir / "check-no-conflict-markers.sh")
    (enf_dir / "check-no-conflict-markers.sh").chmod(0o755)
    agents_dir = ws_root / "scripts" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "tier1-repos.sh").write_text(
        'TIER1_REPOS=(\n  "workspace-hub"\n  "digitalmodel"\n)\n'
    )
    shutil.copy(INSTALLER_SCRIPT, agents_dir / "install-pre-commit-hook-cross-repo.sh")
    (agents_dir / "install-pre-commit-hook-cross-repo.sh").chmod(0o755)
    shutil.copy(DRIFT_SCRIPT, enf_dir / "check-pre-commit-hook-drift.sh")
    (enf_dir / "check-pre-commit-hook-drift.sh").chmod(0o755)
    return ws_root, sibling


def test_install_idempotent(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    subprocess.run(["bash", str(installer)], cwd=ws_root, check=True)
    pre_commit = sibling / ".git" / "hooks" / "pre-commit"
    first_content = pre_commit.read_text()
    subprocess.run(["bash", str(installer)], cwd=ws_root, check=True)
    second_content = pre_commit.read_text()
    assert first_content == second_content
    # Wiring sentinel appears exactly once
    assert second_content.count("check-no-conflict-markers") == 1


def test_install_skips_dirty_sibling(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    # Make sibling dirty in scripts/enforcement/
    enf = sibling / "scripts" / "enforcement"
    enf.mkdir(parents=True)
    (enf / "stub.sh").write_text("# dirty\n")
    subprocess.run(["git", "-C", str(sibling), "add", "scripts/enforcement/stub.sh"], check=True)
    # Leave it staged but not committed → dirty index
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    r = subprocess.run(
        ["bash", str(installer)], cwd=ws_root, capture_output=True, text=True
    )
    # Should NOT exit non-zero (skip is graceful), and should emit WARN
    assert "WARN" in (r.stdout + r.stderr) or "dirty" in (r.stdout + r.stderr).lower()
    # Did not overwrite the sibling's vendored content (still our 'dirty' content)
    assert (enf / "stub.sh").read_text() == "# dirty\n"


def test_install_creates_stub_with_REPO_ROOT(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    # Ensure sibling has no pre-commit hook
    pre_commit = sibling / ".git" / "hooks" / "pre-commit"
    if pre_commit.exists():
        pre_commit.unlink()
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    subprocess.run(["bash", str(installer)], cwd=ws_root, check=True)
    content = pre_commit.read_text()
    assert "REPO_ROOT" in content
    assert "git rev-parse --show-toplevel" in content


def test_worktree_install_uses_git_dir(tmp_workspace_with_sibling, tmp_path: Path) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    # Replace sibling with a git worktree (so .git is a file, not a directory)
    parent = ws_root.parent
    # Create a "real" repo elsewhere, then worktree-add into sibling's path
    real_repo = parent.parent / "real-digitalmodel"
    real_repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(real_repo)], check=True)
    subprocess.run(["git", "-C", str(real_repo), "config", "user.email", "t@e.com"], check=True)
    subprocess.run(["git", "-C", str(real_repo), "config", "user.name", "T"], check=True)
    subprocess.run(
        ["git", "-C", str(real_repo), "config", "commit.gpgsign", "false"], check=True
    )
    (real_repo / "README.md").write_text("# init\n")
    subprocess.run(["git", "-C", str(real_repo), "add", "README.md"], check=True)
    subprocess.run(
        ["git", "-C", str(real_repo), "commit", "-q", "-m", "init", "--no-verify"],
        check=True,
    )
    shutil.rmtree(sibling)
    subprocess.run(
        ["git", "-C", str(real_repo), "worktree", "add", "-b", "wt-branch", str(sibling)],
        check=True,
    )
    assert (sibling / ".git").is_file()  # confirm worktree layout
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    r = subprocess.run(
        ["bash", str(installer)], cwd=ws_root, capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr + r.stdout
    # Hook should land in the real git dir's hooks folder, not in sibling/.git/hooks
    common_dir = subprocess.run(
        ["git", "-C", str(sibling), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    pre_commit = Path(common_dir) / "hooks" / "pre-commit"
    if not pre_commit.is_absolute():
        pre_commit = sibling / common_dir / "hooks" / "pre-commit"
    assert pre_commit.exists(), f"hook missing at {pre_commit}"
    assert "check-no-conflict-markers" in pre_commit.read_text()


# ── Drift-check tests (3 cases) ───────────────────────────────────────────


def test_drift_detected(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    subprocess.run(["bash", str(installer)], cwd=ws_root, check=True)
    # Tamper with sibling's vendored copy
    vendored = sibling / "scripts" / "enforcement" / "check-no-conflict-markers.sh"
    vendored.write_text("#!/usr/bin/env bash\nexit 0  # tampered\n")
    drift = ws_root / "scripts" / "enforcement" / "check-pre-commit-hook-drift.sh"
    r = subprocess.run(
        ["bash", str(drift)], cwd=ws_root, capture_output=True, text=True
    )
    assert r.returncode == 1, r.stdout
    assert "digitalmodel" in (r.stdout + r.stderr)


def test_drift_missing_copy_fails(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    # Don't install; sibling has no vendored copy
    drift = ws_root / "scripts" / "enforcement" / "check-pre-commit-hook-drift.sh"
    r = subprocess.run(
        ["bash", str(drift)], cwd=ws_root, capture_output=True, text=True
    )
    assert r.returncode == 1, r.stdout
    assert "missing" in (r.stdout + r.stderr).lower()


def test_drift_clean_passes(tmp_workspace_with_sibling) -> None:
    ws_root, sibling = tmp_workspace_with_sibling
    installer = ws_root / "scripts" / "agents" / "install-pre-commit-hook-cross-repo.sh"
    subprocess.run(["bash", str(installer)], cwd=ws_root, check=True)
    drift = ws_root / "scripts" / "enforcement" / "check-pre-commit-hook-drift.sh"
    r = subprocess.run(
        ["bash", str(drift)], cwd=ws_root, capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr + r.stdout
