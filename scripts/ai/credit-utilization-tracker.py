#!/usr/bin/env python3
"""Provider utilization tracker for weekly AI credit/usage visibility.

This tracker combines two signal families:
1. Quota snapshots from query-quota.sh / ~/.agent-usage/weekly-log.jsonl
2. Activity from repo-local orchestrator session exports under logs/orchestrator/

Quota-based utilization is preferred when the provider exposes real weekly data
(e.g. Codex week_messages / weekly_limit). When quota is unavailable or only
estimated, the tracker falls back to activity-vs-recent-peak so the weekly
report still provides directional guidance.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE_HUB = Path(
    os.environ.get("WORKSPACE_HUB", str(Path(__file__).resolve().parents[2]))
).resolve()
LOGS_ROOT = WORKSPACE_HUB / "logs" / "orchestrator"
LATEST_QUOTA_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "agent-quota-latest.json"
QUOTA_LOG_PATH = Path.home() / ".agent-usage" / "weekly-log.jsonl"
DEFAULT_JSON_OUT = WORKSPACE_HUB / "config" / "ai-tools" / "provider-utilization-weekly.json"
DEFAULT_MD_OUT = WORKSPACE_HUB / "docs" / "reports" / "provider-utilization-weekly.md"
PROVIDERS = ("claude", "codex", "gemini", "hermes")
UNDERUTIL_THRESHOLD = 15.0

SUBSCRIPTIONS = {
    "claude": {"cost_monthly": 200.0, "plan": "Claude Max"},
    "codex": {"cost_monthly": 40.0, "plan": "OpenAI / Codex subscriptions"},
    "gemini": {"cost_monthly": 20.0, "plan": "Google AI Pro"},
    "hermes": {"cost_monthly": 0.0, "plan": "Orchestrator / no direct subscription"},
}
TOTAL_MONTHLY = sum(item["cost_monthly"] for item in SUBSCRIPTIONS.values())


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            for fmt in ("%Y-%m-%d", "%Y%m%d"):
                try:
                    dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            else:
                return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def week_key(dt: datetime) -> str:
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                records.append(obj)
    return records


def fallback_session_key(provider: str, file_path: Path, obj: dict[str, Any]) -> str:
    session_id = str(obj.get("session_id", "") or "").strip()
    if session_id:
        return session_id
    # Older exported logs may not carry runtime session ids. Fall back to the
    # session file identity instead of per-record timestamps so we do not
    # massively overcount sessions.
    return f"{provider}:{file_path.stem}"


def aggregate_provider_activity(
    logs_root: Path = LOGS_ROOT,
    providers: tuple[str, ...] = PROVIDERS,
) -> dict[str, dict[str, dict[str, Any]]]:
    weekly: dict[str, dict[str, dict[str, Any]]] = {}
    for provider in providers:
        provider_dir = logs_root / provider
        provider_weeks: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "sessions": set(),
                "post_records": 0,
                "tool_counts": Counter(),
                "first_ts": None,
                "last_ts": None,
            }
        )
        for file_path in sorted(provider_dir.glob("session_*.jsonl")):
            with file_path.open("r", encoding="utf-8", errors="replace") as handle:
                for raw in handle:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        obj = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("hook") != "post":
                        continue
                    ts = parse_ts(obj.get("ts"))
                    if ts is None:
                        # fall back to filename day when record timestamp is missing
                        day = file_path.stem.split("_")[-1]
                        ts = parse_ts(day)
                    if ts is None:
                        continue
                    wk = week_key(ts)
                    bucket = provider_weeks[wk]
                    bucket["sessions"].add(fallback_session_key(provider, file_path, obj))
                    bucket["post_records"] += 1
                    bucket["tool_counts"][str(obj.get("tool", "unknown"))] += 1
                    bucket["first_ts"] = min(filter(None, [bucket["first_ts"], ts]), default=ts)
                    bucket["last_ts"] = max(filter(None, [bucket["last_ts"], ts]), default=ts)
        normalized: dict[str, dict[str, Any]] = {}
        for wk, data in provider_weeks.items():
            normalized[wk] = {
                "sessions": len(data["sessions"]),
                "post_records": data["post_records"],
                "top_tools": [{"tool": name, "count": count} for name, count in data["tool_counts"].most_common(5)],
                "first_ts": data["first_ts"].isoformat().replace("+00:00", "Z") if data["first_ts"] else None,
                "last_ts": data["last_ts"].isoformat().replace("+00:00", "Z") if data["last_ts"] else None,
            }
        weekly[provider] = normalized
    return weekly


def quota_snapshot_to_provider_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    providers: dict[str, dict[str, Any]] = {}
    for agent in snapshot.get("agents", []):
        provider = str(agent.get("provider", "") or "").strip()
        if provider:
            providers[provider] = dict(agent)
    return providers


def load_quota_weekly(
    weekly_log_path: Path = QUOTA_LOG_PATH,
    latest_quota_path: Path = LATEST_QUOTA_PATH,
) -> dict[str, dict[str, dict[str, Any]]]:
    weekly: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    snapshots = load_jsonl(weekly_log_path)
    latest = load_json(latest_quota_path)
    if latest:
        snapshots.append(latest)

    for snapshot in snapshots:
        ts = parse_ts(snapshot.get("timestamp"))
        if ts is None:
            continue
        wk = week_key(ts)
        providers = quota_snapshot_to_provider_map(snapshot)
        for provider, agent in providers.items():
            existing = weekly[wk].get(provider)
            current = dict(agent)
            current["snapshot_ts"] = ts.isoformat().replace("+00:00", "Z")
            if existing is None:
                weekly[wk][provider] = current
                continue
            existing_ts = parse_ts(existing.get("snapshot_ts")) or datetime.min.replace(tzinfo=timezone.utc)
            if ts >= existing_ts:
                merged = dict(existing)
                merged.update(current)
            else:
                merged = dict(current)
                merged.update(existing)
            for numeric_key in ("week_messages", "today_messages"):
                existing_value = existing.get(numeric_key)
                current_value = current.get(numeric_key)
                numeric_values = [value for value in (existing_value, current_value) if isinstance(value, (int, float))]
                if numeric_values:
                    merged[numeric_key] = max(numeric_values)
                else:
                    merged.pop(numeric_key, None)
            weekly[wk][provider] = merged
    return {wk: providers for wk, providers in weekly.items()}


def compute_quota_utilization(snapshot: dict[str, Any] | None) -> tuple[float | None, str, str]:
    if not snapshot:
        return None, "unavailable", "no quota snapshot"
    source = str(snapshot.get("source", "") or "unavailable")
    week_pct = snapshot.get("week_pct")
    if isinstance(week_pct, (int, float)):
        return float(week_pct), "quota", f"week_pct from {source}"
    week_messages = snapshot.get("week_messages")
    weekly_limit = snapshot.get("weekly_limit")
    if isinstance(week_messages, (int, float)) and isinstance(weekly_limit, (int, float)) and weekly_limit:
        pct = (float(week_messages) / float(weekly_limit)) * 100.0
        return min(100.0, pct), "quota", f"week_messages/weekly_limit from {source}"
    today_messages = snapshot.get("today_messages")
    daily_limit = snapshot.get("daily_limit")
    if isinstance(today_messages, (int, float)) and isinstance(daily_limit, (int, float)) and daily_limit:
        pct = (float(today_messages) / float(daily_limit)) * 100.0
        return min(100.0, pct), "estimated_daily_quota", f"today_messages/daily_limit from {source}"
    pct_remaining = snapshot.get("pct_remaining")
    if isinstance(pct_remaining, (int, float)):
        pct = max(0.0, 100.0 - float(pct_remaining))
        return pct, "remaining_pct", f"100-pct_remaining from {source}"
    return None, "unavailable", f"quota unavailable from {source}"


def summarize_provider_week(
    provider: str,
    week: str,
    activity: dict[str, Any],
    quota_snapshot: dict[str, Any] | None,
    activity_peak_by_provider: dict[str, int],
) -> dict[str, Any]:
    sessions = int(activity.get("sessions", 0) or 0)
    post_records = int(activity.get("post_records", 0) or 0)
    peak = max(1, int(activity_peak_by_provider.get(provider, 0) or 0))
    activity_pct = round((post_records / peak) * 100.0, 1) if post_records else 0.0
    quota_pct, quota_basis, quota_note = compute_quota_utilization(quota_snapshot)

    reported_pct = activity_pct
    utilization_basis = "activity_vs_recent_peak"
    if quota_pct is not None and quota_basis == "quota":
        reported_pct = round(quota_pct, 1)
        utilization_basis = quota_basis

    note_parts = [quota_note]
    if utilization_basis != "quota":
        note_parts.append("using activity fallback")

    return {
        "provider": provider,
        "week": week,
        "sessions": sessions,
        "post_records": post_records,
        "activity_utilization_pct": activity_pct,
        "quota_utilization_pct": round(quota_pct, 1) if quota_pct is not None else None,
        "reported_utilization_pct": reported_pct,
        "utilization_basis": utilization_basis,
        "quota_basis": quota_basis,
        "quota_source": (quota_snapshot or {}).get("source", "unavailable"),
        "quota_snapshot_ts": (quota_snapshot or {}).get("snapshot_ts"),
        "top_tools": activity.get("top_tools", []),
        "first_ts": activity.get("first_ts"),
        "last_ts": activity.get("last_ts"),
        "note": "; ".join(part for part in note_parts if part),
    }


def build_report(
    weeks_back: int = 8,
    logs_root: Path = LOGS_ROOT,
    weekly_log_path: Path = QUOTA_LOG_PATH,
    latest_quota_path: Path = LATEST_QUOTA_PATH,
) -> dict[str, Any]:
    activity_by_provider = aggregate_provider_activity(logs_root=logs_root)
    quota_by_week = load_quota_weekly(weekly_log_path=weekly_log_path, latest_quota_path=latest_quota_path)

    all_weeks = set(quota_by_week.keys())
    for provider_data in activity_by_provider.values():
        all_weeks.update(provider_data.keys())
    all_weeks = sorted(all_weeks)
    if weeks_back > 0:
        all_weeks = all_weeks[-weeks_back:]

    activity_peak_by_provider = {
        provider: max((week_data.get("post_records", 0) for week_data in provider_data.values()), default=0)
        for provider, provider_data in activity_by_provider.items()
    }

    now = datetime.now(timezone.utc)
    current_week = week_key(now)
    weekly_data: dict[str, dict[str, Any]] = {}
    alerts: list[dict[str, Any]] = []

    for wk in all_weeks:
        week_payload: dict[str, Any] = {}
        for provider in PROVIDERS:
            activity = activity_by_provider.get(provider, {}).get(wk, {})
            quota_snapshot = quota_by_week.get(wk, {}).get(provider)
            summary = summarize_provider_week(
                provider=provider,
                week=wk,
                activity=activity,
                quota_snapshot=quota_snapshot,
                activity_peak_by_provider=activity_peak_by_provider,
            )
            week_payload[provider] = summary
            if wk == current_week and summary["reported_utilization_pct"] < UNDERUTIL_THRESHOLD and provider != "hermes":
                alerts.append(
                    {
                        "provider": provider,
                        "reported_utilization_pct": summary["reported_utilization_pct"],
                        "basis": summary["utilization_basis"],
                        "message": f"{provider} at {summary['reported_utilization_pct']}% ({summary['utilization_basis']})",
                    }
                )
        weekly_data[wk] = week_payload

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "current_week": current_week,
        "report_weeks": weeks_back,
        "subscriptions": SUBSCRIPTIONS,
        "total_monthly_spend": TOTAL_MONTHLY,
        "weekly_data": weekly_data,
        "underutilization_alerts": alerts,
        "paths": {
            "logs_root": str(logs_root),
            "quota_weekly_log": str(weekly_log_path),
            "quota_latest": str(latest_quota_path),
        },
    }


def utilization_bar(value: float | None) -> str:
    if value is None:
        return "n/a"
    cells = max(0, min(10, int(round(value / 10.0))))
    return "█" * cells + "░" * (10 - cells)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Provider utilization weekly report",
        "",
        f"Generated: {report['generated_at']}",
        f"Current week: {report['current_week']}",
        f"Total monthly spend tracked: ${report['total_monthly_spend']}/mo",
        "",
        "Quota-based utilization is preferred when available; otherwise the report falls back to activity-vs-recent-peak based on exported session logs.",
        "",
    ]
    for wk in sorted(report["weekly_data"].keys(), reverse=True):
        marker = " (current)" if wk == report["current_week"] else ""
        lines.extend(
            [
                f"## {wk}{marker}",
                "",
                "| Provider | Sessions | Post records | Reported util | Basis | Quota util | Notes |",
                "|---|---:|---:|---:|---|---:|---|",
            ]
        )
        for provider in PROVIDERS:
            item = report["weekly_data"][wk][provider]
            quota_display = "n/a" if item["quota_utilization_pct"] is None else f"{item['quota_utilization_pct']:.1f}%"
            lines.append(
                f"| {provider} | {item['sessions']} | {item['post_records']} | {item['reported_utilization_pct']:.1f}% | {item['utilization_basis']} | {quota_display} | {item['note']} |"
            )
        lines.append("")

    if report["underutilization_alerts"]:
        lines.append("## Current-week underutilization alerts")
        lines.append("")
        for alert in report["underutilization_alerts"]:
            lines.append(f"- {alert['message']}")
        lines.append("")

    return "\n".join(lines)


def render_dashboard(report: dict[str, Any]) -> str:
    wk = report["current_week"]
    lines = [
        f"Provider utilization dashboard — {wk}",
        f"Total monthly spend tracked: ${report['total_monthly_spend']}/mo",
        "",
        "provider   sessions  records  util   basis",
        "---------  --------  -------  -----  ------------------------",
    ]
    for provider in PROVIDERS:
        item = report["weekly_data"].get(wk, {}).get(provider, {})
        util = item.get("reported_utilization_pct")
        util_text = "n/a" if util is None else f"{util:5.1f}%"
        lines.append(
            f"{provider:<9}  {item.get('sessions', 0):>8}  {item.get('post_records', 0):>7}  {utilization_bar(util) if util is not None else 'n/a':<10} {item.get('utilization_basis', 'n/a')}"
        )
        lines.append(f"{'':<9}  {'':>8}  {'':>7}  {util_text:<10} {item.get('note', '')}")
    if report["underutilization_alerts"]:
        lines.append("")
        lines.append("alerts:")
        for alert in report["underutilization_alerts"]:
            lines.append(f"- {alert['message']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly provider utilization tracker")
    parser.add_argument("--weeks", type=int, default=8, help="Weeks of history to include")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON_OUT), help="JSON output path")
    parser.add_argument("--output-md", default=str(DEFAULT_MD_OUT), help="Markdown output path")
    parser.add_argument("--dashboard", action="store_true", help="Print compact terminal dashboard")
    parser.add_argument("--json-only", action="store_true", help="Write only JSON, skip markdown")
    args = parser.parse_args()

    report = build_report(weeks_back=args.weeks)
    if args.dashboard:
        print(render_dashboard(report))
        return

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {output_json}")

    if not args.json_only:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(render_markdown(report) + "\n", encoding="utf-8")
        print(f"Markdown → {output_md}")

    if report["underutilization_alerts"]:
        print(f"\nAlerts: {len(report['underutilization_alerts'])}")
        for alert in report["underutilization_alerts"]:
            print(f"- {alert['message']}")


if __name__ == "__main__":
    main()
