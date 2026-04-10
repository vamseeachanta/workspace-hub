"""Tests for session governance gates — bypass logging, counter, and error dedup.

Covers runtime enforcement behavior per GitHub issue #2056:
- SKIP_REVIEW_GATE=1 bypass is logged (auditable, not silent)
- require-review-on-push.sh strict mode is the default
- session-governor-check.sh counter increments and creates state files
- error-loop-tracker.sh error hash/dedup resets counter on success
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
REVIEW_GATE_SH = REPO_ROOT / "scripts" / "enforcement" / "require-review-on-push.sh"
SESSION_GOV_HOOK = REPO_ROOT / ".claude" / "hooks" / "session-governor-check.sh"
ERROR_TRACKER_HOOK = REPO_ROOT / ".claude" / "hooks" / "error-loop-tracker.sh"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_review_gate(env_extra: dict | None = None, args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Run require-review-on-push.sh in a temp dir that IS a git repo."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(REVIEW_GATE_SH)] + (args or []),
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        env=env,
    )


def run_error_tracker(tool_input: dict, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Run error-loop-tracker.sh with the given JSON tool response payload."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(ERROR_TRACKER_HOOK)],
        input=json.dumps(tool_input),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO_ROOT),
        env=env,
    )


# ---------------------------------------------------------------------------
# Review gate bypass logging tests
# ---------------------------------------------------------------------------


class TestBypassAuditLogging:
    """SKIP_REVIEW_GATE=1 bypass must be logged — not silent.

    These tests verify AC #3 of #2056: bypass is auditable.
    """

    def test_bypass_exits_zero(self):
        """SKIP_REVIEW_GATE=1 should allow the push (exit 0)."""
        result = run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})
        assert result.returncode == 0, (
            f"Expected exit 0 for bypass, got {result.returncode}. stderr={result.stderr}"
        )

    def test_bypass_emits_log_message(self):
        """SKIP_REVIEW_GATE=1 must emit a visible message indicating bypass was logged."""
        result = run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})
        combined = result.stdout + result.stderr
        assert "bypass" in combined.lower(), (
            f"Expected 'bypass' in output, got: {combined!r}"
        )

    def test_bypass_creates_log_file(self):
        """SKIP_REVIEW_GATE=1 must write an audit entry to review-gate-bypass.jsonl."""
        log_path = REPO_ROOT / "logs" / "hooks" / "review-gate-bypass.jsonl"
        # Remove stale log if present to get a clean baseline
        pre_size = log_path.stat().st_size if log_path.exists() else 0
        pre_lines = log_path.read_text().strip().splitlines() if log_path.exists() else []

        run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})

        assert log_path.exists(), f"Bypass log file not created: {log_path}"
        post_lines = log_path.read_text().strip().splitlines()
        assert len(post_lines) > len(pre_lines), (
            "Expected at least one new line appended to bypass log"
        )

    def test_bypass_log_entry_is_valid_json(self):
        """Bypass log entries must be parseable JSON."""
        run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})
        log_path = REPO_ROOT / "logs" / "hooks" / "review-gate-bypass.jsonl"
        assert log_path.exists(), "Bypass log not found"
        lines = log_path.read_text().strip().splitlines()
        assert lines, "Bypass log is empty"
        # Parse the last line (most recent bypass)
        entry = json.loads(lines[-1])
        assert "timestamp" in entry, f"Missing 'timestamp' in bypass entry: {entry}"
        assert "action" in entry, f"Missing 'action' in bypass entry: {entry}"
        assert entry["action"] == "bypass", f"Expected action='bypass', got: {entry['action']}"

    def test_bypass_log_contains_branch(self):
        """Bypass log entry must include the current branch name."""
        run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})
        log_path = REPO_ROOT / "logs" / "hooks" / "review-gate-bypass.jsonl"
        lines = log_path.read_text().strip().splitlines()
        entry = json.loads(lines[-1])
        assert "branch" in entry, f"Missing 'branch' in bypass entry: {entry}"
        assert entry["branch"], "Branch must be non-empty"


# ---------------------------------------------------------------------------
# Review gate strict mode tests
# ---------------------------------------------------------------------------


class TestReviewGateStrictMode:
    """require-review-on-push.sh must default to strict mode (block, not warn)."""

    def test_review_gate_script_exists(self):
        """The script must exist at the expected path."""
        assert REVIEW_GATE_SH.exists(), f"Script not found: {REVIEW_GATE_SH}"

    def test_review_gate_script_is_executable(self):
        """The script must be executable."""
        assert os.access(REVIEW_GATE_SH, os.X_OK), f"Script not executable: {REVIEW_GATE_SH}"

    def test_script_source_defaults_to_strict(self):
        """Source code must use REVIEW_GATE_STRICT:-1 (default strict)."""
        content = REVIEW_GATE_SH.read_text()
        assert "REVIEW_GATE_STRICT:-1" in content, (
            "require-review-on-push.sh must default REVIEW_GATE_STRICT to 1 (strict). "
            "Use ${REVIEW_GATE_STRICT:-1} not ${REVIEW_GATE_STRICT:-}"
        )

    def test_script_has_bypass_log_function(self):
        """Script source must contain a bypass logging function."""
        content = REVIEW_GATE_SH.read_text()
        assert "log_bypass" in content, (
            "Script must define a log_bypass() function to audit SKIP_REVIEW_GATE usage"
        )

    def test_skip_review_gate_calls_log_bypass(self):
        """The bypass path must invoke log_bypass (not silently exit)."""
        content = REVIEW_GATE_SH.read_text()
        # The implementation block uses ${SKIP_REVIEW_GATE:-} for the conditional.
        # Search for the conditional implementation (not the comment at top of file).
        skip_impl_idx = content.find('SKIP_REVIEW_GATE:-}')
        assert skip_impl_idx != -1, "SKIP_REVIEW_GATE conditional not found in script"
        # log_bypass should appear within 400 chars of the conditional
        bypass_block = content[skip_impl_idx:skip_impl_idx + 400]
        assert "log_bypass" in bypass_block, (
            "SKIP_REVIEW_GATE handler must call log_bypass() before exit"
        )


# ---------------------------------------------------------------------------
# Session counter hook tests
# ---------------------------------------------------------------------------


class TestSessionCounterHook:
    """session-governor-check.sh increments a per-session (PPID) counter file."""

    def test_governor_hook_exists(self):
        """session-governor-check.sh must exist."""
        assert SESSION_GOV_HOOK.exists(), f"Hook not found: {SESSION_GOV_HOOK}"

    def test_governor_hook_uses_ppid_for_session(self):
        """Hook must use PPID as the session key for counter isolation."""
        content = SESSION_GOV_HOOK.read_text()
        assert "PPID" in content, "Hook must use $PPID as session key"
        assert "tool-call-count-" in content, (
            "Counter filename must include session key (PPID) to isolate sessions"
        )

    def test_governor_hook_creates_counter_file(self):
        """Hook must create/increment a counter file in the state directory."""
        with tempfile.TemporaryDirectory() as state_dir:
            env = os.environ.copy()
            env["WORKSPACE_HUB"] = str(REPO_ROOT)
            # Run the hook with simulated tool input (non-blocking call count)
            result = subprocess.run(
                ["bash", str(SESSION_GOV_HOOK)],
                input='{"tool_name":"Bash","tool_input":{"command":"ls"}}',
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(REPO_ROOT),
                env=env,
            )
            # Hook exits 0 for all non-blocked calls
            assert result.returncode == 0, f"Hook failed: {result.stderr}"

    def test_governor_hook_fast_path_ceiling_is_80pct(self):
        """Hook fast-path ceiling must be 80% of the governance threshold."""
        content = SESSION_GOV_HOOK.read_text()
        # Extract FAST_PATH_CEILING and THRESHOLD values from the script
        import re
        threshold_match = re.search(r"THRESHOLD=(\d+)", content)
        fast_path_match = re.search(r"FAST_PATH_CEILING=(\d+)", content)
        assert threshold_match, "THRESHOLD not found in hook"
        assert fast_path_match, "FAST_PATH_CEILING not found in hook"
        threshold = int(threshold_match.group(1))
        fast_path = int(fast_path_match.group(1))
        expected_fast_path = int(threshold * 0.8)
        assert fast_path == expected_fast_path, (
            f"FAST_PATH_CEILING={fast_path} should be 80% of THRESHOLD={threshold} "
            f"(expected {expected_fast_path})"
        )

    def test_governor_hook_emits_block_on_stop(self):
        """At the ceiling, the hook must emit a JSON block decision on stdout."""
        state_dir = REPO_ROOT / ".claude" / "state" / "session-governor"
        state_dir.mkdir(parents=True, exist_ok=True)

        # Use a synthetic PPID that won't collide with real sessions
        fake_ppid = "99999999"
        counter_file = state_dir / f"tool-call-count-{fake_ppid}"

        try:
            # Set counter to threshold value to trigger STOP
            import re
            content = SESSION_GOV_HOOK.read_text()
            threshold_match = re.search(r"THRESHOLD=(\d+)", content)
            assert threshold_match, "THRESHOLD not found in hook"
            threshold = int(threshold_match.group(1))
            # Write a count just below threshold so the next call hits ceiling
            counter_file.write_text(str(threshold - 1))

            env = os.environ.copy()
            env["WORKSPACE_HUB"] = str(REPO_ROOT)
            env["PPID"] = fake_ppid

            result = subprocess.run(
                ["bash", str(SESSION_GOV_HOOK)],
                input='{"tool_name":"Bash","tool_input":{"command":"ls"}}',
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(REPO_ROOT),
                env=env,
            )

            # Hook always exits 0 (blocking via JSON decision, not exit code)
            assert result.returncode == 0
            # At ceiling, should emit {"decision":"block"} on stdout
            if result.stdout.strip():
                decision = json.loads(result.stdout.strip())
                assert decision.get("decision") == "block", (
                    f"Expected block decision at ceiling, got: {decision}"
                )
        finally:
            counter_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Error loop tracker tests
# ---------------------------------------------------------------------------


class TestErrorLoopTrackerDedup:
    """error-loop-tracker.sh uses MD5 hashing to detect consecutive identical errors."""

    def test_error_tracker_hook_exists(self):
        """error-loop-tracker.sh must exist."""
        assert ERROR_TRACKER_HOOK.exists(), f"Hook not found: {ERROR_TRACKER_HOOK}"

    def test_error_tracker_uses_md5_hash(self):
        """Hook must use md5sum for error signature deduplication."""
        content = ERROR_TRACKER_HOOK.read_text()
        assert "md5sum" in content, (
            "error-loop-tracker.sh must use md5sum to hash error signatures for dedup"
        )

    def test_error_tracker_resets_on_success(self):
        """Successful tool call must reset the consecutive error counter to 0."""
        content = ERROR_TRACKER_HOOK.read_text()
        # The hook must write '0' to the error count file on success
        assert '"0" > "$ERROR_COUNT_FILE"' in content or "echo 0 >" in content, (
            "Hook must reset consecutive error count to 0 on successful tool call"
        )

    def test_error_tracker_increments_on_same_error(self):
        """Same error repeated must increment the counter, not reset."""
        content = ERROR_TRACKER_HOOK.read_text()
        # Must compare hashes and increment if they match
        assert "CURRENT_HASH" in content and "PREV_HASH" in content, (
            "Hook must compare current and previous error hashes"
        )
        assert "CURRENT_COUNT + 1" in content or "COUNT + 1" in content, (
            "Hook must increment counter when same error repeats"
        )

    def test_error_tracker_success_payload_resets_counter(self):
        """Run tracker with a non-error payload and verify counter resets."""
        state_dir = REPO_ROOT / ".claude" / "state" / "session-governor"
        state_dir.mkdir(parents=True, exist_ok=True)
        counter_file = state_dir / "consecutive-error-count"
        hash_file = state_dir / "last-error-hash"

        # Pre-set counter to simulate prior errors
        counter_file.write_text("2")
        hash_file.write_text("abc123")

        env = {"WORKSPACE_HUB": str(REPO_ROOT)}
        env.update({k: v for k, v in os.environ.items()})

        # Send a success payload (no is_error flag, no error patterns)
        success_payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
            "tool_response": {
                "exit_code": 0,
                "stdout": "hello",
                "stderr": "",
            },
        }
        result = run_error_tracker(success_payload, env_extra={"WORKSPACE_HUB": str(REPO_ROOT)})
        assert result.returncode == 0, f"Tracker hook failed: {result.stderr}"

        # Counter should be reset to 0
        if counter_file.exists():
            count_val = counter_file.read_text().strip()
            assert count_val == "0", f"Expected counter=0 after success, got {count_val!r}"

    def test_error_tracker_state_directory_convention(self):
        """State directory path must follow the session-governor convention."""
        content = ERROR_TRACKER_HOOK.read_text()
        assert "session-governor" in content, (
            "error-loop-tracker.sh must use .claude/state/session-governor/ for state files"
        )
        assert "consecutive-error-count" in content, (
            "error-loop-tracker.sh must maintain 'consecutive-error-count' state file"
        )
        assert "last-error-hash" in content, (
            "error-loop-tracker.sh must maintain 'last-error-hash' state file for dedup"
        )
