"""
stage_exit_checks.py — Stage-specific gate check functions (WRK-1044).

Each check returns (ok: bool | None, message: str).
  True  = gate passes
  False = gate fails (block stage exit)
  None  = warn only (non-blocking)

Public entry point: run_d_item_checks(stage, assets_dir, repo_root) → bool
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize_path(path: str, wrk_id: str) -> str:
    """Substitute WRK-NNN token with actual wrk_id in artifact path strings.

    D1 fix: exit_stage.py Stage 1 was blocking because the literal string
    'WRK-NNN' appeared in expected artifact paths without substitution.
    """
    return path.replace("WRK-NNN", wrk_id)


def _read_yaml(path: Path) -> dict:
    """Load YAML; return empty dict on any error."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _iso_to_epoch(ts: str) -> float | None:
    """Convert ISO 8601 timestamp string to epoch seconds; return None on failure."""
    from datetime import datetime, timezone
    ts = ts.strip().rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# D1 — Stage 1 capture gate
# ---------------------------------------------------------------------------

def check_s1_capture_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 1 exit: user-review-capture.yaml must exist with scope_approved: true."""
    path = assets_dir / "evidence" / "user-review-capture.yaml"
    if not path.exists():
        return False, "user-review-capture.yaml missing — Stage 1 capture not complete"
    data = _read_yaml(path)
    if not data.get("scope_approved"):
        return False, (
            f"user-review-capture.yaml: scope_approved="
            f"{data.get('scope_approved')!r} (must be true)"
        )
    return True, "stage1 capture gate passed"


# ---------------------------------------------------------------------------
# D3 — Stage 17 reviewer in human allowlist
# ---------------------------------------------------------------------------

def check_s17_reviewer_allowlist(
    assets_dir: Path,
    allowlist: tuple[str, ...] = ("user", "vamsee"),
) -> tuple[bool | None, str]:
    """Stage 17 exit: reviewer in user-review-close.yaml must be in allowlist."""
    path = assets_dir / "evidence" / "user-review-close.yaml"
    if not path.exists():
        return False, "user-review-close.yaml missing"
    data = _read_yaml(path)
    reviewer = str(data.get("reviewer", "")).strip()
    if reviewer not in allowlist:
        return False, (
            f"reviewer={reviewer!r} not in allowlist {allowlist} — "
            "Stage 17 requires human reviewer"
        )
    return True, f"reviewer={reviewer!r} in allowlist"


# ---------------------------------------------------------------------------
# D4 — Stage 19 integrated_repo_tests count ≥ 3
# ---------------------------------------------------------------------------

def check_s19_integrated_tests(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 19 exit: execute.yaml must have ≥ 3 integrated_repo_tests entries."""
    path = assets_dir / "evidence" / "execute.yaml"
    if not path.exists():
        return False, "execute.yaml missing"
    data = _read_yaml(path)
    tests = data.get("integrated_repo_tests") or []
    count = len(tests) if isinstance(tests, list) else 0
    if count < 3:
        return False, f"integrated_repo_tests count={count}; need ≥ 3 (D4)"
    return True, f"integrated_repo_tests count={count} OK"


# ---------------------------------------------------------------------------
# D5 — Stage 15 future-work.yaml spun-off-new all captured: true
# ---------------------------------------------------------------------------

def check_s15_future_work(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 15 exit: future-work.yaml spun-off-new items must all be captured."""
    path = assets_dir / "evidence" / "future-work.yaml"
    if not path.exists():
        return None, "future-work.yaml absent (WARN — no future work recorded)"
    data = _read_yaml(path)
    recs = data.get("recommendations") or []
    uncaptured = [
        r.get("id", "?")
        for r in recs
        if isinstance(r, dict)
        and r.get("disposition") == "spun-off-new"
        and r.get("captured") is not True
    ]
    if uncaptured:
        return False, (
            f"future-work spun-off-new items not captured: {uncaptured} — "
            "create WRK items before Stage 15 exit"
        )
    return True, "all spun-off-new future-work items captured"


# ---------------------------------------------------------------------------
# D6 — Stage 19 stage evidence covers all 20 stages
# ---------------------------------------------------------------------------

def check_s19_stage_evidence(
    workspace_root: str, wrk_id: str
) -> tuple[bool | None, str]:
    """Stage 19 exit: stage-evidence.yaml must cover all 20 stages."""
    # Find WRK file
    queue_dir = Path(workspace_root) / ".claude" / "work-queue"
    wrk_path = None
    for folder in ("working", "done", "pending"):
        candidate = queue_dir / folder / f"{wrk_id}.md"
        if candidate.exists():
            wrk_path = candidate
            break
    if wrk_path is None:
        return None, f"{wrk_id}.md not found in work-queue"

    text = wrk_path.read_text(encoding="utf-8")
    # Extract stage_evidence_ref from frontmatter
    ref_match = re.search(r"^stage_evidence_ref:\s*(.+)$", text, re.MULTILINE)
    if not ref_match:
        return False, "stage_evidence_ref missing in WRK frontmatter"
    ref = ref_match.group(1).strip().strip('"').strip("'")
    ev_path = Path(workspace_root) / ref
    if not ev_path.exists():
        return False, f"stage evidence file missing: {ref}"
    data = _read_yaml(ev_path)
    stages = data.get("stages") or []
    count = len(stages) if isinstance(stages, list) else 0
    if count < 20:
        return False, f"stage-evidence has {count} stages; need 20 (D6)"
    return True, f"stage-evidence covers {count} stages OK"


# ---------------------------------------------------------------------------
# D7 — Stage 5/7/17 browser-open timestamp < approval timestamp
# ---------------------------------------------------------------------------

def check_s5_browser_timestamps(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 5 exit: browser-open event must be BEFORE approval (not inverted).

    P1-C fix: fail-open ONLY when browser-open yaml is absent.
    If present with inverted timestamps → hard FAIL.
    """
    evidence_dir = assets_dir / "evidence"
    browser_path = evidence_dir / "user-review-browser-open.yaml"
    if not browser_path.exists():
        return None, "user-review-browser-open.yaml absent (fail-open)"
    data = _read_yaml(browser_path)
    events = data.get("events") or []

    # Stage→approval artifact mapping
    approval_map = {
        "plan_draft": (
            evidence_dir / "user-review-plan-draft.yaml",
            ("reviewed_at", "confirmed_at"),
        ),
        "plan_final": (
            evidence_dir / "plan-final-review.yaml",
            ("confirmed_at",),
        ),
    }
    for event in events:
        if not isinstance(event, dict):
            continue
        stage = str(event.get("stage", "")).strip().lower()
        if stage not in approval_map:
            continue
        opened_at_str = str(event.get("opened_at", "")).strip()
        opened_ts = _iso_to_epoch(opened_at_str)
        if opened_ts is None:
            continue
        approval_path, fields = approval_map[stage]
        if not approval_path.exists():
            continue
        approval_data = _read_yaml(approval_path)
        approval_ts = None
        for field in fields:
            val = str(approval_data.get(field, "")).strip()
            if val:
                ts = _iso_to_epoch(val)
                if ts is not None:
                    approval_ts = ts
                    break
        if approval_ts is None:
            continue
        if opened_ts > approval_ts:
            return False, (
                f"stage={stage}: browser opened at {opened_at_str} which is "
                f"AFTER approval — timestamps inverted (hard FAIL, D7/P1-C)"
            )
    return True, "browser-open timestamps OK"


# ---------------------------------------------------------------------------
# D8 — published_at ≤ confirmed_at (delegates to verifier function)
# ---------------------------------------------------------------------------

def check_s5_publish_order(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 5 exit: plan HTML published_at must not be after confirmed_at.

    P1-F fix: delegates to existing check_plan_publish_predates_approval()
    in verify-gate-evidence.py to avoid duplicate canonical implementation.
    """
    try:
        import verify_gate_evidence as vge
        if hasattr(vge, "check_plan_publish_predates_approval"):
            return vge.check_plan_publish_predates_approval(assets_dir)
    except ImportError:
        pass

    # Fallback inline implementation for standalone use
    evidence_dir = assets_dir / "evidence"
    publish_path = evidence_dir / "user-review-publish.yaml"
    final_review_path = evidence_dir / "plan-final-review.yaml"
    draft_review_path = evidence_dir / "user-review-plan-draft.yaml"

    if not publish_path.exists():
        return None, "user-review-publish.yaml absent (fail-open)"

    publish_data = _read_yaml(publish_path)
    events = publish_data.get("events") or []

    for event in events:
        if not isinstance(event, dict):
            continue
        published_str = str(event.get("published_at", "")).strip()
        stage = str(event.get("stage", "")).strip().lower()
        pub_ts = _iso_to_epoch(published_str)
        if pub_ts is None:
            continue
        # Find corresponding approval timestamp
        if stage == "plan_final" and final_review_path.exists():
            conf_data = _read_yaml(final_review_path)
            conf_str = str(conf_data.get("confirmed_at", "")).strip()
        elif stage == "plan_draft" and draft_review_path.exists():
            conf_data = _read_yaml(draft_review_path)
            conf_str = str(conf_data.get("reviewed_at", "")).strip()
        else:
            continue
        conf_ts = _iso_to_epoch(conf_str)
        if conf_ts is not None and pub_ts > conf_ts:
            return False, (
                f"stage={stage}: published_at={published_str} is after "
                f"confirmed_at={conf_str} — plan published after approval (D8)"
            )
    return True, "publish order OK"


# ---------------------------------------------------------------------------
# D11 — All R-09 sentinel fields at claim entry
# ---------------------------------------------------------------------------

def check_s8_sentinel_fields(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 8 (Claim) entry: all R-09 sentinel fields must be non-unknown/empty.

    P1-D fix: covers all required fields, not just session_id.
    """
    evidence_dir = assets_dir / "evidence"
    errors: list[str] = []

    # activation.yaml fields
    activation_path = evidence_dir / "activation.yaml"
    if activation_path.exists():
        data = _read_yaml(activation_path)
        for field in ("session_id", "orchestrator_agent"):
            val = str(data.get(field, "")).strip()
            if not val or val == "unknown":
                errors.append(f"activation.yaml: {field}={val!r} is sentinel/empty")

    # claim-evidence.yaml fields
    claim_path = evidence_dir / "claim-evidence.yaml"
    if not claim_path.exists():
        claim_path = evidence_dir / "claim.yaml"
    if claim_path.exists():
        data = _read_yaml(claim_path)
        for field in ("best_fit_provider", "session_owner"):
            val = str(data.get(field, "")).strip()
            if not val or val == "unknown":
                errors.append(f"{claim_path.name}: {field}={val!r} is sentinel/empty")
        route = str(data.get("route", "")).strip()
        if not route:
            errors.append(f"{claim_path.name}: route='' (empty)")
        qs = data.get("quota_snapshot") or {}
        if isinstance(qs, dict):
            qs_status = str(qs.get("status", "")).strip().lower()
            pct = qs.get("pct_remaining")
            if qs_status == "available" and pct is None:
                errors.append(
                    f"{claim_path.name}: quota_snapshot.pct_remaining=null "
                    f"when status=available"
                )

    if errors:
        return False, "; ".join(errors)
    return True, "all R-09 sentinel fields OK"


# ---------------------------------------------------------------------------
# D12 — P1 finding in cross-review → require override artifact
# ---------------------------------------------------------------------------

def check_s6_p1_pause(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 6 exit: P1 findings require cross-review-p1-override.yaml to proceed."""
    evidence_dir = assets_dir / "evidence"
    p1_files: list[str] = []
    for review_file in evidence_dir.glob("cross-review-*.md"):
        text = review_file.read_text(encoding="utf-8")
        if re.search(
            r"\[P1\]|\*\*P1\b|##\s*P1\s+Findings?|P1-\d+|^\s*P1\s*:", text, re.IGNORECASE | re.MULTILINE
        ):
            p1_files.append(review_file.name)

    if not p1_files:
        return True, "no P1 findings in cross-review files"

    override_path = evidence_dir / "cross-review-p1-override.yaml"
    if not override_path.exists():
        return False, (
            f"P1 finding(s) in {p1_files} — write "
            "evidence/cross-review-p1-override.yaml "
            "(reviewer in allowlist + override_reason + overridden_at) to proceed"
        )

    data = _read_yaml(override_path)
    reviewer = str(data.get("reviewer", "")).strip()
    allowlist = ("user", "vamsee")
    if reviewer not in allowlist:
        return False, (
            f"cross-review-p1-override.yaml: reviewer={reviewer!r} "
            f"not in allowlist {allowlist}"
        )
    return None, f"P1 findings overridden by {reviewer!r} (WARN — proceed with caution)"


# ---------------------------------------------------------------------------
# D13 — gate-evidence-summary.json 0 MISSING
# ---------------------------------------------------------------------------

def check_s14_gate_summary(assets_dir: Path) -> tuple[bool | None, str]:
    """Stage 14 exit: gate-evidence-summary.json must have 0 MISSING gates."""
    path = assets_dir / "evidence" / "gate-evidence-summary.json"
    if not path.exists():
        return None, "gate-evidence-summary.json absent (WARN)"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"gate-evidence-summary.json parse error: {exc}"
    gates = data.get("gates") or []
    # Exclude warn=true entries (expected-pending gates like reclaim, close-review)
    hard_fails = [
        g.get("name", "?")
        for g in gates
        if g.get("ok") is False and not g.get("warn")
    ]
    if hard_fails:
        return False, f"MISSING gates in summary: {hard_fails}"
    return True, "gate-evidence-summary: all gates PASS"
