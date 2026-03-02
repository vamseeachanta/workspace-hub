from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_verify_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "verify-gate-evidence.py"
    spec = importlib.util.spec_from_file_location("verify_gate_evidence", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resource_intelligence_gate_passes_with_machine_checkable_contract(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "resource-intelligence.yaml").write_text(
        """
wrk_id: WRK-999
stage: resource_intelligence
completion_status: continue_to_planning
top_p1_gaps: []
top_p2_gaps: []
top_p3_gaps: []
skills:
  core_used:
    - work-queue
    - engineering-context-loader
    - document-inventory
  optional_used: []
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_resource_intelligence_gate(tmp_path)
    assert ok is True
    assert "completion_status=continue_to_planning" in detail


def test_resource_intelligence_gate_fails_if_continue_has_p1_gaps(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "resource-intelligence.yaml").write_text(
        """
completion_status: continue_to_planning
top_p1_gaps:
  - missing source
skills:
  core_used:
    - work-queue
    - engineering-context-loader
    - document-inventory
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_resource_intelligence_gate(tmp_path)
    assert ok is False
    assert "requires empty top_p1_gaps" in detail


def test_claim_gate_canonical_requires_claim_expiry(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "claim.yaml").write_text(
        """
stage: claim
session_owner: codex
best_fit_provider: codex
quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_claim_gate(tmp_path)
    assert ok is False
    assert "claim_expires_at missing" in detail


def test_future_work_gate_fails_required_for_signoff_without_wrk_id(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "future-work.yaml").write_text(
        """
recommendations:
  - title: follow up item
    required_for_signoff: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_future_work_gate(tmp_path)
    assert ok is False
    assert "required_for_signoff recommendations missing wrk_id" in detail


def test_reclaim_gate_block_requires_reason(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "reclaim.yaml").write_text(
        """
reclaim_decision: block
prior_claim_ref: assets/WRK-999/evidence/claim.yaml
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_reclaim_gate(tmp_path)
    assert ok is False
    assert "block_reason required" in detail

