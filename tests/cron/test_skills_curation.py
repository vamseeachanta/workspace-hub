"""Tests for the skills-curation cron wrapper (#2281).

The wrapper is a thin shell launcher around the deterministic Python audit script.
These tests deliberately evolve the contract from the old Claude-prompt launcher
to the new deterministic entrypoint.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "skills-curation.sh"


def test_skills_curation_wrapper_prints_deterministic_command(tmp_path: Path) -> None:
    """--dry-run must show the deterministic Python invocation, not a Claude prompt."""
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(REPO_ROOT)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    # Must reference the deterministic Python script, not claude CLI
    assert "weekly_skills_audit.py" in result.stdout
    # Must NOT reference claude CLI invocation
    assert "claude -p" not in result.stdout
    assert "--dangerously-skip-permissions" not in result.stdout


def test_skills_curation_wrapper_dry_run_does_not_execute(tmp_path: Path) -> None:
    """--dry-run must not produce any output artifacts."""
    out_dir = tmp_path / "logs" / "maintenance" / "skills-curation"
    out_dir.mkdir(parents=True)

    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["SKILLS_AUDIT_OUTPUT_ROOT"] = str(tmp_path)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    # No artifacts should be created in dry-run mode
    json_files = list(out_dir.glob("*.json"))
    assert json_files == [], f"dry-run created artifacts: {json_files}"


def test_skills_curation_wrapper_passes_output_root_env(tmp_path: Path) -> None:
    """Wrapper must forward SKILLS_AUDIT_OUTPUT_ROOT to the Python script."""
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(REPO_ROOT)
    env["SKILLS_AUDIT_OUTPUT_ROOT"] = str(tmp_path)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "weekly_skills_audit.py" in result.stdout
    assert f"--output-dir {tmp_path}" in result.stdout


def test_skills_curation_wrapper_help_exits_zero() -> None:
    """--help must exit 0 and show usage."""
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(REPO_ROOT)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()


def test_skills_curation_wrapper_ignores_stale_workspace_env(tmp_path: Path) -> None:
    """Wrapper should derive repo root from its own path, not inherited WORKSPACE_HUB."""
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = "/tmp/not-the-repo"
    env["SKILLS_AUDIT_OUTPUT_ROOT"] = str(tmp_path)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert str(REPO_ROOT / "scripts" / "skills" / "weekly_skills_audit.py") in result.stdout
