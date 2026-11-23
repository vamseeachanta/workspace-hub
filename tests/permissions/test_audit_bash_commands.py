"""
TDD tests for audit-bash-commands.py (WRK-1119 Phase 1).

Red phase: all tests written before implementation exists.
"""

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper: load the script module dynamically so tests can import its functions
# without requiring the script to be on sys.path.
# ---------------------------------------------------------------------------
SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "permissions"
    / "audit-bash-commands.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_bash_commands", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Test 1 — extraction
# ---------------------------------------------------------------------------


def test_extract_bash_commands_from_session(tmp_path):
    """extract_bash_commands should return exactly the Bash tool-use commands."""
    session_file = tmp_path / "session.jsonl"

    lines = [
        # Bash tool-use #1 — nested inside message.content
        json.dumps(
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Bash",
                            "input": {"command": "git diff HEAD~1"},
                        }
                    ]
                }
            }
        ),
        # Non-Bash tool-use inside message.content — must be ignored
        json.dumps(
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Read",
                            "input": {"file_path": "/some/file"},
                        }
                    ]
                }
            }
        ),
        # Bash tool-use #2 — flat format (line itself is the tool_use object)
        json.dumps(
            {
                "type": "tool_use",
                "name": "Bash",
                "input": {"command": "uv run --no-project python foo.py"},
            }
        ),
        # Unrelated line — must be ignored
        json.dumps({"type": "text", "text": "Some assistant text"}),
    ]
    session_file.write_text("\n".join(lines) + "\n")

    mod = _load_module()
    commands = mod.extract_bash_commands(session_file)

    assert len(commands) == 2, f"Expected 2 Bash commands, got {len(commands)}: {commands}"
    assert "git diff HEAD~1" in commands
    assert "uv run --no-project python foo.py" in commands


# ---------------------------------------------------------------------------
# Test 2 — normalization
# ---------------------------------------------------------------------------


def test_normalize_command_to_prefix():
    """normalize_command_to_prefix should strip args and expand multi-word prefixes."""
    mod = _load_module()
    norm = mod.normalize_command_to_prefix

    cases = [
        ("git diff HEAD~1", "git diff"),
        ("git log --oneline -5", "git log"),
        ("uv run --no-project python foo.py", "uv run"),
        ("ls -la /tmp", "ls"),
        ("python -m pytest tests/", "python -m"),
        ("bash scripts/foo.sh", "bash"),
        # Relative path — keep full path token up to first space
        ("./scripts/foo.sh --flag", "./scripts/foo.sh"),
    ]

    for cmd, expected in cases:
        result = norm(cmd)
        assert result == expected, f"normalize({cmd!r}) → {result!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# Test 3 — allow-pattern suggestion
# ---------------------------------------------------------------------------


def test_suggest_allow_pattern():
    """suggest_allow_pattern should produce the correct Bash(prefix:*) pattern."""
    mod = _load_module()
    suggest = mod.suggest_allow_pattern

    cases = [
        ("git diff", "Bash(git diff:*)"),
        ("git log", "Bash(git log:*)"),
        ("ls", "Bash(ls:*)"),
        ("pwd", "Bash(pwd)"),
        ("uv run", "Bash(uv run:*)"),
        # Relative-path scripts map to a directory-level wildcard
        ("./scripts/foo.sh", "Bash(./scripts/*:*)"),
    ]

    for prefix, expected in cases:
        result = suggest(prefix)
        assert result == expected, f"suggest({prefix!r}) → {result!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# Test 4 — end-to-end audit via subprocess
# ---------------------------------------------------------------------------


def test_end_to_end_audit(tmp_path):
    """Running the script against synthetic JSONL files produces correct YAML output."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()

    # Session A: git diff ×3, git log ×1, ls ×1
    session_a = sessions_dir / "session_a.jsonl"
    lines_a = []
    for cmd in [
        "git diff HEAD~1",
        "git diff --stat",
        "git diff HEAD~2 --name-only",
        "git log --oneline -5",
        "ls -la",
    ]:
        lines_a.append(
            json.dumps(
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": cmd},
                }
            )
        )
    session_a.write_text("\n".join(lines_a) + "\n")

    # Session B: git diff ×2, uv run ×2
    session_b = sessions_dir / "session_b.jsonl"
    lines_b = []
    for cmd in [
        "git diff HEAD",
        "git diff origin/main",
        "uv run --no-project python script.py",
        "uv run --no-project python -c 'import json'",
    ]:
        lines_b.append(
            json.dumps(
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": cmd},
                }
            )
        )
    session_b.write_text("\n".join(lines_b) + "\n")

    output_file = tmp_path / "audit_output.yaml"

    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "python",
            str(SCRIPT_PATH),
            "--sessions-dir",
            str(sessions_dir),
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"Script exited {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert output_file.exists(), "Output file was not created"

    content = output_file.read_text()
    assert content.strip(), "Output file is empty"

    # git diff should be the top entry (5 occurrences: 3 from A + 2 from B)
    # Verify the git diff entry has count: 5 as adjacent fields in the same record block
    assert re.search(
        r"prefix:\s*git diff\s*\n\s*count:\s*5\b",
        content,
    ), f"Expected 'git diff' entry with count 5 (adjacent) in output:\n{content}"
