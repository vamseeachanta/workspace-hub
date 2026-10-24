"""Guard the Git/provider boundary after the issue #3852 wiring repair.

Basis: Git githooks, pre-push; Claude Code hooks, matcher and JSON input/output
sections (accessed 2026-10-22). These assertions inspect repository manifests;
they do not establish that a provider loads them or executes a hook.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("manifest", [".claude/settings.json", ".codex/hooks.json"])
def test_git_state_size_checkers_are_not_registered_as_provider_hooks(manifest):
    """Ref-line consumers must not be enrolled as native JSON consumers.

    The old test required removed command-shaped matchers. Merely replacing
    those matchers with Bash would send JSON to the Git checker and infer the
    current branch rather than validate the actual push refspecs.
    """
    settings = json.loads((ROOT / manifest).read_text())
    for entries in settings["hooks"].values():
        for entry in entries:
            for hook in entry["hooks"]:
                command = hook.get("command", "")
                assert "check-state-file-size-prepush.sh" not in command
                assert "check-state-file-size-precommit.sh" not in command


def test_native_review_hook_uses_tool_name_matcher():
    """The retained native review hook declares Bash, not a shell command."""
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    registrations = [
        entry for entry in settings["hooks"]["PreToolUse"]
        if any("cross-review-gate.sh" in hook.get("command", "")
               for hook in entry["hooks"])
    ]
    assert len(registrations) == 1
    assert registrations[0]["matcher"] == "Bash"
