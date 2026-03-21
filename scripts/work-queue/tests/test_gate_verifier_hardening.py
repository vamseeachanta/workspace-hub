"""
Tests T11-T33: gate-verifier hardening checks for WRK-1035 Phase 3 (T11-T30)
and WRK-1039 hardening additions (T31-T33).

Each test creates minimal YAML fixtures in tmp_path and exercises exactly
one condition of the new check functions added in Phase 3.
"""
import json
import subprocess
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
# (removed: check_browser_open_elapsed_time — WRK-5107 HTML purge)
check_codex_keyword_in_review = _mod.check_codex_keyword_in_review
check_sentinel_values = _mod.check_sentinel_values
# (removed: check_publish_commit_uniqueness — WRK-5107 HTML purge)
check_stage_evidence_paths = _mod.check_stage_evidence_paths
check_done_pending_contradiction = _mod.check_done_pending_contradiction
# (removed: check_plan_publish_predates_approval — WRK-5107 HTML purge)
check_workstation_contract_strict = _mod.check_workstation_contract_strict
check_reclaim_gate_na = _mod.check_reclaim_gate_na
check_claim_artifact_path = _mod.check_claim_artifact_path
check_iso_datetime_with_time = _mod.check_iso_datetime_with_time
check_stage1_capture_gate = _mod.check_stage1_capture_gate
get_list_field = _mod.get_list_field

REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFIER_PATH = SCRIPTS_DIR / "verify-gate-evidence.py"


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


# T15-T17 removed — browser-open elapsed time tests purged (WRK-5107)


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


# T22-T23 removed — publish commit uniqueness tests purged (WRK-5107)


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


# T26 removed — plan publish predates approval test purged (WRK-5107)


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


# ---------------------------------------------------------------------------
# T31 — get_list_field: list-style YAML workstation field shows first item
# ---------------------------------------------------------------------------

def test_T31_workstation_list_field_shows_first_item():
    """get_list_field returns first list item for multi-line YAML lists, not None."""
    front = (
        "plan_workstations:\n"
        "  - dev-primary\n"
        "execution_workstations:\n"
        "  - dev-primary\n"
        "  - dev-secondary\n"
    )
    plan_ws = get_list_field(front, "plan_workstations")
    exec_ws = get_list_field(front, "execution_workstations")

    assert plan_ws == "dev-primary", (
        f"Expected 'dev-primary', got {plan_ws!r} — workstation gate must not show 'missing'"
    )
    assert exec_ws == "dev-primary", (
        f"Expected 'dev-primary', got {exec_ws!r}"
    )


# ---------------------------------------------------------------------------
# T32 — exit_stage.py resolves pending/ paths relative to queue root
# ---------------------------------------------------------------------------

def test_T32_exit_stage_resolves_pending_path(tmp_path):
    """exit_stage.py path resolution: pending/WRK-NNN.md resolved from queue root."""
    # Simulate the path resolution logic extracted from exit_stage.py
    import os

    def _resolve_path(stage_dir: str, rel: str) -> str:
        """Mirrors the fixed logic in exit_stage.py."""
        from pathlib import Path as P
        if rel.startswith(("done/", "pending/", "working/")):
            queue_root = str(P(stage_dir).parent.parent)
            return os.path.join(queue_root, rel)
        return os.path.join(stage_dir, rel)

    # Build a minimal queue layout
    queue_root = tmp_path / ".claude" / "work-queue"
    pending = queue_root / "pending"
    pending.mkdir(parents=True)
    wrk_file = pending / "WRK-TEST.md"
    wrk_file.write_text("# Test\n")

    # stage_dir is assets/WRK-TEST (exit_stage.py uses assets/<wrk_id>, not evidence subdir)
    stage_dir = str(queue_root / "assets" / "WRK-TEST")

    resolved = _resolve_path(stage_dir, "pending/WRK-TEST.md")
    assert os.path.exists(resolved), (
        f"pending/ path should resolve to queue root level, got {resolved!r}"
    )


# ---------------------------------------------------------------------------
# T33 — --json flag on failing WRK returns valid JSON with pass=false
# ---------------------------------------------------------------------------

def test_T33_json_flag_failing_wrk_returns_valid_json():
    """verify-gate-evidence.py WRK-NNN --json exits 1 and emits valid JSON with pass=false."""
    # WRK-1019 is a known audit WRK with fabricated timestamps (always exits 1)
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(VERIFIER_PATH), "WRK-1019", "--json"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1, (
        f"Expected exit 1 for known-failing WRK-1019, got {result.returncode}"
    )
    # Last line of stdout should be valid JSON
    stdout_lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
    assert stdout_lines, "Expected JSON output on stdout"
    last_line = stdout_lines[-1]
    payload = json.loads(last_line)  # raises if not valid JSON
    assert payload.get("pass") is False, f"Expected pass=false in JSON, got: {payload}"
    assert "wrk_id" in payload
    assert "missing" in payload
