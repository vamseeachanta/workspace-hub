#!/usr/bin/env python3
"""Generate a provider routing scorecard from utilization + audit artifacts.

Purpose:
- translate provider utilization and session-audit telemetry into actionable routing
  guidance for Claude, Codex, Gemini, and Hermes
- surface who should receive the next work packets
- keep recommendations grounded in tracked telemetry instead of intuition
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
UTILIZATION_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-utilization-weekly.json"
AUDIT_PATH = WORKSPACE_HUB / "analysis" / "provider-session-ecosystem-audit.json"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-routing-scorecard.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-routing-scorecard.md"
TARGET_PROVIDERS = ("claude", "codex", "gemini")

ROUTING_RULES = {
    "claude": {
        "preferred_work": [
            "adversarial plan review",
            "adversarial implementation review",
            "long-context synthesis",
            "complex repo strategy and architecture",
        ],
        "avoid_when_underutilized": [
            "bounded test-fix loops",
            "mechanical refactors",
            "commodity grep/read sweeps",
        ],
    },
    "codex": {
        "preferred_work": [
            "bounded implementation",
            "test writing and repair",
            "mechanical cleanup/refactors",
            "issue execution with crisp scope",
        ],
        "avoid_when_underutilized": [
            "large open-ended research",
            "broad ecosystem synthesis",
        ],
    },
    "gemini": {
        "preferred_work": [
            "batched research/recon",
            "risk enumeration",
            "competitor/standards scans",
            "issue expansion and scouting",
        ],
        "avoid_when_underutilized": [
            "high-volume mechanical coding",
            "tight verification loops",
        ],
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_provider_metrics(utilization: dict[str, Any], provider: str) -> dict[str, Any]:
    week = utilization["current_week"]
    return dict(utilization["weekly_data"][week][provider])


def audit_metrics(audit: dict[str, Any], provider: str) -> dict[str, Any]:
    providers = audit.get("providers", {})
    return dict(providers.get(provider, {}))


def classify_status(reported_util: float, quota_basis: str, missing_reads: int, python3_calls: int, post_records: int) -> str:
    density = (python3_calls / post_records * 1000.0) if post_records else 0.0
    if quota_basis == "quota" and reported_util < 10:
        return "underused"
    if reported_util < 5:
        return "underused"
    if missing_reads > 1000 or density > 25:
        return "needs_cleanup"
    if reported_util >= 40 and missing_reads < 200:
        return "healthy"
    return "watch"


def build_recommendation(provider: str, metrics: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    reported = float(metrics.get("reported_utilization_pct") or 0.0)
    quota_basis = str(metrics.get("quota_basis") or "unavailable")
    missing_reads = int(audit.get("missing_repo_reads") or 0)
    post_records = int(audit.get("post_records") or 0)
    python3_calls = int(audit.get("python3_bash_calls") or 0)
    density = round((python3_calls / post_records * 1000.0), 2) if post_records else 0.0
    migration_density = 0.0
    top_hint = None
    hints = audit.get("missing_repo_read_remediation_hints") or []
    if hints:
        mapped_reads = sum(int(item.get("total_count") or 0) for item in hints)
        migration_density = round((mapped_reads / post_records * 1000.0), 2) if post_records else 0.0
        top_hint = hints[0].get("rule_id")

    status = classify_status(reported, quota_basis, missing_reads, python3_calls, post_records)

    priority = "medium"
    if provider in {"codex", "gemini"} and reported < 15:
        priority = "highest"
    elif provider == "claude" and reported < 15:
        priority = "high"
    elif status == "needs_cleanup":
        priority = "high"

    recommendation = {
        "provider": provider,
        "status": status,
        "priority": priority,
        "reported_utilization_pct": reported,
        "quota_basis": quota_basis,
        "quota_source": metrics.get("quota_source"),
        "sessions_current_week": metrics.get("sessions", 0),
        "post_records_current_week": metrics.get("post_records", 0),
        "audit_post_records": post_records,
        "missing_repo_reads": missing_reads,
        "python3_per_1k_records": density,
        "migration_debt_per_1k_records": migration_density,
        "top_migration_hint": top_hint,
        "top_tools": metrics.get("top_tools") or audit.get("top_tools") or [],
        "preferred_work": ROUTING_RULES[provider]["preferred_work"],
        "avoid_work": ROUTING_RULES[provider]["avoid_when_underutilized"],
        "actions": [],
    }

    if provider == "codex":
        recommendation["actions"].extend(
            [
                "Route bounded implementation/test/refactor issues to Codex immediately.",
                "Use Codex for repetitive repo-hardening tasks before spending more Claude review cycles.",
            ]
        )
    elif provider == "gemini":
        recommendation["actions"].extend(
            [
                "Batch 5-6 related research/recon tasks into Gemini sessions.",
                "Use Gemini for scouting/risk-analysis packets instead of leaving the lane idle.",
            ]
        )
    elif provider == "claude":
        recommendation["actions"].extend(
            [
                "Reserve Claude for adversarial review, plan review, and long-context synthesis.",
                "Do not burn Claude on mechanical loops that Codex can absorb.",
            ]
        )

    if missing_reads > 1000:
        recommendation["actions"].append("Reduce stale-path drift before increasing provider load; wasted reads are burning credits.")
    if quota_basis in {"unavailable", "estimated_daily_quota", "remaining_pct"}:
        recommendation["actions"].append("Telemetry is weak; treat utilization as directional, not exact weekly headroom.")

    return recommendation


def build_scorecard(utilization: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    recommendations = []
    for provider in TARGET_PROVIDERS:
        recommendations.append(
            build_recommendation(
                provider,
                latest_provider_metrics(utilization, provider),
                audit_metrics(audit, provider),
            )
        )

    recommended_order = sorted(
        recommendations,
        key=lambda item: (
            {"highest": 0, "high": 1, "medium": 2, "low": 3}.get(item["priority"], 9),
            item["reported_utilization_pct"],
        ),
    )

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": now,
        "current_week": utilization["current_week"],
        "inputs": {
            "utilization_path": str(UTILIZATION_PATH),
            "audit_path": str(AUDIT_PATH),
            "utilization_generated_at": utilization.get("generated_at"),
            "audit_generated_at": audit.get("generated_at"),
        },
        "recommended_provider_order": [item["provider"] for item in recommended_order],
        "recommendations": recommendations,
        "summary": {
            "highest_priority_provider": recommended_order[0]["provider"] if recommended_order else None,
            "highest_priority_reason": recommended_order[0]["actions"][0] if recommended_order else None,
        },
    }


def render_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Provider routing scorecard",
        "",
        f"Generated: {scorecard['generated_at']}",
        f"Current week: {scorecard['current_week']}",
        f"Recommended provider order: {', '.join(scorecard['recommended_provider_order'])}",
        "",
        "This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.",
        "",
    ]
    for item in scorecard["recommendations"]:
        lines.extend(
            [
                f"## {item['provider']}",
                "",
                f"- Status: {item['status']}",
                f"- Priority: {item['priority']}",
                f"- Current-week reported utilization: {item['reported_utilization_pct']}%",
                f"- Quota basis: {item['quota_basis']} ({item['quota_source']})",
                f"- Current-week sessions / post records: {item['sessions_current_week']} / {item['post_records_current_week']}",
                f"- Audit post records: {item['audit_post_records']}",
                f"- Missing repo reads: {item['missing_repo_reads']}",
                f"- Python3 per 1k records: {item['python3_per_1k_records']}",
                f"- Migration debt per 1k records: {item['migration_debt_per_1k_records']}",
                "",
                "### Preferred work",
            ]
        )
        lines.extend([f"- {entry}" for entry in item["preferred_work"]])
        lines.extend(["", "### Avoid", *[f"- {entry}" for entry in item["avoid_work"]], "", "### Recommended actions"])
        lines.extend([f"- {entry}" for entry in item["actions"]])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate provider routing scorecard")
    parser.add_argument("--utilization", default=str(UTILIZATION_PATH))
    parser.add_argument("--audit", default=str(AUDIT_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    utilization = load_json(Path(args.utilization))
    audit = load_json(Path(args.audit))
    scorecard = build_scorecard(utilization, audit)

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(scorecard, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {json_out}")

    if not args.json_only:
        md_out = Path(args.output_md)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(scorecard) + "\n", encoding="utf-8")
        print(f"Markdown → {md_out}")


if __name__ == "__main__":
    main()
