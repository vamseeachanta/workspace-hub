"""Tests for config protection PreToolUse hook (#1801)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "config-protection-pretooluse.sh"


def _run_hook(payload: dict, *, env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        timeout=10,
    )


def test_non_protected_file_is_ignored() -> None:
    result = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/example.py",
                "old_string": "print('old')",
                "new_string": "print('new')",
            },
        }
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_pyproject_metadata_edit_is_allowed() -> None:
    result = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "pyproject.toml",
                "old_string": 'description = "old"',
                "new_string": 'description = "new"',
            },
        }
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_ruff_ignore_broadening_is_blocked() -> None:
    result = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "pyproject.toml",
                "old_string": "[tool.ruff.lint]\nselect = ['E', 'F']\n",
                "new_string": "[tool.ruff.lint]\nignore = ['E501']\n",
            },
        }
    )
    assert result.returncode == 0
    assert '"decision":"block"' in result.stdout.replace(" ", "")
    assert "pyproject.toml" in result.stdout


def test_claude_guard_removal_is_blocked() -> None:
    result = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "CLAUDE.md",
                "old_string": "- Plan before acting\n- TDD mandatory\n",
                "new_string": "- Workflow overview\n",
            },
        }
    )
    assert result.returncode == 0
    assert '"decision":"block"' in result.stdout.replace(" ", "")
    assert "Plan before acting" in result.stdout or "TDD mandatory" in result.stdout


def test_explicit_bypass_env_allows_change() -> None:
    result = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": ".flake8",
                "old_string": "ignore = E203\n",
                "new_string": "ignore = E203,W503\n",
            },
        },
        env_extra={"CONFIG_PROTECTION_APPROVED": "1"},
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
