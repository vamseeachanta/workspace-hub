#!/usr/bin/env python3
"""Confidence-weighted GitHub agent auto-labeler.

Default behavior is dry-run: generate a candidate list and optional report.
Use --apply for conservative live labeling of only high-confidence issues.
Add --comment to explain newly applied labels in bounded single-writer use.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.issue_publication import public_issue_view

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
WORK_QUEUE_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-work-queue.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-autolabel-candidates.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-autolabel-candidates.md"
CONFIDENCE_THRESHOLD = 0.90
PROVIDERS = ("claude", "codex", "agy")
LEGACY_PROVIDER_ALIASES = {"gemini": "agy"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_provider_label(issue: dict[str, Any]) -> bool:
    return any(
        label.startswith("ai:") or label.startswith("agent:")
        for label in issue.get("labels", [])
    )


def compute_confidence(provider: str, issue: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    if issue.get("execution_ready"):
        score += 0.35
        reasons.append("execution-ready")
    if issue.get("priority_rank") in (0, 1, 2):
        score += 0.15
        reasons.append("priority-labeled")
    routing_reason = str(issue.get("routing_reason", ""))
    if routing_reason == "implementation/test/fix language" and provider == "codex":
        score += 0.35
        reasons.append("strong-codex-language-match")
    elif routing_reason == "strategy/workflow/architecture language" and provider == "claude":
        score += 0.35
        reasons.append("strong-claude-language-match")
    elif routing_reason == "research/triage/audit language" and provider == "agy":
        score += 0.35
        reasons.append("strong-agy-language-match")
    elif routing_reason.startswith("existing "):
        score = 0.0
        reasons.append("already-labeled")
    else:
        score += 0.10
        reasons.append("weak-heuristic-match")

    provider_priority = str(issue.get("provider_priority", ""))
    if provider_priority == "highest":
        score += 0.10
        reasons.append("provider-highest-priority")
    elif provider_priority == "high":
        score += 0.05
        reasons.append("provider-high-priority")

    if has_provider_label(issue):
        score = 0.0
        reasons.append("provider-label-exists")

    return round(min(score, 1.0), 2), reasons


def collect_candidates(work_queue: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for provider in PROVIDERS:
        for issue in work_queue["provider_queues"][provider]["top_issues"]:
            confidence, reasons = compute_confidence(provider, issue)
            if has_provider_label(issue):
                continue
            candidates.append(
                {
                    **public_issue_view(issue),
                    "target_label": f"ai:{LEGACY_PROVIDER_ALIASES.get(provider, provider)}",
                    "confidence": confidence,
                    "confidence_reasons": reasons,
                    "eligible": confidence >= CONFIDENCE_THRESHOLD,
                }
            )
    candidates.sort(key=lambda item: (-item["confidence"], item["priority_rank"], item["number"]))
    return candidates


def render_markdown(payload: dict[str, Any]) -> str:
    payload = public_issue_view(payload)
    lines = [
        "# Provider autolabel candidates",
        "",
        f"Generated: {payload['generated_at']}",
        f"Apply mode: {payload['apply_mode']}",
        f"Threshold: {payload['threshold']}",
        "",
        "| Issue | Target label | Confidence | Eligible | Reasons |",
        "|---|---|---:|---|---|",
    ]
    for item in payload["candidates"]:
        eligible = "yes" if item["eligible"] else "no"
        lines.append(
            f"| #{item['number']} {item['title']} | {item['target_label']} | {item['confidence']:.2f} | {eligible} | {', '.join(item['confidence_reasons'])} |"
        )
    return "\n".join(lines)


def gh_issue_edit_add_label(issue_number: int, label: str) -> None:
    subprocess.run(
        ["gh", "issue", "edit", str(issue_number), "--add-label", label],
        check=True,
        capture_output=True,
        text=True,
    )


def gh_issue_records(issue_number: int, resource: str, field: str) -> list[str]:
    """Read every page and reject incomplete deduplication evidence."""
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         f"repos/{{owner}}/{{repo}}/issues/{issue_number}/{resource}"],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = json.loads(result.stdout)
    if not isinstance(pages, list) or not pages or any(
        not isinstance(page, list) for page in pages
    ):
        raise ValueError(f"Incomplete issue {resource} read")
    records = []
    for page in pages:
        for record in page:
            if not isinstance(record, dict) or not isinstance(record.get(field), str):
                raise ValueError(f"Incomplete issue {resource} read")
            records.append(record[field])
    return records


def explanation_marker(issue_number: int, label: str) -> str:
    """Keep the issue and label binding stable across runs in this repository."""
    return f"<!-- provider-autolabel:issue={issue_number};label={label} -->"


def render_explanation(item: dict[str, Any]) -> str:
    """Publish fixed routing evidence only, without arbitrary queue metadata."""
    item = public_issue_view(item)
    # These are the strong language matches in compute_confidence, not free prose.
    routing_reason = item.get("routing_reason")
    if routing_reason not in (
        "implementation/test/fix language",
        "strategy/workflow/architecture language",
        "research/triage/audit language",
    ):
        routing_reason = "unavailable"
    provider_priority = item.get("provider_priority")
    if provider_priority not in ("highest", "high"):
        provider_priority = "unavailable"
    ready = "yes" if item.get("execution_ready") else "no"
    return (
        f"Automated provider label applied: `{item['target_label']}`.\n\n"
        f"- Confidence: {item['confidence']:.2f}\n"
        f"- Routing reason: {routing_reason}\n"
        f"- Provider priority: {provider_priority}\n"
        f"- Execution-ready: {ready}\n\n"
        f"{explanation_marker(item['number'], item['target_label'])}"
    )


def gh_issue_comment(issue_number: int, body: str) -> None:
    subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--body", body],
        check=True,
        capture_output=True,
        text=True,
    )


def build_payload(
    work_queue: dict[str, Any], apply_mode: bool, limit: int, comment: bool = False,
) -> dict[str, Any]:
    candidates = collect_candidates(work_queue)
    eligible = [item for item in candidates if item["eligible"]]
    applied: list[dict[str, Any]] = []

    if apply_mode:
        for item in eligible[:limit]:
            labels = gh_issue_records(item["number"], "labels", "name")
            if has_provider_label({"labels": labels}):
                continue
            if comment:
                bodies = gh_issue_records(item["number"], "comments", "body")
                marker = explanation_marker(item["number"], item["target_label"])
                if any(marker in body for body in bodies):
                    continue
            # Complete all deduplication reads before either write. A label
            # failure raises here, so it can never produce an explanation.
            gh_issue_edit_add_label(item["number"], item["target_label"])
            applied.append({
                "number": item["number"],
                "target_label": item["target_label"],
                "confidence": item["confidence"],
            })
            if comment:
                gh_issue_comment(item["number"], render_explanation(item))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "apply_mode": apply_mode,
        "threshold": CONFIDENCE_THRESHOLD,
        "eligible_count": len(eligible),
        "applied": applied,
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Confidence-weighted GitHub agent auto-labeler")
    parser.add_argument("--work-queue", default=str(WORK_QUEUE_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--comment", action="store_true",
        help="explain newly applied labels (requires --apply; single writer only)",
    )
    parser.add_argument("--limit", type=int, default=3, help="max labels to apply in one run")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    work_queue = load_json(Path(args.work_queue))
    payload = build_payload(
        work_queue, apply_mode=args.apply, limit=args.limit, comment=args.comment,
    )

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(payload) + "\n", encoding="utf-8")
        print(f"Markdown → {md_out}")

    if payload["applied"]:
        print("Applied labels:")
        for item in payload["applied"]:
            print(f"- #{item['number']} -> {item['target_label']} ({item['confidence']})")


if __name__ == "__main__":
    main()
