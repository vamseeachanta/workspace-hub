"""Tests for #2070 Claude settings hook wiring."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"


def test_claude_settings_wires_state_size_guards_to_git_commit_and_push() -> None:
    settings = json.loads(SETTINGS.read_text())
    pretool = settings["hooks"]["PreToolUse"]

    commands_by_matcher = {
        entry["matcher"]: [hook["command"] for hook in entry["hooks"]]
        for entry in pretool
    }

    assert "bash .claude/hooks/check-state-file-size-precommit.sh" in commands_by_matcher[
        "Bash(git commit*)"
    ]
    assert "bash .claude/hooks/check-state-file-size-prepush.sh" in commands_by_matcher[
        "Bash(git push*)"
    ]
