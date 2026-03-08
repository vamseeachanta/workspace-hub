"""
Tests T11-T30: gate-verifier hardening checks for WRK-1035 Phase 3.

Each test creates minimal YAML fixtures in tmp_path and exercises exactly
one condition of the new check functions added in Phase 3.
"""
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Ensure the module under test is importable regardless of working directory
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "verify_gate_evidence",
    SCRIPTS_DIR / "verify-gate-evidence.py",
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

check_approval_ordering = _mod.check_approval_ordering
check_midnight_utc_sentinel = _mod.check_midnight_utc_sentinel
check_browser_open_elapsed_time = _mod.check_browser_open_elapsed_time
check_codex_keyword_in_review = _mod.check_codex_keyword_in_review
check_sentinel_values = _mod.check_sentinel_values
check_publish_commit_uniqueness = _mod.check_publish_commit_uniqueness
check_stage_evidence_paths = _mod.check_stage_evidence_paths
check_done_pending_contradiction = _mod.check_done_pending_contradiction
check_plan_publish_predates_approval = _mod.check_plan_publish_predates_approval
check_workstation_contract_strict = _mod.check_workstation_contract_strict
check_reclaim_gate_na = _mod.check_reclaim_gate_na
check_claim_artifact_path = _mod.check_claim_artifact_path
check_iso_datetime_with_time = _mod.check_iso_datetime_with_time
check_stage1_capture_gate = _mod.check_stage1_capture_gate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_assets(tmp_path: Path) -> Path:
    """Create a minimal assets directory with an evidence/ subdirectory."""
    assets = tmp_path / "assets"
    (assets / "evidence").mkdir(parents=True)
    return assets


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# T11 — check_approval_ordering FAIL on inverted timestamps
# ---------------------------------------------------------------------------

def test_T11_approval_ordering_fail_inverted(tmp_path):
    """claim-evidence.claimed_at BEFORE plan-final-review.confirmed_at → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "plan-final-review.yaml", (
        "confirmed_at: '2026-03-08T12:00:00Z'\n"
        "decision: passed\n"
    ))
    # claim timestamp earlier than plan-final — ordering violation
    _write(ev / "claim-evidence.yaml", (
        "claimed_at: '2026-03-08T10:00:00Z'\n"
    ))

    ok, detail = check_approval_ordering(assets, phase="claim")
    assert ok is False
    assert "ordering violation" in detail


# ---------------------------------------------------------------------------
# T12 — check_approval_ordering PASS on correct order
# ---------------------------------------------------------------------------

def test_T12_approval_ordering_pass(tmp_path):
    """Correctly ordered timestamps across lifecycle stages → PASS."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "plan-final-review.yaml", "confirmed_at: '2026-03-08T10:00:00Z'\ndecision: passed\n")
    _write(ev / "claim-evidence.yaml", "claimed_at: '2026-03-08T11:00:00Z'\n")
    _write(ev / "execute.yaml", "executed_at: '2026-03-08T12:00:00Z'\n")
    _write(ev / "user-review-close.yaml", (
        "confirmed_at: '2026-03-08T13:00:00Z'\n"
        "reviewer: vamsee\n"
        "decision: approved\n"
    ))

    ok, detail = check_approval_ordering(assets, phase="close")
    assert ok is True
    assert "OK" in detail


# ---------------------------------------------------------------------------
# T13 — check_midnight_utc_sentinel FAIL on T00:00:00Z
# ---------------------------------------------------------------------------

def test_T13_midnight_utc_sentinel_fail(tmp_path):
    """Stage 5 approval artifact with T00:00:00Z → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "user-review-plan-draft.yaml", (
        "reviewed_at: '2026-03-08T00:00:00Z'\n"
        "approval_decision: approve_as_is\n"
    ))

    ok, detail = check_midnight_utc_sentinel(assets)
    assert ok is False
    assert "midnight UTC sentinel" in detail
    assert "user-review-plan-draft.yaml" in detail


# ---------------------------------------------------------------------------
# T14 — check_midnight_utc_sentinel PASS on normal ISO timestamp
# ---------------------------------------------------------------------------

def test_T14_midnight_utc_sentinel_pass(tmp_path):
    """Normal ISO timestamp (non-midnight) → PASS."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "user-review-plan-draft.yaml", (
        "reviewed_at: '2026-03-08T14:30:00Z'\n"
        "approval_decision: approve_as_is\n"
    ))

    ok, detail = check_midnight_utc_sentinel(assets)
    assert ok is True


# ---------------------------------------------------------------------------
# T15 — check_browser_open_elapsed_time FAIL when delta < 300s
# ---------------------------------------------------------------------------

def test_T15_browser_elapsed_fail_too_quick(tmp_path):
    """Delta < 300s between browser-open and plan_draft approval → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    # browser opened at 12:00, plan_draft reviewed at 12:03 (180s later — below 300s threshold)
    _write(assets / "evidence" / "user-review-browser-open.yaml", (
        "events:\n"
        "  - stage: plan_draft\n"
        "    opened_at: '2026-03-08T12:00:00Z'\n"
        "    opened_in_default_browser: true\n"
        "    html_ref: plan.html\n"
        "    reviewer: vamsee\n"
    ))
    _write(ev / "user-review-plan-draft.yaml", (
        "reviewed_at: '2026-03-08T12:03:00Z'\n"
        "approval_decision: approve_as_is\n"
    ))

    ok, detail = check_browser_open_elapsed_time(assets, human_allowlist={"vamsee"})
    assert ok is False
    assert "180" in detail or "stage=plan_draft" in detail


# ---------------------------------------------------------------------------
# T16 — check_browser_open_elapsed_time PASS when delta >= 300s
# ---------------------------------------------------------------------------

def test_T16_browser_elapsed_pass(tmp_path):
    """Delta >= 300s → PASS."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    # browser opened at 12:00, reviewed at 12:10 (600s later)
    _write(assets / "evidence" / "user-review-browser-open.yaml", (
        "events:\n"
        "  - stage: plan_draft\n"
        "    opened_at: '2026-03-08T12:00:00Z'\n"
        "    opened_in_default_browser: true\n"
        "    html_ref: plan.html\n"
        "    reviewer: vamsee\n"
    ))
    _write(ev / "user-review-plan-draft.yaml", (
        "reviewed_at: '2026-03-08T12:10:00Z'\n"
        "approval_decision: approve_as_is\n"
    ))

    ok, detail = check_browser_open_elapsed_time(assets, human_allowlist={"vamsee"})
    assert ok is True


# ---------------------------------------------------------------------------
# T17 — check_browser_open_elapsed_time FAIL at Stage 17 (close_review) delta < 300s
# ---------------------------------------------------------------------------

def test_T17_browser_elapsed_fail_close_review(tmp_path):
    """close_review stage with delta < 300s → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(assets / "evidence" / "user-review-browser-open.yaml", (
        "events:\n"
        "  - stage: close_review\n"
        "    opened_at: '2026-03-08T15:00:00Z'\n"
        "    opened_in_default_browser: true\n"
        "    html_ref: impl.html\n"
        "    reviewer: vamsee\n"
    ))
    # confirmed only 60 seconds later
    _write(ev / "user-review-close.yaml", (
        "confirmed_at: '2026-03-08T15:01:00Z'\n"
        "reviewer: vamsee\n"
        "decision: approved\n"
    ))

    ok, detail = check_browser_open_elapsed_time(assets, human_allowlist={"vamsee"})
    assert ok is False
    assert "close_review" in detail or "60" in detail


# ---------------------------------------------------------------------------
# T18 — check_codex_keyword_in_review FAIL when "codex" absent
# ---------------------------------------------------------------------------

def test_T18_codex_keyword_fail(tmp_path):
    """Review file present but contains no mention of 'codex' → FAIL."""
    assets = _make_assets(tmp_path)

    _write(assets / "review-synthesis.md", (
        "# Review\nReviewed by Claude only.\nNo issues found.\n"
    ))

    ok, detail = check_codex_keyword_in_review(assets)
    assert ok is False
    assert "codex" in detail.lower()


# ---------------------------------------------------------------------------
# T19 — check_codex_keyword_in_review PASS when "codex" present
# ---------------------------------------------------------------------------

def test_T19_codex_keyword_pass(tmp_path):
    """Review file mentions 'Codex' → PASS."""
    assets = _make_assets(tmp_path)

    _write(assets / "review-synthesis.md", (
        "# Review\nCodex reviewed this implementation.\nAPPROVED.\n"
    ))

    ok, detail = check_codex_keyword_in_review(assets)
    assert ok is True


# ---------------------------------------------------------------------------
# T20 — check_sentinel_values FAIL on session_id="unknown" in activation.yaml
# ---------------------------------------------------------------------------

def test_T20_sentinel_values_fail_session_id_unknown(tmp_path):
    """activation.yaml with session_id='unknown' → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "activation.yaml", (
        "wrk_id: WRK-9999\n"
        "set_active_wrk: true\n"
        "session_id: unknown\n"
        "orchestrator_agent: claude\n"
    ))

    ok, detail = check_sentinel_values(assets)
    assert ok is False
    assert "session_id" in detail
    assert "unknown" in detail


# ---------------------------------------------------------------------------
# T21 — check_sentinel_values FAIL on empty route in claim-evidence.yaml
# ---------------------------------------------------------------------------

def test_T21_sentinel_values_fail_empty_route(tmp_path):
    """claim-evidence.yaml with route='' → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "claim-evidence.yaml", (
        "session_owner: vamsee\n"
        "best_fit_provider: claude\n"
        "route: ''\n"
        "claimed_at: '2026-03-08T12:00:00Z'\n"
    ))

    ok, detail = check_sentinel_values(assets)
    assert ok is False
    assert "route" in detail


# ---------------------------------------------------------------------------
# T22 — check_publish_commit_uniqueness FAIL all three same commit
# ---------------------------------------------------------------------------

def test_T22_publish_commit_uniqueness_fail_all_same(tmp_path):
    """All three stages share the same commit hash → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "user-review-publish.yaml", (
        "events:\n"
        "  - stage: plan_draft\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T10:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [plan.html]\n"
        "  - stage: plan_final\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T11:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [plan.html]\n"
        "  - stage: close_review\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T12:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [impl.html]\n"
    ))

    ok, detail = check_publish_commit_uniqueness(assets)
    assert ok is False
    assert "abc1234" in detail


# ---------------------------------------------------------------------------
# T23 — check_publish_commit_uniqueness WARN when plan_draft+plan_final share commit
# ---------------------------------------------------------------------------

def test_T23_publish_commit_uniqueness_warn_plan_draft_final_same(tmp_path):
    """plan_draft and plan_final share commit but close_review differs → WARN (None)."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "user-review-publish.yaml", (
        "events:\n"
        "  - stage: plan_draft\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T10:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [plan.html]\n"
        "  - stage: plan_final\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T11:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [plan.html]\n"
        "  - stage: close_review\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: def5678\n"
        "    published_at: '2026-03-08T14:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [impl.html]\n"
    ))

    ok, detail = check_publish_commit_uniqueness(assets)
    assert ok is None
    assert "abc1234" in detail


# ---------------------------------------------------------------------------
# T24 — check_stage_evidence_paths FAIL when referenced path doesn't exist
# ---------------------------------------------------------------------------

def test_T24_stage_evidence_paths_fail_missing(tmp_path):
    """stage-evidence.yaml references a path that doesn't exist → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "stage-evidence.yaml", (
        "wrk_id: WRK-9999\n"
        "stages:\n"
        "  - order: 1\n"
        "    stage: Capture\n"
        "    status: done\n"
        "    evidence: specs/wrk/WRK-9999/nonexistent-artifact.md\n"
    ))

    ok, detail = check_stage_evidence_paths(assets, workspace_root=REPO_ROOT)
    assert ok is False
    assert "nonexistent-artifact.md" in detail or "not found" in detail


# ---------------------------------------------------------------------------
# T25 — check_done_pending_contradiction FAIL
# ---------------------------------------------------------------------------

def test_T25_done_pending_contradiction_fail(tmp_path):
    """A stage with status='done' and comment containing 'pending' → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "stage-evidence.yaml", (
        "wrk_id: WRK-9999\n"
        "stages:\n"
        "  - order: 1\n"
        "    stage: Capture\n"
        "    status: done\n"
        "    evidence: capture.yaml\n"
        "    comment: This is still pending review\n"
    ))

    ok, detail = check_done_pending_contradiction(assets)
    assert ok is False
    assert "pending" in detail.lower()


# ---------------------------------------------------------------------------
# T26 — check_plan_publish_predates_approval FAIL
# ---------------------------------------------------------------------------

def test_T26_plan_publish_predates_approval_fail(tmp_path):
    """Plan draft published before user approved it → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    # published at 10:00, reviewed at 11:00 → published BEFORE review
    _write(ev / "user-review-publish.yaml", (
        "events:\n"
        "  - stage: plan_draft\n"
        "    pushed_to_origin: true\n"
        "    remote: origin\n"
        "    branch: main\n"
        "    commit: abc1234\n"
        "    published_at: '2026-03-08T10:00:00Z'\n"
        "    reviewer: vamsee\n"
        "    documents: [plan.html]\n"
    ))
    _write(ev / "user-review-plan-draft.yaml", (
        "reviewed_at: '2026-03-08T11:00:00Z'\n"
        "approval_decision: approve_as_is\n"
    ))

    ok, detail = check_plan_publish_predates_approval(assets)
    assert ok is False
    assert "predates" in detail or "< reviewed_at" in detail or "published_at" in detail


# ---------------------------------------------------------------------------
# T27 — check_workstation_contract_strict FAIL when fields absent
# ---------------------------------------------------------------------------

def test_T27_workstation_contract_strict_fail(tmp_path):
    """Frontmatter missing plan_workstations and execution_workstations → FAIL."""
    front = (
        "wrk_id: WRK-9999\n"
        "title: Test item\n"
        "status: working\n"
    )

    ok, detail = check_workstation_contract_strict(front)
    assert ok is False
    assert "plan_workstations" in detail or "execution_workstations" in detail


# ---------------------------------------------------------------------------
# T28 — check_reclaim_gate_na returns (None, ...) when Stage 18 n/a + no reclaim log
# ---------------------------------------------------------------------------

def test_T28_reclaim_gate_na_warn(tmp_path):
    """Stage 18 marked n/a and no reclaim.yaml → WARN (None return)."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "stage-evidence.yaml", (
        "wrk_id: WRK-9999\n"
        "stages:\n"
        "  - order: 18\n"
        "    stage: Reclaim\n"
        "    status: n/a\n"
        "    evidence: n/a\n"
    ))
    # No reclaim.yaml present

    ok, detail = check_reclaim_gate_na(assets)
    assert ok is None
    assert "n/a" in detail.lower()


# ---------------------------------------------------------------------------
# T29 — check_claim_artifact_path: canonical PASS, legacy WARN, neither FAIL
# ---------------------------------------------------------------------------

def test_T29_claim_artifact_path_canonical_pass(tmp_path):
    """Canonical evidence/claim-evidence.yaml exists → PASS."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "claim-evidence.yaml", "session_owner: vamsee\n")

    ok, detail = check_claim_artifact_path(assets)
    assert ok is True
    assert "claim-evidence.yaml" in detail


def test_T29b_claim_artifact_path_legacy_warn(tmp_path):
    """Only legacy evidence/claim.yaml exists → WARN (None)."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "claim.yaml", "session_owner: vamsee\n")

    ok, detail = check_claim_artifact_path(assets)
    assert ok is None
    assert "legacy" in detail.lower()


def test_T29c_claim_artifact_path_fail(tmp_path):
    """Neither canonical nor legacy claim artifact exists → FAIL."""
    assets = _make_assets(tmp_path)

    ok, detail = check_claim_artifact_path(assets)
    assert ok is False
    assert "no claim artifact" in detail.lower()


# ---------------------------------------------------------------------------
# T30 — check_iso_datetime_with_time FAIL on date-only "2026-03-08"
# ---------------------------------------------------------------------------

def test_T30_iso_datetime_with_time_fail(tmp_path):
    """Approval artifact with date-only confirmed_at '2026-03-08' → FAIL."""
    assets = _make_assets(tmp_path)
    ev = assets / "evidence"

    _write(ev / "user-review-close.yaml", (
        "reviewer: vamsee\n"
        "confirmed_at: '2026-03-08'\n"
        "decision: approved\n"
    ))

    ok, detail = check_iso_datetime_with_time(assets)
    assert ok is False
    assert "2026-03-08" in detail
    assert "date-only" in detail
