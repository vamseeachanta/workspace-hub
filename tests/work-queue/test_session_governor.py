"""
Tests for session-governor.py — hard-stop checkpoint verification and runtime enforcement.

Covers:
  - Checkpoint config loading and schema validation
  - Gate verification logic (present/missing gates)
  - Report generation structure
  - Edge cases: empty config, unknown gate types
  - Runtime enforcement: tool-call ceiling, error-loop breaker verdicts
  - Plan-approval gate hook behavior (#1839)
  - Strict review gate defaults (#1839)
  - Old 500-ceiling hook removal (#1839)

Run: uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v
"""

from __future__ import annotations

import os
import sys
import textwrap

import pytest
import yaml

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "workflow"))

from session_governor import (
    CheckpointConfig,
    GateStatus,
    LimitResult,
    SessionVerdict,
    check_session_limits,
    load_checkpoints,
    session_limits_verdict,
    verify_gates,
)


# ── Config loading tests ────────────────────────────────────────────────


SAMPLE_CONFIG_YAML = textwrap.dedent("""\
    version: 1
    checkpoints:
      - id: plan-approval
        name: Plan Approval
        stage: pre-implement
        type: hard-stop
        description: User must approve plan before implementation begins.
        enforced: true

      - id: review-verdict
        name: Review Verdict
        stage: post-review
        type: hard-stop
        description: User reviews cross-review results, approves or rejects.
        enforced: true

      - id: session-close
        name: Session Close
        stage: end
        type: hard-stop
        description: User confirms session summary and next priorities.
        enforced: false

      - id: tdd-red
        name: TDD Red Phase
        stage: pre-implement
        type: auto-gate
        description: Tests written and failing before implementation.
        enforced: true

      - id: tool-call-ceiling
        name: Tool Call Ceiling
        stage: runtime
        type: auto-gate
        description: Auto-pause at 200 tool calls.
        enforced: true
        threshold: 200
""")


@pytest.fixture
def sample_config() -> CheckpointConfig:
    """Parse sample YAML into a CheckpointConfig."""
    data = yaml.safe_load(SAMPLE_CONFIG_YAML)
    return load_checkpoints(data)


# ── Schema tests ────────────────────────────────────────────────────────


class TestConfigLoading:
    """Checkpoint config loads correctly from YAML data."""

    def test_loads_all_checkpoints(self, sample_config: CheckpointConfig):
        assert len(sample_config.checkpoints) == 5

    def test_checkpoint_has_required_fields(self, sample_config: CheckpointConfig):
        cp = sample_config.checkpoints[0]
        assert cp.id == "plan-approval"
        assert cp.name == "Plan Approval"
        assert cp.stage == "pre-implement"
        assert cp.type == "hard-stop"
        assert cp.enforced is True

    def test_version_present(self, sample_config: CheckpointConfig):
        assert sample_config.version == 1

    def test_hard_stops_filtered(self, sample_config: CheckpointConfig):
        hard_stops = [c for c in sample_config.checkpoints if c.type == "hard-stop"]
        assert len(hard_stops) == 3

    def test_auto_gates_filtered(self, sample_config: CheckpointConfig):
        auto_gates = [c for c in sample_config.checkpoints if c.type == "auto-gate"]
        assert len(auto_gates) == 2

    def test_threshold_parsed(self, sample_config: CheckpointConfig):
        ceiling = next(c for c in sample_config.checkpoints if c.id == "tool-call-ceiling")
        assert ceiling.threshold == 200


# ── Gate verification tests ─────────────────────────────────────────────


class TestGateVerification:
    """verify_gates checks which required gates are present in session artifacts."""

    def test_all_gates_present(self, sample_config: CheckpointConfig):
        """When all gate IDs are in the passed set, all should be PASS."""
        passed_gates = {"plan-approval", "review-verdict", "session-close", "tdd-red", "tool-call-ceiling"}
        results = verify_gates(sample_config, passed_gates)
        assert all(r.status == GateStatus.PASS for r in results)

    def test_missing_enforced_gate_fails(self, sample_config: CheckpointConfig):
        """Missing an enforced gate should produce FAIL status."""
        passed_gates = {"review-verdict", "session-close", "tdd-red", "tool-call-ceiling"}
        results = verify_gates(sample_config, passed_gates)
        plan_result = next(r for r in results if r.checkpoint_id == "plan-approval")
        assert plan_result.status == GateStatus.FAIL

    def test_missing_unenforced_gate_warns(self, sample_config: CheckpointConfig):
        """Missing a non-enforced gate should produce WARN, not FAIL."""
        passed_gates = {"plan-approval", "review-verdict", "tdd-red", "tool-call-ceiling"}
        results = verify_gates(sample_config, passed_gates)
        close_result = next(r for r in results if r.checkpoint_id == "session-close")
        assert close_result.status == GateStatus.WARN

    def test_empty_passed_gates(self, sample_config: CheckpointConfig):
        """No gates passed — enforced ones FAIL, unenforced WARN."""
        results = verify_gates(sample_config, set())
        fail_count = sum(1 for r in results if r.status == GateStatus.FAIL)
        warn_count = sum(1 for r in results if r.status == GateStatus.WARN)
        # 4 enforced checkpoints should FAIL, 1 unenforced should WARN
        assert fail_count == 4
        assert warn_count == 1

    def test_overall_pass_when_all_enforced_present(self, sample_config: CheckpointConfig):
        """Overall verdict is PASS when all enforced gates pass (unenforced can be missing)."""
        passed_gates = {"plan-approval", "review-verdict", "tdd-red", "tool-call-ceiling"}
        results = verify_gates(sample_config, passed_gates)
        enforced_results = [r for r in results if r.enforced]
        assert all(r.status == GateStatus.PASS for r in enforced_results)

    def test_overall_fail_when_enforced_missing(self, sample_config: CheckpointConfig):
        """Overall verdict is FAIL when any enforced gate is missing."""
        passed_gates = {"session-close"}
        results = verify_gates(sample_config, passed_gates)
        enforced_results = [r for r in results if r.enforced]
        assert any(r.status == GateStatus.FAIL for r in enforced_results)


# ── Edge case tests ─────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases: empty configs, unknown gate IDs."""

    def test_empty_checkpoints(self):
        """Config with no checkpoints should load and verify without error."""
        data = {"version": 1, "checkpoints": []}
        config = load_checkpoints(data)
        results = verify_gates(config, set())
        assert results == []

    def test_extra_passed_gates_ignored(self, sample_config: CheckpointConfig):
        """Gates in passed set that aren't in config are silently ignored."""
        passed_gates = {"plan-approval", "review-verdict", "session-close",
                        "tdd-red", "tool-call-ceiling", "nonexistent-gate"}
        results = verify_gates(sample_config, passed_gates)
        assert len(results) == 5  # only config-defined gates reported


# ── Runtime enforcement tests (Phase 2) ────────────────────────────────


RUNTIME_CONFIG_YAML = textwrap.dedent("""\
    version: 1
    checkpoints:
      - id: tool-call-ceiling
        name: Tool Call Ceiling
        stage: runtime
        type: auto-gate
        description: Auto-pause at 200 tool calls.
        enforced: true
        threshold: 200

      - id: error-loop-breaker
        name: Error Loop Breaker
        stage: runtime
        type: auto-gate
        description: If same error repeats 3x, hard stop.
        enforced: true
        threshold: 3

      - id: plan-approval
        name: Plan Approval
        stage: pre-implement
        type: hard-stop
        description: User must approve plan.
        enforced: true
""")


@pytest.fixture
def runtime_config() -> CheckpointConfig:
    data = yaml.safe_load(RUNTIME_CONFIG_YAML)
    return load_checkpoints(data)


class TestCheckSessionLimits:
    """check_session_limits evaluates live metrics against thresholds."""

    def test_low_counts_continue(self, runtime_config: CheckpointConfig):
        """Well below thresholds → all CONTINUE."""
        results = check_session_limits(runtime_config, tool_call_count=50, consecutive_error_count=0)
        assert all(r.verdict == SessionVerdict.CONTINUE for r in results)

    def test_tool_calls_at_threshold_stops(self, runtime_config: CheckpointConfig):
        """Exactly at threshold → STOP."""
        results = check_session_limits(runtime_config, tool_call_count=200)
        tc = next(r for r in results if r.checkpoint_id == "tool-call-ceiling")
        assert tc.verdict == SessionVerdict.STOP

    def test_tool_calls_over_threshold_stops(self, runtime_config: CheckpointConfig):
        """Over threshold → STOP."""
        results = check_session_limits(runtime_config, tool_call_count=300)
        tc = next(r for r in results if r.checkpoint_id == "tool-call-ceiling")
        assert tc.verdict == SessionVerdict.STOP

    def test_tool_calls_warning_zone_pauses(self, runtime_config: CheckpointConfig):
        """80-99% of threshold → PAUSE."""
        results = check_session_limits(runtime_config, tool_call_count=170)
        tc = next(r for r in results if r.checkpoint_id == "tool-call-ceiling")
        assert tc.verdict == SessionVerdict.PAUSE

    def test_error_loop_at_threshold_stops(self, runtime_config: CheckpointConfig):
        """3 consecutive errors → STOP."""
        results = check_session_limits(runtime_config, consecutive_error_count=3)
        el = next(r for r in results if r.checkpoint_id == "error-loop-breaker")
        assert el.verdict == SessionVerdict.STOP

    def test_error_loop_below_continues(self, runtime_config: CheckpointConfig):
        """1 error → CONTINUE (below 80% of 3)."""
        results = check_session_limits(runtime_config, consecutive_error_count=1)
        el = next(r for r in results if r.checkpoint_id == "error-loop-breaker")
        assert el.verdict == SessionVerdict.CONTINUE

    def test_only_runtime_gates_checked(self, runtime_config: CheckpointConfig):
        """Hard-stop gates without thresholds are not in results."""
        results = check_session_limits(runtime_config, tool_call_count=50)
        ids = {r.checkpoint_id for r in results}
        assert "plan-approval" not in ids

    def test_overall_verdict_stop_wins(self, runtime_config: CheckpointConfig):
        """If any check is STOP, overall is STOP."""
        results = check_session_limits(runtime_config, tool_call_count=200, consecutive_error_count=0)
        assert session_limits_verdict(results) == SessionVerdict.STOP

    def test_overall_verdict_pause_if_no_stop(self, runtime_config: CheckpointConfig):
        """If worst is PAUSE, overall is PAUSE."""
        results = check_session_limits(runtime_config, tool_call_count=165, consecutive_error_count=0)
        assert session_limits_verdict(results) == SessionVerdict.PAUSE

    def test_overall_verdict_continue_when_clear(self, runtime_config: CheckpointConfig):
        """All clear → CONTINUE."""
        results = check_session_limits(runtime_config, tool_call_count=10, consecutive_error_count=0)
        assert session_limits_verdict(results) == SessionVerdict.CONTINUE

    def test_empty_config_returns_empty(self):
        """Config with no runtime gates → empty results."""
        data = {"version": 1, "checkpoints": []}
        config = load_checkpoints(data)
        results = check_session_limits(config, tool_call_count=999)
        assert results == []


# ── Hook integration tests (Phase 2b) ────────────────────────────


class TestHookIntegration:
    """Tests for the session-governor-check.sh hook wiring behavior.

    These tests verify:
    - The hook script exists and is executable
    - The governor produces correct exit codes for hook consumption
    - The counter-based fast-path logic aligns with governor thresholds
    - The JSON block protocol matches repo convention
    """

    def test_hook_script_exists_and_executable(self):
        """The hook script must exist at the expected path and be executable."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "session-governor-check.sh")
        assert os.path.isfile(hook_path), f"Hook not found: {hook_path}"
        assert os.access(hook_path, os.X_OK), f"Hook not executable: {hook_path}"

    def test_hook_registered_in_settings(self):
        """The hook must be registered in .claude/settings.json PreToolUse."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        pre_tool_hooks = settings.get("hooks", {}).get("PreToolUse", [])
        found = any(
            "session-governor-check.sh" in h.get("command", "")
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        assert found, "session-governor-check.sh not found in PreToolUse hooks"

    def test_governor_exit_code_continue(self, runtime_config: CheckpointConfig):
        """Governor exit 0 (CONTINUE) when well below thresholds."""
        results = check_session_limits(runtime_config, tool_call_count=50, consecutive_error_count=0)
        verdict = session_limits_verdict(results)
        assert verdict == SessionVerdict.CONTINUE
        # Hook maps exit 0 → silent allow
        assert verdict.value == "CONTINUE"

    def test_governor_exit_code_pause(self, runtime_config: CheckpointConfig):
        """Governor exit 1 (PAUSE) at 80-99% of threshold."""
        results = check_session_limits(runtime_config, tool_call_count=170, consecutive_error_count=0)
        verdict = session_limits_verdict(results)
        assert verdict == SessionVerdict.PAUSE
        # Hook maps exit 1 → warn on stderr, allow tool call

    def test_governor_exit_code_stop(self, runtime_config: CheckpointConfig):
        """Governor exit 2 (STOP) at threshold — hook should emit block decision."""
        results = check_session_limits(runtime_config, tool_call_count=200, consecutive_error_count=0)
        verdict = session_limits_verdict(results)
        assert verdict == SessionVerdict.STOP
        # Hook maps exit 2 → {"decision":"block"} on stdout

    def test_fast_path_ceiling_aligns_with_threshold(self, runtime_config: CheckpointConfig):
        """Hook fast-path ceiling (160) should be 80% of the 200-call threshold."""
        ceiling_cp = next(
            c for c in runtime_config.checkpoints if c.id == "tool-call-ceiling"
        )
        fast_path = int(ceiling_cp.threshold * 0.8)
        assert fast_path == 160, f"Expected 160, got {fast_path}"

    def test_block_json_format(self, runtime_config: CheckpointConfig):
        """format_limits_report produces valid JSON consumable by hooks."""
        from session_governor import format_limits_report
        results = check_session_limits(runtime_config, tool_call_count=200)
        report = format_limits_report(results)
        import json
        parsed = json.loads(report)
        assert parsed["verdict"] == "STOP"
        assert isinstance(parsed["checks"], list)
        assert len(parsed["checks"]) > 0

    def test_governor_cli_exit_codes(self):
        """Verify the CLI returns correct exit codes for hook consumption."""
        import subprocess
        governor = os.path.join(REPO_ROOT, "scripts", "workflow", "session_governor.py")

        # CONTINUE (exit 0)
        result = subprocess.run(
            ["uv", "run", governor, "--check-limits", "--tool-calls", "50"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Expected 0, got {result.returncode}"

        # PAUSE (exit 1) — 85% of the 1000-call threshold
        result = subprocess.run(
            ["uv", "run", governor, "--check-limits", "--tool-calls", "850"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 1, f"Expected 1, got {result.returncode}"

        # STOP (exit 2) — at the 1000-call threshold
        result = subprocess.run(
            ["uv", "run", governor, "--check-limits", "--tool-calls", "1000"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 2, f"Expected 2, got {result.returncode}"


# ── Plan-approval gate tests (#1839) ──────────────────────────────


class TestPlanApprovalGate:
    """Tests for the plan-approval-gate.sh hook (#1839).

    Verifies:
    - Hook script exists and is executable
    - Hook is registered in settings.json
    - Approval marker directory convention exists
    - Hook blocks Write/Edit to implementation paths when no marker
    - Hook allows safe paths (docs, tests, .claude, .planning) without marker
    - Hook allows all paths when marker exists
    """

    def test_hook_exists_and_executable(self):
        """plan-approval-gate.sh must exist and be executable."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "plan-approval-gate.sh")
        assert os.path.isfile(hook_path), f"Hook not found: {hook_path}"
        assert os.access(hook_path, os.X_OK), f"Hook not executable: {hook_path}"

    def test_hook_registered_in_settings(self):
        """plan-approval-gate.sh must be in PreToolUse hooks."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        pre_tool_hooks = settings.get("hooks", {}).get("PreToolUse", [])
        found = any(
            "plan-approval-gate.sh" in h.get("command", "")
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        assert found, "plan-approval-gate.sh not found in PreToolUse hooks"

    def test_hook_matches_write_edit_bash(self):
        """Hook matcher must include Write, Edit, MultiEdit, and Bash."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        pre_tool_hooks = settings.get("hooks", {}).get("PreToolUse", [])
        for entry in pre_tool_hooks:
            for h in entry.get("hooks", []):
                if "plan-approval-gate.sh" in h.get("command", ""):
                    matcher = entry.get("matcher", "")
                    assert "Write" in matcher
                    assert "Edit" in matcher
                    assert "Bash" in matcher
                    return
        pytest.fail("plan-approval-gate.sh entry not found")

    def test_approval_dir_exists(self):
        """The .planning/plan-approved/ directory must exist."""
        approval_dir = os.path.join(REPO_ROOT, ".planning", "plan-approved")
        assert os.path.isdir(approval_dir), f"Missing: {approval_dir}"

    def test_hook_blocks_impl_without_marker(self):
        """Hook blocks Write to implementation path when no marker exists."""
        import subprocess
        import tempfile

        hook = os.path.join(REPO_ROOT, ".claude", "hooks", "plan-approval-gate.sh")
        # Use a temp dir as workspace with no approval markers
        with tempfile.TemporaryDirectory() as tmpdir:
            input_json = '{"tool_name":"Write","tool_input":{"file_path":"/src/app.py"}}'
            result = subprocess.run(
                ["bash", hook],
                input=input_json, capture_output=True, text=True, timeout=10,
                env={**os.environ, "WORKSPACE_HUB": tmpdir},
            )
            # Hook should emit block decision on stdout
            assert "block" in result.stdout.lower() or "block" in result.stderr.lower(), (
                f"Expected block, got stdout={result.stdout!r} stderr={result.stderr!r}"
            )

    def test_hook_allows_safe_paths_without_marker(self):
        """Hook allows writes to safe paths even without approval marker."""
        import subprocess
        import tempfile

        hook = os.path.join(REPO_ROOT, ".claude", "hooks", "plan-approval-gate.sh")
        safe_paths = [
            "/ws/.planning/some-plan.md",
            "/ws/tests/test_foo.py",
            "/ws/.claude/hooks/new-hook.sh",
            "/ws/docs/governance/update.md",
            "/ws/README.md",
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            for safe_path in safe_paths:
                input_json = f'{{"tool_name":"Write","tool_input":{{"file_path":"{safe_path}"}}}}'
                result = subprocess.run(
                    ["bash", hook],
                    input=input_json, capture_output=True, text=True, timeout=10,
                    env={**os.environ, "WORKSPACE_HUB": tmpdir},
                )
                assert "block" not in result.stdout.lower(), (
                    f"Safe path {safe_path} was blocked: {result.stdout}"
                )

    def test_hook_allows_with_marker(self):
        """Hook allows implementation writes when approval marker exists."""
        import subprocess
        import tempfile

        hook = os.path.join(REPO_ROOT, ".claude", "hooks", "plan-approval-gate.sh")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create approval marker
            marker_dir = os.path.join(tmpdir, ".planning", "plan-approved")
            os.makedirs(marker_dir)
            with open(os.path.join(marker_dir, "1839.md"), "w") as f:
                f.write("approved")

            input_json = '{"tool_name":"Write","tool_input":{"file_path":"/src/app.py"}}'
            result = subprocess.run(
                ["bash", hook],
                input=input_json, capture_output=True, text=True, timeout=10,
                env={**os.environ, "WORKSPACE_HUB": tmpdir},
            )
            assert "block" not in result.stdout.lower(), (
                f"Should allow with marker, got: {result.stdout}"
            )


# ── Strict review gate tests (#1839) ─────────────────────────────


class TestStrictReviewGate:
    """Tests for strict review gate defaults (#1839).

    Verifies:
    - REVIEW_GATE_STRICT=1 in settings.json env
    - pre-push-review is enforced: true in governance-checkpoints.yaml
    - require-review-on-push.sh defaults to strict (blocks without review)
    """

    def test_env_has_strict_flag(self):
        """settings.json env must have REVIEW_GATE_STRICT=1."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        env = settings.get("env", {})
        assert env.get("REVIEW_GATE_STRICT") == "1", (
            f"Expected REVIEW_GATE_STRICT=1, got {env.get('REVIEW_GATE_STRICT')}"
        )

    def test_yaml_pre_push_enforced(self):
        """pre-push-review must be enforced: true in governance-checkpoints.yaml."""
        config_path = os.path.join(
            REPO_ROOT, "scripts", "workflow", "governance-checkpoints.yaml"
        )
        with open(config_path) as f:
            data = yaml.safe_load(f)
        pre_push = next(
            (c for c in data["checkpoints"] if c["id"] == "pre-push-review"),
            None,
        )
        assert pre_push is not None, "pre-push-review checkpoint not found"
        assert pre_push["enforced"] is True, (
            f"Expected enforced=true, got {pre_push['enforced']}"
        )

    def test_yaml_tool_call_ceiling_is_per_session_budget(self):
        """tool-call-ceiling threshold must be a sane per-session budget (>= 500)."""
        config_path = os.path.join(
            REPO_ROOT, "scripts", "workflow", "governance-checkpoints.yaml"
        )
        with open(config_path) as f:
            data = yaml.safe_load(f)
        ceiling = next(
            (c for c in data["checkpoints"] if c["id"] == "tool-call-ceiling"),
            None,
        )
        assert ceiling is not None, "tool-call-ceiling checkpoint not found"
        assert ceiling["threshold"] >= 500, (
            f"Per-session threshold must be >= 500, got {ceiling['threshold']}. "
            "The ceiling tracks calls per Claude process (PPID), not per day — "
            "a 200-call daily ceiling blocks multi-session days."
        )

    def test_script_defaults_to_strict(self):
        """require-review-on-push.sh must default to strict mode."""
        script_path = os.path.join(
            REPO_ROOT, "scripts", "enforcement", "require-review-on-push.sh"
        )
        with open(script_path) as f:
            content = f.read()
        # The script should use ${REVIEW_GATE_STRICT:-1} (default 1 = strict)
        assert "REVIEW_GATE_STRICT:-1" in content, (
            "Script must default REVIEW_GATE_STRICT to 1 (strict mode)"
        )


# ── Old ceiling hook removal tests (#1839) ───────────────────────


class TestOldCeilingRemoved:
    """Tests verifying the old 500-call tool-call-ceiling.sh is removed from hooks.

    The old PostToolUse hook (500 ceiling) is superseded by the PreToolUse
    session-governor-check.sh (200 ceiling). Only one ceiling mechanism
    should be active.
    """

    def test_ceiling_hook_not_in_post_tool_use(self):
        """tool-call-ceiling.sh must NOT be in PostToolUse hooks."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        post_tool_hooks = settings.get("hooks", {}).get("PostToolUse", [])
        found = any(
            "tool-call-ceiling.sh" in h.get("command", "")
            for entry in post_tool_hooks
            for h in entry.get("hooks", [])
        )
        assert not found, "tool-call-ceiling.sh should be removed from PostToolUse"

    def test_governor_hook_still_in_pre_tool_use(self):
        """session-governor-check.sh must still be in PreToolUse (the replacement)."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        pre_tool_hooks = settings.get("hooks", {}).get("PreToolUse", [])
        found = any(
            "session-governor-check.sh" in h.get("command", "")
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        assert found, "session-governor-check.sh must remain in PreToolUse"


# ── Error loop breaker tests (#2056) ───────────────────────────────


class TestErrorLoopBreaker:
    """Tests for the error-loop-tracker.sh PostToolUse hook (#2056).

    Verifies:
    - Hook script exists and is executable
    - Hook is registered in settings.json PostToolUse
    - Hook matcher covers all tool types
    - State files are created in session-governor directory
    - Governor correctly evaluates consecutive error counts
    - PreToolUse hook reads error count from state file
    - Error loop at threshold triggers STOP verdict
    """

    def test_hook_exists_and_executable(self):
        """error-loop-tracker.sh must exist and be executable."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "error-loop-tracker.sh")
        assert os.path.isfile(hook_path), f"Hook not found: {hook_path}"
        assert os.access(hook_path, os.X_OK), f"Hook not executable: {hook_path}"

    def test_hook_registered_in_post_tool_use(self):
        """error-loop-tracker.sh must be in PostToolUse hooks."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        post_tool_hooks = settings.get("hooks", {}).get("PostToolUse", [])
        found = any(
            "error-loop-tracker.sh" in h.get("command", "")
            for entry in post_tool_hooks
            for h in entry.get("hooks", [])
        )
        assert found, "error-loop-tracker.sh not found in PostToolUse hooks"

    def test_hook_matches_all_tools(self):
        """Hook matcher must cover all major tool types."""
        import json
        settings_path = os.path.join(REPO_ROOT, ".claude", "settings.json")
        with open(settings_path) as f:
            settings = json.load(f)
        post_tool_hooks = settings.get("hooks", {}).get("PostToolUse", [])
        for entry in post_tool_hooks:
            for h in entry.get("hooks", []):
                if "error-loop-tracker.sh" in h.get("command", ""):
                    matcher = entry.get("matcher", "")
                    assert "Bash" in matcher, "Matcher must include Bash"
                    assert "Write" in matcher, "Matcher must include Write"
                    assert "Edit" in matcher, "Matcher must include Edit"
                    assert "Read" in matcher, "Matcher must include Read"
                    return
        pytest.fail("error-loop-tracker.sh entry not found")

    def test_state_directory_exists(self):
        """The session-governor state directory must exist."""
        state_dir = os.path.join(REPO_ROOT, ".claude", "state", "session-governor")
        assert os.path.isdir(state_dir), f"Missing: {state_dir}"

    def test_governor_error_loop_stop_at_3(self, runtime_config: CheckpointConfig):
        """Governor returns STOP when consecutive errors reach 3 (threshold)."""
        results = check_session_limits(
            runtime_config, tool_call_count=50, consecutive_error_count=3
        )
        el = next(r for r in results if r.checkpoint_id == "error-loop-breaker")
        assert el.verdict == SessionVerdict.STOP

    def test_governor_error_loop_continue_at_1(self, runtime_config: CheckpointConfig):
        """Governor returns CONTINUE when consecutive errors are 1 (below 80% of 3)."""
        results = check_session_limits(
            runtime_config, tool_call_count=50, consecutive_error_count=1
        )
        el = next(r for r in results if r.checkpoint_id == "error-loop-breaker")
        assert el.verdict == SessionVerdict.CONTINUE

    def test_governor_error_loop_wins_over_tool_calls(self, runtime_config: CheckpointConfig):
        """Error loop STOP takes priority even if tool calls are low."""
        results = check_session_limits(
            runtime_config, tool_call_count=10, consecutive_error_count=3
        )
        verdict = session_limits_verdict(results)
        assert verdict == SessionVerdict.STOP

    def test_pretooluse_hook_reads_error_count(self):
        """session-governor-check.sh must read consecutive-error-count, not hardcode 0."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "session-governor-check.sh")
        with open(hook_path) as f:
            content = f.read()
        # Must read from the state file, not pass hardcoded 0
        assert "consecutive-error-count" in content, (
            "Hook must read from consecutive-error-count state file"
        )
        assert '--consecutive-errors "$CONSEC_ERRORS"' in content, (
            "Hook must pass $CONSEC_ERRORS to governor, not hardcoded 0"
        )

    def test_pretooluse_hook_no_hardcoded_zero(self):
        """session-governor-check.sh must NOT hardcode --consecutive-errors 0."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "session-governor-check.sh")
        with open(hook_path) as f:
            content = f.read()
        assert "--consecutive-errors 0" not in content, (
            "Hook must not hardcode --consecutive-errors 0 (should use state file)"
        )

    def test_error_tracker_resets_on_success(self):
        """error-loop-tracker.sh must reset counter on successful tool call."""
        hook_path = os.path.join(REPO_ROOT, ".claude", "hooks", "error-loop-tracker.sh")
        with open(hook_path) as f:
            content = f.read()
        # Hook must write 0 to error count on non-error
        assert '"0" > "$ERROR_COUNT_FILE"' in content or "'0' > " in content, (
            "Hook must reset error count to 0 on successful tool call"
        )
