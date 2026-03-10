"""
Tests for WRK-1097: unclaimed-but-active item detection.

Tests cover:
1. pending + lock age 30min → UNCLAIMED_ACTIVE (not HIGH_UNBLOCKED)
2. pending + lock age 3h → HIGH_UNBLOCKED (stale, not unclaimed)
3. pending + no lock → HIGH_UNBLOCKED (normal)
4. pending + lock age exactly 7200s → stale boundary (not UNCLAIMED_ACTIVE)
5. active-sessions.sh: item in pending/ + lock age 30min → reported as unclaimed
6. active-sessions.sh: item in working/ + lock age 30min → reported as claimed
7. active-sessions.sh: lock age > 2h → skipped (stale)
8. start_stage.py: stage 9 + item in pending/ → sys.exit(1), stderr has claim message
9. start_stage.py: stage 9 + item in working/ → no error (exit 0)
10. start_stage.py: stage 2 + item in pending/ → no error (pre-claim OK)
"""

from __future__ import annotations

import datetime
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ── helpers ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _make_lock(assets_dir: Path, wrk_id: str, age_seconds: int) -> Path:
    """Write a session-lock.yaml with locked_at = now - age_seconds."""
    ev = assets_dir / wrk_id / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    locked_at = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=age_seconds)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    lock_path = ev / "session-lock.yaml"
    lock_path.write_text(
        f"wrk_id: {wrk_id}\n"
        f"session_pid: 99999\n"
        f"hostname: test-host\n"
        f'locked_at: "{locked_at}"\n'
        f"status: in_progress\n"
    )
    return lock_path


def _make_wrk_md(queue_dir: Path, location: str, wrk_id: str) -> Path:
    """Write a minimal WRK markdown file in the given queue subdirectory."""
    folder = queue_dir / location
    folder.mkdir(parents=True, exist_ok=True)
    md = folder / f"{wrk_id}.md"
    md.write_text(
        textwrap.dedent(
            f"""\
            ---
            id: {wrk_id}
            title: Test item {wrk_id}
            status: pending
            priority: high
            category: harness
            subcategory: testing
            computer: ace-linux-1
            blocked_by: []
            ---
            """
        )
    )
    return md


def _run_whats_next(tmp_queue: Path, wrk_assets: Path) -> subprocess.CompletedProcess:
    """Run whats-next.sh pointing at a tmp queue/assets setup."""
    script = REPO_ROOT / "scripts" / "work-queue" / "whats-next.sh"
    env = os.environ.copy()
    # Override queue by setting REPO_ROOT via a wrapper that shadows git rev-parse
    # Instead: pass env var that won't work directly — we need a different approach.
    # whats-next.sh uses $(git rev-parse --show-toplevel) so we create a fake repo.
    return subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True,
        env={**env, "GIT_DIR": str(tmp_queue / ".git"), "GIT_WORK_TREE": str(tmp_queue)},
    )


def _run_active_sessions(
    repo_root: Path, extra_args: list[str] | None = None
) -> subprocess.CompletedProcess:
    script = repo_root / "scripts" / "work-queue" / "active-sessions.sh"
    cmd = ["bash", str(script)] + (extra_args or [])
    return subprocess.run(cmd, capture_output=True, text=True)


# ── Tests 1–4: whats-next.sh session-lock bucketing ──────────────────────────

class TestWhatNextSessionLock:
    """
    Tests for the has_recent_session_lock / UNCLAIMED_ACTIVE bucket in whats-next.sh.

    Because whats-next.sh reads from $(git rev-parse --show-toplevel), we need a
    minimal fake repo. Each test creates a temp directory with the necessary structure
    and patches git to point at it.
    """

    @pytest.fixture()
    def fake_repo(self, tmp_path: Path) -> Path:
        """Create a minimal fake git repo with queue structure."""
        repo = tmp_path / "repo"
        repo.mkdir()
        # init bare enough for git rev-parse
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "--allow-empty", "-m", "init"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
        )
        # Create queue structure
        for d in ("pending", "working", "blocked", "archive"):
            (repo / ".claude" / "work-queue" / d).mkdir(parents=True)
        return repo

    def _run_script(self, repo: Path, env_extra: dict | None = None) -> subprocess.CompletedProcess:
        script = REPO_ROOT / "scripts" / "work-queue" / "whats-next.sh"
        env = os.environ.copy()
        env["HOME"] = str(repo)  # isolate
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            ["bash", str(script), "--all"],
            capture_output=True,
            text=True,
            cwd=str(repo),
            env=env,
        )

    def test_pending_with_recent_lock_goes_to_unclaimed_active(
        self, fake_repo: Path
    ) -> None:
        """Test 1: pending + lock age 30min → UNCLAIMED_ACTIVE (not HIGH_UNBLOCKED)."""
        wrk_id = "WRK-9901"
        _make_wrk_md(fake_repo / ".claude" / "work-queue", "pending", wrk_id)
        _make_lock(fake_repo / ".claude" / "work-queue" / "assets", wrk_id, 1800)  # 30min

        result = self._run_script(fake_repo)
        assert "UNCLAIMED" in result.stdout, (
            f"Expected UNCLAIMED section in output, got:\n{result.stdout}"
        )
        assert wrk_id in result.stdout

    def test_pending_with_stale_lock_goes_to_high_unblocked(
        self, fake_repo: Path
    ) -> None:
        """Test 2: pending + lock age 3h → HIGH_UNBLOCKED (stale, not unclaimed)."""
        wrk_id = "WRK-9902"
        _make_wrk_md(fake_repo / ".claude" / "work-queue", "pending", wrk_id)
        _make_lock(fake_repo / ".claude" / "work-queue" / "assets", wrk_id, 10800)  # 3h

        result = self._run_script(fake_repo)
        # Should appear in HIGH section, NOT in UNCLAIMED
        assert "HIGH PRIORITY" in result.stdout or wrk_id in result.stdout
        # Specifically: UNCLAIMED section should NOT contain this WRK
        lines = result.stdout.splitlines()
        in_unclaimed = False
        for line in lines:
            if "UNCLAIMED" in line:
                in_unclaimed = True
            if in_unclaimed and wrk_id in line:
                pytest.fail(f"{wrk_id} should not be in UNCLAIMED section (lock is stale)")
            if in_unclaimed and "──" in line and wrk_id not in line:
                in_unclaimed = False  # section end

    def test_pending_with_no_lock_goes_to_high_unblocked(
        self, fake_repo: Path
    ) -> None:
        """Test 3: pending + no lock → HIGH_UNBLOCKED (normal behaviour)."""
        wrk_id = "WRK-9903"
        _make_wrk_md(fake_repo / ".claude" / "work-queue", "pending", wrk_id)
        # No lock file

        result = self._run_script(fake_repo)
        assert wrk_id in result.stdout, "WRK should appear somewhere in output"
        # UNCLAIMED section should not exist OR not contain this WRK
        if "UNCLAIMED" in result.stdout:
            lines = result.stdout.splitlines()
            in_unclaimed = False
            for line in lines:
                if "UNCLAIMED" in line:
                    in_unclaimed = True
                if in_unclaimed and wrk_id in line:
                    pytest.fail(f"{wrk_id} should not be in UNCLAIMED section (no lock)")

    def test_lock_at_exactly_7200s_is_stale_boundary(
        self, fake_repo: Path
    ) -> None:
        """Test 4: pending + lock age exactly 7200s → stale (not UNCLAIMED_ACTIVE)."""
        wrk_id = "WRK-9904"
        _make_wrk_md(fake_repo / ".claude" / "work-queue", "pending", wrk_id)
        _make_lock(fake_repo / ".claude" / "work-queue" / "assets", wrk_id, 7200)  # exactly 2h

        result = self._run_script(fake_repo)
        if "UNCLAIMED" in result.stdout:
            lines = result.stdout.splitlines()
            in_unclaimed = False
            for line in lines:
                if "UNCLAIMED" in line:
                    in_unclaimed = True
                if in_unclaimed and wrk_id in line:
                    pytest.fail(
                        f"{wrk_id} should not be in UNCLAIMED section (lock age == MAX)"
                    )


# ── Tests 5–7: active-sessions.sh ─────────────────────────────────────────────

class TestActiveSessions:
    """Tests for scripts/work-queue/active-sessions.sh."""

    @pytest.fixture(autouse=True)
    def check_script_exists(self) -> None:
        script = REPO_ROOT / "scripts" / "work-queue" / "active-sessions.sh"
        if not script.exists():
            pytest.skip("active-sessions.sh not yet implemented")

    def test_pending_item_with_recent_lock_reported_as_unclaimed(
        self, tmp_path: Path
    ) -> None:
        """Test 5: pending/ + lock age 30min → reported as unclaimed."""
        # Create a fake repo structure that active-sessions.sh can traverse
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "--allow-empty", "-m", "init"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
        )
        assets = repo / ".claude" / "work-queue" / "assets"
        assets.mkdir(parents=True)
        pending = repo / ".claude" / "work-queue" / "pending"
        pending.mkdir(parents=True)

        wrk_id = "WRK-9905"
        (pending / f"{wrk_id}.md").write_text(f"---\nid: {wrk_id}\n---\n")
        _make_lock(assets, wrk_id, 1800)  # 30min

        script = REPO_ROOT / "scripts" / "work-queue" / "active-sessions.sh"
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        combined = result.stdout + result.stderr
        assert wrk_id in combined, f"Expected {wrk_id} in output:\n{combined}"
        assert "unclaimed" in combined.lower(), (
            f"Expected 'unclaimed' in output for pending item:\n{combined}"
        )

    def test_working_item_with_recent_lock_reported_as_claimed(
        self, tmp_path: Path
    ) -> None:
        """Test 6: working/ + lock age 30min → reported as claimed."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "--allow-empty", "-m", "init"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
        )
        assets = repo / ".claude" / "work-queue" / "assets"
        assets.mkdir(parents=True)
        working = repo / ".claude" / "work-queue" / "working"
        working.mkdir(parents=True)

        wrk_id = "WRK-9906"
        (working / f"{wrk_id}.md").write_text(f"---\nid: {wrk_id}\n---\n")
        _make_lock(assets, wrk_id, 1800)  # 30min

        script = REPO_ROOT / "scripts" / "work-queue" / "active-sessions.sh"
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        combined = result.stdout + result.stderr
        assert wrk_id in combined, f"Expected {wrk_id} in output:\n{combined}"
        assert "claimed" in combined.lower(), (
            f"Expected 'claimed' in output for working item:\n{combined}"
        )

    def test_stale_lock_older_than_2h_is_skipped(
        self, tmp_path: Path
    ) -> None:
        """Test 7: lock age > 2h → item skipped (not reported as active)."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "--allow-empty", "-m", "init"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
        )
        assets = repo / ".claude" / "work-queue" / "assets"
        assets.mkdir(parents=True)
        pending = repo / ".claude" / "work-queue" / "pending"
        pending.mkdir(parents=True)

        wrk_id = "WRK-9907"
        (pending / f"{wrk_id}.md").write_text(f"---\nid: {wrk_id}\n---\n")
        _make_lock(assets, wrk_id, 10800)  # 3h — stale

        script = REPO_ROOT / "scripts" / "work-queue" / "active-sessions.sh"
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        combined = result.stdout + result.stderr
        # Stale locks should not appear in the active session list
        assert wrk_id not in combined, (
            f"{wrk_id} should be skipped (stale lock), but appeared in:\n{combined}"
        )


# ── Tests 8–10: start_stage.py stage guard ───────────────────────────────────

class TestStartStagePendingGuard:
    """Tests for the stage ≥9 pending/ guard in start_stage.py."""

    START_STAGE = REPO_ROOT / "scripts" / "work-queue" / "start_stage.py"

    def _run(
        self,
        wrk_id: str,
        stage: int,
        repo_root: Path,
        extra_env: dict | None = None,
    ) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["WORKSPACE_HUB"] = str(repo_root)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["uv", "run", "--no-project", "python", str(self.START_STAGE), wrk_id, str(stage)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )

    @pytest.fixture()
    def fake_repo(self, tmp_path: Path) -> Path:
        """Minimal fake repo for start_stage.py tests."""
        repo = tmp_path / "repo"
        repo.mkdir()
        queue = repo / ".claude" / "work-queue"
        for d in ("pending", "working", "blocked", "done", "archive"):
            (queue / d).mkdir(parents=True)
        # Copy stage contracts so start_stage.py can find them
        stages_src = REPO_ROOT / "scripts" / "work-queue" / "stages"
        import shutil
        shutil.copytree(
            str(stages_src),
            str(repo / "scripts" / "work-queue" / "stages"),
        )
        return repo

    def test_stage9_with_item_in_pending_exits_nonzero(
        self, fake_repo: Path
    ) -> None:
        """Test 8: stage 9 + item in pending/ → sys.exit(1), stderr has claim message."""
        wrk_id = "WRK-9908"
        (fake_repo / ".claude" / "work-queue" / "pending" / f"{wrk_id}.md").write_text(
            f"---\nid: {wrk_id}\n---\n"
        )
        # Also create assets dir so start_stage doesn't fail on missing output_dir
        (fake_repo / ".claude" / "work-queue" / "assets" / wrk_id).mkdir(parents=True)

        result = self._run(wrk_id, 9, fake_repo)
        assert result.returncode != 0, (
            f"Expected non-zero exit for stage 9 with item in pending/, got 0.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "claim" in result.stderr.lower(), (
            f"Expected 'claim' in stderr, got:\n{result.stderr}"
        )

    def test_stage9_with_item_in_working_exits_zero(
        self, fake_repo: Path
    ) -> None:
        """Test 9: stage 9 + item in working/ → no error (exit 0)."""
        wrk_id = "WRK-9909"
        (fake_repo / ".claude" / "work-queue" / "working" / f"{wrk_id}.md").write_text(
            f"---\nid: {wrk_id}\n---\n"
        )
        (fake_repo / ".claude" / "work-queue" / "assets" / wrk_id).mkdir(parents=True)

        result = self._run(wrk_id, 9, fake_repo / ".claude" / "work-queue")
        assert result.returncode == 0, (
            f"Expected exit 0 for stage 9 with item in working/, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_stage2_with_item_in_pending_exits_zero(
        self, fake_repo: Path
    ) -> None:
        """Test 10: stage 2 + item in pending/ → no error (pre-claim stages OK)."""
        wrk_id = "WRK-9910"
        (fake_repo / ".claude" / "work-queue" / "pending" / f"{wrk_id}.md").write_text(
            f"---\nid: {wrk_id}\n---\n"
        )
        (fake_repo / ".claude" / "work-queue" / "assets" / wrk_id).mkdir(parents=True)

        result = self._run(wrk_id, 2, fake_repo / ".claude" / "work-queue")
        assert result.returncode == 0, (
            f"Expected exit 0 for stage 2 with item in pending/, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
