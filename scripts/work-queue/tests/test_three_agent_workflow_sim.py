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
