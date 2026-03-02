#!/usr/bin/env python3
"""Validate orchestrator gate evidence for a WRK item."""

import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import]
except Exception:
    yaml = None


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
        if completion not in {"continue_to_planning", "pause_and_revise"}:
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
                if not isinstance(rec, dict):
                    return False, f"{fw_file.name}: recommendations[{idx}] must be an object"
                if rec.get("required_for_signoff") and not rec.get("wrk_id"):
                    missing_required_wrks.append(idx)
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
    decision = str(data.get("reclaim_decision", "")).strip().lower()
    if decision not in {"reclaim_and_resume", "pause_and_replan", "block"}:
        return False, f"{reclaim_file.name}: invalid reclaim_decision={decision or 'missing'}"
    if decision == "reclaim_and_resume" and not data.get("prior_claim_ref"):
        return False, f"{reclaim_file.name}: prior_claim_ref required for reclaim_and_resume"
    if decision == "block" and not data.get("block_reason"):
        return False, f"{reclaim_file.name}: block_reason required when reclaim_decision=block"
    return True, f"{reclaim_file.name}: reclaim_decision={decision}"


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


def run_checks(wrk_id: str) -> int:
    workspace_root = Path(__file__).resolve().parents[2]
    queue_dir = workspace_root / ".claude" / "work-queue"
    wrk_path = None
    for folder in ["pending", "working", "done"]:
        candidate = queue_dir / folder / f"{wrk_id}.md"
        if candidate.exists():
            wrk_path = candidate
            break
    if wrk_path is None:
        print(f"✖ Work item {wrk_id} not found in pending/ or working/", file=sys.stderr)
        return 2

    front = parse_frontmatter(wrk_path.read_text(encoding="utf-8"))
    assets_dir = queue_dir / "assets" / wrk_id
    if not assets_dir.is_dir():
        print(f"✖ Assets directory missing: {assets_dir}", file=sys.stderr)
        return 2

    plan_reviewed = parse_bool(get_field(front, "plan_reviewed"))
    plan_approved = parse_bool(get_field(front, "plan_approved"))
    plan_ref = get_field(front, "plan_html_review_final_ref")
    plan_path = abs_path(workspace_root, plan_ref) if plan_ref else assets_dir / "plan-html-review-final.md"

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
                f"plan_workstations={get_field(front, 'plan_workstations') or 'missing'}, "
                f"execution_workstations={get_field(front, 'execution_workstations') or 'missing'}"
            ),
        }
    )
    ri_ok, ri_details = check_resource_intelligence_gate(assets_dir)
    gates.append({"name": "Resource-intelligence gate", "ok": ri_ok, "warn": ri_ok is None, "details": ri_details})
    gates.append(
        {"name": "Cross-review gate", "ok": bool(review_file), "details": f"artifact={'none' if not review_file else review_file}"}
    )
    gates.append(
        {
            "name": "TDD gate",
            "ok": len(test_candidates) > 0,
            "details": f"test files={[p.name for p in test_candidates]}" if test_candidates else "none",
        }
    )
    legal_notes = "none"
    legal_ok = False
    if legal_file:
        contents = legal_file.read_text(encoding="utf-8")
        match = re.search(r"^result:\s*(.+)$", contents, re.MULTILINE | re.IGNORECASE)
        legal_result = match.group(1).strip() if match else None
        legal_ok = bool(legal_result and "pass" in legal_result.lower())
        legal_notes = f"result={legal_result or 'missing'}"
    gates.append({"name": "Legal gate", "ok": legal_ok, "details": f"artifact={legal_file if legal_file else 'missing'}, {legal_notes}"})

    # Claim gate — WARN for legacy items (no metadata_version), FAIL for hardened items
    claim_ok, claim_details = check_claim_gate(assets_dir)
    gates.append({"name": "Claim gate", "ok": claim_ok, "warn": claim_ok is None, "details": claim_details})

    # Future-work gate — WARN when file absent (legacy), FAIL when file present but invalid
    fw_ok, fw_details = check_future_work_gate(assets_dir)
    gates.append({"name": "Future-work gate", "ok": fw_ok, "warn": fw_ok is None, "details": fw_details})

    # Reclaim gate — WARN when absent (no reclaim triggered), FAIL when present but invalid
    reclaim_ok, reclaim_details = check_reclaim_gate(assets_dir)
    gates.append({"name": "Reclaim gate", "ok": reclaim_ok, "warn": reclaim_ok is None, "details": reclaim_details})

    success = True
    print(f"Gate evidence for {wrk_id} (assets: {assets_dir}):")
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

    if not success:
        print("→ Gate evidence incomplete. Please collect the missing artifacts before claiming.", file=sys.stderr)
        return 1

    print("→ All orchestrator gates have documented evidence.")
    return 0


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: verify-gate-evidence.py WRK-<id>")
        sys.exit(1)
    wrk_id = sys.argv[1]
    code = run_checks(wrk_id)
    sys.exit(code)


if __name__ == "__main__":
    main()
