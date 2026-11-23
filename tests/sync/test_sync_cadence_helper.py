"""Tests for scripts/sync/sync-cadence-helper.sh — byte-identical guard."""

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "sync" / "sync-cadence-helper.sh"


def _run(canonical: Path, vendored: Path | None, *args, env_extra: dict | None = None):
    env = os.environ.copy()
    env["CADENCE_CANONICAL"] = str(canonical)
    env["CADENCE_VENDORED"] = str(vendored) if vendored else "/nonexistent"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        env=env, capture_output=True, text=True, timeout=10,
    )


def test_sync_passes_when_identical(tmp_path):
    c = tmp_path / "canonical.sh"
    v = tmp_path / "vendored.sh"
    c.write_text("same content\n")
    v.write_text("same content\n")
    r = _run(c, v)
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_sync_fails_on_drift(tmp_path):
    c = tmp_path / "canonical.sh"
    v = tmp_path / "vendored.sh"
    c.write_text("canonical\n")
    v.write_text("drifted\n")
    r = _run(c, v)
    assert r.returncode == 1, f"should fail on drift, stdout={r.stdout} stderr={r.stderr}"
    assert "DRIFT" in r.stderr
    assert "FAIL" in r.stderr


def test_sync_fix_restores_parity(tmp_path):
    c = tmp_path / "canonical.sh"
    v = tmp_path / "vendored.sh"
    c.write_text("canonical content\n")
    v.write_text("drifted content\n")
    r = _run(c, v, "--fix")
    assert r.returncode == 0, r.stderr
    assert v.read_text() == "canonical content\n"


def test_sync_tolerates_missing_vendored(tmp_path):
    """worldenergydata absent → strict check still passes."""
    c = tmp_path / "canonical.sh"
    c.write_text("canonical\n")
    r = _run(c, tmp_path / "does_not_exist.sh")
    assert r.returncode == 0, r.stderr
    assert "not present" in r.stdout or "OK" in r.stdout


def test_sync_fails_when_canonical_missing(tmp_path):
    r = _run(tmp_path / "nope.sh", tmp_path / "also_nope.sh")
    assert r.returncode == 1
    assert "canonical helper missing" in r.stderr
