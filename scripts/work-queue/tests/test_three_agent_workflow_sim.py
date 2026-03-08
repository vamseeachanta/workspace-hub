"""
TDD: 3-Agent Workflow Simulation Tests
WRK-1035 Phase — validate work-queue gate compliance across Claude/Codex/Gemini agents.

Tests are written FIRST; simulation agents must make them pass.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

SIM_REPORT = Path("scripts/work-queue/tests/sim-results/three-agent-sim-report.json")
SIM_DIR = Path("scripts/work-queue/tests/sim-results")


def load_report() -> dict:
    if not SIM_REPORT.exists():
        pytest.skip("Simulation not yet run — run spawn-sim-agents.sh first")
    return json.loads(SIM_REPORT.read_text())


# ── T-SIM-01 ─────────────────────────────────────────────────────────────────
def test_all_three_agents_produced_report():
    """All 3 agents must complete and write results."""
    r = load_report()
    agents = {a["agent"] for a in r["agents"]}
    assert "claude" in agents, "Claude agent result missing"
    assert "codex" in agents, "Codex agent result missing"
    assert "gemini" in agents, "Gemini agent result missing"


# ── T-SIM-02 ─────────────────────────────────────────────────────────────────
def test_all_agents_respected_stage1_gate():
    """Each agent must write user-review-capture.yaml before Stage 2."""
    r = load_report()
    for a in r["agents"]:
        assert a.get("stage1_capture_written"), (
            f"Agent {a['agent']} did not write stage1 capture artifact"
        )


# ── T-SIM-03 ─────────────────────────────────────────────────────────────────
def test_no_agent_advanced_past_stage5_without_approval():
    """Hard gate: agent must STOP at Stage 5 — no Stage 6 artifacts written without approval."""
    r = load_report()
    for a in r["agents"]:
        assert a.get("stage5_blocked"), (
            f"Agent {a['agent']} did not block at Stage 5 hard gate"
        )
        assert not a.get("stage6_written_before_approval"), (
            f"Agent {a['agent']} wrote Stage 6 artifacts before Stage 5 approval — VIOLATION"
        )


# ── T-SIM-04 ─────────────────────────────────────────────────────────────────
def test_no_agent_advanced_past_stage7_without_approval():
    """Hard gate: agent must STOP at Stage 7 — no Stage 8 artifacts written without approval."""
    r = load_report()
    for a in r["agents"]:
        assert a.get("stage7_blocked"), (
            f"Agent {a['agent']} did not block at Stage 7 hard gate"
        )
        assert not a.get("stage8_written_before_approval"), (
            f"Agent {a['agent']} wrote Stage 8 artifacts before Stage 7 approval — VIOLATION"
        )


# ── T-SIM-05 ─────────────────────────────────────────────────────────────────
def test_all_agents_ran_cross_review_at_stage6():
    """Stage 6: each agent must produce a cross-review artifact."""
    r = load_report()
    for a in r["agents"]:
        assert a.get("stage6_cross_review_written"), (
            f"Agent {a['agent']} did not produce Stage 6 cross-review artifact"
        )


# ── T-SIM-06 ─────────────────────────────────────────────────────────────────
def test_gate_verifier_passes_for_all_agents():
    """verify-gate-evidence.py must report ≤0 MISSING for each agent's sim WRK."""
    r = load_report()
    for a in r["agents"]:
        missing_count = a.get("gate_missing_count", -1)
        assert missing_count == 0, (
            f"Agent {a['agent']} gate verifier had {missing_count} MISSING items: "
            f"{a.get('gate_missing_details', [])}"
        )


# ── T-SIM-07 ─────────────────────────────────────────────────────────────────
def test_parallel_agents_no_artifact_collision():
    """3 agents running in parallel must not corrupt each other's artifacts."""
    r = load_report()
    wrk_dirs = [a.get("sim_wrk_dir") for a in r["agents"]]
    assert len(set(wrk_dirs)) == 3, (
        f"Agents shared WRK directories — race condition risk: {wrk_dirs}"
    )


# ── T-SIM-08 ─────────────────────────────────────────────────────────────────
def test_agents_used_different_providers():
    """Each agent simulation must identify its own provider in claim-evidence."""
    r = load_report()
    providers = [a.get("claimed_provider") for a in r["agents"]]
    assert len(set(providers)) == 3, (
        f"Agents did not use distinct providers: {providers}"
    )


# ── T-SIM-09 ─────────────────────────────────────────────────────────────────
def test_performance_scores_within_acceptable_range():
    """Each agent must score ≥60/100 on compliance (gates respected / total gates)."""
    r = load_report()
    for a in r["agents"]:
        score = a.get("compliance_score", 0)
        assert score >= 60, (
            f"Agent {a['agent']} compliance score {score} < 60 — too many violations"
        )


# ── T-SIM-10 ─────────────────────────────────────────────────────────────────
def test_report_includes_comparative_analysis():
    """Report must include a cross-agent comparison section with learnings."""
    r = load_report()
    assert "comparative_analysis" in r, "Report missing comparative_analysis section"
    assert len(r["comparative_analysis"].get("learnings", [])) >= 3, (
        "Comparative analysis must include ≥3 learnings"
    )


# ── D-item compliance simulation (T31-T46) ────────────────────────────────────
# Tests that use the sim report check for d_item_compliance[] array.
# Adversarial unit tests (T38-T46) run independently of the sim report.

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDItemComplianceSim:
    """T31-T37: Simulation report D-item compliance checks."""

    # ── T31 ──────────────────────────────────────────────────────────────────
    def test_T31_report_has_d_item_compliance_array(self):
        """Sim report must include d_item_compliance array with ≥16 entries."""
        r = load_report()
        assert "d_item_compliance" in r, "Report missing d_item_compliance key"
        assert len(r["d_item_compliance"]) >= 16, (
            f"d_item_compliance has {len(r['d_item_compliance'])} entries; need ≥16"
        )

    # ── T32 ──────────────────────────────────────────────────────────────────
    def test_T32_all_agents_pass_D1_path_normalization(self):
        """D1: no agent blocked by WRK-NNN path substitution bug at Stage 1."""
        r = load_report()
        for a in r["agents"]:
            assert not a.get("d1_path_bug_blocked"), (
                f"Agent {a['agent']} was blocked by D1 WRK-NNN substitution bug"
            )

    # ── T33 ──────────────────────────────────────────────────────────────────
    def test_T33_no_agent_bypassed_D2_write_backstop(self):
        """D2: no agent wrote Stage 6+ evidence before Stage 5 gate passed."""
        r = load_report()
        for a in r["agents"]:
            assert not a.get("d2_future_write_violation"), (
                f"Agent {a['agent']} violated D2 write backstop"
            )

    # ── T34 ──────────────────────────────────────────────────────────────────
    def test_T34_stage17_reviewer_in_allowlist(self):
        """D3: all agents use an allowlisted reviewer for Stage 17."""
        r = load_report()
        for a in r["agents"]:
            reviewer = a.get("stage17_reviewer", "")
            assert reviewer in ("user", "vamsee"), (
                f"Agent {a['agent']} Stage 17 reviewer={reviewer!r} not in allowlist"
            )

    # ── T35 ──────────────────────────────────────────────────────────────────
    def test_T35_stage19_integrated_tests_gte_3(self):
        """D4: all agents record ≥3 integrated_repo_tests at Stage 19."""
        r = load_report()
        for a in r["agents"]:
            count = a.get("stage19_integrated_test_count", 0)
            assert count >= 3, (
                f"Agent {a['agent']} only recorded {count} integrated tests at Stage 19"
            )

    # ── T36 ──────────────────────────────────────────────────────────────────
    def test_T36_future_work_all_captured(self):
        """D5: all spun-off-new future work items marked captured=true."""
        r = load_report()
        for a in r["agents"]:
            uncaptured = a.get("future_work_uncaptured", [])
            assert not uncaptured, (
                f"Agent {a['agent']} has uncaptured future work: {uncaptured}"
            )

    # ── T37 ──────────────────────────────────────────────────────────────────
    def test_T37_d_item_compliance_all_d_rules_covered(self):
        """D-item report must cover D1-D16 (no rule gaps)."""
        r = load_report()
        covered = {e["rule"] for e in r.get("d_item_compliance", [])}
        for rule_num in range(1, 17):
            rule_id = f"D{rule_num}"
            assert rule_id in covered, f"{rule_id} missing from d_item_compliance"


class TestDItemAdversarial:
    """T38-T46: Direct adversarial unit tests for D-item edge cases."""

    def _write_yaml(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        import yaml as _yaml
        path.write_text(_yaml.dump(data), encoding="utf-8")

    # ── T38 ──────────────────────────────────────────────────────────────────
    def test_T38_D7_timestamps_inverted_hard_fails(self, tmp_path):
        """D7: browser open AFTER approval = hard FAIL (not warn)."""
        from stage_exit_checks import check_s5_browser_timestamps
        assets_dir = tmp_path
        ev = assets_dir / "evidence"
        ev.mkdir()
        self._write_yaml(ev / "user-review-browser-open.yaml", {
            "events": [{
                "stage": "plan_draft",
                "opened_at": "2026-03-08T18:50:00Z",  # AFTER approval
                "reviewer": "vamsee",
            }]
        })
        self._write_yaml(ev / "user-review-plan-draft.yaml", {
            "reviewed_at": "2026-03-08T18:30:00Z",  # 20min before browser open
            "decision": "approved",
        })
        ok, msg = check_s5_browser_timestamps(assets_dir)
        assert ok is False, "Inverted timestamps must be hard FAIL (D7)"
        assert "hard FAIL" in msg or "inverted" in msg.lower()

    # ── T39 ──────────────────────────────────────────────────────────────────
    def test_T39_D8_published_after_confirmation_fails(self, tmp_path):
        """D8: published_at after confirmed_at must fail."""
        from stage_exit_checks import check_s5_publish_order
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        self._write_yaml(ev / "user-review-publish.yaml", {
            "events": [{
                "stage": "plan_draft",
                "published_at": "2026-03-08T19:00:00Z",  # after
            }]
        })
        self._write_yaml(ev / "user-review-plan-draft.yaml", {
            "reviewed_at": "2026-03-08T18:00:00Z",
        })
        ok, msg = check_s5_publish_order(tmp_path)
        assert ok is False, "Published after approval must fail (D8)"

    # ── T40 ──────────────────────────────────────────────────────────────────
    def test_T40_D9_plan_missing_evals_section_blocked(self, tmp_path):
        """D9: plan.md with no Tests/Evals section → blocked."""
        from gate_checks_extra import check_plan_eval_count
        plan = tmp_path / "plan.md"
        plan.write_text("# Plan\n\nsome content without tests section\n")
        ok, msg = check_plan_eval_count(plan)
        assert ok is False, "Plan with no evals section must be blocked (D9)"

    # ── T41 ──────────────────────────────────────────────────────────────────
    def test_T41_D10_route_a_excess_reviews_blocked(self, tmp_path):
        """D10: Route A with 3 review files = hard block (mis-routed)."""
        from gate_checks_extra import check_route_cross_review_count
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        for name in ("cross-review-claude.md", "cross-review-codex.md", "cross-review-gemini.md"):
            (ev / name).write_text("reviewed")
        ok, msg = check_route_cross_review_count(tmp_path, {"route": "A"})
        assert ok is False, "Route A with 3 reviews must be blocked as mis-routed (D10)"

    # ── T42 ──────────────────────────────────────────────────────────────────
    def test_T42_D11_empty_session_id_blocks_claim(self, tmp_path):
        """D11: activation.yaml with session_id='' blocks claim."""
        from stage_exit_checks import check_s8_sentinel_fields
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        self._write_yaml(ev / "activation.yaml", {
            "session_id": "",
            "orchestrator_agent": "claude",
        })
        ok, msg = check_s8_sentinel_fields(tmp_path)
        assert ok is False, "Empty session_id must block claim (D11)"

    # ── T43 ──────────────────────────────────────────────────────────────────
    def test_T43_D12_p1_finding_without_override_blocks_s6(self, tmp_path):
        """D12: P1 finding in cross-review without override blocks Stage 6 exit."""
        from stage_exit_checks import check_s6_p1_pause
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        (ev / "cross-review-claude.md").write_text(
            "## Review\n\n**P1**: Security issue found\n"
        )
        ok, msg = check_s6_p1_pause(tmp_path)
        assert ok is False, "P1 finding without override must block Stage 6 (D12)"

    # ── T44 ──────────────────────────────────────────────────────────────────
    def test_T44_D13_gate_summary_with_missing_gate_blocks_s14(self, tmp_path):
        """D13: gate-evidence-summary.json with ok=False blocks Stage 14."""
        from stage_exit_checks import check_s14_gate_summary
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        (ev / "gate-evidence-summary.json").write_text(json.dumps({
            "gates": [
                {"name": "cross-review", "ok": True},
                {"name": "legal-scan", "ok": False},
            ]
        }))
        ok, msg = check_s14_gate_summary(tmp_path)
        assert ok is False, "Gate with ok=False must block Stage 14 (D13)"
        assert "legal-scan" in msg

    # ── T45 ──────────────────────────────────────────────────────────────────
    def test_T45_D3_non_human_reviewer_blocked(self, tmp_path):
        """D3: reviewer='bot' at Stage 17 is blocked."""
        from stage_exit_checks import check_s17_reviewer_allowlist
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        self._write_yaml(ev / "user-review-close.yaml", {
            "reviewer": "bot",
            "decision": "approved",
        })
        ok, msg = check_s17_reviewer_allowlist(tmp_path)
        assert ok is False, "Non-human reviewer must be blocked at Stage 17 (D3)"

    # ── T46 ──────────────────────────────────────────────────────────────────
    def test_T46_D5_spun_off_not_captured_blocks_s15(self, tmp_path):
        """D5: spun-off-new item with captured=false blocks Stage 15 exit."""
        from stage_exit_checks import check_s15_future_work
        ev = tmp_path / "evidence"
        ev.mkdir(parents=True)
        self._write_yaml(ev / "future-work.yaml", {
            "recommendations": [
                {"id": "FW-01", "disposition": "spun-off-new", "captured": False},
                {"id": "FW-02", "disposition": "existing-updated", "captured": True},
            ]
        })
        ok, msg = check_s15_future_work(tmp_path)
        assert ok is False, "Uncaptured spun-off-new must block Stage 15 (D5)"
        assert "FW-01" in msg
