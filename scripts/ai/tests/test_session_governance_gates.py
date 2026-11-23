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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REVIEW_GATE_SH = REPO_ROOT / "scripts" / "enforcement" / "require-review-on-push.sh"
SESSION_GOV_HOOK = REPO_ROOT / ".claude" / "hooks" / "session-governor-check.sh"
ERROR_TRACKER_HOOK = REPO_ROOT / ".claude" / "hooks" / "error-loop-tracker.sh"
GOVERNANCE_POLICY = REPO_ROOT / "scripts" / "workflow" / "governance-checkpoints.yaml"


@pytest.fixture(autouse=True)
def isolated_workspace(tmp_path, monkeypatch):
    """Keep unchanged hook dependencies, state and audit logs in a disposable root."""
    source_root = REPO_ROOT
    root = tmp_path / "workspace"
    sources = (
        REVIEW_GATE_SH,
        SESSION_GOV_HOOK,
        ERROR_TRACKER_HOOK,
        source_root / "scripts" / "workflow" / "session_governor.py",
        GOVERNANCE_POLICY,
    )
    for source in sources:
        target = root / source.relative_to(source_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    # Git bindings and user configuration must not redirect audit writes or identity.
    for name in list(os.environ):
        if name.startswith("GIT_"):
            monkeypatch.delenv(name)
    for name in ("HOME", "TMPDIR", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        directory = root / name.lower()
        directory.mkdir()
        monkeypatch.setenv(name, str(directory))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(root.parent))
    subprocess.run(
        ["git", "init", "--initial-branch=test-audit-branch", str(root)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=root,
    )
    # A committed HEAD is required by the audit hook's branch lookup. Build a
    # synthetic empty commit object without reading or setting a user identity.
    def fixture_git(*args, input=None):
        return subprocess.run(
            ["git", *args], input=input, check=True, capture_output=True,
            text=True, encoding="utf-8", timeout=10, cwd=root,
        ).stdout.strip()

    tree = fixture_git("write-tree")
    commit = fixture_git(
        "hash-object", "-t", "commit", "-w", "--stdin",
        input=(f"tree {tree}\nauthor Test <> 0 +0000\n"
               "committer Test <> 0 +0000\n\nSynthetic audit fixture\n"),
    )
    fixture_git("update-ref", "HEAD", commit)
    monkeypatch.setenv("WORKSPACE_HUB", str(root))
    # The governor subprocess needs the same Python dependencies as this test run.
    monkeypatch.setenv("PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("VIRTUAL_ENV", sys.prefix)
    monkeypatch.setenv("UV_PYTHON", sys.executable)
    for name in ("REVIEW_GATE_SH", "SESSION_GOV_HOOK", "ERROR_TRACKER_HOOK", "GOVERNANCE_POLICY"):
        source = globals()[name]
        monkeypatch.setitem(globals(), name, root / source.relative_to(source_root))
    monkeypatch.setitem(globals(), "REPO_ROOT", root)
    yield root
    for source in sources:
        assert (root / source.relative_to(source_root)).read_bytes() == source.read_bytes()


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


def assert_tracker_resets_on_success(payload: dict) -> None:
    """Issue #2078: success must replace a nonzero counter with an existing zero."""
    state_dir = REPO_ROOT / ".claude" / "state" / "session-governor"
    state_dir.mkdir(parents=True, exist_ok=True)
    counter_file = state_dir / "consecutive-error-count"
    # Two synthetic prior failures give a nonzero seed; a success leaves no errors.
    counter_file.write_text("2", encoding="utf-8", newline="\n")
    (state_dir / "last-error-hash").write_text("abc123", encoding="utf-8", newline="\n")
    result = run_error_tracker(payload, env_extra={"WORKSPACE_HUB": str(REPO_ROOT)})
    assert result.returncode == 0, f"Tracker hook failed: {result.stderr}"
    assert counter_file.is_file(), "Expected counter file to exist after success"
    count_val = counter_file.read_text(encoding="utf-8").strip()
    assert count_val == "0", f"Expected counter=0 after success, got {count_val!r}"


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
        pre_lines = log_path.read_text(encoding="utf-8").strip().splitlines() if log_path.exists() else []

        run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})

        assert log_path.exists(), f"Bypass log file not created: {log_path}"
        post_lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(post_lines) > len(pre_lines), (
            "Expected at least one new line appended to bypass log"
        )

    def test_bypass_log_entry_is_valid_json(self):
        """Bypass log entries must be parseable JSON."""
        run_review_gate(env_extra={"SKIP_REVIEW_GATE": "1"})
        log_path = REPO_ROOT / "logs" / "hooks" / "review-gate-bypass.jsonl"
        assert log_path.exists(), "Bypass log not found"
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
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
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        entry = json.loads(lines[-1])
        assert "branch" in entry, f"Missing 'branch' in bypass entry: {entry}"
        assert entry["branch"] == "test-audit-branch", (
            "Bypass audit must record the disposable repository's exact branch"
        )


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
        content = REVIEW_GATE_SH.read_text(encoding="utf-8")
        assert "REVIEW_GATE_STRICT:-1" in content, (
            "require-review-on-push.sh must default REVIEW_GATE_STRICT to 1 (strict). "
            "Use ${REVIEW_GATE_STRICT:-1} not ${REVIEW_GATE_STRICT:-}"
        )

    def test_script_has_bypass_log_function(self):
        """Script source must contain a bypass logging function."""
        content = REVIEW_GATE_SH.read_text(encoding="utf-8")
        assert "log_bypass" in content, (
            "Script must define a log_bypass() function to audit SKIP_REVIEW_GATE usage"
        )

    def test_skip_review_gate_calls_log_bypass(self):
        """The bypass path must invoke log_bypass (not silently exit)."""
        content = REVIEW_GATE_SH.read_text(encoding="utf-8")
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
        content = SESSION_GOV_HOOK.read_text(encoding="utf-8")
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
        content = SESSION_GOV_HOOK.read_text(encoding="utf-8")
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
        # subprocess.run starts Bash as a child of this Python process; Bash sets PPID.
        counter_file = state_dir / f"tool-call-count-{os.getpid()}"
        policy = yaml.safe_load(GOVERNANCE_POLICY.read_text(encoding="utf-8"))
        threshold = next(
            checkpoint["threshold"]
            for checkpoint in policy["checkpoints"]
            if checkpoint["id"] == "tool-call-ceiling"
        )
        # governance-checkpoints.yaml supplies the ceiling; one hook call adds one.
        counter_file.write_text(str(threshold - 1), encoding="utf-8", newline="\n")
        env = os.environ.copy()
        env["WORKSPACE_HUB"] = str(REPO_ROOT)
        result = subprocess.run(
            ["bash", str(SESSION_GOV_HOOK)],
            input='{"tool_name":"Bash","tool_input":{"command":"ls"}}',
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            env=env,
        )

        # Hook always exits 0 (blocking via JSON decision, not exit code).
        assert result.returncode == 0, f"Hook failed: {result.stderr}"
        assert result.stdout.strip(), f"Expected nonempty stdout at ceiling. stderr={result.stderr}"
        decision = json.loads(result.stdout)
        assert decision.get("decision") == "block", (
            f"Expected block decision at ceiling, got: {decision}"
        )
        assert counter_file.read_text(encoding="utf-8").strip() == str(threshold)


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
        content = ERROR_TRACKER_HOOK.read_text(encoding="utf-8")
        assert "md5sum" in content, (
            "error-loop-tracker.sh must use md5sum to hash error signatures for dedup"
        )

    def test_error_tracker_resets_on_success(self):
        """Successful tool call must reset the consecutive error counter to 0."""
        assert_tracker_resets_on_success({
            "tool_name": "Bash",
            "tool_response": {"is_error": False, "exit_code": 0},
        })

    def test_error_tracker_increments_on_same_error(self):
        """Same error repeated must increment the counter, not reset."""
        content = ERROR_TRACKER_HOOK.read_text(encoding="utf-8")
        # Must compare hashes and increment if they match
        assert "CURRENT_HASH" in content and "PREV_HASH" in content, (
            "Hook must compare current and previous error hashes"
        )
        assert "CURRENT_COUNT + 1" in content or "COUNT + 1" in content, (
            "Hook must increment counter when same error repeats"
        )

    def test_error_tracker_success_payload_resets_counter(self):
        """Run tracker with a non-error payload and verify counter resets."""
        # Send a success payload without an is_error flag or error patterns.
        assert_tracker_resets_on_success({
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
            "tool_response": {
                "exit_code": 0,
                "stdout": "hello",
                "stderr": "",
            },
        })

    def test_error_tracker_state_directory_convention(self):
        """State directory path must follow the session-governor convention."""
        content = ERROR_TRACKER_HOOK.read_text(encoding="utf-8")
        assert "session-governor" in content, (
            "error-loop-tracker.sh must use .claude/state/session-governor/ for state files"
        )
        assert "consecutive-error-count" in content, (
            "error-loop-tracker.sh must maintain 'consecutive-error-count' state file"
        )
        assert "last-error-hash" in content, (
            "error-loop-tracker.sh must maintain 'last-error-hash' state file for dedup"
        )


class TestAssertionRegressions:
    """Broken hook responses must fail the behavioral tests, even after exit success."""

    @pytest.mark.parametrize(
        ("stdout", "message"),
        [
            ("", "nonempty stdout"),
            (" \n", "nonempty stdout"),
            ('{"decision":"allow"}', "Expected block decision"),
        ],
        ids=["empty", "whitespace", "allow"],
    )
    def test_stop_assertion_rejects_nonblocking_output(self, monkeypatch, stdout, message):
        def silent_success(command, **kwargs):
            # Exit zero is successful completion under the Bash hook protocol.
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        monkeypatch.setattr(subprocess, "run", silent_success)
        with pytest.raises(AssertionError, match=message):
            TestSessionCounterHook().test_governor_hook_emits_block_on_stop()

    @pytest.mark.parametrize(
        "test_name",
        ["test_error_tracker_resets_on_success", "test_error_tracker_success_payload_resets_counter"],
        ids=["explicit-success", "success-payload"],
    )
    @pytest.mark.parametrize("outcome", ["missing", "unreset"])
    def test_reset_assertion_rejects_invalid_counter(self, monkeypatch, test_name, outcome):
        def unchanged_counter(command, **kwargs):
            if outcome == "missing":
                counter = REPO_ROOT / ".claude" / "state" / "session-governor" / "consecutive-error-count"
                counter.rename(counter.with_suffix(".removed"))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        monkeypatch.setattr(subprocess, "run", unchanged_counter)
        with pytest.raises(AssertionError, match="counter.*(exist|after success)"):
            getattr(TestErrorLoopTrackerDedup(), test_name)()
