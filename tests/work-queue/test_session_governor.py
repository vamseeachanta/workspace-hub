"""
Tests for session-governor.py — hard-stop checkpoint verification.

Covers:
  - Checkpoint config loading and schema validation
  - Gate verification logic (present/missing gates)
  - Report generation structure
  - Edge cases: empty config, unknown gate types

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
    load_checkpoints,
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
