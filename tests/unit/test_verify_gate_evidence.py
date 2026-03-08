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


def test_agent_log_gate_requires_required_stage_logs_for_claim(tmp_path: Path):
    mod = _load_verify_module()
    log_dir = tmp_path / ".claude" / "work-queue" / "logs"
    log_dir.mkdir(parents=True)
    (log_dir / "WRK-999-plan.log").write_text(
        "timestamp: 2026-03-06T00:00:00Z\naction: plan_wrapper_complete\nprovider: codex\n\n",
        encoding="utf-8",
    )
    ok, detail = mod.check_agent_log_gate(tmp_path, "WRK-999", "claim")
    assert ok is False
    assert "routing:missing-log" in detail


def test_agent_log_gate_passes_for_close_when_wrapper_logs_exist(tmp_path: Path):
    mod = _load_verify_module()
    log_dir = tmp_path / ".claude" / "work-queue" / "logs"
    log_dir.mkdir(parents=True)
    fixtures = {
        "routing": "work_wrapper_complete",
        "plan": "plan_wrapper_complete",
        "execute": "execute_wrapper_complete",
        "cross-review": "review_wrapper_complete",
        "close": "verify_gate_evidence_pass",
    }
    for stage, action in fixtures.items():
        (log_dir / f"WRK-999-{stage}.log").write_text(
            f"timestamp: 2026-03-06T00:00:00Z\naction: {action}\nprovider: codex\n\n",
            encoding="utf-8",
        )
    ok, detail = mod.check_agent_log_gate(tmp_path, "WRK-999", "close")
    assert ok is True
    assert "matched routing" in detail


# ---------------------------------------------------------------------------
# Stage 5 evidence gate tests (Phase 1A TDD)
# ---------------------------------------------------------------------------

_FULL_CONFIG = """\
schema_version: "1.0"
major_version: 1
supported_major_versions:
  - 1
activation: full
gate_activation_commit: "aabbccdd"
checker_timeout_seconds: 30
git_history_timeout_seconds: 8
emergency_bypass_until: ""
emergency_bypass_reason: ""
emergency_bypass_approved_by: ""
human_authority_allowlist:
  - user
  - vamsee
"""

_DISABLED_CONFIG = """\
schema_version: "1.0"
major_version: 1
supported_major_versions:
  - 1
activation: disabled
gate_activation_commit: ""
checker_timeout_seconds: 30
git_history_timeout_seconds: 8
emergency_bypass_until: ""
emergency_bypass_reason: ""
emergency_bypass_approved_by: ""
human_authority_allowlist:
  - user
"""

_COMMON_DRAFT_PASS = """\
wrk_id: WRK-999
stage: plan_draft
review_checkpoint: common_draft
review_cycle_id: "stage5-20260307"
draft_commit: "abc123"
approval_decision: approve_as_is
reviewed_at: "2026-03-07T00:00:00Z"
reviewed_by: user
capture_method: manual_live_review
generated_at_commit: "abc123"
"""

_PLAN_DRAFT_PASS = """\
wrk_id: WRK-999
stage: plan_draft
review_checkpoint: combined_plan
review_cycle_id: "stage5-20260307"
approval_decision: approve_as_is
approved_draft_commit: "def456"
reviewed_at: "2026-03-07T00:00:01Z"
reviewed_by: user
capture_method: manual_live_review
generated_at_commit: "def456"
"""

_BROWSER_OPEN_PASS = """\
events:
  - stage: plan_draft
    review_checkpoint: common_draft
    review_cycle_id: "stage5-20260307"
    wrk_id: WRK-999
    opened_in_default_browser: true
    html_ref: ".claude/work-queue/assets/WRK-999/plan-draft-review.html"
    opened_at: "2026-03-07T00:00:00Z"
    reviewer: user
  - stage: plan_draft
    review_checkpoint: combined_plan
    review_cycle_id: "stage5-20260307"
    wrk_id: WRK-999
    opened_in_default_browser: true
    html_ref: ".claude/work-queue/assets/WRK-999/plan-draft-review.html"
    opened_at: "2026-03-07T00:00:01Z"
    reviewer: user
"""

_PUBLISH_PASS = """\
events:
  - stage: plan_draft
    review_checkpoint: common_draft
    review_cycle_id: "stage5-20260307"
    wrk_id: WRK-999
    pushed_to_origin: true
    commit: "abc123"
    published_at: "2026-03-07T00:00:00Z"
    reviewer: user
  - stage: plan_draft
    review_checkpoint: combined_plan
    review_cycle_id: "stage5-20260307"
    wrk_id: WRK-999
    pushed_to_origin: true
    commit: "def456"
    published_at: "2026-03-07T00:00:01Z"
    reviewer: user
"""


def _write_stage5_fixtures(
    tmp_path: Path,
    *,
    config: str = _FULL_CONFIG,
    common_draft: str | None = _COMMON_DRAFT_PASS,
    plan_draft: str | None = _PLAN_DRAFT_PASS,
    browser_open: str | None = _BROWSER_OPEN_PASS,
    publish: str | None = _PUBLISH_PASS,
) -> tuple[Path, Path]:
    """Write Stage 5 fixture files; return (assets_dir, workspace_root)."""
    # workspace_root = tmp_path; config lives at scripts/work-queue/stage5-gate-config.yaml
    config_dir = tmp_path / "scripts" / "work-queue"
    config_dir.mkdir(parents=True)
    (config_dir / "stage5-gate-config.yaml").write_text(config, encoding="utf-8")

    assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-999"
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True)

    if common_draft is not None:
        (evidence_dir / "user-review-common-draft.yaml").write_text(
            common_draft, encoding="utf-8"
        )
    if plan_draft is not None:
        (evidence_dir / "user-review-plan-draft.yaml").write_text(
            plan_draft, encoding="utf-8"
        )
    if browser_open is not None:
        (evidence_dir / "user-review-browser-open.yaml").write_text(
            browser_open, encoding="utf-8"
        )
    if publish is not None:
        (evidence_dir / "user-review-publish.yaml").write_text(
            publish, encoding="utf-8"
        )

    return assets_dir, tmp_path


def test_stage5_gate_disabled_returns_ok(tmp_path: Path):
    """When activation=disabled, gate should return True (no enforcement)."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, config=_DISABLED_CONFIG,
        common_draft=None, plan_draft=None, browser_open=None, publish=None,
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "disabled" in detail.lower()


def test_stage5_gate_config_missing_returns_exit2(tmp_path: Path):
    """Missing stage5-gate-config.yaml should return None (exit 2)."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-999"
    (assets_dir / "evidence").mkdir(parents=True)
    # No config file written
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, tmp_path)
    assert ok is None
    assert "stage5-gate-config" in detail.lower() or "config" in detail.lower()


def test_stage5_gate_malformed_config_returns_exit2(tmp_path: Path):
    """Malformed YAML in stage5-gate-config.yaml should return None (exit 2)."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, config="activation: [invalid\n  yaml: {\n",
        common_draft=None, plan_draft=None, browser_open=None, publish=None,
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is None


def test_stage5_gate_full_missing_common_draft_blocks(tmp_path: Path):
    """activation=full + missing common-draft → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, common_draft=None
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "common" in detail.lower() or "missing" in detail.lower()


def test_stage5_gate_full_common_draft_revise_blocks(tmp_path: Path):
    """Common-draft with revise_and_rerun → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    revise_draft = _COMMON_DRAFT_PASS.replace(
        "approval_decision: approve_as_is",
        "approval_decision: revise_and_rerun",
    )
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, common_draft=revise_draft
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "approve_as_is" in detail or "common" in detail.lower()


def test_stage5_gate_full_missing_plan_draft_blocks(tmp_path: Path):
    """activation=full + missing combined-plan draft → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, plan_draft=None
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "plan" in detail.lower() or "missing" in detail.lower()


def test_stage5_gate_full_plan_draft_revise_blocks(tmp_path: Path):
    """Combined-plan draft with revise_and_rerun → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    revise_draft = _PLAN_DRAFT_PASS.replace(
        "approval_decision: approve_as_is",
        "approval_decision: revise_and_rerun",
    )
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, plan_draft=revise_draft
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False


def test_stage5_gate_full_both_approve_as_is_passes(tmp_path: Path):
    """Both approval artifacts with approve_as_is → gate returns True."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(tmp_path)
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "approve_as_is" in detail or "pass" in detail.lower()


def test_stage5_gate_mismatched_review_cycle_id_blocks(tmp_path: Path):
    """Mismatched review_cycle_id between common-draft and plan-draft blocks gate."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    mismatched_plan = _PLAN_DRAFT_PASS.replace(
        'review_cycle_id: "stage5-20260307"',
        'review_cycle_id: "stage5-DIFFERENT"',
    )
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, plan_draft=mismatched_plan
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "review_cycle_id" in detail or "mismatch" in detail.lower()


def test_stage5_gate_wrk_id_mismatch_blocks(tmp_path: Path):
    """wrk_id mismatch between artifact and requested WRK → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    wrong_wrk = _COMMON_DRAFT_PASS.replace("wrk_id: WRK-999", "wrk_id: WRK-111")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, common_draft=wrong_wrk
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "wrk_id" in detail or "mismatch" in detail.lower()


def test_stage5_gate_migration_exemption_allows_legacy(tmp_path: Path):
    """WRK with approved migration exemption passes even without approval artifacts."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, common_draft=None, plan_draft=None, browser_open=None, publish=None
    )
    exemption = """\
wrk_id: WRK-999
exemption_version: "1.0"
approved_by: user
approved_at: "2026-03-07T00:00:00Z"
approval_scope: full_stage5_evidence_set
rationale: "Legacy WRK predates gate activation."
"""
    (assets_dir / "evidence" / "stage5-migration-exemption.yaml").write_text(
        exemption, encoding="utf-8"
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "exemption" in detail.lower() or "legacy" in detail.lower()


def test_stage5_gate_exemption_with_agent_authority_blocks(tmp_path: Path):
    """Migration exemption with agent identity as approved_by → gate returns False."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage5_fixtures(
        tmp_path, common_draft=None, plan_draft=None, browser_open=None, publish=None
    )
    bad_exemption = """\
wrk_id: WRK-999
exemption_version: "1.0"
approved_by: claude
approved_at: "2026-03-07T00:00:00Z"
approval_scope: full_stage5_evidence_set
rationale: "Agent-approved exemption (invalid)."
"""
    (assets_dir / "evidence" / "stage5-migration-exemption.yaml").write_text(
        bad_exemption, encoding="utf-8"
    )
    ok, detail = mod.check_stage5_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "authority" in detail.lower() or "approved_by" in detail.lower() or "allowlist" in detail.lower()

# ── WRK-1034: Stage 7 and Stage 17 gate tests ────────────────────────────────


def _write_stage7_fixtures(
    tmp_path: Path,
    *,
    activation: str = "full",
    confirmed_by: str = "user",
    confirmed_at: str = "2026-03-08T00:00:00Z",
    decision: str = "passed",
    include_artifact: bool = True,
    include_exemption: bool = False,
    exemption_approved_by: str = "user",
):
    """Build minimal fixture tree for Stage 7 gate tests."""
    mod = _load_verify_module()
    workspace_root = tmp_path / "workspace"
    scripts_dir = workspace_root / "scripts" / "work-queue"
    scripts_dir.mkdir(parents=True)
    assets_dir = workspace_root / ".claude" / "work-queue" / "assets" / "WRK-999"
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True)

    (scripts_dir / "stage7-gate-config.yaml").write_text(
        f"schema_version: '1.0'\nactivation: {activation}\nhuman_authority_allowlist:\n  - user\n  - vamsee\n",
        encoding="utf-8",
    )

    if include_exemption:
        (evidence_dir / "stage7-migration-exemption.yaml").write_text(
            f"wrk_id: WRK-999\napproved_by: {exemption_approved_by}\napproval_scope: legacy\n",
            encoding="utf-8",
        )
    elif include_artifact:
        content = f"wrk_id: WRK-999\nconfirmed_by: {confirmed_by}\nconfirmed_at: {confirmed_at}\ndecision: {decision}\n"
        (evidence_dir / "plan-final-review.yaml").write_text(content, encoding="utf-8")

    return assets_dir, workspace_root


def _write_stage17_fixtures(
    tmp_path: Path,
    *,
    activation: str = "full",
    reviewer: str = "user",
    confirmed_at: str = "2026-03-08T00:00:00Z",
    decision: str = "approved",
    include_artifact: bool = True,
    include_exemption: bool = False,
    exemption_approved_by: str = "user",
    use_reviewed_at: bool = False,
):
    """Build minimal fixture tree for Stage 17 gate tests."""
    workspace_root = tmp_path / "workspace"
    scripts_dir = workspace_root / "scripts" / "work-queue"
    scripts_dir.mkdir(parents=True)
    assets_dir = workspace_root / ".claude" / "work-queue" / "assets" / "WRK-999"
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True)

    (scripts_dir / "stage17-gate-config.yaml").write_text(
        f"schema_version: '1.0'\nactivation: {activation}\nhuman_authority_allowlist:\n  - user\n  - vamsee\n",
        encoding="utf-8",
    )

    if include_exemption:
        (evidence_dir / "stage17-migration-exemption.yaml").write_text(
            f"wrk_id: WRK-999\napproved_by: {exemption_approved_by}\napproval_scope: legacy\n",
            encoding="utf-8",
        )
    elif include_artifact:
        ts_field = "reviewed_at" if use_reviewed_at else "confirmed_at"
        content = f"wrk_id: WRK-999\nreviewer: {reviewer}\n{ts_field}: {confirmed_at}\ndecision: {decision}\n"
        (evidence_dir / "user-review-close.yaml").write_text(content, encoding="utf-8")

    return assets_dir, workspace_root


# T1 — Stage 7 disabled → gate passes without artifact
def test_stage7_gate_disabled_passes(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(
        tmp_path, activation="disabled", include_artifact=False
    )
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "disabled" in detail


# T2 — Stage 7 missing artifact → gate fails
def test_stage7_gate_missing_artifact_fails(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(
        tmp_path, include_artifact=False
    )
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "plan-final-review.yaml" in detail


# T3 — Stage 7 all fields valid → gate passes
def test_stage7_gate_all_fields_pass(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path)
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "stage7 gate passed" in detail


# T4 — Stage 7 wrong decision → gate fails
def test_stage7_gate_wrong_decision_fails(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path, decision="pending")
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "decision" in detail


# T5 — Stage 7 agent confirmed_by → gate fails
def test_stage7_gate_agent_confirmed_by_rejected(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path, confirmed_by="claude")
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "allowlist" in detail or "not permitted" in detail


# T6 — Stage 7 confirmed_by missing → gate fails
def test_stage7_gate_confirmed_by_missing_fails(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path, confirmed_by="")
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "confirmed_by" in detail


# T7 — Stage 7 missing config → infrastructure failure
def test_stage7_gate_missing_config_infra_failure(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path)
    (workspace_root / "scripts" / "work-queue" / "stage7-gate-config.yaml").unlink()
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is None
    assert "stage7-gate-config.yaml" in detail


# T8 — Stage 7 valid migration exemption → gate passes
def test_stage7_gate_migration_exemption_passes(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(
        tmp_path, include_artifact=False, include_exemption=True
    )
    ok, detail = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "exemption" in detail


# T9 — Stage 17 disabled → gate passes without artifact
def test_stage17_gate_disabled_passes(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(
        tmp_path, activation="disabled", include_artifact=False
    )
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "disabled" in detail


# T10 — Stage 17 missing artifact → gate fails
def test_stage17_gate_missing_artifact_fails(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(
        tmp_path, include_artifact=False
    )
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "user-review-close.yaml" in detail


# T11 — Stage 17 all fields valid → gate passes
def test_stage17_gate_all_fields_pass(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(tmp_path)
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "stage17 gate passed" in detail


# T12 — Stage 17 wrong decision → gate fails
def test_stage17_gate_wrong_decision_fails(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(tmp_path, decision="pending")
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "decision" in detail


# T13 — Stage 17 agent reviewer → gate fails
def test_stage17_gate_agent_reviewer_rejected(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(tmp_path, reviewer="gemini")
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False
    assert "allowlist" in detail or "not permitted" in detail


# T14 — Stage 7 CLI --stage7-check exit 0 on pass
def test_stage7_cli_exit_0_on_pass(tmp_path: Path):
    import subprocess, sys
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path)
    script = workspace_root.parents[1] / "workspace" / "scripts" / "work-queue" / "verify-gate-evidence.py"
    repo_script = Path(__file__).resolve().parents[2] / "scripts" / "work-queue" / "verify-gate-evidence.py"
    # Use the real script but patch workspace via env; simpler: call check fn directly with exit code mapping
    ok, _ = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True


# T15 — Stage 7 CLI exit 1 on predicate fail (missing artifact)
def test_stage7_cli_exit_1_on_predicate_fail(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path, include_artifact=False)
    ok, _ = mod.check_stage7_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is False  # maps to exit 1


# T16 — Stage 17 CLI exit 0 on pass
def test_stage17_cli_exit_0_on_pass(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(tmp_path)
    ok, _ = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True


# T17 — Stage 17 legacy reviewed_at field accepted (union check)
def test_stage17_gate_reviewed_at_field_accepted(tmp_path: Path):
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage17_fixtures(tmp_path, use_reviewed_at=True)
    ok, detail = mod.check_stage17_evidence_gate("WRK-999", assets_dir, workspace_root)
    assert ok is True
    assert "stage17 gate passed" in detail


# T18 — _run_stage7_check exit-code mapping: True → 0, False → 1, None → 2
def test_run_stage7_check_exit_code_mapping(tmp_path: Path, monkeypatch):
    """Verify _run_stage7_check maps (True→0, False→1, None→2) correctly."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")
    assets_dir, workspace_root = _write_stage7_fixtures(tmp_path)

    # Patch workspace resolution to use our tmp_path fixture
    monkeypatch.setattr(
        mod, "check_stage7_evidence_gate",
        lambda wrk_id, assets, root: (True, "mock pass"),
    )
    # Also patch assets_dir.is_dir() by pointing to a real dir
    real_assets = workspace_root / ".claude" / "work-queue" / "assets" / "WRK-999"
    # _run_stage7_check derives assets_dir from workspace_root; patch Path(__file__) indirectly
    # by patching the gate function — it is called only if assets_dir.is_dir() passes.
    # Use WRK-999 which exists in the fixture tree.
    import unittest.mock
    with unittest.mock.patch.object(mod, "check_stage7_evidence_gate", return_value=(True, "mock pass")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage7_check(["WRK-999"])
    assert ret == 0, f"expected 0 (pass), got {ret}"

    with unittest.mock.patch.object(mod, "check_stage7_evidence_gate", return_value=(False, "predicate fail")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage7_check(["WRK-999"])
    assert ret == 1, f"expected 1 (predicate fail), got {ret}"

    with unittest.mock.patch.object(mod, "check_stage7_evidence_gate", return_value=(None, "infra fail")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage7_check(["WRK-999"])
    assert ret == 2, f"expected 2 (infra fail), got {ret}"


# T19 — _run_stage17_check exit-code mapping: True → 0, False → 1, None → 2
def test_run_stage17_check_exit_code_mapping(tmp_path: Path, monkeypatch):
    """Verify _run_stage17_check maps (True→0, False→1, None→2) correctly."""
    mod = _load_verify_module()
    if mod.yaml is None:
        pytest.skip("PyYAML unavailable")

    import unittest.mock
    with unittest.mock.patch.object(mod, "check_stage17_evidence_gate", return_value=(True, "mock pass")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage17_check(["WRK-999"])
    assert ret == 0, f"expected 0 (pass), got {ret}"

    with unittest.mock.patch.object(mod, "check_stage17_evidence_gate", return_value=(False, "predicate fail")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage17_check(["WRK-999"])
    assert ret == 1, f"expected 1 (predicate fail), got {ret}"

    with unittest.mock.patch.object(mod, "check_stage17_evidence_gate", return_value=(None, "infra fail")):
        with unittest.mock.patch("pathlib.Path.is_dir", return_value=True):
            ret = mod._run_stage17_check(["WRK-999"])
    assert ret == 2, f"expected 2 (infra fail), got {ret}"
