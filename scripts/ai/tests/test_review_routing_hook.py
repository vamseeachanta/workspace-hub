"""Tests for the review routing hook integration.

Tests that the routing gate hook:
1. Fires on gh pr create commands (via cross-review-gate.sh integration)
2. Runs the routing gate against the current diff
3. Annotates the block message with reviewer recommendations
4. Passes through for non-PR commands
5. Handles edge cases (no diff, empty diff, script errors)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
HOOK_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "cross-review-gate.sh"
ROUTING_GATE = REPO_ROOT / "scripts" / "ai" / "review_routing_gate.py"


def run_hook_with_input(tool_input: dict, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Run the cross-review-gate hook with simulated Claude tool input."""
    env = os.environ.copy()
    env["REPO_ROOT_OVERRIDE"] = str(REPO_ROOT)
    if env_extra:
        env.update(env_extra)

    return subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        input=json.dumps(tool_input),
        capture_output=True,
        text=True,
        timeout=20,
        cwd=str(REPO_ROOT),
        env=env,
    )


class TestHookProtocol:
    """Test the hook follows Claude hook protocol correctly."""

    def test_non_bash_tool_passes_through(self):
        """Non-Bash tool calls should pass through without blocking."""
        result = run_hook_with_input({
            "tool_name": "Write",
            "tool_input": {"file_path": "foo.py", "content": "bar"}
        })
        assert result.returncode == 0
        # Should produce no block decision
        stdout = result.stdout.strip()
        if stdout:
            try:
                parsed = json.loads(stdout)
                assert parsed.get("decision") != "block"
            except json.JSONDecodeError:
                pass  # Non-JSON output is fine for pass-through

    def test_non_pr_bash_passes_through(self):
        """Regular bash commands should not trigger review routing."""
        result = run_hook_with_input({
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"}
        })
        assert result.returncode == 0
        stdout = result.stdout.strip()
        if stdout:
            try:
                parsed = json.loads(stdout)
                assert parsed.get("decision") != "block"
            except json.JSONDecodeError:
                pass

    def test_empty_command_passes_through(self):
        """Empty command should not cause errors."""
        result = run_hook_with_input({
            "tool_name": "Bash",
            "tool_input": {"command": ""}
        })
        assert result.returncode == 0

    def test_malformed_json_input_doesnt_crash(self):
        """Hook should handle malformed input gracefully."""
        result = subprocess.run(
            ["bash", str(HOOK_SCRIPT)],
            input="not-json",
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0  # Should not crash


class TestRoutingGateIntegration:
    """Test that the routing gate is invoked for PR-related commands."""

    def test_routing_gate_script_exists(self):
        """The routing gate Python script must exist."""
        assert ROUTING_GATE.exists(), f"Missing: {ROUTING_GATE}"

    def test_routing_gate_importable(self):
        """The routing gate module should be importable."""
        result = subprocess.run(
            ["uv", "run", "python", "-c",
             "import sys; sys.path.insert(0, 'scripts/ai'); "
             "from review_routing_gate import analyze_diff_for_triggers, build_recommendation; "
             "print('OK')"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        assert "OK" in result.stdout

    def test_routing_gate_cli_works(self):
        """The routing gate should work via CLI with --stdin."""
        diff = "diff --git a/foo.py b/foo.py\\n--- a/foo.py\\n+++ b/foo.py\\n@@ -1 +1 @@\\n-old\\n+new\\n"
        result = subprocess.run(
            ["uv", "run", "python", str(ROUTING_GATE), "--stdin"],
            input=diff,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "reviewers" in output
        assert "codex" in output["reviewers"]


class TestRoutingRecommendationAnnotation:
    """Test that routing recommendations are surfaced in hook output."""

    def test_routing_annotation_includes_reviewers(self):
        """When the routing gate runs, output should mention recommended reviewers."""
        # We test the Python script directly since the hook integration
        # depends on require-cross-review.sh which checks git state
        diff = "diff --git a/foo.py b/foo.py\n--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new\n"
        result = subprocess.run(
            ["uv", "run", "python", str(ROUTING_GATE), "--stdin", "--pretty"],
            input=diff,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["orchestrator"] == "claude"
        assert "codex" in output["reviewers"]
        assert output["priority"] in ("low", "normal", "high")

    def test_architecture_change_recommends_gemini(self):
        """Architecture-heavy changes should recommend Gemini as third reviewer."""
        lines = []
        for d in ["scripts/ai", "coordination", "docs/standards", ".claude/rules"]:
            lines.append(f"diff --git a/{d}/f.py b/{d}/f.py")
            lines.append(f"--- a/{d}/f.py")
            lines.append(f"+++ b/{d}/f.py")
            lines.append("@@ -1 +1 @@")
            lines.append("-old")
            lines.append("+new")
        diff = "\n".join(lines)
        result = subprocess.run(
            ["uv", "run", "python", str(ROUTING_GATE), "--stdin"],
            input=diff,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "gemini" in output["reviewers"]
        assert "architecture-heavy" in output["triggers_matched"]
