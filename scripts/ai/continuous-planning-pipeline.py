#!/usr/bin/env python3
"""Read-only continuous planning pipeline lane report.

Classifies open issues into approval, execution, active-dispatch, QA, and
planning feedstock lanes using GitHub issue JSON plus local plan/review/marker
and optional dispatch-ledger evidence.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "continuous-planning-pipeline.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "continuous-planning-pipeline.md"
DEFAULT_PROVIDERS = ("claude", "codex", "gemini")
NON_TERMINAL_DISPATCH_STATES = {"candidate", "scheduled", "running", "blocked", "failed", "no-fire", "stale"}
LANE_NAMES = {
    "A": "approval_candidates",
    "B": "execution_ready",
    "C": "planning_feedstock",
    "D": "active_dispatch",
    "E": "implementation_review",
}
HANDOFF_FIELDS = (
    "issue",
    "pr/branch",
    "dispatch id",
    "plan sha",
    "approval marker",
    "changed files",
    "tests/ci",
    "artifacts",
    "risks",
    "implementation-review status",
    "recommended human action",
    "review effort",
    "priority reason",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dumps_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label_names(issue: dict[str, Any]) -> list[str]:
    return [str(label.get("name", "")) if isinstance(label, dict) else str(label) for label in issue.get("labels", [])]


def issue_state(issue: dict[str, Any]) -> str:
    return str(issue.get("state") or "OPEN").upper()


def priority_rank(issue: dict[str, Any]) -> int:
    labels = set(label_names(issue))
    if "priority:critical" in labels:
        return 0
    if "priority:high" in labels:
        return 1
    if "priority:medium" in labels:
        return 2
    if "priority:low" in labels:
        return 3
    return 4


def discover_plan_files(root: Path) -> dict[int, Path]:
    plans: dict[int, Path] = {}
    for path in sorted((root / "docs" / "plans").glob("*-issue-*-*.md")):
        match = re.search(r"issue-(\d+)-", path.name)
        if not match:
            continue
        number = int(match.group(1))
        if number not in plans or path.name > plans[number].name:
            plans[number] = path
    return plans


def parse_verdict(text: str) -> str:
    match = re.search(r"\b(APPROVE|MINOR|MAJOR|UNAVAILABLE)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else "UNKNOWN"


def parse_plan_sha(text: str) -> str | None:
    match = re.search(r"^Plan-SHA256\s*:\s*([a-fA-F0-9]{64})\s*$", text, re.MULTILINE)
    return match.group(1).lower() if match else None


def discover_reviews(root: Path, required_providers: tuple[str, ...]) -> dict[int, dict[str, dict[str, Any]]]:
    reviews: dict[int, dict[str, dict[str, Any]]] = {}
    pattern = root / "scripts" / "review" / "results" / "*-plan-*-*.md"
    for name in glob.glob(str(pattern)):
        path = Path(name)
        match = re.search(r"-plan-(\d+)-([A-Za-z0-9_-]+)\.md$", path.name)
        if not match:
            continue
        number = int(match.group(1))
        provider = match.group(2).lower()
        if provider not in required_providers:
            continue
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        reviews.setdefault(number, {})[provider] = {
            "path": str(path.relative_to(root)),
            "empty": text.strip() == "",
            "verdict": "EMPTY" if text.strip() == "" else parse_verdict(text),
            "plan_sha256": parse_plan_sha(text),
        }
    return reviews


def review_summary(
    number: int,
    plan_path: Path | None,
    reviews: dict[int, dict[str, dict[str, Any]]],
    required_providers: tuple[str, ...],
    allow_legacy_review_artifacts: bool,
) -> tuple[bool, list[str], dict[str, Any]]:
    warnings: list[str] = []
    provider_data = reviews.get(number, {})
    plan_sha = sha256_file(plan_path) if plan_path and plan_path.exists() else None
    clean = True
    evidence: dict[str, Any] = {"required_providers": list(required_providers), "providers": {}, "plan_sha256": plan_sha}

    for provider in required_providers:
        data = provider_data.get(provider)
        if not data:
            clean = False
            warnings.append("missing_review")
            evidence["providers"][provider] = {"status": "missing"}
            continue
        evidence["providers"][provider] = data
        verdict = data["verdict"]
        if data.get("empty"):
            clean = False
            warnings.append("empty_review")
            continue
        if verdict == "MAJOR":
            clean = False
            warnings.append("major_review")
        elif verdict == "UNAVAILABLE":
            clean = False
            warnings.append("unavailable_review")
        elif verdict not in {"APPROVE", "MINOR"}:
            clean = False
            warnings.append("unknown_review")

        artifact_sha = data.get("plan_sha256")
        if artifact_sha and plan_sha and artifact_sha != plan_sha:
            clean = False
            warnings.append("sha_mismatch_review")
        elif not artifact_sha:
            warnings.append("legacy_review_no_sha")
            if not allow_legacy_review_artifacts:
                clean = False

    return clean, sorted(set(warnings)), evidence


def discover_markers(root: Path) -> tuple[dict[int, Path], list[str]]:
    markers: dict[int, Path] = {}
    out_of_scope: list[str] = []
    for path in sorted((root / ".planning" / "plan-approved").glob("*.md")):
        if path.stem.isdigit():
            markers[int(path.stem)] = path
        else:
            out_of_scope.append(path.name)
    return markers, out_of_scope


def marker_quality(path: Path | None, root: Path | None = None) -> tuple[str | None, list[str]]:
    if path is None or not path.exists():
        return None, ["approved_no_marker"]
    text = path.read_text(encoding="utf-8").lower()
    warnings: list[str] = []
    if "self-approved" in text or "auto-approved" in text or "worker session" in text:
        warnings.append("self_approved_marker")
    if root is not None:
        try:
            age_s = datetime.now().timestamp() - path.stat().st_mtime
            rel = path.relative_to(root)
            in_repo = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-dir"], capture_output=True, text=True, timeout=5)
            if in_repo.returncode == 0 and age_s < 120:
                history = subprocess.run(["git", "-C", str(root), "log", "--oneline", "-1", "--", str(rel)], capture_output=True, text=True, timeout=10)
                if history.returncode == 0 and not history.stdout.strip():
                    warnings.append("uncommitted_marker")
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    has_binding = "issue:" in text and "plan:" in text and "approved by:" in text
    quality = "revision-bound" if has_binding and "approval source" in text else "minimal"
    return quality, warnings


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def normalize_dispatch_row(row: dict[str, Any], path: Path, root: Path, now: datetime) -> tuple[int | None, dict[str, Any] | None, str | None]:
    raw_issue = row.get("issue") or row.get("issue_number") or row.get("number")
    try:
        number = int(raw_issue)
    except (TypeError, ValueError):
        return None, None, "ledger_untrusted"
    normalized = {**row, "ledger_path": str(path.relative_to(root))}
    state = str(normalized.get("state", "")).lower()
    scheduled_at = parse_time(normalized.get("scheduled_at_utc") or normalized.get("scheduled_at"))
    heartbeat_at = parse_time(normalized.get("heartbeat_at_utc") or normalized.get("heartbeat_at") or normalized.get("updated_at"))
    if state == "scheduled" and scheduled_at and now - scheduled_at > timedelta(minutes=45):
        normalized["original_state"] = state
        normalized["state"] = "stale"
        normalized["stale_reason"] = "scheduled_without_start_after_45m"
    elif state == "running" and heartbeat_at and now - heartbeat_at > timedelta(hours=2):
        normalized["original_state"] = state
        normalized["state"] = "stale"
        normalized["stale_reason"] = "running_without_heartbeat_after_2h"
    return number, normalized, None


def load_dispatch(root: Path) -> tuple[dict[int, dict[str, Any]], list[str]]:
    dispatch: dict[int, dict[str, Any]] = {}
    files = sorted((root / "docs" / "reports" / "continuous-work").glob("dispatch-ledger-*.json"))
    warnings = [] if files else ["ledger_missing"]
    now = datetime.now(timezone.utc)
    for path in files:
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warnings.append("ledger_untrusted")
            continue
        if not isinstance(rows, list):
            warnings.append("ledger_untrusted")
            continue
        for row in rows:
            if not isinstance(row, dict):
                warnings.append("ledger_untrusted")
                continue
            number, normalized, warning = normalize_dispatch_row(row, path, root, now)
            if warning:
                warnings.append(warning)
                continue
            assert number is not None and normalized is not None
            prior = dispatch.get(number)
            if prior and str(prior.get("state", "")).lower() in NON_TERMINAL_DISPATCH_STATES:
                normalized["conflict"] = True
                normalized["prior_dispatch_id"] = prior.get("dispatch_id") or prior.get("id")
            dispatch[number] = normalized
    return dispatch, sorted(set(warnings))


def has_canonical_approval_comment(issue: dict[str, Any], plan_path: Path | None, plan_sha: str | None) -> tuple[bool, list[str]]:
    comments = issue.get("comments")
    if comments is None:
        return False, ["comment_check_failed"]
    if not comments:
        return False, ["approval_comment_ambiguous"]
    required = ["approve", "revise", "hold", "execution remains unauthorized", "approval marker"]
    plan_name = plan_path.name if plan_path else ""
    for comment in comments:
        body = str(comment.get("body", "")).lower()
        if plan_sha and plan_sha.lower() not in body:
            continue
        if plan_name and plan_name.lower() not in body:
            continue
        if "review artifacts" not in body and "review artifact" not in body:
            continue
        if all(token in body for token in required):
            return True, []
    return False, ["approval_comment_ambiguous"]


def pr_handoff_state(issue: dict[str, Any]) -> tuple[str | None, list[str]]:
    pr = issue.get("pull_request") or issue.get("pullRequest")
    refs = issue.get("closedByPullRequestsReferences") or []
    if not pr and refs:
        first_ref = refs[0]
        pr = {
            "url": first_ref.get("url", ""),
            "body": "\n".join(
                str(comment.get("body", "")) for comment in issue.get("comments", [])
            ),
        }
    if not pr:
        return None, []
    body = str(pr.get("body", "")).lower()
    missing = [field for field in HANDOFF_FIELDS if field not in body]
    if missing:
        return "open-pr", ["lane_e_handoff_missing"]
    return "review-ready", []


def empty_lanes() -> dict[str, list[dict[str, Any]]]:
    return {lane: [] for lane in LANE_NAMES}


def classify_issue(
    issue: dict[str, Any],
    *,
    root: Path,
    plans: dict[int, Path],
    reviews: dict[int, dict[str, dict[str, Any]]],
    markers: dict[int, Path],
    dispatch: dict[int, dict[str, Any]],
    ledger_warnings: list[str],
    required_providers: tuple[str, ...],
    allow_legacy_review_artifacts: bool,
) -> dict[str, Any]:
    number = int(issue["number"])
    labels = label_names(issue)
    warnings: list[str] = []
    if "status:plan-approved" in labels and "status:plan-review" in labels:
        warnings.append("dual_status_labels")

    plan_path = plans.get(number)
    if "status:plan-approved" in labels and not plan_path:
        warnings.append("approved_no_plan")
    review_clean = False
    review_evidence: dict[str, Any] = {"required_providers": list(required_providers), "providers": {}, "plan_sha256": None}
    if plan_path or "status:plan-approved" in labels or "status:plan-review" in labels:
        review_clean, review_warnings, review_evidence = review_summary(
            number, plan_path, reviews, required_providers, allow_legacy_review_artifacts
        )
        warnings.extend(review_warnings)
    quality, marker_warnings = marker_quality(markers.get(number), root=root)
    marker_exists = markers.get(number) is not None
    if "status:plan-approved" in labels:
        warnings.extend(marker_warnings)

    substate: str | None = None
    lane = "C"
    primary_action = "plan_issue"

    pr_state, pr_warnings = pr_handoff_state(issue)
    if pr_state:
        lane = "E"
        substate = pr_state
        primary_action = "review_implementation" if pr_state == "review-ready" else "complete_lane_e_handoff"
        warnings.extend(pr_warnings)
    elif number in dispatch and str(dispatch[number].get("state", "")).lower() in NON_TERMINAL_DISPATCH_STATES:
        lane = "D"
        substate = str(dispatch[number].get("state", "active"))
        primary_action = "morning_decision_before_requeue" if substate in {"stale", "no-fire", "failed"} else "check_dispatch_state"
        warnings.append("stale_dispatch" if substate == "stale" else "active_lease_conflict")
        if dispatch[number].get("conflict"):
            warnings.append("active_lease_conflict")
    elif issue_state(issue) != "OPEN":
        lane = "closed"
        primary_action = "ignore_closed"
    elif "status:plan-approved" in labels and plan_path and marker_exists and review_clean and not marker_warnings:
        lane = "B"
        primary_action = "dispatch_implementation"
    elif "status:plan-review" in labels and plan_path and review_clean:
        ok_comment, comment_warnings = has_canonical_approval_comment(
            issue, plan_path, review_evidence.get("plan_sha256")
        )
        if ok_comment:
            lane = "A"
            primary_action = "request_approval"
        else:
            warnings.extend(comment_warnings)
            primary_action = "repost_approval_request"
    else:
        primary_action = "write_or_repair_plan"

    # Missing or untrusted dispatch ledger is a global observability warning.
    # It should not become every issue's primary blocker; issue-level Lane D rows
    # still add active/stale/conflict warnings when evidence exists.
    warnings = sorted(set(warnings))
    plan_rel = str(plan_path.relative_to(root)) if plan_path else None
    return {
        "number": number,
        "title": str(issue.get("title", "")),
        "url": str(issue.get("url", "")),
        "labels": labels,
        "lane": lane,
        "substate": substate,
        "primary_action": primary_action,
        "primary_blocker": warnings[0] if warnings and lane not in {"A", "B", "D", "E"} else None,
        "secondary_notes": warnings[1:],
        "warnings": warnings,
        "plan": plan_rel,
        "review_clean": review_clean,
        "review_evidence": review_evidence,
        "approval_marker": str(markers[number].relative_to(root)) if marker_exists else None,
        "marker_quality": quality,
        "dispatch_state": dispatch.get(number),
        "priority_rank": priority_rank(issue),
    }


def compute_buffer_health(lanes: dict[str, list[dict[str, Any]]], *, lane_e_cap: int) -> dict[str, dict[str, Any]]:
    targets = {"lane_a": (5, 10, len(lanes["A"])), "lane_b": (5, 10, len(lanes["B"])), "lane_c": (10, 20, len(lanes["C"]))}
    health = {}
    for name, (minimum, maximum, count) in targets.items():
        if count < minimum:
            status = "below_minimum"
        elif count > maximum:
            status = "above_maximum"
        else:
            status = "healthy"
        health[name] = {"count": count, "minimum": minimum, "maximum": maximum, "status": status}
    health["lane_e"] = {"count": len(lanes["E"]), "maximum": lane_e_cap, "status": "saturated" if len(lanes["E"]) >= lane_e_cap else "ok"}
    return health


def recommendations(buffer_health: dict[str, dict[str, Any]]) -> list[str]:
    recs: list[str] = []
    if buffer_health["lane_e"]["status"] == "saturated" or buffer_health["lane_a"]["status"] == "below_minimum":
        recs.append("Recommend planning/QA only until approval candidates and review backlog recover.")
    if buffer_health["lane_b"]["status"] == "below_minimum":
        recs.append("Refill evidence-clean execution-ready Lane B before overnight implementation dispatch.")
    if not recs:
        recs.append("Lane buffers are within operating thresholds; dispatch can proceed from Lane B with caps.")
    return recs


def build_snapshot(
    issues: list[dict[str, Any]],
    *,
    root: Path = WORKSPACE_HUB,
    generated_at: str | None = None,
    required_providers: tuple[str, ...] = DEFAULT_PROVIDERS,
    allow_legacy_review_artifacts: bool = False,
    lane_e_cap: int = 5,
    max_new_implementation_prs_per_night: int = 3,
) -> dict[str, Any]:
    root = Path(root)
    plans = discover_plan_files(root)
    reviews = discover_reviews(root, required_providers)
    markers, out_of_scope_markers = discover_markers(root)
    dispatch, ledger_warnings = load_dispatch(root)
    lanes = empty_lanes()
    all_items: list[dict[str, Any]] = []

    open_approved_numbers = {int(i["number"]) for i in issues if issue_state(i) == "OPEN" and "status:plan-approved" in label_names(i)}
    orphan_markers = sorted(n for n in markers if n not in open_approved_numbers)

    for issue in sorted(issues, key=lambda i: (priority_rank(i), int(i["number"]))):
        entry = classify_issue(
            issue,
            root=root,
            plans=plans,
            reviews=reviews,
            markers=markers,
            dispatch=dispatch,
            ledger_warnings=ledger_warnings,
            required_providers=required_providers,
            allow_legacy_review_artifacts=allow_legacy_review_artifacts,
        )
        all_items.append(entry)
        if entry["lane"] in lanes:
            lanes[entry["lane"]].append(entry)

    buffer_health = compute_buffer_health(lanes, lane_e_cap=lane_e_cap)
    warning_summary: dict[str, int] = {}
    for entry in all_items:
        for warning in entry["warnings"]:
            warning_summary[warning] = warning_summary.get(warning, 0) + 1
    if orphan_markers:
        warning_summary["marker_without_open_approved_issue"] = len(orphan_markers)

    return {
        "generated_at": generated_at or utc_now(),
        "thresholds": {
            "lane_a": [5, 10],
            "lane_b": [5, 10],
            "lane_c": [10, 20],
            "lane_e_cap": lane_e_cap,
            "max_new_implementation_prs_per_night": max_new_implementation_prs_per_night,
        },
        "required_providers": list(required_providers),
        "allow_legacy_review_artifacts": allow_legacy_review_artifacts,
        "lanes": lanes,
        "items": all_items,
        "buffer_health": buffer_health,
        "warning_summary": dict(sorted(warning_summary.items())),
        "global_warnings": ledger_warnings,
        "orphan_markers": orphan_markers,
        "out_of_scope_markers": out_of_scope_markers,
        "recommendations": recommendations(buffer_health),
    }


def top_actions(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    lane_weight = {"E": 0, "A": 1, "B": 2, "D": 3, "C": 4}
    items = list(snapshot.get("items", []))
    items.sort(
        key=lambda entry: (
            lane_weight.get(entry.get("lane"), 9),
            0 if entry.get("substate") == "review-ready" else 1,
            entry.get("priority_rank", 9),
            entry.get("number", 0),
        )
    )
    return items[:5]


def render_markdown(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Continuous planning pipeline",
        "",
        f"Generated: {snapshot['generated_at']}",
        "",
        "## Top actions today",
        "",
    ]
    actions = top_actions(snapshot)
    if not actions:
        lines.append("- No open actions found.")
    for entry in actions:
        blocker = entry.get("primary_blocker") or entry.get("primary_action")
        lines.append(f"- #{entry['number']} [{entry['lane']}] {entry['title']} — {blocker}")
    lines.extend(["", "## Morning user approval packet", ""])
    for entry in snapshot["lanes"]["A"]:
        lines.append(f"- #{entry['number']} {entry['title']} — approval requested; plan `{entry.get('plan')}`")
    if not snapshot["lanes"]["A"]:
        lines.append("- No evidence-clean approval candidates currently available.")
    lines.extend(["", "## Overnight dispatch packet", ""])
    if snapshot["buffer_health"]["lane_e"]["status"] == "saturated":
        lines.append("- Lane E saturated; do not launch new implementation work.")
    limit = int(snapshot.get("thresholds", {}).get("max_new_implementation_prs_per_night", 3))
    ready_items = snapshot["lanes"]["B"]
    for entry in ready_items[:limit]:
        lines.append(f"- #{entry['number']} {entry['title']} — execution-ready with marker `{entry.get('approval_marker')}`")
    if len(ready_items) > limit:
        lines.append(f"- Additional Lane B candidates exist but new implementation dispatch is limited to {limit} per night.")
    if not ready_items:
        lines.append("- No evidence-clean Lane B dispatch candidates currently available.")
    lines.extend(["", "## Buffer health", ""])
    for key, value in snapshot["buffer_health"].items():
        lines.append(f"- {key}: {value['count']} ({value['status']})")
    lines.extend(["", "## Warning summary", ""])
    if snapshot.get("global_warnings"):
        for warning in snapshot["global_warnings"]:
            lines.append(f"- global: {warning}")
    if snapshot["warning_summary"]:
        for warning, count in snapshot["warning_summary"].items():
            lines.append(f"- {warning}: {count}")
    elif not snapshot.get("global_warnings"):
        lines.append("- No warnings.")
    lines.extend(["", "## Recommendations", ""])
    for rec in snapshot["recommendations"]:
        lines.append(f"- {rec}")
    return "\n".join(lines) + "\n"


def gh_issue_list() -> list[dict[str, Any]]:
    cmd = ["gh", "issue", "list", "--state", "open", "--limit", "200", "--json", "number,title,labels,updatedAt,body,url,state"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    issues = json.loads(result.stdout)
    enriched: list[dict[str, Any]] = []
    for issue in issues:
        issue.setdefault("state", "OPEN")
        labels = set(label_names(issue))
        # Live gh issue list does not include comment/PR evidence needed for
        # Lane A/E. Enrich every open issue: unlabeled implementation output can
        # still be Lane E, while labeled plan-review/approved issues need
        # comments for approval-comment and handoff evidence.
        view_cmd = [
            "gh",
            "issue",
            "view",
            str(issue["number"]),
            "--json",
            "comments,closedByPullRequestsReferences",
        ]
        try:
            view = subprocess.run(view_cmd, check=True, capture_output=True, text=True, timeout=30)
            issue.update(json.loads(view.stdout))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            issue["comments"] = None if labels.intersection({"status:plan-review", "status:plan-approved"}) else []
            issue["comment_fetch_failed"] = True
        enriched.append(issue)
    return enriched


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate read-only continuous planning lane reports")
    parser.add_argument("--issues-json", help="Offline issue JSON fixture; otherwise gh issue list is used")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--required-providers", default=",".join(DEFAULT_PROVIDERS), help="Comma-separated provider verdicts required for clean review")
    parser.add_argument("--allow-legacy-review-artifacts", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--fail-under-buffer", action="store_true", help="Exit 3 when Lane A/B/C are below minimum")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    providers = tuple(p.strip().lower() for p in args.required_providers.split(",") if p.strip())
    issues = load_json(Path(args.issues_json)) if args.issues_json else gh_issue_list()
    snapshot = build_snapshot(
        issues,
        required_providers=providers,
        allow_legacy_review_artifacts=args.allow_legacy_review_artifacts,
    )
    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(dumps_json(snapshot), encoding="utf-8")
    print(f"JSON → {json_out}")
    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(snapshot), encoding="utf-8")
        print(f"Markdown → {md_out}")
    if args.fail_under_buffer:
        for key in ("lane_a", "lane_b", "lane_c"):
            if snapshot["buffer_health"][key]["status"] == "below_minimum":
                return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
