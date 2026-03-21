#!/usr/bin/env python3
"""Validate orchestrator gate evidence for a WRK item."""

import re
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # type: ignore[import]
except Exception:
    yaml = None

# gate_checks_archive lives alongside this file in scripts/work-queue/
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    from gate_checks_archive import check_archive_readiness, GITHUB_ISSUE_RE  # type: ignore[import]
except ImportError:
    check_archive_readiness = None  # type: ignore[assignment]
    GITHUB_ISSUE_RE = re.compile(r"^https://(?:www\.)?github\.com/[^/]+/[^/]+/issues/\d+$")


def parse_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("front matter not found")
    return parts[1]


def get_field(front: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:[ \t]*(.+?)$", front, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def get_list_field(front: str, key: str) -> str | None:
    """Return first list item value for a multi-line YAML list field, or None."""
    block = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+-[^\n]*\n?)*)", front, re.MULTILINE)
    if not block:
        return None
    first = re.search(r"^\s+-\s+(\S+)", block.group(1), re.MULTILINE)
    return first.group(1) if first else None


def has_nonempty_field(front: str, key: str) -> bool:
    scalar = get_field(front, key)
    if scalar and scalar not in {"[]", "null", "~"}:
        return True
    block = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+-[^\n]*\n?)*)", front, re.MULTILINE)
    if not block:
        return False
    return bool(re.search(r"^\s+-\s+\S+", block.group(1), re.MULTILINE))


def parse_bool(value: str | None) -> bool:
    if not value:
        return False
    return value.lower() in {"1", "true", "yes", "y"}


def check_claim_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Check claim evidence for required metadata (canonical + WRK-677 legacy schema).

    Returns:
        (True,  detail) — gate OK
        (False, detail) — gate FAIL (hard error)
        (None,  detail) — WARN only (legacy item or absent file, no failure)
    """
    claim_file = evidence_file(assets_dir, "claim.yaml", ["claim-evidence.yaml"])
    if claim_file is None:
        return None, "claim evidence absent (legacy item — WARN)"

    data, yaml_err = load_yaml(claim_file)
    if yaml_err:
        return None, f"could not parse {claim_file.name}: {yaml_err}"
    assert data is not None

    is_canonical = claim_file.name == "claim.yaml" or str(data.get("stage", "")).lower() == "claim"
    if is_canonical:
        errors = []
        if not data.get("session_owner"):
            errors.append("session_owner missing")
        if not data.get("best_fit_provider"):
            errors.append("best_fit_provider missing")
        if not data.get("quota_snapshot_ref") and not ((data.get("quota_snapshot") or {}).get("timestamp")):
            errors.append("quota_snapshot_ref missing")
        if not data.get("claim_expires_at"):
            errors.append("claim_expires_at missing")
        if errors:
            return False, f"{claim_file.name}: " + "; ".join(errors)
        return True, f"{claim_file.name}: canonical claim evidence OK"

    # str() coercion handles both YAML string "1" and integer 1
    version = str(data.get("metadata_version", "")).strip()
    if version != "1":
        return None, f"{claim_file.name}: metadata_version={version!r} (legacy schema — WARN only)"

    # Hard checks for metadata_version "1" items
    errors = []
    if not data.get("session_owner"):
        errors.append("session_owner missing")
    qs = data.get("quota_snapshot") or {}
    qs_status = str(qs.get("status", "unknown")).lower()
    if qs_status in ("rate-limited", "quota-exceeded"):
        errors.append(f"quota_snapshot.status={qs_status!r} — provider unavailable")
    if not qs.get("timestamp"):
        errors.append("quota_snapshot.timestamp missing")
    bs = data.get("blocking_state") or {}
    if bs.get("blocked"):
        blocked_by = bs.get("blocked_by", [])
        errors.append(f"blocking_state.blocked=true, blocked_by={blocked_by}")
    if errors:
        return False, "; ".join(errors)

    owner = data.get("session_owner", "?")
    pct = qs.get("pct_remaining")
    pct_str = f"{pct}%" if pct is not None else "null"
    quota_note = f"quota={qs_status}({pct_str})"
    if qs_status == "unknown":
        quota_note += " [WARN: source unavailable]"
    return True, f"{claim_file.name}: version=1, owner={owner}, {quota_note}"


def _load_gate_config(workspace_root: Path, filename: str) -> tuple[dict | None, str]:
    """Load a stage gate config YAML by filename.

    Returns (data, "") on success or (None, error_message) on failure.
    """
    config_path = workspace_root / "scripts" / "work-queue" / filename
    if not config_path.exists():
        return None, f"{filename} not found at {config_path}"
    if yaml is None:
        return None, f"PyYAML unavailable — cannot load {filename}"
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"{filename} parse error: {exc}"
    if not isinstance(data, dict):
        return None, f"{filename} root is not a mapping"
    return data, ""


def _load_stage5_config(workspace_root: Path) -> tuple[dict | None, str]:
    """Load stage5-gate-config.yaml; return (data, error_msg) or (None, err)."""
    return _load_gate_config(workspace_root, "stage5-gate-config.yaml")


def _validate_exemption(
    exemption_path: Path, wrk_id: str, human_allowlist: set[str]
) -> tuple[str | None, str]:
    """Validate a migration exemption YAML.

    Returns (approved_by, "") on success or (None, error_msg) on failure.
    """
    try:
        ex = yaml.safe_load(exemption_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"{exemption_path.name} parse error: {exc}"
    if not isinstance(ex, dict):
        return None, f"{exemption_path.name} root is not a mapping"
    approved_by = str(ex.get("approved_by", "")).strip()
    if not approved_by:
        return None, f"{exemption_path.name}: approved_by missing"
    if not human_allowlist:
        return None, f"{exemption_path.name}: human_authority_allowlist is empty — gate cannot validate human identity"
    if approved_by not in human_allowlist:
        return (
            None,
            f"{exemption_path.name}: approved_by='{approved_by}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )
    approval_scope = str(ex.get("approval_scope", "")).strip()
    if not approval_scope:
        return None, f"{exemption_path.name}: approval_scope missing"
    ex_wrk = str(ex.get("wrk_id", "")).strip()
    if ex_wrk and ex_wrk != wrk_id:
        return None, f"{exemption_path.name}: wrk_id mismatch ({ex_wrk} != {wrk_id})"
    return approved_by, ""


def check_stage5_evidence_gate(
    wrk_id: str, assets_dir: Path, workspace_root: Path
) -> tuple[bool | None, str]:
    """Check Stage 5 evidence gate (canonical checker — Phase 1A).

    Returns:
        (True,  detail) — gate passes
        (False, detail) — predicate failure / Stage 5 incomplete
        (None,  detail) — infrastructure/path failure (exit 2 semantics)
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot validate Stage 5 evidence"

    # 1. Load activation config
    config, config_err = _load_stage5_config(workspace_root)
    if config is None:
        return None, config_err

    activation = str(config.get("activation", "disabled")).strip()
    human_allowlist = set(config.get("human_authority_allowlist") or [])

    # 2. If gate is disabled, no enforcement
    if activation == "disabled":
        return True, "stage5-gate-config.yaml: activation=disabled (no enforcement)"

    # TODO(WRK-1017 deferred): canary_plan_cross_review and canary_claim_close modes are
    # documented in stage5-gate-config.yaml but not yet implemented. Any non-disabled
    # activation currently falls through to full enforcement. Implement canary scoping
    # (restrict check to specific entrypoints) before enabling canary modes in production.

    evidence_dir = assets_dir / "evidence"

    # 3. Check migration exemption (before artifact checks)
    exemption_path = evidence_dir / "stage5-migration-exemption.yaml"
    if exemption_path.exists():
        approved_by, ex_err = _validate_exemption(exemption_path, wrk_id, human_allowlist)
        if ex_err:
            return False, ex_err
        return True, f"stage5-migration-exemption.yaml: legacy exemption approved by {approved_by}"

    # 4. Validate common-draft artifact
    common_draft_path = evidence_dir / "user-review-common-draft.yaml"
    if not common_draft_path.exists():
        return False, "user-review-common-draft.yaml missing — Stage 5 common-draft review required"
    try:
        cd = yaml.safe_load(common_draft_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"user-review-common-draft.yaml parse error: {exc}"
    if not isinstance(cd, dict):
        return None, "user-review-common-draft.yaml root is not a mapping"
    cd_wrk = str(cd.get("wrk_id", "")).strip()
    if cd_wrk and cd_wrk != wrk_id:
        return False, f"user-review-common-draft.yaml: wrk_id mismatch ({cd_wrk} != {wrk_id})"
    cd_decision = str(cd.get("approval_decision", "")).strip()
    if cd_decision != "approve_as_is":
        return (
            False,
            f"user-review-common-draft.yaml: approval_decision='{cd_decision}'; "
            f"Stage 6 requires approve_as_is",
        )
    cd_cycle = str(cd.get("review_cycle_id", "")).strip()

    # 5. Validate combined-plan artifact
    plan_draft_path = evidence_dir / "user-review-plan-draft.yaml"
    if not plan_draft_path.exists():
        return False, "user-review-plan-draft.yaml missing — Stage 5 combined-plan review required"
    try:
        pd = yaml.safe_load(plan_draft_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"user-review-plan-draft.yaml parse error: {exc}"
    if not isinstance(pd, dict):
        return None, "user-review-plan-draft.yaml root is not a mapping"
    pd_wrk = str(pd.get("wrk_id", "")).strip()
    if pd_wrk and pd_wrk != wrk_id:
        return False, f"user-review-plan-draft.yaml: wrk_id mismatch ({pd_wrk} != {wrk_id})"
    pd_decision = str(pd.get("approval_decision", "")).strip()
    if pd_decision != "approve_as_is":
        return (
            False,
            f"user-review-plan-draft.yaml: approval_decision='{pd_decision}'; "
            f"Stage 6 requires approve_as_is",
        )
    pd_cycle = str(pd.get("review_cycle_id", "")).strip()

    # 6. Cross-artifact review_cycle_id consistency
    if cd_cycle and pd_cycle and cd_cycle != pd_cycle:
        return (
            False,
            f"review_cycle_id mismatch: common-draft='{cd_cycle}' vs plan-draft='{pd_cycle}'; "
            f"artifacts from different review cycles may not satisfy the gate together",
        )

    return (
        True,
        f"stage5 gate passed: common-draft=approve_as_is, "
        f"plan-draft=approve_as_is, review_cycle_id='{pd_cycle or cd_cycle}'",
    )


def check_stage7_evidence_gate(
    wrk_id: str, assets_dir: Path, workspace_root: Path
) -> tuple[bool | None, str]:
    """Check Stage 7 evidence gate (User Review — Plan Final).

    Canonical artifact: evidence/plan-final-review.yaml
    Required fields:   confirmed_by (human in allowlist), confirmed_at, decision=passed

    Returns:
        (True,  detail) — gate passes
        (False, detail) — predicate failure
        (None,  detail) — infrastructure failure (exit 2 semantics)
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot validate Stage 7 evidence"

    config, config_err = _load_gate_config(workspace_root, "stage7-gate-config.yaml")
    if config is None:
        return None, config_err

    activation = str(config.get("activation", "disabled")).strip()
    human_allowlist = set(config.get("human_authority_allowlist") or [])

    if activation == "disabled":
        return True, "stage7-gate-config.yaml: activation=disabled (no enforcement)"

    evidence_dir = assets_dir / "evidence"

    # Migration exemption (escape hatch for in-flight WRKs that predate the gate)
    exemption_path = evidence_dir / "stage7-migration-exemption.yaml"
    if exemption_path.exists():
        approved_by, ex_err = _validate_exemption(exemption_path, wrk_id, human_allowlist)
        if ex_err:
            return False, ex_err
        return True, f"stage7-migration-exemption.yaml: legacy exemption approved by {approved_by}"

    artifact_path = evidence_dir / "plan-final-review.yaml"
    if not artifact_path.exists():
        return False, "plan-final-review.yaml missing — Stage 7 plan-final review required"

    data, yaml_err = load_yaml(artifact_path)
    if yaml_err:
        return None, f"plan-final-review.yaml parse error: {yaml_err}"
    assert data is not None

    artifact_wrk = str(data.get("wrk_id", "")).strip()
    if artifact_wrk and artifact_wrk != wrk_id:
        return False, f"plan-final-review.yaml: wrk_id mismatch ({artifact_wrk} != {wrk_id})"

    confirmed_by = str(data.get("confirmed_by", "")).strip()
    if not confirmed_by:
        return False, "plan-final-review.yaml: confirmed_by missing"
    if not human_allowlist:
        return False, "stage7-gate-config.yaml: human_authority_allowlist is empty — gate cannot validate human identity"
    if confirmed_by not in human_allowlist:
        return (
            False,
            f"plan-final-review.yaml: confirmed_by='{confirmed_by}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )

    confirmed_at = str(data.get("confirmed_at", "")).strip()
    if not confirmed_at:
        return False, "plan-final-review.yaml: confirmed_at missing"

    decision = str(data.get("decision", "")).strip().lower()
    if decision != "passed":
        return (
            False,
            f"plan-final-review.yaml: decision='{decision}'; Stage 8+ requires decision=passed",
        )

    return (
        True,
        f"stage7 gate passed: confirmed_by={confirmed_by}, confirmed_at={confirmed_at}, "
        f"decision={decision}",
    )


def check_stage17_evidence_gate(
    wrk_id: str, assets_dir: Path, workspace_root: Path
) -> tuple[bool | None, str]:
    """Check Stage 17 evidence gate (User Review — Implementation).

    Canonical artifact: evidence/user-review-close.yaml
    Required fields:   reviewer (human in allowlist), confirmed_at|reviewed_at,
                       decision in {approved, accepted, passed}

    Returns:
        (True,  detail) — gate passes
        (False, detail) — predicate failure
        (None,  detail) — infrastructure failure (exit 2 semantics)
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot validate Stage 17 evidence"

    config, config_err = _load_gate_config(workspace_root, "stage17-gate-config.yaml")
    if config is None:
        return None, config_err

    activation = str(config.get("activation", "disabled")).strip()
    human_allowlist = set(config.get("human_authority_allowlist") or [])

    if activation == "disabled":
        return True, "stage17-gate-config.yaml: activation=disabled (no enforcement)"

    evidence_dir = assets_dir / "evidence"

    # Migration exemption
    exemption_path = evidence_dir / "stage17-migration-exemption.yaml"
    if exemption_path.exists():
        approved_by, ex_err = _validate_exemption(exemption_path, wrk_id, human_allowlist)
        if ex_err:
            return False, ex_err
        return True, f"stage17-migration-exemption.yaml: legacy exemption approved by {approved_by}"

    artifact_path = evidence_dir / "user-review-close.yaml"
    if not artifact_path.exists():
        return False, "user-review-close.yaml missing — Stage 17 implementation review required"

    data, yaml_err = load_yaml(artifact_path)
    if yaml_err:
        return None, f"user-review-close.yaml parse error: {yaml_err}"
    assert data is not None

    artifact_wrk = str(data.get("wrk_id", "")).strip()
    if artifact_wrk and artifact_wrk != wrk_id:
        return False, f"user-review-close.yaml: wrk_id mismatch ({artifact_wrk} != {wrk_id})"

    reviewer = str(data.get("reviewer", "")).strip()
    if not reviewer:
        return False, "user-review-close.yaml: reviewer missing"
    if not human_allowlist:
        return False, "stage17-gate-config.yaml: human_authority_allowlist is empty — gate cannot validate human identity"
    if reviewer not in human_allowlist:
        return (
            False,
            f"user-review-close.yaml: reviewer='{reviewer}' not in "
            f"human_authority_allowlist; agent identities are not permitted",
        )

    # Accept either confirmed_at (new) or reviewed_at (legacy soft-gate field name)
    confirmed_at = (
        str(data.get("confirmed_at", "")).strip()
        or str(data.get("reviewed_at", "")).strip()
    )
    if not confirmed_at:
        return False, "user-review-close.yaml: confirmed_at (or reviewed_at) missing"

    decision = str(data.get("decision", "")).strip().lower()
    if decision not in {"approved", "accepted", "passed"}:
        return (
            False,
            f"user-review-close.yaml: decision='{decision}'; must be approved|accepted|passed",
        )

    return (
        True,
        f"stage17 gate passed: reviewer={reviewer}, confirmed_at={confirmed_at}, "
        f"decision={decision}",
    )


def _parse_iso_timestamp(value: str) -> float | None:
    """Parse an ISO-8601 timestamp string to a POSIX epoch float.

    All timestamps in work-queue artifacts are UTC.  Formats that include an
    explicit UTC indicator (Z or +00:00) are parsed as UTC-aware datetimes.
    Formats without a UTC indicator are also assumed UTC (not local time) to
    avoid DST-day false positives on machines in non-UTC timezones.

    Returns None if the value cannot be parsed or is date-only.
    """
    import datetime

    value = value.strip()
    if not value:
        return None
    # date-only values have no time component — skip them (not a valid timestamp)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return None
    # Try multiple formats (including space-separator from YAML datetime auto-parse).
    # All formats are treated as UTC regardless of explicit indicator, because all
    # work-queue timestamps are UTC by convention.
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f+00:00",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S+00:00",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            dt = datetime.datetime.strptime(value, fmt).replace(
                tzinfo=datetime.timezone.utc
            )
            return dt.timestamp()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Gap 1 — Approval ordering
# ---------------------------------------------------------------------------


def check_approval_ordering(assets_dir: Path, phase: str = "close") -> tuple[bool | None, str]:
    """Assert chronological ordering of approval timestamps across lifecycle stages.

    Checks:
        plan-final-review.yaml confirmed_at  <  claim-evidence.yaml claimed_at
        claim-evidence.yaml claimed_at       <  execute.yaml executed_at          (close only)
        execute.yaml executed_at             <  user-review-close.yaml confirmed_at (close only)

    Returns:
        (True,  detail) — ordering correct or not enough data to compare
        (False, detail) — ordering violation detected
        (None,  detail) — infrastructure/parse failure
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot check approval ordering"

    evidence_dir = assets_dir / "evidence"

    def _read_ts(filepath: Path, *fields: str) -> tuple[float | None, str]:
        if not filepath.exists():
            return None, ""
        data, err = load_yaml(filepath)
        if err or data is None:
            return None, f"parse error: {err}"
        for field in fields:
            val = str(data.get(field, "")).strip()
            if val:
                ts = _parse_iso_timestamp(val)
                if ts is not None:
                    return ts, val
        return None, ""

    plan_final_path = evidence_dir / "plan-final-review.yaml"
    claim_path = assets_dir / "evidence" / "claim-evidence.yaml"
    if not claim_path.exists():
        claim_path = assets_dir / "claim.yaml"
    execute_path = evidence_dir / "execute.yaml"
    close_path = evidence_dir / "user-review-close.yaml"

    plan_ts, plan_val = _read_ts(plan_final_path, "confirmed_at")
    claim_ts, claim_val = _read_ts(claim_path, "claimed_at", "confirmed_at")
    execute_ts, execute_val = _read_ts(execute_path, "executed_at", "completed_at")
    close_ts, close_val = _read_ts(close_path, "confirmed_at", "reviewed_at")

    comparisons = []
    if phase == "claim":
        comparisons = [
            (plan_ts, plan_val, "plan-final-review.confirmed_at", claim_ts, claim_val, "claim-evidence.claimed_at"),
        ]
    else:
        comparisons = [
            (plan_ts, plan_val, "plan-final-review.confirmed_at", claim_ts, claim_val, "claim-evidence.claimed_at"),
            (claim_ts, claim_val, "claim-evidence.claimed_at", execute_ts, execute_val, "execute.executed_at"),
            (execute_ts, execute_val, "execute.executed_at", close_ts, close_val, "user-review-close.confirmed_at"),
        ]

    for earlier_ts, earlier_val, earlier_name, later_ts, later_val, later_name in comparisons:
        if earlier_ts is None or later_ts is None:
            continue
        if earlier_ts >= later_ts:
            return (
                False,
                f"timestamp ordering violation: {earlier_name} ({earlier_val}) >= {later_name} ({later_val})",
            )

    return True, f"approval ordering OK (phase={phase})"


# ---------------------------------------------------------------------------
# Gap 2 — Midnight UTC sentinel detection
# ---------------------------------------------------------------------------


def check_midnight_utc_sentinel(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when any approval artifact has a T00:00:00Z sentinel timestamp.

    Checks: user-review-plan-draft.yaml, plan-final-review.yaml, user-review-close.yaml
    Fields: reviewed_at, confirmed_at
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot check midnight UTC sentinel"

    evidence_dir = assets_dir / "evidence"
    sentinel_pattern = re.compile(r"T00:00:00(Z|\+00:00)$")
    check_files = [
        evidence_dir / "user-review-plan-draft.yaml",
        evidence_dir / "plan-final-review.yaml",
        evidence_dir / "user-review-close.yaml",
    ]
    for filepath in check_files:
        if not filepath.exists():
            continue
        data, err = load_yaml(filepath)
        if err or data is None:
            continue
        for field in ("reviewed_at", "confirmed_at"):
            val = str(data.get(field, "")).strip()
            if val and sentinel_pattern.search(val):
                return False, f"midnight UTC sentinel detected in {filepath.name}.{field}: {val}"

    return True, "no midnight UTC sentinel found"


# ---------------------------------------------------------------------------
# Gap 3 — (removed: browser-open elapsed time — WRK-5107 HTML purge)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Gap 4 — Codex keyword in cross-review artifacts
# ---------------------------------------------------------------------------


def check_codex_keyword_in_review(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when 'codex' is absent from all cross-review artifacts.

    Looks for review files in assets_dir and assets_dir/evidence/.
    """
    evidence_dir = assets_dir / "evidence"
    candidate_patterns = [
        "review-synthesis.md",
        "cross-review.yaml",
        "cross-review-impl.md",
    ]
    review_files: list[Path] = []
    for pattern in candidate_patterns:
        for search_dir in (assets_dir, evidence_dir):
            p = search_dir / pattern
            if p.exists():
                review_files.append(p)
    # Also pick up any cross-review-*.md files
    for search_dir in (assets_dir, evidence_dir):
        if search_dir.exists():
            for p in search_dir.glob("cross-review-*.md"):
                if p not in review_files:
                    review_files.append(p)

    if not review_files:
        return True, "no review files found — skip codex keyword check (handled by cross-review gate)"

    codex_found = False
    for rf in review_files:
        try:
            content = rf.read_text(encoding="utf-8")
        except Exception:
            continue
        if re.search(r"codex", content, re.IGNORECASE):
            codex_found = True
            break

    # Also check cross-review.yaml reviewer field
    if not codex_found:
        cr_yaml = evidence_dir / "cross-review.yaml"
        if not cr_yaml.exists():
            cr_yaml = assets_dir / "cross-review.yaml"
        if cr_yaml.exists() and yaml is not None:
            data, _ = load_yaml(cr_yaml)
            if data:
                reviewer = str(data.get("reviewer", "")).strip().lower()
                if reviewer and reviewer != "claude" and "codex" not in reviewer:
                    pass  # reviewer present but not claude-only — might be ok
                if reviewer == "claude":
                    return False, "cross-review.yaml: reviewer=claude only (no codex)"

    if not codex_found:
        return False, "cross-review artifacts present but none mention 'codex'"

    return True, f"codex keyword found in review artifacts ({len(review_files)} file(s) checked)"


# ---------------------------------------------------------------------------
# Gap 5 — Sentinel values in activation / claim artifacts
# ---------------------------------------------------------------------------


def check_sentinel_values(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when sentinel placeholder values are present in activation or claim artifacts."""
    if yaml is None:
        return None, "PyYAML unavailable — cannot check sentinel values"

    errors: list[str] = []

    # Check activation.yaml
    activation_path = assets_dir / "evidence" / "activation.yaml"
    if activation_path.exists():
        data, err = load_yaml(activation_path)
        if data and not err:
            if str(data.get("session_id", "")).strip() == "unknown":
                errors.append("activation.yaml: session_id='unknown'")
            if str(data.get("orchestrator_agent", "")).strip() == "unknown":
                errors.append("activation.yaml: orchestrator_agent='unknown'")

    # Check claim-evidence.yaml (canonical path)
    claim_path = assets_dir / "evidence" / "claim-evidence.yaml"
    if not claim_path.exists():
        claim_path = assets_dir / "claim.yaml"
    if claim_path.exists():
        data, err = load_yaml(claim_path)
        if data and not err:
            if str(data.get("best_fit_provider", "")).strip() == "unknown":
                errors.append(f"{claim_path.name}: best_fit_provider='unknown'")
            if str(data.get("session_owner", "")).strip() == "unknown":
                errors.append(f"{claim_path.name}: session_owner='unknown'")
            route = str(data.get("route", "")).strip()
            if route == "":
                errors.append(f"{claim_path.name}: route='' (empty)")
            qs = data.get("quota_snapshot") or {}
            if isinstance(qs, dict):
                qs_status = str(qs.get("status", "")).strip().lower()
                pct = qs.get("pct_remaining")
                if qs_status == "available" and pct is None:
                    errors.append(f"{claim_path.name}: quota_snapshot.pct_remaining=null when status=available")

    if errors:
        return False, "; ".join(errors)
    return True, "no sentinel values found"


# ---------------------------------------------------------------------------
# Gap 6 — Publish commit uniqueness
# ---------------------------------------------------------------------------


def check_publish_commit_uniqueness(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when all three publish stages share the same commit hash (placeholder)."""
    if yaml is None:
        return None, "PyYAML unavailable — cannot check publish commit uniqueness"

    publish_file = evidence_file(assets_dir, "user-review-publish.yaml", [])
    if publish_file is None:
        return True, "user-review-publish.yaml absent — skip commit uniqueness check"

    data, err = load_yaml(publish_file)
    if err or data is None:
        return None, f"could not parse user-review-publish.yaml: {err}"

    events = data.get("events") or []
    if not isinstance(events, list):
        return True, "events not a list — skip commit uniqueness check"

    stage_commits: dict[str, str] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        stage = str(event.get("stage", "")).strip().lower()
        commit = str(event.get("commit", "")).strip()
        if stage and commit:
            stage_commits[stage] = commit

    pd_commit = stage_commits.get("plan_draft")
    pf_commit = stage_commits.get("plan_final")
    cr_commit = stage_commits.get("close_review")

    all_commits = [c for c in (pd_commit, pf_commit, cr_commit) if c]
    if len(all_commits) < 2:
        return True, "insufficient commit data — skip uniqueness check"

    if pd_commit and pf_commit and cr_commit and pd_commit == pf_commit == cr_commit:
        return False, f"all three publish stages share commit {pd_commit!r} (likely placeholder)"

    if pd_commit and pf_commit and pd_commit == pf_commit:
        return None, f"plan_draft and plan_final share commit {pd_commit!r} — possible placeholder (WARN)"

    return True, f"publish commits appear unique across stages"


# ---------------------------------------------------------------------------
# Gap 7 — Stage evidence paths exist on disk
# ---------------------------------------------------------------------------


def check_stage_evidence_paths(assets_dir: Path, workspace_root: Path) -> tuple[bool | None, str]:
    """FAIL when stage-evidence.yaml references a path that does not exist on disk."""
    if yaml is None:
        return None, "PyYAML unavailable — cannot check stage evidence paths"

    # Find stage-evidence.yaml in evidence/ subdir
    se_path = assets_dir / "evidence" / "stage-evidence.yaml"
    if not se_path.exists():
        return True, "stage-evidence.yaml absent — skip path existence check"

    data, err = load_yaml(se_path)
    if err or data is None:
        return None, f"could not parse stage-evidence.yaml: {err}"

    stages = data.get("stages") or []
    if not isinstance(stages, list):
        return True, "stages not a list — skip"

    for idx, row in enumerate(stages, start=1):
        if not isinstance(row, dict):
            continue
        ev_ref = str(row.get("evidence", "")).strip()
        if not ev_ref or ev_ref.lower() in {"n/a", "none", "-", ""}:
            continue
        # Only check if it looks like a file path (contains / or .)
        if "/" not in ev_ref and "." not in ev_ref:
            continue
        candidate = abs_path(workspace_root, ev_ref)
        if not candidate.exists():
            # Queue markdown files (pending/working/done/WRK-*.md) may have moved to
            # archive/ or done/ after the WRK was closed — check there before failing.
            fname = candidate.name
            queue_root = workspace_root / ".claude" / "work-queue"
            archive_matches = list((queue_root / "archive").rglob(fname))
            done_matches = list((queue_root / "done").rglob(fname))
            if archive_matches or done_matches:
                continue  # found in archive/done — path stale but not fabricated
            return False, f"stage-evidence.yaml: stage[{idx}] evidence path not found: {ev_ref}"

    return True, "all stage evidence paths verified"


# ---------------------------------------------------------------------------
# Gap 8 — Done+pending contradiction
# ---------------------------------------------------------------------------


def check_done_pending_contradiction(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when a stage marked 'done' has a comment containing 'pending', 'not started', or 'TBD'."""
    if yaml is None:
        return None, "PyYAML unavailable — cannot check done/pending contradiction"

    se_path = assets_dir / "evidence" / "stage-evidence.yaml"
    if not se_path.exists():
        return True, "stage-evidence.yaml absent — skip done/pending check"

    data, err = load_yaml(se_path)
    if err or data is None:
        return None, f"could not parse stage-evidence.yaml: {err}"

    stages = data.get("stages") or []
    contradiction_pattern = re.compile(r"\b(pending|not started|TBD)\b", re.IGNORECASE)

    for idx, row in enumerate(stages, start=1):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).strip().lower()
        if status != "done":
            continue
        comment = str(row.get("comment", "") or row.get("notes", "") or "").strip()
        if comment and contradiction_pattern.search(comment):
            return (
                False,
                f"stage-evidence.yaml: stage[{idx}] (order={row.get('order', '?')}) "
                f"status=done but comment contains contradiction: {comment!r}",
            )

    return True, "no done/pending contradictions found"


# ---------------------------------------------------------------------------
# Gap 9 — (removed: plan publish predates approval — WRK-5107 HTML purge)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Gap 10 — Workstation contract (strict variant for close phase)
# ---------------------------------------------------------------------------


def check_workstation_contract_strict(front: str) -> tuple[bool | None, str]:
    """FAIL (strict) when plan_workstations or execution_workstations are absent.

    Used as a hard gate in the close phase (complements the existing soft gate in run_checks).
    """
    missing = []
    if not has_nonempty_field(front, "plan_workstations"):
        missing.append("plan_workstations")
    if not has_nonempty_field(front, "execution_workstations"):
        missing.append("execution_workstations")
    if missing:
        return False, f"workstation contract fields missing in WRK frontmatter: {missing}"
    return True, "workstation contract fields present"


# ---------------------------------------------------------------------------
# Gap 11 — Reclaim gate n/a
# ---------------------------------------------------------------------------


def check_reclaim_gate_na(assets_dir: Path) -> tuple[bool | None, str]:
    """Validate Stage 18 reclaim n/a handling.

    - Stage 18 status n/a AND no reclaim.yaml → WARN (expected, no reclaim triggered)
    - reclaim log exists but reclaim.yaml absent → WARN
    - reclaim.yaml present → defer to existing check_reclaim_gate
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot check reclaim gate n/a"

    reclaim_yaml = assets_dir / "evidence" / "reclaim.yaml"

    # Check stage-evidence.yaml for Stage 18 status
    se_path = assets_dir / "evidence" / "stage-evidence.yaml"
    stage18_na = False
    if se_path.exists():
        data, _ = load_yaml(se_path)
        if data:
            stages = data.get("stages") or []
            for row in stages:
                if isinstance(row, dict) and row.get("order") == 18:
                    if str(row.get("status", "")).strip().lower() == "n/a":
                        stage18_na = True
                    break

    if stage18_na and not reclaim_yaml.exists():
        return None, "n/a: Stage 18 is n/a and no reclaim log exists"

    # Stage 18 n/a with placeholder reclaim.yaml (status:n/a) — accept as WARN
    if stage18_na and reclaim_yaml.exists():
        data, _ = load_yaml(reclaim_yaml)
        if data and str(data.get("status", "")).strip().lower() == "n/a":
            return None, "n/a: Stage 18 is n/a; reclaim.yaml is placeholder"

    # Check for reclaim log without reclaim.yaml
    if not reclaim_yaml.exists():
        # Look for any reclaim log file
        reclaim_log = assets_dir / "evidence" / "reclaim-log.yaml"
        if reclaim_log.exists():
            return None, "reclaim log exists but reclaim.yaml absent — WARN"
        return None, "reclaim.yaml absent (no reclaim triggered — WARN)"

    # Defer to existing gate logic
    return check_reclaim_gate(assets_dir)


# ---------------------------------------------------------------------------
# Gap 12 — Claim artifact path (3-state)
# ---------------------------------------------------------------------------


def check_claim_artifact_path(assets_dir: Path) -> tuple[bool | None, str]:
    """3-state check for claim artifact location.

    PASS:  assets_dir/evidence/claim-evidence.yaml exists (canonical)
    WARN:  assets_dir/evidence/claim.yaml exists (legacy path)
    FAIL:  neither exists
    """
    canonical = assets_dir / "evidence" / "claim-evidence.yaml"
    if canonical.exists():
        return True, f"canonical claim artifact found: {canonical.name}"

    legacy = assets_dir / "evidence" / "claim.yaml"
    if legacy.exists():
        return None, f"legacy claim path: {legacy.name} (should be claim-evidence.yaml)"

    return False, "no claim artifact found (expected evidence/claim-evidence.yaml)"


# ---------------------------------------------------------------------------
# Gap 13 — ISO datetime with time component
# ---------------------------------------------------------------------------


def check_iso_datetime_with_time(assets_dir: Path) -> tuple[bool | None, str]:
    """FAIL when any approval timestamp field contains a date-only value (YYYY-MM-DD)."""
    if yaml is None:
        return None, "PyYAML unavailable — cannot check ISO datetime format"

    date_only_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    timestamp_fields = {"reviewed_at", "confirmed_at", "confirmed"}

    evidence_dir = assets_dir / "evidence"
    if not evidence_dir.exists():
        return True, "evidence/ absent — skip ISO datetime check"

    for yaml_file in evidence_dir.glob("*.yaml"):
        data, err = load_yaml(yaml_file)
        if err or data is None:
            continue
        for field in timestamp_fields:
            val = str(data.get(field, "")).strip()
            if val and date_only_pattern.match(val):
                return (
                    False,
                    f"{yaml_file.name}.{field}: date-only value {val!r} — time component required",
                )

    return True, "all timestamp fields have time components"


# ---------------------------------------------------------------------------
# Gap 14 — Stage 1 capture gate
# ---------------------------------------------------------------------------


def check_stage1_capture_gate(
    assets_dir: Path, human_allowlist: set[str]
) -> tuple[bool | None, str]:
    """Check user-review-capture.yaml for Stage 1 scope approval.

    Route A bypass: if n/a: true and n/a_reason non-empty → PASS.
    """
    if yaml is None:
        return None, "PyYAML unavailable — cannot check stage1 capture gate"

    capture_file = assets_dir / "evidence" / "user-review-capture.yaml"
    if not capture_file.exists():
        return False, "user-review-capture.yaml missing"

    data, err = load_yaml(capture_file)
    if err or data is None:
        return None, f"could not parse user-review-capture.yaml: {err}"

    # Route A n/a bypass
    if data.get("n/a") is True or data.get("na") is True:
        na_reason = str(data.get("n/a_reason", data.get("na_reason", ""))).strip()
        if na_reason:
            return True, f"user-review-capture.yaml: n/a bypass — {na_reason}"
        return False, "user-review-capture.yaml: n/a=true but n/a_reason missing"

    # scope_approved check
    if data.get("scope_approved") is not True:
        return False, f"user-review-capture.yaml: scope_approved must be true (found {data.get('scope_approved')!r})"

    # confirmed_at check
    confirmed_at = str(data.get("confirmed_at", "")).strip()
    if not confirmed_at:
        return False, "user-review-capture.yaml: confirmed_at missing"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", confirmed_at):
        return False, f"user-review-capture.yaml: confirmed_at is date-only {confirmed_at!r} — time required"

    # reviewer allowlist check
    reviewer = str(data.get("reviewer", "")).strip()
    if not reviewer:
        return False, "user-review-capture.yaml: reviewer missing"
    if human_allowlist and reviewer not in human_allowlist:
        return (
            False,
            f"user-review-capture.yaml: reviewer='{reviewer}' not in human_authority_allowlist",
        )

    return True, f"stage1 capture gate passed: reviewer={reviewer}, confirmed_at={confirmed_at}"


def check_resource_intelligence_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Check resource intelligence evidence with canonical + legacy compatibility."""
    ri_file = evidence_file(assets_dir, "resource-intelligence.yaml", ["resource-intelligence-summary.md"])
    if ri_file is None:
        return None, "resource-intelligence evidence absent (legacy item — WARN)"

    if ri_file.suffix.lower() == ".yaml":
        data, yaml_err = load_yaml(ri_file)
        if yaml_err:
            return None, f"could not parse {ri_file.name}: {yaml_err}"
        assert data is not None
        completion = str(data.get("completion_status", "")).strip().lower()
        top_p1 = data.get("top_p1_gaps") or []
        if not isinstance(top_p1, list):
            return False, "resource-intelligence.yaml: top_p1_gaps must be a list"
        skills = data.get("skills") or {}
        core_used = skills.get("core_used") or []
        if not isinstance(core_used, list):
            return False, "resource-intelligence.yaml: skills.core_used must be a list"
        if len(core_used) < 3:
            return False, "resource-intelligence.yaml: skills.core_used must include at least 3 core skills"
        if completion == "continue_to_planning" and len(top_p1) > 0:
            return False, "resource-intelligence.yaml: continue_to_planning requires empty top_p1_gaps"
        if completion == "pause_and_revise" and len(top_p1) == 0:
            return False, "resource-intelligence.yaml: pause_and_revise requires one or more top_p1_gaps"
        if completion not in {"continue_to_planning", "pause_and_revise", "complete", "done"}:
            return False, "resource-intelligence.yaml: invalid completion_status"
        return True, f"{ri_file.name}: completion_status={completion}, p1_count={len(top_p1)}, core_skills={len(core_used)}"

    # Legacy markdown summary check
    content = strip_code_fences(ri_file.read_text(encoding="utf-8"))
    user_decision = re.search(r"^user_decision:\s+(.+)$", content, re.MULTILINE)
    if not user_decision:
        return None, f"{ri_file.name}: user_decision missing (legacy summary — WARN)"
    return True, f"{ri_file.name}: legacy summary present"


def check_future_work_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Check future-work evidence for follow-up WRKs or no-follow-ups rationale.

    Returns:
        (True,  detail) — gate OK
        (False, detail) — gate FAIL (file present but empty/invalid)
        (None,  detail) — WARN only (file absent — legacy item)
    """
    fw_file = evidence_file(assets_dir, "future-work.yaml", ["future-work-recommendations.md"])
    if fw_file is None:
        return None, "future-work evidence absent (legacy item — WARN)"
    if fw_file.suffix.lower() == ".yaml":
        data, yaml_err = load_yaml(fw_file)
        if yaml_err:
            return None, f"could not parse {fw_file.name}: {yaml_err}"
        assert data is not None
        recs = data.get("recommendations") or []
        if not isinstance(recs, list):
            return False, f"{fw_file.name}: recommendations must be a list"
        no_followups = str(data.get("no_follow_ups_rationale", "")).strip()
        if recs:
            missing_required_wrks = []
            for idx, rec in enumerate(recs, start=1):
                if rec is None or isinstance(rec, (int, float)):
                    return False, f"{fw_file.name}: recommendations[{idx}] must be a dict or non-empty string"
                if isinstance(rec, str):
                    if not rec.strip():
                        return False, f"{fw_file.name}: recommendations[{idx}] must be a dict or non-empty string"
                    continue  # bare string recommendation — accepted
                if not isinstance(rec, dict):
                    return False, f"{fw_file.name}: recommendations[{idx}] must be a dict or non-empty string"
                if rec.get("required_for_signoff") and not rec.get("wrk_id"):
                    missing_required_wrks.append(idx)
                disposition = str(rec.get("disposition", "")).strip().lower()
                if disposition not in {"existing-updated", "spun-off-new"}:
                    return False, (
                        f"{fw_file.name}: recommendations[{idx}] disposition must be "
                        "existing-updated|spun-off-new"
                    )
                if not str(rec.get("status", "")).strip():
                    return False, f"{fw_file.name}: recommendations[{idx}] status missing"
                captured = rec.get("captured")
                if captured is not True:
                    return False, f"{fw_file.name}: recommendations[{idx}] captured must be true before close"
            if missing_required_wrks:
                return False, f"{fw_file.name}: required_for_signoff recommendations missing wrk_id at {missing_required_wrks}"
            return True, f"{fw_file.name}: recommendations={len(recs)}"
        if no_followups:
            return True, f"{fw_file.name}: no_follow_ups_rationale=present"
        return False, f"{fw_file.name}: empty recommendations and no_follow_ups_rationale missing"

    content = strip_code_fences(fw_file.read_text(encoding="utf-8"))
    # Exclude the wrk_id: metadata header line (self-reference) from the WRK ref search
    content_no_self = re.sub(r"^wrk_id:\s+WRK-\d+.*$", "", content, flags=re.MULTILINE)
    has_wrk_ref = bool(re.search(r"\bWRK-\d+\b", content_no_self))
    rationale_match = re.search(r"^no_follow_ups_rationale:\s+\S", content, re.MULTILINE)
    if has_wrk_ref or rationale_match:
        summary = "has_wrk_refs=true" if has_wrk_ref else "no_follow_ups_rationale=present"
        return True, f"{fw_file.name}: {summary}"
    return False, f"{fw_file.name}: present but lists no WRKs and no_follow_ups_rationale is empty"


def check_resource_intelligence_update_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Require post-work resource intelligence update before close."""
    update_file = evidence_file(assets_dir, "resource-intelligence-update.yaml", [])
    if update_file is None:
        return False, "resource-intelligence-update.yaml missing"
    data, yaml_err = load_yaml(update_file)
    if yaml_err:
        return False, f"could not parse {update_file.name}: {yaml_err}"
    assert data is not None
    additions = data.get("additions") or []
    if additions and not isinstance(additions, list):
        return False, f"{update_file.name}: additions must be a list"
    rationale = str(data.get("no_additions_rationale", "")).strip()
    if additions:
        return True, f"{update_file.name}: additions={len(additions)}"
    if rationale:
        return True, f"{update_file.name}: no_additions_rationale=present"
    return False, f"{update_file.name}: add additions[] or no_additions_rationale"


def check_user_review_close_gate(assets_dir: Path) -> tuple[bool, str]:
    """Require explicit user review artifact for close readiness."""
    review_file = evidence_file(assets_dir, "user-review-close.yaml", [])
    if review_file is None:
        return False, "user-review-close.yaml missing"
    data, yaml_err = load_yaml(review_file)
    if yaml_err:
        return False, f"could not parse {review_file.name}: {yaml_err}"
    assert data is not None
    missing = [
        key
        for key in ("reviewer", "reviewed_at", "decision")
        if not str(data.get(key, "")).strip()
    ]
    if missing:
        return False, f"{review_file.name}: missing fields: {missing}"
    decision = str(data.get("decision", "")).strip().lower()
    if decision not in {"approved", "accepted", "passed"}:
        return False, f"{review_file.name}: decision must be approved|accepted|passed"
    return True, f"{review_file.name}: decision={decision}"


# (removed: check_html_open_default_browser_gate — WRK-5107 HTML purge)
# (removed: check_user_review_publish_gate — WRK-5107 HTML purge)


def check_github_issue_gate(front: str) -> tuple[bool, str]:
    """Validate github_issue_ref in WRK frontmatter (regex only, no network).

    Accepts: https://github.com/<owner>/<repo>/issues/<number>
    Rejects: PR URLs, comment anchors, malformed strings, missing field.
    """
    ref = get_field(front, "github_issue_ref")
    if not ref:
        return False, "github_issue_ref missing from frontmatter"
    if not GITHUB_ISSUE_RE.match(ref):
        return False, f"github_issue_ref invalid (must be a GitHub issue URL): {ref}"
    return True, f"github_issue_ref OK: {ref}"


def check_activation_gate(assets_dir: Path, wrk_id: str) -> tuple[bool, str]:
    """Require explicit activation evidence (set-active-wrk + session init snapshot)."""
    activation_file = evidence_file(assets_dir, "activation.yaml", [])
    if activation_file is None:
        return False, "activation.yaml missing"
    data, yaml_err = load_yaml(activation_file)
    if yaml_err:
        return False, f"could not parse {activation_file.name}: {yaml_err}"
    assert data is not None
    if str(data.get("wrk_id", "")).strip() != wrk_id:
        return False, f"{activation_file.name}: wrk_id mismatch"
    if data.get("set_active_wrk") is not True:
        return False, f"{activation_file.name}: set_active_wrk must be true"
    if not str(data.get("session_id", "")).strip():
        return False, f"{activation_file.name}: session_id missing"
    if not str(data.get("orchestrator_agent", "")).strip():
        return False, f"{activation_file.name}: orchestrator_agent missing"
    return True, f"{activation_file.name}: activation evidence OK"


def strip_code_fences(content: str) -> str:
    """Remove fenced code blocks to prevent false-positive confirmation matches."""
    return re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.DOTALL)


def check_reclaim_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Check reclaim evidence when reclaim stage artifacts are present."""
    reclaim_file = evidence_file(assets_dir, "reclaim.yaml", [])
    if reclaim_file is None:
        return None, "reclaim.yaml absent (no reclaim triggered — WARN)"
    data, yaml_err = load_yaml(reclaim_file)
    if yaml_err:
        return False, f"could not parse {reclaim_file.name}: {yaml_err}"
    assert data is not None
    # Placeholder n/a reclaim (Stage 18 was n/a, file written as documentation)
    if str(data.get("status", "")).strip().lower() == "n/a":
        return None, "reclaim.yaml: status=n/a (Stage 18 not triggered — WARN)"
    decision = str(data.get("reclaim_decision", "")).strip().lower()
    if decision not in {"reclaim_and_resume", "pause_and_replan", "block"}:
        return False, f"{reclaim_file.name}: invalid reclaim_decision={decision or 'missing'}"
    if decision == "reclaim_and_resume" and not data.get("prior_claim_ref"):
        return False, f"{reclaim_file.name}: prior_claim_ref required for reclaim_and_resume"
    if decision == "block" and not data.get("block_reason"):
        return False, f"{reclaim_file.name}: block_reason required when reclaim_decision=block"
    return True, f"{reclaim_file.name}: reclaim_decision={decision}"


def check_execute_integrated_tests_gate(assets_dir: Path) -> tuple[bool, str]:
    """Require 3+ unique integrated/repo tests in execute evidence before close."""
    execute_file = evidence_file(assets_dir, "execute.yaml", ["execute-evidence.yaml"])
    if execute_file is None:
        return False, "execute evidence missing (required: evidence/execute.yaml)"
    data, yaml_err = load_yaml(execute_file)
    if yaml_err:
        return False, f"could not parse {execute_file.name}: {yaml_err}"
    assert data is not None

    tests = data.get("integrated_repo_tests")
    if not isinstance(tests, list):
        return False, f"{execute_file.name}: integrated_repo_tests must be a list"
    # Count unique test names to prevent duplicate padding
    unique_names = {str(t.get("name", "")).strip() for t in tests if isinstance(t, dict)}
    count = len(unique_names)
    if count < 3:
        return False, f"{execute_file.name}: integrated_repo_tests must have 3+ unique tests (found {count})"

    required_fields = ("name", "scope", "command", "result", "artifact_ref")
    for idx, test in enumerate(tests, start=1):
        if not isinstance(test, dict):
            return False, f"{execute_file.name}: integrated_repo_tests[{idx}] must be an object"
        missing = [field for field in required_fields if not str(test.get(field, "")).strip()]
        if missing:
            return False, f"{execute_file.name}: integrated_repo_tests[{idx}] missing fields: {missing}"
        scope = str(test.get("scope", "")).strip().lower()
        if scope not in {"integrated", "repo"}:
            return False, f"{execute_file.name}: integrated_repo_tests[{idx}] scope must be integrated|repo"
        result = str(test.get("result", "")).strip().lower()
        if result not in {"pass", "passed"}:
            return False, f"{execute_file.name}: integrated_repo_tests[{idx}] result must be pass|passed"

    return True, f"{execute_file.name}: integrated_repo_tests={count} (all passing)"


def check_plan_confirmation(plan_path: Path) -> tuple[bool, str]:
    """Check that plan-html-review-final.md contains a valid confirmation block."""
    if not plan_path.exists():
        return False, "plan artifact missing"
    content = strip_code_fences(plan_path.read_text(encoding="utf-8"))
    has_confirmed_by = bool(re.search(r"^confirmed_by:\s+[a-zA-Z0-9]", content, re.MULTILINE))
    has_confirmed_at = bool(re.search(r"^confirmed_at:\s+[0-9]", content, re.MULTILINE))
    decision_match = re.search(r"^decision:\s+(.+)$", content, re.MULTILINE)
    decision_val = decision_match.group(1).strip() if decision_match else None
    decision_ok = bool(decision_val and decision_val.lower().strip() == "passed")
    if has_confirmed_by and has_confirmed_at and decision_ok:
        return True, f"confirmed_by=present, confirmed_at=present, decision={decision_val}"
    missing = []
    if not has_confirmed_by:
        missing.append("confirmed_by")
    if not has_confirmed_at:
        missing.append("confirmed_at")
    if not decision_ok:
        missing.append(f"decision={decision_val or 'missing'} (need 'passed')")
    return False, "confirmation block incomplete — " + ", ".join(missing)


def check_stage_evidence_gate(front: str, workspace_root: Path, wrk_id: str, phase: str = "close") -> tuple[bool, str]:
    """Require a per-WRK stage evidence ledger for close readiness."""
    ref = get_field(front, "stage_evidence_ref")
    if not ref:
        return False, "stage_evidence_ref missing in WRK frontmatter"
    path = abs_path(workspace_root, ref)
    if not path.exists():
        return False, f"stage evidence file missing: {ref}"
    data, yaml_err = load_yaml(path)
    if yaml_err:
        return False, f"could not parse {path.name}: {yaml_err}"
    assert data is not None
    stages = data.get("stages") or []
    if not isinstance(stages, list):
        return False, f"{path.name}: stages must be a list"
    required_orders_legacy = set(range(1, 20))
    required_orders_current = set(range(1, 21))
    seen_orders = set()
    rows_by_order: dict[int, dict] = {}
    allowed_statuses = {"pending", "in_progress", "done", "n/a", "blocked"}
    for idx, row in enumerate(stages, start=1):
        if not isinstance(row, dict):
            return False, f"{path.name}: stages[{idx}] must be an object"
        order = row.get("order")
        if not isinstance(order, int):
            return False, f"{path.name}: stages[{idx}] order must be integer"
        if order in rows_by_order:
            return False, f"{path.name}: duplicate stage order {order}"
        seen_orders.add(order)
        if not str(row.get("stage", "")).strip():
            return False, f"{path.name}: stages[{idx}] stage missing"
        status = str(row.get("status", "")).strip().lower()
        if not status:
            return False, f"{path.name}: stages[{idx}] status missing"
        if status not in allowed_statuses:
            return False, f"{path.name}: stages[{idx}] invalid status {status!r}"
        # Evidence string is informational — stage ordering/status is the primary gate
        # Empty evidence is accepted (exit_stage.py auto-generator doesn't populate it)
        rows_by_order[order] = row
    if seen_orders == required_orders_current:
        expected_orders = required_orders_current
        preclose_orders = range(1, 19)  # 1..18 must be done|n/a before close
    elif seen_orders == required_orders_legacy:
        expected_orders = required_orders_legacy
        # Legacy 19-stage ledgers still require stage 17 (User Review - Implementation)
        # before close; stage 18 (Reclaim) remains conditional.
        preclose_orders = range(1, 18)  # 1..17 must be done|n/a before close
    else:
        missing_current = sorted(required_orders_current - seen_orders)
        missing_legacy = sorted(required_orders_legacy - seen_orders)
        if len(missing_current) <= len(missing_legacy):
            return False, f"{path.name}: missing stage orders {missing_current}"
        return False, f"{path.name}: missing stage orders {missing_legacy}"
    if str(data.get("wrk_id", "")).strip() not in {"", wrk_id}:
        return False, f"{path.name}: wrk_id mismatch"

    if phase == "close":
        # Close readiness requires all mandatory pre-close stages completed.
        for order in preclose_orders:
            status = str(rows_by_order[order].get("status", "")).strip().lower()
            if status not in {"done", "n/a"}:
                return False, f"{path.name}: stage order {order} must be done|n/a before close (found {status})"
    return True, f"{path.name}: stages={len(stages)}, contract={len(expected_orders)}-stage"


def write_gate_summary(wrk_id: str, assets_dir: Path, phase: str, gates: list[dict]) -> None:
    """Persist gate summary for auditability in assets evidence folder."""
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    summary_json = evidence_dir / "gate-evidence-summary.json"
    summary_md = evidence_dir / "gate-evidence-summary.md"
    serializable = []
    for gate in gates:
        ok = gate.get("ok")
        warn = gate.get("warn", False)
        if warn:
            status = "WARN"
        elif ok:
            status = "PASS"
        else:
            status = "FAIL"
        serializable.append(
            {
                "name": gate.get("name"),
                "status": status,
                "ok": bool(ok),
                "warn": bool(warn),
                "details": gate.get("details", ""),
            }
        )
    summary_payload = {
        "wrk_id": wrk_id,
        "phase": phase,
        "summary_file": str(summary_json.relative_to(assets_dir.parent.parent)),
        "gates": serializable,
    }
    summary_json.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    lines = [
        f"# Gate Evidence Summary ({wrk_id}, phase={phase})",
        "",
        "| Gate | Status | Details |",
        "|---|---|---|",
    ]
    for item in serializable:
        details = str(item["details"]).replace("|", "\\|")
        lines.append(f"| {item['name']} | {item['status']} | {details} |")
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def abs_path(workspace_root: Path, referenced: str) -> Path:
    candidate = Path(referenced)
    if candidate.is_absolute():
        return candidate
    if referenced.startswith("./") or referenced.startswith("../") or referenced.startswith("."):
        return (workspace_root / referenced).resolve()
    return (workspace_root / referenced).resolve()


def first_matching_file(directory: Path, names: list[str]) -> Path | None:
    for name in names:
        candidate = directory / name
        if candidate.exists():
            return candidate
    return None


def evidence_file(assets_dir: Path, canonical_name: str, legacy_names: list[str]) -> Path | None:
    canonical = assets_dir / "evidence" / canonical_name
    if canonical.exists():
        return canonical
    for legacy in legacy_names:
        candidate = assets_dir / legacy
        if candidate.exists():
            return candidate
    return None


def load_yaml(path: Path) -> tuple[dict | None, str | None]:
    if yaml is None:
        return None, "PyYAML unavailable"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, str(exc)
    if not isinstance(data, dict):
        return None, "YAML root is not a mapping"
    return data, None


def parse_gate_log(log_path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


LOG_GATE_SINCE = datetime(2026, 3, 9, tzinfo=timezone.utc)


def _check_legacy_discriminator(wrk_frontmatter: dict) -> tuple[bool | None, str]:
    """Two-tier legacy discriminator for check_agent_log_gate.

    Returns:
      (True, reason)  — skip gate (legacy or backfill)
      (False, reason) — enforce gate (new WRK, malformed, or boundary/post-cutoff)
      (None, "")      — discriminator not applicable (no wrk_frontmatter)
    """
    id_raw = str(wrk_frontmatter.get("id", "")).strip()
    if not id_raw.upper().startswith("WRK-"):
        return False, f"non-WRK-NNN id format: {id_raw!r}"
    suffix = id_raw[4:]
    try:
        id_num = int(suffix)
    except ValueError:
        return False, f"non-integer WRK id suffix: {suffix!r}"

    # Tier 1: numeric id < 658 → unconditional legacy skip
    if id_num < 658:
        return True, f"legacy WRK (id={id_num} < 658) — log gate skipped"

    # Tier 2: id >= 658 — check created_at against LOG_GATE_SINCE
    created_raw = str(wrk_frontmatter.get("created_at", "")).strip()
    if not created_raw:
        return False, f"id={id_num} >= 658 and created_at absent — gate enforced"
    try:
        # Normalize Z suffix for Python 3.8 fromisoformat compatibility
        normalized = created_raw.replace("Z", "+00:00")
        parsed_dt = datetime.fromisoformat(normalized)
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return False, f"id={id_num} >= 658 and created_at malformed ({created_raw!r}) — gate enforced"
    if parsed_dt < LOG_GATE_SINCE:
        return True, f"pre-cutoff backfill (id={id_num}, created_at={created_raw}) — log gate skipped"
    return False, f"id={id_num} >= 658, created_at={created_raw} >= cutoff — gate enforced"


def check_agent_log_gate(
    workspace_root: Path,
    wrk_id: str,
    phase: str,
    wrk_frontmatter: dict | None = None,
) -> tuple[bool, str]:
    # Apply legacy discriminator when frontmatter is provided
    if wrk_frontmatter is not None:
        skip, reason = _check_legacy_discriminator(wrk_frontmatter)
        if skip is True:
            return True, reason
        if skip is False:
            pass  # proceed to log check

    log_dir = workspace_root / ".claude" / "work-queue" / "logs"
    if not log_dir.exists():
        return False, "work-queue log directory missing"

    # Only require PRIOR-PHASE log entries (routing, plan, execute, cross-review).
    # Current-phase signals are intentionally excluded for two reasons:
    # 1. Terminal signals (verify_gate_evidence_pass, claim_evidence, close_item) are
    #    circular: they are written AFTER this function returns, so the gate could never
    #    pass on first invocation. (WRK-1017 P1 fix, Codex review round 1)
    # 2. Pre-phase signals (set_active_wrk, verify_gate_evidence_start) couple the
    #    validator to specific wrappers and break: (a) archive-item.sh which logs to
    #    WRK-*-archive.log not WRK-*-close.log, and (b) standalone/CI invocations that
    #    have no wrapper pre-log. (WRK-1017 revert of P2 over-fix, Codex review round 2)
    required_by_phase: dict[str, list[tuple[str, set[str]]]] = {
        "claim": [
            ("routing", {"work_wrapper_complete", "work_queue_skill"}),
            ("plan", {"plan_wrapper_complete", "plan_draft_complete"}),
        ],
        "close": [
            ("routing", {"work_wrapper_complete", "work_queue_skill"}),
            ("plan", {"plan_wrapper_complete", "plan_draft_complete"}),
            ("execute", {"execute_wrapper_complete", "tdd_eval"}),
            ("cross-review", {"review_wrapper_complete", "agent_cross_review"}),
        ],
        # archive phase: same requirements as close (close gate must have passed first)
        "archive": [
            ("routing", {"work_wrapper_complete", "work_queue_skill"}),
            ("plan", {"plan_wrapper_complete", "plan_draft_complete"}),
            ("execute", {"execute_wrapper_complete", "tdd_eval"}),
            ("cross-review", {"review_wrapper_complete", "agent_cross_review"}),
        ],
    }
    requirements = required_by_phase.get(phase, [])
    missing: list[str] = []
    matched: list[str] = []
    for stage, accepted_actions in requirements:
        log_path = log_dir / f"{wrk_id}-{stage}.log"
        if not log_path.exists():
            missing.append(f"{stage}:missing-log")
            continue
        entries = parse_gate_log(log_path)
        provider_entries = [e for e in entries if str(e.get("provider", "")).strip()]
        if not provider_entries:
            missing.append(f"{stage}:missing-provider")
            continue
        actions = {str(e.get("action", "")).strip() for e in provider_entries}
        if not (actions & accepted_actions):
            missing.append(f"{stage}:missing-actions={sorted(accepted_actions)}")
            continue
        matched.append(f"{stage}:{sorted(actions & accepted_actions)}")
    if missing:
        return False, " ; ".join(missing)
    return True, "matched " + ", ".join(matched)


def run_checks(wrk_id: str, phase: str = "close", workspace_root: Path | None = None) -> int:
    if workspace_root is None:
        workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    wrk_path = None
    for folder in ["pending", "working", "done"]:
        candidate = queue_dir / folder / f"{wrk_id}.md"
        if candidate.exists():
            wrk_path = candidate
            break
    if wrk_path is None:
        # Also search archive/ subdirectories (YYYY-MM/ and flat)
        for archive_candidate in (queue_dir / "archive").rglob(f"{wrk_id}.md"):
            wrk_path = archive_candidate
            break
    if wrk_path is None:
        print(f"✖ Work item {wrk_id} not found in pending/, working/, done/, or archive/", file=sys.stderr)
        return 2

    front = parse_frontmatter(wrk_path.read_text(encoding="utf-8"))
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(f"✖ Assets directory missing: {assets_dir}", file=sys.stderr)
        return 2

    plan_reviewed = parse_bool(get_field(front, "plan_reviewed"))
    plan_approved = parse_bool(get_field(front, "plan_approved"))
    plan_ref = get_field(front, "spec_ref")
    plan_path = abs_path(workspace_root, plan_ref) if plan_ref else assets_dir / "plan.md"

    review_file = first_matching_file(assets_dir, ["review.html", "review.md", "results.md", "review-results.md", "review-synthesis.md"])
    test_candidates = list(p for p in assets_dir.glob("*.md") if "test" in p.name.lower())
    legal_file = first_matching_file(assets_dir, ["legal-scan.md"])

    confirmation_ok, confirmation_details = check_plan_confirmation(plan_path)
    gates = []
    gates.append(
        {
            "name": "Plan gate",
            "ok": plan_reviewed and plan_approved and plan_path.exists() and confirmation_ok,
            "details": (
                f"reviewed={plan_reviewed}, approved={plan_approved}, "
                f"artifact={'missing' if not plan_path.exists() else plan_path.name}, "
                f"confirmation={confirmation_details}"
            ),
        }
    )
    gates.append(
        {
            "name": "Workstation contract gate",
            "ok": has_nonempty_field(front, "plan_workstations") and has_nonempty_field(front, "execution_workstations"),
            "details": (
                f"plan_workstations="
                f"{get_field(front, 'plan_workstations') or get_list_field(front, 'plan_workstations') or 'missing'}, "
                f"execution_workstations="
                f"{get_field(front, 'execution_workstations') or get_list_field(front, 'execution_workstations') or 'missing'}"
            ),
        }
    )
    if phase == "close":
        stage_ok, stage_details = check_stage_evidence_gate(front, workspace_root, wrk_id, phase=phase)
        gates.append({"name": "Stage evidence gate", "ok": stage_ok, "details": stage_details})
    ri_ok, ri_details = check_resource_intelligence_gate(assets_dir)
    gates.append({"name": "Resource-intelligence gate", "ok": bool(ri_ok), "details": ri_details})
    activation_ok, activation_details = check_activation_gate(assets_dir, wrk_id)
    gates.append({"name": "Activation gate", "ok": activation_ok, "details": activation_details})
    wrk_fm = {
        "id": get_field(front, "id") or "",
        "created_at": get_field(front, "created_at") or "",
    }
    # Agent log gate — optional when frontmatter has no multi-agent indicators
    _has_multi_agent = (
        has_nonempty_field(front, "agent_team")
        or has_nonempty_field(front, "multi_agent")
        or has_nonempty_field(front, "spawn_agents")
    )
    log_ok, log_details = check_agent_log_gate(workspace_root, wrk_id, phase, wrk_frontmatter=wrk_fm)
    if _has_multi_agent:
        gates.append({"name": "Agent log gate", "ok": log_ok, "details": log_details})
    else:
        gates.append({"name": "Agent log gate", "ok": log_ok or True, "warn": not log_ok, "details": log_details + " (optional — no multi-agent indicators)"})
    gh_ok, gh_details = check_github_issue_gate(front)
    gates.append({"name": "GitHub issue gate", "ok": gh_ok, "details": gh_details})
    gates.append(
        {"name": "Cross-review gate", "ok": bool(review_file), "details": f"artifact={'none' if not review_file else review_file}"}
    )
    if phase == "close":
        gates.append(
            {
                "name": "TDD gate",
                "ok": len(test_candidates) > 0,
                "details": f"test files={[p.name for p in test_candidates]}" if test_candidates else "none",
            }
        )
        execute_tests_ok, execute_tests_details = check_execute_integrated_tests_gate(assets_dir)
        gates.append({"name": "Integrated test gate", "ok": execute_tests_ok, "details": execute_tests_details})
    legal_notes = "none"
    legal_ok = False
    if legal_file:
        contents = legal_file.read_text(encoding="utf-8")
        match = re.search(r"^result:\s*(.+)$", contents, re.MULTILINE | re.IGNORECASE)
        legal_result = match.group(1).strip() if match else None
        legal_ok = bool(legal_result and "pass" in legal_result.lower())
        legal_notes = f"result={legal_result or 'missing'}"
    if phase == "close":
        gates.append({"name": "Legal gate", "ok": legal_ok, "details": f"artifact={legal_file if legal_file else 'missing'}, {legal_notes}"})

    # Claim gate — WARN for legacy items (no metadata_version), FAIL for hardened items
    claim_ok, claim_details = check_claim_gate(assets_dir)
    gates.append({"name": "Claim gate", "ok": bool(claim_ok), "warn": claim_ok is None, "details": claim_details})

    if phase == "close":
        fw_ok, fw_details = check_future_work_gate(assets_dir)
        gates.append({"name": "Future-work gate", "ok": bool(fw_ok), "details": fw_details})
        riu_ok, riu_details = check_resource_intelligence_update_gate(assets_dir)
        gates.append({"name": "Resource-intelligence update gate", "ok": bool(riu_ok), "details": riu_details})
        close_review_ok, close_review_details = check_user_review_close_gate(assets_dir)
        gates.append({"name": "User-review close gate", "ok": close_review_ok, "details": close_review_details})

    # Reclaim gate — WARN when absent (no reclaim triggered), FAIL when present but invalid
    reclaim_ok, reclaim_details = check_reclaim_gate(assets_dir)
    gates.append({"name": "Reclaim gate", "ok": reclaim_ok, "warn": reclaim_ok is None, "details": reclaim_details})

    # -----------------------------------------------------------------------
    # Hardening gates (WRK-1035 Phase 3) — loaded for both claim and close
    # -----------------------------------------------------------------------

    # Load human_allowlist from stage7-gate-config.yaml (same source as existing stage gates)
    _s7_config, _ = _load_gate_config(workspace_root, "stage7-gate-config.yaml")
    _human_allowlist: set[str] = set((_s7_config or {}).get("human_authority_allowlist") or [])

    # Gap 1 — Approval ordering (both phases)
    ord_ok, ord_details = check_approval_ordering(assets_dir, phase=phase)
    gates.append({"name": "Approval ordering gate", "ok": bool(ord_ok), "warn": ord_ok is None, "details": ord_details})

    # Gap 2 — Midnight UTC sentinel (both phases)
    midnight_ok, midnight_details = check_midnight_utc_sentinel(assets_dir)
    gates.append({"name": "Midnight UTC sentinel gate", "ok": bool(midnight_ok), "warn": midnight_ok is None, "details": midnight_details})

    # Gap 3 — (removed: browser open elapsed time — WRK-5107 HTML purge)

    # Gap 5 — Sentinel values (both phases)
    sentinel_ok, sentinel_details = check_sentinel_values(assets_dir)
    gates.append({"name": "Sentinel values gate", "ok": bool(sentinel_ok), "warn": sentinel_ok is None, "details": sentinel_details})

    # Gap 12 — Claim artifact path (both phases)
    cap_ok, cap_details = check_claim_artifact_path(assets_dir)
    gates.append({"name": "Claim artifact path gate", "ok": bool(cap_ok), "warn": cap_ok is None, "details": cap_details})

    # Gap 13 — ISO datetime with time component (both phases)
    iso_ok, iso_details = check_iso_datetime_with_time(assets_dir)
    gates.append({"name": "ISO datetime format gate", "ok": bool(iso_ok), "warn": iso_ok is None, "details": iso_details})

    if phase == "claim":
        # Gap 14 — Stage 1 capture gate (claim phase entry check)
        s1_ok, s1_details = check_stage1_capture_gate(assets_dir, _human_allowlist)
        gates.append({"name": "Stage1 capture gate", "ok": bool(s1_ok), "warn": s1_ok is None, "details": s1_details})

    if phase == "close":
        # Gap 4 — Codex keyword in cross-review artifacts
        codex_ok, codex_details = check_codex_keyword_in_review(assets_dir)
        gates.append({"name": "Codex keyword in review gate", "ok": bool(codex_ok), "warn": codex_ok is None, "details": codex_details})

        # Gap 6 — (removed: publish commit uniqueness — WRK-5107 HTML purge)

        # Gap 7 — Stage evidence paths exist on disk
        sep_ok, sep_details = check_stage_evidence_paths(assets_dir, workspace_root)
        gates.append({"name": "Stage evidence paths gate", "ok": bool(sep_ok), "warn": sep_ok is None, "details": sep_details})

        # Gap 8 — Done/pending contradiction
        dp_ok, dp_details = check_done_pending_contradiction(assets_dir)
        gates.append({"name": "Done/pending contradiction gate", "ok": bool(dp_ok), "warn": dp_ok is None, "details": dp_details})

        # Gap 9 — (removed: plan publish predates approval — WRK-5107 HTML purge)

        # Gap 10 — Workstation contract (strict)
        ws_ok, ws_details = check_workstation_contract_strict(front)
        gates.append({"name": "Workstation contract (strict) gate", "ok": bool(ws_ok), "warn": ws_ok is None, "details": ws_details})

        # Gap 11 — Reclaim gate n/a
        rna_ok, rna_details = check_reclaim_gate_na(assets_dir)
        gates.append({"name": "Reclaim n/a gate", "ok": bool(rna_ok), "warn": rna_ok is None, "details": rna_details})

    if phase == "archive":
        if check_archive_readiness is not None:
            ar_ok, ar_details = check_archive_readiness(assets_dir)
            gates.append({
                "name": "Archive readiness gate",
                "ok": ar_ok is True,
                "warn": ar_ok is None,
                "details": ar_details,
            })
        else:
            gates.append({
                "name": "Archive readiness gate",
                "ok": False,
                "warn": False,
                "details": "gate_checks_archive module not found",
            })

    success = True
    print(f"Gate evidence for {wrk_id} (phase={phase}, assets: {assets_dir}):")
    for gate in gates:
        is_warn = gate.get("warn", False)
        if is_warn:
            status = "WARN"
        elif gate["ok"]:
            status = "OK"
        else:
            status = "MISSING"
        print(f"  - {gate['name']}: {status} ({gate['details']})")
        if not gate["ok"] and not is_warn:
            success = False

    write_gate_summary(wrk_id, assets_dir, phase, gates)

    if not success:
        print("→ Gate evidence incomplete. Please collect the missing artifacts before claiming.", file=sys.stderr)
        return 1

    print("→ All orchestrator gates have documented evidence.")
    return 0


def _run_stage5_check(args: list[str]) -> int:
    """Handle --stage5-check <WRK-id> invocation from plan.sh / cross-review.sh.

    Exit codes:
        0 = Stage 5 gate passes (or disabled)
        1 = predicate failure (Stage 5 incomplete)
        2 = infrastructure/path failure
    """
    if len(args) < 1:
        print("Usage: verify-gate-evidence.py --stage5-check WRK-<id>", file=sys.stderr)
        return 2
    wrk_id = args[0]
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(
            f"✖ Stage 5 check: assets directory not found for {wrk_id}: {assets_dir}",
            file=sys.stderr,
        )
        return 2
    ok, detail = check_stage5_evidence_gate(wrk_id, assets_dir, workspace_root)
    if ok is None:
        print(f"✖ Stage 5 gate infrastructure failure for {wrk_id}: {detail}", file=sys.stderr)
        return 2
    if not ok:
        print(f"✖ Stage 5 gate predicate failure for {wrk_id}: {detail}", file=sys.stderr)
        return 1
    print(f"✔ Stage 5 gate passed for {wrk_id}: {detail}")
    return 0


def _run_stage7_check(args: list[str]) -> int:
    """Handle --stage7-check <WRK-id> invocation from claim-item.sh.

    Exit codes:
        0 = Stage 7 gate passes (or disabled)
        1 = predicate failure (plan-final review incomplete / not by human)
        2 = infrastructure/path failure
    """
    if len(args) < 1:
        print("Usage: verify-gate-evidence.py --stage7-check WRK-<id>", file=sys.stderr)
        return 2
    wrk_id = args[0]
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(
            f"✖ Stage 7 check: assets directory not found for {wrk_id}: {assets_dir}",
            file=sys.stderr,
        )
        return 2
    ok, detail = check_stage7_evidence_gate(wrk_id, assets_dir, workspace_root)
    if ok is None:
        print(f"✖ Stage 7 gate infrastructure failure for {wrk_id}: {detail}", file=sys.stderr)
        return 2
    if not ok:
        print(f"✖ Stage 7 gate predicate failure for {wrk_id}: {detail}", file=sys.stderr)
        return 1
    print(f"✔ Stage 7 gate passed for {wrk_id}: {detail}")
    return 0


def _run_stage17_check(args: list[str]) -> int:
    """Handle --stage17-check <WRK-id> invocation from close-item.sh.

    Exit codes:
        0 = Stage 17 gate passes (or disabled)
        1 = predicate failure (impl review incomplete / not by human)
        2 = infrastructure/path failure
    """
    if len(args) < 1:
        print("Usage: verify-gate-evidence.py --stage17-check WRK-<id>", file=sys.stderr)
        return 2
    wrk_id = args[0]
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(
            f"✖ Stage 17 check: assets directory not found for {wrk_id}: {assets_dir}",
            file=sys.stderr,
        )
        return 2
    ok, detail = check_stage17_evidence_gate(wrk_id, assets_dir, workspace_root)
    if ok is None:
        print(f"✖ Stage 17 gate infrastructure failure for {wrk_id}: {detail}", file=sys.stderr)
        return 2
    if not ok:
        print(f"✖ Stage 17 gate predicate failure for {wrk_id}: {detail}", file=sys.stderr)
        return 1
    print(f"✔ Stage 17 gate passed for {wrk_id}: {detail}")
    return 0


def _parse_gate_statuses(output: str) -> dict[str, str]:
    """Parse gate output lines into {gate_name: status} dict."""
    statuses: dict[str, str] = {}
    for line in output.splitlines():
        line = line.strip().lstrip("- ")
        if ": OK (" in line:
            name = line.split(":")[0].strip()
            statuses[name] = "OK"
        elif ": MISSING (" in line:
            name = line.split(":")[0].strip()
            statuses[name] = "MISSING"
        elif ": WARN (" in line:
            name = line.split(":")[0].strip()
            statuses[name] = "WARN"
    return statuses


def run_checks_with_retry(
    wrk_id: str,
    phase: str = "close",
    max_retries: int = 1,
    workspace_root: Path | None = None,
) -> tuple[int, int]:
    """Run gate checks with optional retry and diagnostic output.

    Returns (exit_code, attempt_count).
    Backoff schedule: 1s, 3s, 9s (3^i for i=0,1,2...).
    """
    import io
    import contextlib
    import time

    prev_statuses: dict[str, str] = {}

    for attempt in range(1, max_retries + 1):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run_checks(wrk_id, phase=phase, workspace_root=workspace_root)
        output = buf.getvalue()
        current_statuses = _parse_gate_statuses(output)

        if max_retries > 1:
            print(f"[verify-gate-evidence] attempt={attempt}/{max_retries}")

        # Show delta from previous attempt
        if prev_statuses and attempt > 1:
            for gate, status in current_statuses.items():
                prev = prev_statuses.get(gate)
                if prev and prev != status:
                    print(f"  delta: {gate}: {prev} -> {status}")

        # On failure, show only MISSING gates (not full output)
        if code != 0:
            missing = [g for g, s in current_statuses.items() if s == "MISSING"]
            if missing:
                print(f"  unmet gates: {missing}")
        else:
            # On success, print full output
            print(output, end="")

        if code == 0:
            return 0, attempt

        prev_statuses = current_statuses

        # Backoff before next attempt (not after last)
        if attempt < max_retries:
            delay = 3 ** (attempt - 1)  # 1, 3, 9
            time.sleep(delay)

    if max_retries > 1:
        missing = [g for g, s in prev_statuses.items() if s == "MISSING"]
        print(
            f"[verify-gate-evidence] FAILED after {max_retries}/{max_retries} attempts. "
            f"Unmet gates: {missing}",
            file=sys.stderr,
        )
    # Machine-parseable marker for callers (e.g. close-item.sh log signal)
    print(f"GATE_ATTEMPTS={max_retries}")

    return 1, max_retries


def run_checks_json(wrk_id: str, phase: str = "close") -> int:
    """D14 — JSON-mode gate check. Writes one JSON line to stdout; exit 0/1.

    Compatible with all --phase modes. Does not suppress other output;
    the JSON summary line is appended after normal output.
    """
    import io, contextlib
    # Capture normal stdout to avoid mixing with JSON
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run_checks(wrk_id, phase=phase)
    captured = buf.getvalue()
    # Rebuild gate list from captured output for JSON summary
    missing: list[str] = []
    warn: list[str] = []
    for line in captured.splitlines():
        if ": MISSING (" in line:
            name = line.strip().lstrip("- ").split(":")[0].strip()
            missing.append(name)
        elif ": WARN (" in line:
            name = line.strip().lstrip("- ").split(":")[0].strip()
            warn.append(name)
    result = {
        "wrk_id": wrk_id,
        "phase": phase,
        "pass": code == 0,
        "missing": missing,
        "warn": warn,
    }
    print(captured, end="")
    print(json.dumps(result))
    return code


def main() -> None:
    args = sys.argv[1:]
    # Stage 5 check mode (called by plan.sh, cross-review.sh, etc.)
    if args and args[0] == "--stage5-check":
        sys.exit(_run_stage5_check(args[1:]))
    if args and args[0] == "--stage7-check":
        sys.exit(_run_stage7_check(args[1:]))
    if args and args[0] == "--stage17-check":
        sys.exit(_run_stage17_check(args[1:]))

    # D14 — --json flag: stdout-only JSON output; compatible with --phase modes
    use_json = "--json" in args
    if use_json:
        args = [a for a in args if a != "--json"]

    # WRK-1160 — --retry N: retry with exponential backoff and diagnostics
    max_retries = 1
    if "--retry" in args:
        idx = args.index("--retry")
        if idx + 1 < len(args):
            try:
                max_retries = int(args[idx + 1])
            except ValueError:
                print("--retry requires an integer argument", file=sys.stderr)
                sys.exit(1)
            args = args[:idx] + args[idx + 2:]
        else:
            print("--retry requires an integer argument", file=sys.stderr)
            sys.exit(1)

    if len(args) not in {1, 3}:
        print("Usage: verify-gate-evidence.py WRK-<id> [--phase claim|close|archive] [--retry N] [--json]")
        sys.exit(1)
    wrk_id = args[0]
    phase = "close"
    if len(args) == 3:
        if args[1] != "--phase" or args[2] not in {"claim", "close", "archive"}:
            print("Usage: verify-gate-evidence.py WRK-<id> [--phase claim|close|archive] [--retry N] [--json]")
            sys.exit(1)
        phase = args[2]
    if use_json:
        code = run_checks_json(wrk_id, phase=phase)
    elif max_retries > 1:
        code, _attempts = run_checks_with_retry(wrk_id, phase=phase, max_retries=max_retries)
    else:
        code = run_checks(wrk_id, phase=phase)
    sys.exit(code)


if __name__ == "__main__":
    main()
