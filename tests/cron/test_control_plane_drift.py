"""Tests for scripts/cron/control-plane-drift.sh — TDD per #2317 plan."""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "control-plane-drift.sh"


REQUIRED = ("AGENTS.md", "CLAUDE.md", ".claude", ".codex", ".gemini")


def _mk_repo(path: Path, files: tuple[str, ...]):
    path.mkdir(parents=True, exist_ok=True)
    # a .git directory so it's recognized as a child repo
    (path / ".git").mkdir(exist_ok=True)
    for name in files:
        target = path / name
        if name.startswith("."):
            target.mkdir(exist_ok=True)
        else:
            target.write_text(f"# {name}\n")


def _run(tmp_path: Path, repos: dict[str, tuple[str, ...]], env_extra: dict | None = None):
    out_dir = tmp_path / "out"
    roots = tmp_path / "roots"
    roots.mkdir(parents=True, exist_ok=True)
    for name, files in repos.items():
        _mk_repo(roots / name, files)

    env = os.environ.copy()
    env["CONTROL_PLANE_OUT_DIR"] = str(out_dir)
    env["CONTROL_PLANE_QUARTER"] = "2026-Q2"
    env["CONTROL_PLANE_SCAN_ROOT"] = str(roots)
    env["REPO_ROOT"] = str(tmp_path)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env, capture_output=True, text=True, timeout=15,
    )
    return r, out_dir / "control-plane-drift-2026-Q2.md"


def test_drift_green_when_all_match(tmp_path):
    r, report = _run(tmp_path, {
        "repo_a": REQUIRED,
        "repo_b": REQUIRED,
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body


def test_drift_yellow_on_one_drift(tmp_path):
    r, report = _run(tmp_path, {
        "repo_a": REQUIRED,
        "repo_b": ("AGENTS.md", "CLAUDE.md", ".claude"),  # missing .codex, .gemini
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** YELLOW" in body
    assert "repo_b" in body


def test_drift_red_on_many(tmp_path):
    repos = {f"repo_{i}": ("AGENTS.md",) for i in range(6)}  # 6 repos each missing 4 files
    r, report = _run(tmp_path, repos)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** RED" in body


def test_drift_detects_missing_file(tmp_path):
    r, report = _run(tmp_path, {
        "repo_a": ("AGENTS.md", "CLAUDE.md", ".codex", ".gemini"),  # no .claude
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert ".claude" in body
    # YELLOW because one repo drifts
    assert "Status:** YELLOW" in body


def test_drift_reports_per_file_status(tmp_path):
    r, report = _run(tmp_path, {"repo_a": REQUIRED})
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    # Header columns for each required file
    assert "AGENTS.md" in body
    assert "CLAUDE.md" in body
    assert ".claude" in body


def test_drift_handles_repo_without_any_harness(tmp_path):
    r, report = _run(tmp_path, {"repo_a": ()})  # just .git, nothing else
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "uninitialized" in body.lower()


def test_drift_skips_non_git_dirs(tmp_path):
    roots = tmp_path / "roots"
    roots.mkdir(parents=True, exist_ok=True)
    # non-repo dir
    plain = roots / "not_a_repo"
    plain.mkdir()
    (plain / "README.md").write_text("hi")
    # actual repo
    _mk_repo(roots / "repo_a", REQUIRED)

    out_dir = tmp_path / "out"
    env = os.environ.copy()
    env["CONTROL_PLANE_OUT_DIR"] = str(out_dir)
    env["CONTROL_PLANE_QUARTER"] = "2026-Q2"
    env["CONTROL_PLANE_SCAN_ROOT"] = str(roots)
    env["REPO_ROOT"] = str(tmp_path)
    r = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=15)
    body = (out_dir / "control-plane-drift-2026-Q2.md").read_text()
    assert "repo_a" in body
    assert "not_a_repo" not in body
