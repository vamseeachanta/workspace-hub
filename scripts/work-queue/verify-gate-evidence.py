#!/usr/bin/env python3
"""Validate orchestrator gate evidence for a WRK item."""

import re
import sys
from pathlib import Path


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
    """Check claim-evidence.yaml for required metadata (WRK-677 hardened schema).

    Returns:
        (True,  detail) — gate OK
        (False, detail) — gate FAIL (hard error)
        (None,  detail) — WARN only (legacy item or absent file, no failure)
    """
    claim_file = assets_dir / "claim-evidence.yaml"
    if not claim_file.exists():
        return None, "claim-evidence.yaml absent (legacy item — WARN)"

    try:
        import yaml  # type: ignore[import]
        data = yaml.safe_load(claim_file.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return None, f"could not parse claim-evidence.yaml: {exc}"

    # str() coercion handles both YAML string "1" and integer 1
    version = str(data.get("metadata_version", "")).strip()
    if version != "1":
        return None, f"metadata_version={version!r} (legacy schema — WARN only)"

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
    return True, f"version=1, owner={owner}, {quota_note}"


def check_future_work_gate(assets_dir: Path) -> tuple[bool | None, str]:
    """Check future-work-recommendations.md for follow-up WRKs or no-follow-ups rationale.

    Returns:
        (True,  detail) — gate OK
        (False, detail) — gate FAIL (file present but empty/invalid)
        (None,  detail) — WARN only (file absent — legacy item)
    """
    fw_file = assets_dir / "future-work-recommendations.md"
    if not fw_file.exists():
        return None, "future-work-recommendations.md absent (legacy item — WARN)"
    content = strip_code_fences(fw_file.read_text(encoding="utf-8"))
    # Exclude the wrk_id: metadata header line (self-reference) from the WRK ref search
    content_no_self = re.sub(r"^wrk_id:\s+WRK-\d+.*$", "", content, flags=re.MULTILINE)
    has_wrk_ref = bool(re.search(r"\bWRK-\d+\b", content_no_self))
    rationale_match = re.search(r"^no_follow_ups_rationale:\s+\S", content, re.MULTILINE)
    if has_wrk_ref or rationale_match:
        summary = "has_wrk_refs=true" if has_wrk_ref else "no_follow_ups_rationale=present"
        return True, summary
    return False, "future-work-recommendations.md present but lists no WRKs and no_follow_ups_rationale is empty"


def strip_code_fences(content: str) -> str:
    """Remove fenced code blocks to prevent false-positive confirmation matches."""
    return re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.DOTALL)


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
