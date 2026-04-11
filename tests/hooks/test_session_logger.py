from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / ".claude" / "hooks" / "session-logger.sh"


def test_session_logger_persists_session_id_to_both_logs(tmp_path: Path) -> None:
    repo = tmp_path / "repo-under-test"
    (repo / ".claude" / "hooks").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / ".claude" / "hooks" / "session-logger.sh")
    (repo / "scripts" / "ai").mkdir(parents=True)
    (repo / "scripts" / "ai" / "session-params.py").write_text("print('')\n", encoding="utf-8")
    (repo / ".git").mkdir()

    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(repo)
    env["CLAUDE_SESSION_LOGGING"] = "true"

    payload = {
        "session_id": "claude-test-1",
        "tool_name": "Bash",
        "tool_input": {"command": "git status --short"},
    }

    script_path = repo / ".claude" / "hooks" / "session-logger.sh"
    result = subprocess.run(
        ["bash", str(script_path), "post"],
        cwd=repo,
        env=env,
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    day = datetime.now().strftime("%Y%m%d")
    state_log = repo / ".claude" / "state" / "sessions" / f"session_{day}.jsonl"
    orch_log = repo / "logs" / "orchestrator" / "claude" / f"session_{day}.jsonl"

    assert state_log.exists()
    assert orch_log.exists()

    state_entries = [json.loads(line) for line in state_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    orch_entries = [json.loads(line) for line in orch_log.read_text(encoding="utf-8").splitlines() if line.strip()]

    state_entry = next(entry for entry in state_entries if entry.get("tool") == "Bash")
    orch_entry = next(entry for entry in orch_entries if entry.get("tool") == "Bash")

    assert state_entry["session_id"] == "claude-test-1"
    assert orch_entry["session_id"] == "claude-test-1"
    assert state_entry["cmd"] == "git status --short"
    assert orch_entry["cmd"] == "git status --short"
    assert state_entry["hook"] == "post"
    assert orch_entry["hook"] == "post"
