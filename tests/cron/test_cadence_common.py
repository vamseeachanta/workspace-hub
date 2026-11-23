"""Tests for scripts/cron/lib/cadence-common.sh — revised plan §TDD Test List."""

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "scripts" / "cron" / "lib" / "cadence-common.sh"


def _source_and_run(snippet: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Source cadence-common.sh then run the given bash snippet, capturing stdout."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", "-c", f'source "{LIB}"; {snippet}'],
        env=env, capture_output=True, text=True, timeout=10,
    )


# --- emit_report_header ---

def test_emit_report_header_format():
    r = _source_and_run('emit_report_header "memory-health" "2026-W16" "GREEN" "2 MB across 12 files"')
    assert r.returncode == 0
    assert "# memory-health — 2026-W16" in r.stdout
    assert "**Status:** GREEN — 2 MB across 12 files" in r.stdout


# --- compute_status_band ---

@pytest.mark.parametrize("value,warn,block,expected", [
    ("3", "5", "10", "GREEN"),
    ("7", "5", "10", "YELLOW"),
    ("15", "5", "10", "RED"),
])
def test_compute_status_band_basic(value, warn, block, expected):
    r = _source_and_run(f'compute_status_band {value} {warn} {block}')
    assert r.returncode == 0
    assert r.stdout.strip() == expected


def test_compute_status_band_at_warn_boundary():
    """Claude P1: exactly value == warn → GREEN (warn is inclusive of GREEN band)."""
    r = _source_and_run('compute_status_band 5 5 10')
    assert r.stdout.strip() == "GREEN"


def test_compute_status_band_at_block_boundary():
    """Claude P1: exactly value == block → YELLOW (block is inclusive of YELLOW band)."""
    r = _source_and_run('compute_status_band 10 5 10')
    assert r.stdout.strip() == "YELLOW"


def test_compute_status_band_floats():
    """Claude P3: accepts decimal values."""
    r = _source_and_run('compute_status_band 12.5 10 15')
    assert r.stdout.strip() == "YELLOW"
    r = _source_and_run('compute_status_band 15.1 10 15')
    assert r.stdout.strip() == "RED"


# --- cadence_period ---

def test_cadence_period_weekly_iso():
    r = _source_and_run('cadence_period weekly')
    assert r.returncode == 0
    assert re.match(r"^\d{4}-W\d{2}$", r.stdout.strip()), r.stdout


def test_cadence_period_monthly():
    r = _source_and_run('cadence_period monthly')
    assert re.match(r"^\d{4}-\d{2}$", r.stdout.strip()), r.stdout


def test_cadence_period_quarterly():
    r = _source_and_run('cadence_period quarterly')
    assert re.match(r"^\d{4}-Q[1-4]$", r.stdout.strip()), r.stdout


def test_cadence_period_unknown_fails():
    r = _source_and_run('cadence_period yearly')
    assert r.returncode != 0


def test_cadence_period_weekly_tz_utc():
    """Gemini P2: TZ=UTC pinning means same period regardless of caller TZ."""
    r_pst = _source_and_run('cadence_period weekly', env_extra={"TZ": "America/Los_Angeles"})
    r_utc = _source_and_run('cadence_period weekly', env_extra={"TZ": "UTC"})
    # The helper exports TZ=UTC internally, so both should agree.
    assert r_pst.stdout.strip() == r_utc.stdout.strip(), (
        f"TZ pinning failed: PST={r_pst.stdout!r} UTC={r_utc.stdout!r}"
    )


# --- cadence_init_repo_root ---

def test_cadence_init_repo_root_from_env(tmp_path):
    """Codex P1: explicit REPO_ROOT env var wins."""
    r = _source_and_run(
        f'cadence_init_repo_root; echo "$REPO_ROOT"',
        env_extra={"REPO_ROOT": str(tmp_path)},
    )
    assert r.stdout.strip() == str(tmp_path)


def test_cadence_init_repo_root_from_git(tmp_path):
    """Codex P1: falls back to git rev-parse inside a real repo."""
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    r = _source_and_run(
        'cadence_init_repo_root; echo "$REPO_ROOT"',
        env_extra={"REPO_ROOT": "", "PWD": str(repo)},
    )
    # bash may change cwd, so we explicitly cd
    r = subprocess.run(
        ["bash", "-c", f'cd "{repo}" && source "{LIB}" && cadence_init_repo_root && echo "$REPO_ROOT"'],
        env={**os.environ, "REPO_ROOT": ""},
        capture_output=True, text=True, timeout=10,
    )
    assert r.stdout.strip() == str(repo.resolve()), r.stdout + r.stderr


def test_cadence_init_repo_root_idempotent(tmp_path):
    """Calling twice doesn't overwrite an already-set REPO_ROOT."""
    r = _source_and_run(
        'cadence_init_repo_root; cadence_init_repo_root; echo "$REPO_ROOT"',
        env_extra={"REPO_ROOT": str(tmp_path)},
    )
    assert r.stdout.strip() == str(tmp_path)
