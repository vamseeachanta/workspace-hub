"""Tests for nightly-readiness.sh R-SKILLS semantics (#3591 item 4).

The "skills committed in last 7 days" clause measures FLEET authoring cadence
(git log on .claude/skills/ is identical on every box), so it must never fail a
single machine's readiness. It is demoted to an advisory note on the OK line.
Per-box session-signals freshness remains the failing condition.

Drives the real shell script against an isolated temp WORKSPACE_HUB (same
harness pattern as test_nightly_readiness_hook_static_and_telegram.py).
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "nightly-readiness.sh"
REAL_CONFIG = REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml"


def _run(ws: Path, config: Path) -> str:
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": str(ws / "home"),
        "WORKSPACE_HUB": str(ws),
        "HARNESS_CONFIG": str(config),
    }
    proc = subprocess.run(
        ["bash", str(SCRIPT)], capture_output=True, text=True,
        env=env, cwd=str(REPO_ROOT), timeout=120,
    )
    return proc.stdout


def _line(output: str, check_id: str) -> str:
    for raw in output.splitlines():
        if check_id in raw and ("OK" in raw or "FAIL" in raw):
            return raw.strip()
    raise AssertionError(f"{check_id} line not found in:\n{output}")


def _mk_ws(tmp_path: Path, *, fresh_signals: bool, stale_skills_repo: bool) -> tuple[Path, Path]:
    ws = tmp_path / "ws"
    (ws / ".claude" / "hooks").mkdir(parents=True)
    signals = ws / ".claude" / "state" / "session-signals"
    signals.mkdir(parents=True)
    (ws / "home").mkdir(parents=True)
    cfg_dir = ws / "scripts" / "readiness"
    cfg_dir.mkdir(parents=True)
    config = cfg_dir / "harness-config.yaml"
    config.write_text(REAL_CONFIG.read_text())
    if fresh_signals:
        (signals / "today.jsonl").write_text('{"ok": true}\n')
    if stale_skills_repo:
        # a skills tree whose last commit is far older than the 7-day window
        skills = ws / ".claude" / "skills" / "fam" / "alpha"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("---\nname: alpha\n---\nbody\n")
        env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws / "home"),
               "GIT_AUTHOR_DATE": "2026-01-01T00:00:00", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00"}
        for cmd in (["git", "init", "-q"],
                    ["git", "config", "user.email", "t@t"],
                    ["git", "config", "user.name", "t"],
                    ["git", "add", "-A"],
                    ["git", "commit", "-q", "-m", "old skills commit"]):
            subprocess.run(cmd, cwd=str(ws), env=env, check=True, capture_output=True)
    return ws, config


def test_r_skills_fleet_cadence_is_advisory_not_fail(tmp_path: Path) -> None:
    # fresh per-box signals + no skills commit in 7 days → OK with an advisory note
    ws, config = _mk_ws(tmp_path, fresh_signals=True, stale_skills_repo=True)
    line = _line(_run(ws, config), "R-SKILLS")
    assert line.startswith("OK"), line
    assert "advisory" in line, line


def test_r_skills_stale_session_signals_still_fails(tmp_path: Path) -> None:
    # per-box signal stays the failing condition: no fresh session-signals → FAIL
    ws, config = _mk_ws(tmp_path, fresh_signals=False, stale_skills_repo=True)
    line = _line(_run(ws, config), "R-SKILLS")
    assert line.startswith("FAIL"), line
    assert "session-signals" in line


def test_r_skills_no_advisory_when_skills_fresh(tmp_path: Path) -> None:
    # fresh signals + a skills commit inside the window → clean OK, no advisory
    ws, config = _mk_ws(tmp_path, fresh_signals=True, stale_skills_repo=True)
    subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "recent skills work",
                    "--", ], cwd=str(ws),
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws / "home")},
                   check=True, capture_output=True)
    # empty commit doesn't touch .claude/skills — make a real touch instead
    skill = ws / ".claude" / "skills" / "fam" / "alpha" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nmore\n")
    subprocess.run(["git", "add", "-A"], cwd=str(ws),
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws / "home")},
                   check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "recent skills work"], cwd=str(ws),
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws / "home")},
                   check=True, capture_output=True)
    line = _line(_run(ws, config), "R-SKILLS")
    assert line.startswith("OK"), line
    assert "advisory" not in line, line
