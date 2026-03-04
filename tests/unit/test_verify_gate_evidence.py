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
    disposition: existing-updated
    status: pending
    captured: true
    required_for_signoff: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_future_work_gate(tmp_path)
    assert ok is False
    assert "required_for_signoff recommendations missing wrk_id" in detail


def test_future_work_gate_fails_when_captured_false(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "future-work.yaml").write_text(
        """
recommendations:
  - wrk_id: WRK-123
    title: follow up item
    disposition: existing-updated
    status: pending
    captured: false
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_future_work_gate(tmp_path)
    assert ok is False
    assert "captured must be true" in detail


def test_future_work_gate_passes_with_disposition_and_captured_true(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "future-work.yaml").write_text(
        """
recommendations:
  - wrk_id: WRK-123
    title: follow up item
    disposition: spun-off-new
    status: pending
    captured: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_future_work_gate(tmp_path)
    assert ok is True
    assert "recommendations=1" in detail


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


def test_integrated_test_gate_fails_when_count_below_three(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "execute.yaml").write_text(
        """
integrated_repo_tests:
  - name: integration-smoke
    scope: integrated
    command: uv run --no-project pytest tests/unit/test_a.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-a.txt
  - name: repo-smoke
    scope: repo
    command: uv run --no-project pytest tests/unit/test_b.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-b.txt
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_execute_integrated_tests_gate(tmp_path)
    assert ok is False
    assert "count must be 3-5" in detail


def test_integrated_test_gate_passes_for_three_passing_tests(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "execute.yaml").write_text(
        """
integrated_repo_tests:
  - name: integration-smoke
    scope: integrated
    command: uv run --no-project pytest tests/unit/test_a.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-a.txt
  - name: repo-regression
    scope: repo
    command: uv run --no-project pytest tests/unit/test_b.py
    result: passed
    artifact_ref: .claude/work-queue/assets/WRK-999/test-b.txt
  - name: repo-contract
    scope: repo
    command: uv run --no-project pytest tests/unit/test_c.py
    result: pass
    artifact_ref: .claude/work-queue/assets/WRK-999/test-c.txt
""".strip()
        + "\n",
        encoding="utf-8",
    )

    ok, detail = mod.check_execute_integrated_tests_gate(tmp_path)
    assert ok is True
    assert "integrated_repo_tests=3" in detail


def test_resource_intelligence_update_gate_requires_additions_or_rationale(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "resource-intelligence-update.yaml").write_text(
        "additions: []\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_resource_intelligence_update_gate(tmp_path)
    assert ok is False
    assert "no_additions_rationale" in detail


def test_user_review_close_gate_requires_approved_decision(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "user-review-close.yaml").write_text(
        """
reviewer: user
reviewed_at: 2026-03-03T15:00:00Z
decision: revise
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_user_review_close_gate(tmp_path)
    assert ok is False
    assert "approved|accepted|passed" in detail


def test_html_open_default_browser_gate_requires_all_stages(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "user-review-browser-open.yaml").write_text(
        """
events:
  - stage: plan_draft
    opened_in_default_browser: true
    html_ref: .claude/work-queue/assets/WRK-999/review.html
    opened_at: 2026-03-03T10:00:00Z
    reviewer: user
  - stage: plan_final
    opened_in_default_browser: true
    html_ref: .claude/work-queue/assets/WRK-999/review.html
    opened_at: 2026-03-03T11:00:00Z
    reviewer: user
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_html_open_default_browser_gate(
        tmp_path, required=["plan_draft", "plan_final", "close_review"]
    )
    assert ok is False
    assert "missing required stages" in detail


def test_stage_evidence_gate_fails_when_missing_ref(tmp_path: Path):
    mod = _load_verify_module()
    front = "id: WRK-999\nstatus: working\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999")
    assert ok is False
    assert "stage_evidence_ref missing" in detail


def test_stage_evidence_gate_passes_with_all_19_orders(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_file = tmp_path / "stage-evidence.yaml"
    rows = "\n".join(
        [
            f"  - order: {i}\n    stage: Stage {i}\n    status: done\n    evidence: ref-{i}"
            for i in range(1, 20)
        ]
    )
    evidence_file.write_text(
        "wrk_id: WRK-999\n"
        "generated_at: \"2026-03-03T00:00:00Z\"\n"
        "reviewed_by: agent\n"
        "stages:\n"
        f"{rows}\n",
        encoding="utf-8",
    )
    front = "id: WRK-999\nstage_evidence_ref: stage-evidence.yaml\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999")
    assert ok is True
    assert "stages=19" in detail


def test_stage_evidence_gate_fails_legacy_close_phase_if_stage17_pending(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_file = tmp_path / "stage-evidence.yaml"
    rows = []
    for i in range(1, 20):
        status = "done"
        if i == 17:
            status = "pending"
        if i in {18, 19}:
            status = "n/a" if i == 18 else "pending"
        rows.append(f"  - order: {i}\n    stage: Stage {i}\n    status: {status}\n    evidence: ref-{i}")
    evidence_file.write_text(
        "wrk_id: WRK-999\n"
        "generated_at: \"2026-03-03T00:00:00Z\"\n"
        "reviewed_by: agent\n"
        "stages:\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    front = "id: WRK-999\nstage_evidence_ref: stage-evidence.yaml\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999", phase="close")
    assert ok is False
    assert "stage order 17 must be done|n/a before close" in detail


def test_stage_evidence_gate_passes_legacy_close_phase_when_stage17_done(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_file = tmp_path / "stage-evidence.yaml"
    rows = []
    for i in range(1, 20):
        status = "done"
        if i == 18:
            status = "n/a"
        if i == 19:
            status = "pending"
        rows.append(f"  - order: {i}\n    stage: Stage {i}\n    status: {status}\n    evidence: ref-{i}")
    evidence_file.write_text(
        "wrk_id: WRK-999\n"
        "generated_at: \"2026-03-03T00:00:00Z\"\n"
        "reviewed_by: agent\n"
        "stages:\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    front = "id: WRK-999\nstage_evidence_ref: stage-evidence.yaml\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999", phase="close")
    assert ok is True
    assert "stages=19" in detail


def test_stage_evidence_gate_passes_with_all_20_orders(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_file = tmp_path / "stage-evidence.yaml"
    rows = "\n".join(
        [
            f"  - order: {i}\n    stage: Stage {i}\n    status: done\n    evidence: ref-{i}"
            for i in range(1, 21)
        ]
    )
    evidence_file.write_text(
        "wrk_id: WRK-999\n"
        "generated_at: \"2026-03-03T00:00:00Z\"\n"
        "reviewed_by: agent\n"
        "stages:\n"
        f"{rows}\n",
        encoding="utf-8",
    )
    front = "id: WRK-999\nstage_evidence_ref: stage-evidence.yaml\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999", phase="close")
    assert ok is True
    assert "stages=20" in detail


def test_stage_evidence_gate_fails_close_phase_if_preclose_stage_pending(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")

    evidence_file = tmp_path / "stage-evidence.yaml"
    rows = []
    for i in range(1, 21):
        status = "done"
        if i == 17:
            status = "pending"
        if i == 18:
            status = "n/a"
        if i in {19, 20}:
            status = "pending"
        rows.append(f"  - order: {i}\n    stage: Stage {i}\n    status: {status}\n    evidence: ref-{i}")
    evidence_file.write_text(
        "wrk_id: WRK-999\n"
        "generated_at: \"2026-03-03T00:00:00Z\"\n"
        "reviewed_by: agent\n"
        "stages:\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    front = "id: WRK-999\nstage_evidence_ref: stage-evidence.yaml\n"
    ok, detail = mod.check_stage_evidence_gate(front, tmp_path, "WRK-999", phase="close")
    assert ok is False
    assert "stage order 17 must be done|n/a before close" in detail


def test_activation_gate_requires_set_active_and_session_fields(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "activation.yaml").write_text(
        """
wrk_id: WRK-999
set_active_wrk: false
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_activation_gate(tmp_path, "WRK-999")
    assert ok is False
    assert "set_active_wrk must be true" in detail


def test_activation_gate_passes_with_required_fields(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "activation.yaml").write_text(
        """
wrk_id: WRK-999
set_active_wrk: true
session_id: session-20260303
orchestrator_agent: codex
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_activation_gate(tmp_path, "WRK-999")
    assert ok is True
    assert "activation evidence OK" in detail


def test_user_review_publish_gate_requires_all_review_stages(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "user-review-publish.yaml").write_text(
        """
events:
  - stage: plan_draft
    pushed_to_origin: true
    remote: origin
    branch: feature/WRK-999
    commit: abcdef1
    documents:
      - .claude/work-queue/assets/WRK-999/review.html
    published_at: 2026-03-04T00:00:00Z
    reviewer: user
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_user_review_publish_gate(
        tmp_path, required=["plan_draft", "plan_final", "close_review"]
    )
    assert ok is False
    assert "missing required stages" in detail


def test_user_review_publish_gate_passes_when_required_stages_are_pushed(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable in test environment")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "user-review-publish.yaml").write_text(
        """
events:
  - stage: plan_draft
    pushed_to_origin: true
    remote: origin
    branch: feature/WRK-999
    commit: abcdef1
    documents:
      - .claude/work-queue/assets/WRK-999/plan-html-review-draft.md
    published_at: 2026-03-04T00:00:00Z
    reviewer: user
  - stage: plan_final
    pushed_to_origin: true
    remote: origin
    branch: feature/WRK-999
    commit: abcdef2
    documents:
      - .claude/work-queue/assets/WRK-999/plan-html-review-final.md
    published_at: 2026-03-04T00:10:00Z
    reviewer: user
  - stage: close_review
    pushed_to_origin: true
    remote: origin
    branch: feature/WRK-999
    commit: abcdef3
    documents:
      - .claude/work-queue/assets/WRK-999/review.html
    published_at: 2026-03-04T00:20:00Z
    reviewer: user
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_user_review_publish_gate(
        tmp_path, required=["plan_draft", "plan_final", "close_review"]
    )
    assert ok is True
    assert "stages=" in detail
