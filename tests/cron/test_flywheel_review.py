"""Smoke test for flywheel-review.py (epic #3085 cadence job)."""
from __future__ import annotations
import pathlib
import subprocess

HUB = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = HUB / "scripts" / "cron" / "flywheel-review.py"


def test_runs_and_reports_against_real_artifacts(tmp_path):
    # Real hub artifacts for metrics; hermetic repos-root with one scoped + one
    # unscoped fake repo so the scan is deterministic and permission-safe.
    (tmp_path / "scoped_repo" / ".git").mkdir(parents=True)
    (tmp_path / "scoped_repo" / ".claude" / "memory").mkdir(parents=True)
    (tmp_path / "plain_repo" / ".git").mkdir(parents=True)
    r = subprocess.run(
        ["python3", str(SCRIPT), "--root", str(HUB),
         "--repos-root", str(tmp_path), "--print-only"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert "Flywheel review" in out
    assert "Scheduled workflows (SSoT)" in out
    assert "Repos with scoped memory | 1 / 2" in out  # deterministic scan


def test_missing_artifact_fails_cleanly(tmp_path):
    # empty hub → required artifact missing → exit 1, not a traceback
    r = subprocess.run(
        ["python3", str(SCRIPT), "--root", str(tmp_path),
         "--repos-root", str(tmp_path), "--print-only"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "missing required artifact" in r.stderr
