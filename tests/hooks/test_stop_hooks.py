from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONSUME_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "consume-signals.sh"
SKILL_NUDGE_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "skill-nudge-stop.sh"


def copy_hook(script: Path, repo: Path) -> Path:
    hooks_dir = repo / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    target = hooks_dir / script.name
    shutil.copy2(script, target)
    return target


def test_consume_signals_handles_jsonl_stop_payload_without_bad_filename(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    script = copy_hook(CONSUME_SCRIPT, repo)

    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(repo)

    lines = [
        json.dumps({"type": "user", "timestamp": "2026-05-15T01:02:03Z", "session_id": "stop-test"}),
        json.dumps({"type": "assistant", "timestamp": "2026-05-15T01:02:04Z"}),
    ]
    payload = "\n".join(lines * 5000)

    result = subprocess.run(
        ["bash", str(script)],
        cwd=repo,
        env=env,
        input=payload,
        capture_output=True,
        text=True,
        timeout=3,
        check=False,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "File name too long" not in result.stderr

    signal_file = repo / ".claude" / "state" / "session-signals" / "2026-05-15.jsonl"
    assert signal_file.exists()
    entries = [json.loads(line) for line in signal_file.read_text(encoding="utf-8").splitlines()]
    assert entries[-1]["event"] == "stop_signal_captured"
    assert entries[-1]["session_id"] == "stop-test"


def test_skill_nudge_stop_does_not_depend_on_git_scan(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    script = copy_hook(SKILL_NUDGE_SCRIPT, repo)
    (repo / ".claude" / "skills" / "example").mkdir(parents=True)
    (repo / ".claude" / "skills" / "example" / "SKILL.md").write_text("# Example\n", encoding="utf-8")

    today = datetime.now().strftime("%Y-%m-%d")
    signal_dir = repo / ".claude" / "state" / "session-signals"
    signal_dir.mkdir(parents=True)
    signal_file = signal_dir / f"{today}.jsonl"
    signal_file.write_text("\n".join("{}" for _ in range(12)) + "\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_git = fake_bin / "git"
    fake_git.write_text("#!/usr/bin/env bash\nsleep 20\n", encoding="utf-8")
    fake_git.chmod(0o755)

    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(repo)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

    result = subprocess.run(
        ["bash", str(script)],
        cwd=repo,
        env=env,
        input=json.dumps({"session_id": "stop-test"}) + "\n",
        capture_output=True,
        text=True,
        timeout=3,
        check=False,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
