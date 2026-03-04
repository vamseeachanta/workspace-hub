#!/usr/bin/env python3
"""Validate orchestrator gate evidence for a WRK item."""

import re
import sys
import json
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


def check_html_open_default_browser_gate(assets_dir: Path, required: list[str]) -> tuple[bool, str]:
    """Require browser-open evidence for each user review stage."""
    evidence = evidence_file(assets_dir, "user-review-browser-open.yaml", [])
    if evidence is None:
        return False, "user-review-browser-open.yaml missing"
    data, yaml_err = load_yaml(evidence)
    if yaml_err:
        return False, f"could not parse {evidence.name}: {yaml_err}"
    assert data is not None
    events = data.get("events") or []
    if not isinstance(events, list):
        return False, f"{evidence.name}: events must be a list"
    seen = set()
    for idx, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            return False, f"{evidence.name}: events[{idx}] must be an object"
        stage = str(event.get("stage", "")).strip().lower()
        if not stage:
            return False, f"{evidence.name}: events[{idx}] stage missing"
        opened = event.get("opened_in_default_browser")
        browser = str(event.get("browser", "")).strip().lower()
        if opened is not True and browser not in {"default", "system-default"}:
            return False, f"{evidence.name}: events[{idx}] must confirm default browser open"
        if not str(event.get("html_ref", "")).strip():
            return False, f"{evidence.name}: events[{idx}] html_ref missing"
        if not str(event.get("opened_at", "")).strip():
            return False, f"{evidence.name}: events[{idx}] opened_at missing"
        if not str(event.get("reviewer", "")).strip():
            return False, f"{evidence.name}: events[{idx}] reviewer missing"
        seen.add(stage)
    missing = [stage for stage in required if stage not in seen]
    if missing:
        return False, f"{evidence.name}: missing required stages {missing}"
    return True, f"{evidence.name}: stages={sorted(seen)}"


def check_user_review_publish_gate(assets_dir: Path, required: list[str]) -> tuple[bool, str]:
    """Require origin-publish evidence for each user review checkpoint."""
    evidence = evidence_file(assets_dir, "user-review-publish.yaml", [])
    if evidence is None:
        return False, "user-review-publish.yaml missing"
    data, yaml_err = load_yaml(evidence)
    if yaml_err:
        return False, f"could not parse {evidence.name}: {yaml_err}"
    assert data is not None
    events = data.get("events") or []
    if not isinstance(events, list):
        return False, f"{evidence.name}: events must be a list"
    seen = set()
    for idx, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            return False, f"{evidence.name}: events[{idx}] must be an object"
        stage = str(event.get("stage", "")).strip().lower()
        if not stage:
            return False, f"{evidence.name}: events[{idx}] stage missing"
        pushed = event.get("pushed_to_origin")
        if pushed is not True:
            return False, f"{evidence.name}: events[{idx}] pushed_to_origin must be true"
        if not str(event.get("remote", "")).strip():
            return False, f"{evidence.name}: events[{idx}] remote missing"
        if not str(event.get("branch", "")).strip():
            return False, f"{evidence.name}: events[{idx}] branch missing"
        if not str(event.get("commit", "")).strip():
            return False, f"{evidence.name}: events[{idx}] commit missing"
        docs = event.get("documents") or []
        if not isinstance(docs, list) or len(docs) == 0:
            return False, f"{evidence.name}: events[{idx}] documents must be a non-empty list"
        if not str(event.get("published_at", "")).strip():
            return False, f"{evidence.name}: events[{idx}] published_at missing"
        if not str(event.get("reviewer", "")).strip():
            return False, f"{evidence.name}: events[{idx}] reviewer missing"
        seen.add(stage)
    missing = [stage for stage in required if stage not in seen]
    if missing:
        return False, f"{evidence.name}: missing required stages {missing}"
    return True, f"{evidence.name}: stages={sorted(seen)}"


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
    decision = str(data.get("reclaim_decision", "")).strip().lower()
    if decision not in {"reclaim_and_resume", "pause_and_replan", "block"}:
        return False, f"{reclaim_file.name}: invalid reclaim_decision={decision or 'missing'}"
    if decision == "reclaim_and_resume" and not data.get("prior_claim_ref"):
        return False, f"{reclaim_file.name}: prior_claim_ref required for reclaim_and_resume"
    if decision == "block" and not data.get("block_reason"):
        return False, f"{reclaim_file.name}: block_reason required when reclaim_decision=block"
    return True, f"{reclaim_file.name}: reclaim_decision={decision}"


def check_execute_integrated_tests_gate(assets_dir: Path) -> tuple[bool, str]:
    """Require 3-5 integrated/repo tests in execute evidence before close."""
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
    count = len(tests)
    if count < 3 or count > 5:
        return False, f"{execute_file.name}: integrated_repo_tests count must be 3-5 (found {count})"

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
        if not str(row.get("evidence", "")).strip():
            return False, f"{path.name}: stages[{idx}] evidence missing"
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


def run_checks(wrk_id: str, phase: str = "close") -> int:
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
    if phase == "close":
        stage_ok, stage_details = check_stage_evidence_gate(front, workspace_root, wrk_id, phase=phase)
        gates.append({"name": "Stage evidence gate", "ok": stage_ok, "details": stage_details})
    ri_ok, ri_details = check_resource_intelligence_gate(assets_dir)
    gates.append({"name": "Resource-intelligence gate", "ok": bool(ri_ok), "details": ri_details})
    activation_ok, activation_details = check_activation_gate(assets_dir, wrk_id)
    gates.append({"name": "Activation gate", "ok": activation_ok, "details": activation_details})
    html_open_required = ["plan_draft", "plan_final"]
    if phase == "close":
        html_open_required.append("close_review")
    html_open_ok, html_open_details = check_html_open_default_browser_gate(assets_dir, html_open_required)
    gates.append({"name": "User-review HTML-open gate", "ok": html_open_ok, "details": html_open_details})
    publish_ok, publish_details = check_user_review_publish_gate(assets_dir, html_open_required)
    gates.append({"name": "User-review publish gate", "ok": publish_ok, "details": publish_details})
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
    gates.append({"name": "Claim gate", "ok": bool(claim_ok), "details": claim_details})

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


def main() -> None:
    if len(sys.argv) not in {2, 4}:
        print("Usage: verify-gate-evidence.py WRK-<id> [--phase claim|close]")
        sys.exit(1)
    wrk_id = sys.argv[1]
    phase = "close"
    if len(sys.argv) == 4:
        if sys.argv[2] != "--phase" or sys.argv[3] not in {"claim", "close"}:
            print("Usage: verify-gate-evidence.py WRK-<id> [--phase claim|close]")
            sys.exit(1)
        phase = sys.argv[3]
    code = run_checks(wrk_id, phase=phase)
    sys.exit(code)


if __name__ == "__main__":
    main()
