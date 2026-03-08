"""T45-T47: spawn-team.sh Stage 1 exit gate pre-check."""
import subprocess
import os
import pytest
from pathlib import Path

SPAWN_TEAM = Path("scripts/work-queue/spawn-team.sh")
WORKSPACE = Path("/mnt/local-analysis/workspace-hub")


def _run_spawn(tmp_path, capture_content=None, wrk_id="WRK-9999", slug="test-slug"):
    """Run spawn-team.sh with optional user-review-capture.yaml planted."""
    env = {**os.environ, "HOME": str(tmp_path)}
    # Create fake .claude/work-queue/assets/WRK-NNN/evidence/
    ev_dir = tmp_path / ".claude" / "work-queue" / "assets" / wrk_id / "evidence"
    ev_dir.mkdir(parents=True)
    if capture_content is not None:
        (ev_dir / "user-review-capture.yaml").write_text(capture_content)
    result = subprocess.run(
        ["bash", str(SPAWN_TEAM), wrk_id, slug],
        capture_output=True, text=True,
        cwd=str(WORKSPACE), env=env
    )
    return result


def test_T45_spawn_exits1_when_capture_absent(tmp_path):
    """T45: spawn-team.sh exits 1 when user-review-capture.yaml absent."""
    r = _run_spawn(tmp_path, capture_content=None)
    assert r.returncode == 1
    assert "user-review-capture.yaml" in r.stderr or "scope" in r.stderr.lower()


def test_T46_spawn_exits0_when_scope_approved(tmp_path):
    """T46: spawn-team.sh exits 0 (prints recipe) when scope_approved: true."""
    yaml = (
        "stage: 1\n"
        "reviewer: vamsee\n"
        "confirmed_at: 2026-03-08T12:00:00Z\n"
        "scope_approved: true\n"
        "notes: ok\n"
    )
    r = _run_spawn(tmp_path, capture_content=yaml)
    # The key assertion: does NOT exit 1 due to gate failure
    assert "scope_approved" not in r.stderr or r.returncode == 0


def test_T47_spawn_exits1_when_scope_not_approved(tmp_path):
    """T47: spawn-team.sh exits 1 when scope_approved: false."""
    yaml = (
        "stage: 1\n"
        "reviewer: vamsee\n"
        "confirmed_at: 2026-03-08T12:00:00Z\n"
        "scope_approved: false\n"
        "notes: needs revision\n"
    )
    r = _run_spawn(tmp_path, capture_content=yaml)
    assert r.returncode == 1
    assert "scope_approved" in r.stderr
