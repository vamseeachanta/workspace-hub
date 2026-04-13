#!/usr/bin/env python3
"""Generate a provider work queue from live GitHub issues + routing scorecard."""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
SCORECARD_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-routing-scorecard.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-work-queue.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-work-queue.md"
PROVIDERS = ("claude", "codex", "gemini")

RESEARCH_TERMS = {
    "research", "audit", "triage", "recon", "reconnaissance", "scan", "inventory",
    "discover", "classification", "prioritize", "summary", "knowledge", "wiki",
    "document-intelligence", "data-pipeline", "investigate",
}
IMPLEMENT_TERMS = {
    "fix", "test", "prepare", "normalize", "repair", "cleanup", "bounded",
    "implement", "writeback", "artifact", "regression", "validator", "script",
}
STRATEGY_TERMS = {
    "design", "epic", "strategy", "workflow", "review", "policy", "architecture",
    "operating model", "enforcement", "compliance",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gh_issue_list() -> list[dict[str, Any]]:
    cmd = [
        "gh", "issue", "list", "--state", "open", "--limit", "200",
        "--json", "number,title,labels,assignees,updatedAt,body,url",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def label_names(issue: dict[str, Any]) -> list[str]:
    return [str(label.get("name", "")) for label in issue.get("labels", [])]


def issue_text(issue: dict[str, Any]) -> str:
    text = f"{issue.get('title', '')}\n{issue.get('body', '')}".lower()
    return text


def existing_agent(issue: dict[str, Any]) -> str | None:
    for label in label_names(issue):
        if label.startswith("agent:"):
            return label.split(":", 1)[1]
    return None


def has_plan_approved(issue: dict[str, Any]) -> bool:
    return "status:plan-approved" in label_names(issue)


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


def suggested_provider(issue: dict[str, Any]) -> tuple[str, str]:
    current = existing_agent(issue)
    if current in PROVIDERS:
        return current, f"existing {current} agent label"

    text = issue_text(issue)
    labels = " ".join(label_names(issue)).lower()
    haystack = f"{text}\n{labels}"

    if any(term in haystack for term in STRATEGY_TERMS):
        return "claude", "strategy/workflow/architecture language"
    if any(term in haystack for term in IMPLEMENT_TERMS):
        return "codex", "implementation/test/fix language"
    if any(term in haystack for term in RESEARCH_TERMS):
        return "gemini", "research/triage/audit language"

    if "cat:data-pipeline" in labels or "cat:document-intelligence" in labels:
        return "gemini", "data-pipeline/document-intelligence label"
    if "bug" in labels:
        return "codex", "bug label"
    return "claude", "default long-context routing"


def issue_summary(issue: dict[str, Any], scorecard: dict[str, Any]) -> dict[str, Any]:
    provider, reason = suggested_provider(issue)
    labels = label_names(issue)
    execution_ready = has_plan_approved(issue)
    provider_meta = next(item for item in scorecard["recommendations"] if item["provider"] == provider)
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))

    work_type = []
    body_lower = body.lower()
    title_lower = title.lower()
    if any(word in title_lower or word in body_lower for word in RESEARCH_TERMS):
        work_type.append("research")
    if any(word in title_lower or word in body_lower for word in IMPLEMENT_TERMS):
        work_type.append("implementation")
    if any(word in title_lower or word in body_lower for word in STRATEGY_TERMS):
        work_type.append("strategy")
    if not work_type:
        work_type.append("general")

    return {
        "number": issue["number"],
        "title": title,
        "url": issue["url"],
        "labels": labels,
        "updatedAt": issue["updatedAt"],
        "execution_ready": execution_ready,
        "priority_rank": priority_rank(issue),
        "suggested_provider": provider,
        "routing_reason": reason,
        "provider_priority": provider_meta["priority"],
        "provider_status": provider_meta["status"],
        "work_type": work_type,
    }


def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        0 if item["execution_ready"] else 1,
        item["priority_rank"],
        item["number"],
    )


def build_queue(scorecard: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_items = [issue_summary(issue, scorecard) for issue in issues]
    for item in sorted(all_items, key=sort_key):
        grouped[item["suggested_provider"]].append(item)

    provider_queues = {}
    for provider in PROVIDERS:
        items = grouped.get(provider, [])
        provider_queues[provider] = {
            "provider": provider,
            "routing_priority": next(x for x in scorecard["recommendations"] if x["provider"] == provider)["priority"],
            "execution_ready_count": sum(1 for item in items if item["execution_ready"]),
            "total_candidates": len(items),
            "top_issues": items[:8],
        }

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": now,
        "current_week": scorecard["current_week"],
        "scorecard_generated_at": scorecard["generated_at"],
        "recommended_provider_order": scorecard["recommended_provider_order"],
        "provider_queues": provider_queues,
    }


def render_markdown(queue: dict[str, Any]) -> str:
    lines = [
        "# Provider work queue",
        "",
        f"Generated: {queue['generated_at']}",
        f"Current week: {queue['current_week']}",
        f"Recommended provider order: {', '.join(queue['recommended_provider_order'])}",
        "",
        "Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.",
        "",
    ]
    for provider in PROVIDERS:
        bucket = queue["provider_queues"][provider]
        lines.extend(
            [
                f"## {provider}",
                "",
                f"- Routing priority: {bucket['routing_priority']}",
                f"- Execution-ready candidates: {bucket['execution_ready_count']}",
                f"- Total routed candidates: {bucket['total_candidates']}",
                "",
                "| Issue | Ready | Why routed here | Labels |",
                "|---|---|---|---|",
            ]
        )
        for item in bucket["top_issues"]:
            label_text = ", ".join(item["labels"][:6])
            ready = "yes" if item["execution_ready"] else "no"
            lines.append(
                f"| #{item['number']} {item['title']} | {ready} | {item['routing_reason']} | {label_text} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate provider work queue from GitHub issues")
    parser.add_argument("--scorecard", default=str(SCORECARD_PATH))
    parser.add_argument("--issues-json", help="Optional pre-fetched issue JSON for tests/offline use")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    scorecard = load_json(Path(args.scorecard))
    issues = load_json(Path(args.issues_json)) if args.issues_json else gh_issue_list()
    queue = build_queue(scorecard, issues)

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(queue) + "\n", encoding="utf-8")
        print(f"Markdown → {md_out}")


if __name__ == "__main__":
    main()
