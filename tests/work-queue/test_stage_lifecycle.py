"""
Tests for WRK-1028: Stage lifecycle enforcement
  - gate_check.py  (P1)  — PreToolUse gates 5→6, 7→8, 17→18
  - start_stage.py (P2)  — stage entry routing
  - exit_stage.py  (P2)  — stage exit validation
All tests import from scripts/work-queue/ via sys.path injection.
Run: uv run --no-project python -m pytest tests/work-queue/test_stage_lifecycle.py -v
"""

import sys
import os
import pytest
import textwrap

# ── path setup ──────────────────────────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "scripts", "work-queue"))

from gate_check import check_gate   # noqa: E402  (imported after path setup)
from start_stage import build_prompt, route_stage  # noqa: E402
from exit_stage import validate_exit, check_human_gate  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────────

def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ════════════════════════════════════════════════════════════════════════════
# GATE-CHECK TESTS  (P1)
# ════════════════════════════════════════════════════════════════════════════

class TestGate5:
    """Gate 5→6: block evidence writes until user-review-plan-draft.yaml approved."""

    def test_gate5_blocked_when_no_approval_file(self, tmp_path):
        """No user-review-plan-draft.yaml → write to cross-review.yaml blocked."""
        assets = tmp_path / "assets" / "WRK-0001"
        assets.mkdir(parents=True)
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "evidence" / "cross-review.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is True
        assert "Gate 5" in result["reason"]

    def test_gate5_blocked_when_decision_not_approved(self, tmp_path):
        """user-review-plan-draft.yaml exists but decision != approved → blocked."""
        assets = tmp_path / "assets" / "WRK-0001" / "evidence"
        assets.mkdir(parents=True)
        _write(str(assets / "user-review-plan-draft.yaml"), "decision: revise\n")
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "cross-review.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is True

    def test_gate5_allowed_when_approved(self, tmp_path):
        """decision: approved present → write to cross-review.yaml allowed."""
        assets = tmp_path / "assets" / "WRK-0001" / "evidence"
        assets.mkdir(parents=True)
        _write(str(assets / "user-review-plan-draft.yaml"), "decision: approved\n")
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "cross-review.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is False


class TestGate7:
    """Gate 7→8: block activation writes until plan-final-review.yaml passed."""

    def test_gate7_blocked_when_no_final_review(self, tmp_path):
        """No plan-final-review.yaml → write to activation.yaml blocked."""
        assets = tmp_path / "assets" / "WRK-0001"
        assets.mkdir(parents=True)
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "evidence" / "activation.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is True
        assert "Gate 7" in result["reason"]

    def test_gate7_blocked_when_fields_missing(self, tmp_path):
        """plan-final-review.yaml exists but missing confirmed_by or decision → blocked."""
        assets = tmp_path / "assets" / "WRK-0001" / "evidence"
        assets.mkdir(parents=True)
        _write(str(assets / "plan-final-review.yaml"), "decision: passed\n")  # no confirmed_by
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "activation.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is True

    def test_gate7_allowed_when_all_fields_present(self, tmp_path):
        """All required fields present → write to activation.yaml allowed."""
        assets = tmp_path / "assets" / "WRK-0001" / "evidence"
        assets.mkdir(parents=True)
        _write(
            str(assets / "plan-final-review.yaml"),
            "confirmed_by: user\nconfirmed_at: 2026-03-07T20:00:00Z\ndecision: passed\n",
        )
        result = check_gate(
            tool_name="Write",
            file_path=str(assets / "activation.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is False


class TestGate17:
    """Gate 17→18: block done/WRK-NNN.md write until user-review-close.yaml approved."""

    def test_gate17_blocked_when_no_close_review(self, tmp_path):
        """No user-review-close.yaml → write to .claude/work-queue/done/WRK-0001.md blocked."""
        done_dir = tmp_path / ".claude" / "work-queue" / "done"
        done_dir.mkdir(parents=True)
        result = check_gate(
            tool_name="Write",
            file_path=str(done_dir / "WRK-0001.md"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
            queue_root=str(tmp_path),
        )
        assert result["blocked"] is True
        assert "Gate 17" in result["reason"]

    def test_gate17_allowed_when_approved(self, tmp_path):
        """decision: approved → write to done/WRK-0001.md allowed."""
        assets = tmp_path / "assets" / "WRK-0001" / "evidence"
        assets.mkdir(parents=True)
        done_dir = tmp_path / ".claude" / "work-queue" / "done"
        done_dir.mkdir(parents=True)
        _write(str(assets / "user-review-close.yaml"), "decision: approved\n")
        result = check_gate(
            tool_name="Write",
            file_path=str(done_dir / "WRK-0001.md"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
            queue_root=str(tmp_path),
        )
        assert result["blocked"] is False


class TestGateFalsePositive:
    """Non-WRK writes must never be blocked."""

    def test_non_wrk_write_not_blocked(self, tmp_path):
        """Write to a README.md → gate returns blocked=False (no false positive)."""
        result = check_gate(
            tool_name="Write",
            file_path="/some/repo/README.md",
            wrk_id=None,
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is False

    def test_non_write_tool_not_blocked(self, tmp_path):
        """Read tool calls are never blocked by gate-check."""
        assets = tmp_path / "assets" / "WRK-0001"
        assets.mkdir(parents=True)
        result = check_gate(
            tool_name="Read",
            file_path=str(assets / "evidence" / "cross-review.yaml"),
            wrk_id="WRK-0001",
            assets_root=str(tmp_path / "assets"),
        )
        assert result["blocked"] is False


# ════════════════════════════════════════════════════════════════════════════
# START-STAGE TESTS  (P2)
# ════════════════════════════════════════════════════════════════════════════

class TestStartStage:
    """start_stage.py routing and prompt-package generation."""

    def _make_contract(self, tmp_path, invocation, stages=None):
        contract = {
            "order": 10,
            "name": "Work Execution",
            "weight": "heavy",
            "invocation": invocation,
            "human_gate": False,
            "skills_required": ["workspace-hub/work-queue-workflow"],
            "entry_reads": [],
            "exit_artifacts": ["evidence/execute.yaml"],
            "blocking_condition": "",
            "log_action": "work_executed",
            "context_budget_kb": 16,
        }
        if stages:
            contract["chained_stages"] = stages
        return contract

    def test_task_agent_writes_prompt_package(self, tmp_path):
        """task_agent invocation → stage-N-prompt.md written with contract content."""
        contract = self._make_contract(tmp_path, "task_agent")
        out = build_prompt(contract, wrk_id="WRK-0001", stage=10, output_dir=str(tmp_path))
        prompt_file = tmp_path / "stage-10-prompt.md"
        assert prompt_file.exists(), "stage-10-prompt.md not written"
        content = prompt_file.read_text()
        assert "Work Execution" in content
        assert "evidence/execute.yaml" in content

    def test_human_session_emits_checklist(self, tmp_path, capsys):
        """human_session → checklist printed to stdout; no prompt package written."""
        contract = self._make_contract(tmp_path, "human_session")
        contract["invocation"] = "human_session"
        route_stage(contract, wrk_id="WRK-0001", stage=10, output_dir=str(tmp_path))
        captured = capsys.readouterr()
        assert "Checklist" in captured.out or "checklist" in captured.out.lower()
        assert not (tmp_path / "stage-10-prompt.md").exists()

    def test_chained_agent_combines_all_stage_contracts(self, tmp_path):
        """chained_agent → prompt package contains all chained stage contracts in sequence."""
        contract = self._make_contract(tmp_path, "chained_agent", stages=[2, 3, 4])
        contract["order"] = 2
        contract["name"] = "Resource Intelligence"
        out = build_prompt(contract, wrk_id="WRK-0001", stage=2, output_dir=str(tmp_path))
        prompt_file = tmp_path / "stage-2-prompt.md"
        assert prompt_file.exists()
        content = prompt_file.read_text()
        assert "chained" in content.lower() or "stages" in content.lower()


# ════════════════════════════════════════════════════════════════════════════
# EXIT-STAGE TESTS  (P2)
# ════════════════════════════════════════════════════════════════════════════

class TestExitStage:
    """exit_stage.py artifact validation and human gate checks."""

    def test_missing_artifact_raises(self, tmp_path):
        """Missing exit artifact → SystemExit(1); no log written."""
        with pytest.raises(SystemExit) as exc:
            validate_exit(
                exit_artifacts=["evidence/execute.yaml"],
                stage_dir=str(tmp_path),
                human_gate=False,
            )
        assert exc.value.code == 1

    def test_happy_advance_exits_zero(self, tmp_path):
        """All artifacts present, no gate → exit 0."""
        ev = tmp_path / "evidence"
        ev.mkdir()
        (ev / "execute.yaml").write_text("status: done\n")
        result = validate_exit(
            exit_artifacts=["evidence/execute.yaml"],
            stage_dir=str(tmp_path),
            human_gate=False,
        )
        assert result is True

    def test_human_gate_missing_decision_raises(self, tmp_path):
        """human_gate=True but decision field missing → SystemExit(1)."""
        ev = tmp_path / "evidence"
        ev.mkdir()
        (ev / "user-review-plan-draft.yaml").write_text("notes: pending\n")
        with pytest.raises(SystemExit) as exc:
            validate_exit(
                exit_artifacts=["evidence/user-review-plan-draft.yaml"],
                stage_dir=str(tmp_path),
                human_gate=True,
                gate_field="decision",
                gate_value="approved",
                gate_file="evidence/user-review-plan-draft.yaml",
            )
        assert exc.value.code == 1

    def test_human_gate_approved_exits_zero(self, tmp_path):
        """human_gate=True and decision: approved → exit 0."""
        ev = tmp_path / "evidence"
        ev.mkdir()
        (ev / "user-review-plan-draft.yaml").write_text("decision: approved\nnotes: ok\n")
        result = validate_exit(
            exit_artifacts=["evidence/user-review-plan-draft.yaml"],
            stage_dir=str(tmp_path),
            human_gate=True,
            gate_field="decision",
            gate_value="approved",
            gate_file="evidence/user-review-plan-draft.yaml",
        )
        assert result is True
