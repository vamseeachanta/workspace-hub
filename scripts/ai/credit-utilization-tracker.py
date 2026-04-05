#!/usr/bin/env python3
"""Weekly AI credit utilization tracker.

Aggregates usage data across all AI providers and generates weekly
utilization reports. All providers are subscription-based (fixed monthly cost),
so "utilization" measures activity level vs the fixed fee — not pay-per-token cost.

Usage:
    uv run scripts/ai/credit-utilization-tracker.py --dashboard
    uv run scripts/ai/credit-utilization-tracker.py --weeks 5
    uv run scripts/ai/credit-utilization-tracker.py --output-json config/ai-tools/weekly-utilization.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────
WORKSPACE_HUB = os.environ.get(
    "WORKSPACE_HUB",
    str(Path(__file__).resolve().parent.parent.parent),
)

SUBSCRIPTIONS = {
    "claude": {"cost_monthly": 200.0, "plan": "Claude Max $200/mo"},
    "codex": {"cost_monthly": 40.0, "plan": "OpenAI x2 ($20/mo each)"},
    "gemini": {"cost_monthly": 20.0, "plan": "Google AI Pro $20/mo"},
    "copilot": {"cost_monthly": 9.0, "plan": "GitHub Copilot $9/mo (annual)"},
}
TOTAL_MONTHLY = sum(s["cost_monthly"] for s in SUBSCRIPTIONS.values())

COST_TRACKING_PATH = os.path.join(
    WORKSPACE_HUB, ".claude/state/session-signals/cost-tracking.jsonl"
)
CODEX_HISTORY_PATH = os.path.join(
    WORKSPACE_HUB, "config/agents/codex/state-snapshots/history.jsonl"
)

DEFAULT_JSON_OUT = os.path.join(
    WORKSPACE_HUB, "config/ai-tools/weekly-utilization.json"
)
DEFAULT_MD_OUT = os.path.join(
    WORKSPACE_HUB, "notes/ai-credit-utilization-weekly.md"
)

UNDERUTIL_THRESHOLD = 0.15  # Alert if <15% weekly utilization


# ── Data loaders ──────────────────────────────────────────────────────────────
def _load_jsonl(path: str, max_lines: int = 0) -> list[dict]:
    """Load a JSONL file, skipping malformed lines."""
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if max_lines and len(records) >= max_lines:
                break
    return records


def _week_key(dt: datetime) -> str:
    """ISO week key like '2026-W14'."""
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _parse_ts(ts_val) -> datetime | None:
    """Parse various timestamp formats."""
    if isinstance(ts_val, (int, float)):
        return datetime.utcfromtimestamp(ts_val)
    if isinstance(ts_val, str):
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(ts_val, fmt)
            except ValueError:
                continue
    return None


# ── Aggregation ───────────────────────────────────────────────────────────────
def aggregate_claude(weeks_back: int = 5) -> dict[str, dict]:
    """Aggregate Claude usage from cost-tracking.jsonl by week."""
    cutoff = datetime.utcnow() - timedelta(weeks=weeks_back)
    records = _load_jsonl(COST_TRACKING_PATH)
    weekly: dict[str, dict] = defaultdict(
        lambda: {"sessions": set(), "input_tokens": 0, "output_tokens": 0, "records": 0}
    )
    for rec in records:
        ts = _parse_ts(rec.get("ts") or rec.get("run_ts"))
        if not ts or ts < cutoff:
            continue
        wk = _week_key(ts)
        weekly[wk]["sessions"].add(rec.get("session_id", ""))
        weekly[wk]["input_tokens"] += rec.get("input_tokens", 0)
        weekly[wk]["output_tokens"] += rec.get("output_tokens", 0)
        weekly[wk]["records"] += 1

    result = {}
    for wk, data in weekly.items():
        total_tokens = data["input_tokens"] + data["output_tokens"]
        session_count = len(data["sessions"])
        # Utilization heuristic: sessions per week / expected sessions
        # With $200/mo, expect ~150+ sessions/week for heavy usage
        utilization = min(1.0, session_count / 150.0)
        result[wk] = {
            "provider": "claude",
            "sessions": session_count,
            "input_tokens": data["input_tokens"],
            "output_tokens": data["output_tokens"],
            "total_tokens": total_tokens,
            "records": data["records"],
            "utilization_pct": round(utilization * 100, 1),
        }
    return result


def aggregate_codex(weeks_back: int = 5) -> dict[str, dict]:
    """Aggregate Codex usage from history.jsonl by week."""
    cutoff = datetime.utcnow() - timedelta(weeks=weeks_back)
    records = _load_jsonl(CODEX_HISTORY_PATH)
    weekly: dict[str, dict] = defaultdict(
        lambda: {"sessions": set(), "messages": 0}
    )
    for rec in records:
        ts = _parse_ts(rec.get("ts"))
        if not ts or ts < cutoff:
            continue
        wk = _week_key(ts)
        weekly[wk]["sessions"].add(rec.get("session_id", ""))
        weekly[wk]["messages"] += 1

    result = {}
    for wk, data in weekly.items():
        session_count = len(data["sessions"])
        # With $40/mo (2 subs), expect ~50+ sessions/week for decent usage
        utilization = min(1.0, session_count / 50.0)
        result[wk] = {
            "provider": "codex",
            "sessions": session_count,
            "messages": data["messages"],
            "utilization_pct": round(utilization * 100, 1),
        }
    return result


def aggregate_gemini(weeks_back: int = 5) -> dict[str, dict]:
    """Gemini usage — no automated data source yet."""
    # Return placeholder for current week
    now = datetime.utcnow()
    wk = _week_key(now)
    return {
        wk: {
            "provider": "gemini",
            "sessions": 0,
            "messages": 0,
            "utilization_pct": 0.0,
            "data_source": "none",
            "manual_entry_required": True,
            "note": "No automated Gemini tracking yet. Usage via h-gemini alias or Copilot proxy is untracked.",
        }
    }


def aggregate_copilot(weeks_back: int = 5) -> dict[str, dict]:
    """Copilot usage — tracked indirectly via Hermes delegation logs."""
    # Copilot usage shows up in Hermes logs when provider=copilot is used
    # For now, placeholder — will be enriched when Hermes logs are parsed
    now = datetime.utcnow()
    wk = _week_key(now)
    return {
        wk: {
            "provider": "copilot",
            "sessions": 0,
            "messages": 0,
            "utilization_pct": 0.0,
            "data_source": "hermes_delegation_logs",
            "manual_entry_required": True,
            "note": "Copilot usage via Hermes delegation (provider=copilot). Tracking TBD.",
        }
    }


# ── Report generation ─────────────────────────────────────────────────────────
def build_report(weeks_back: int = 5) -> dict:
    """Build unified utilization report."""
    claude = aggregate_claude(weeks_back)
    codex = aggregate_codex(weeks_back)
    gemini = aggregate_gemini(weeks_back)
    copilot = aggregate_copilot(weeks_back)

    # Collect all weeks
    all_weeks = sorted(set(list(claude.keys()) + list(codex.keys()) + list(gemini.keys()) + list(copilot.keys())))

    # Current week
    now = datetime.utcnow()
    current_week = _week_key(now)

    weekly_data = {}
    alerts = []
    for wk in all_weeks:
        wk_data = {
            "claude": claude.get(wk, {"provider": "claude", "sessions": 0, "utilization_pct": 0.0}),
            "codex": codex.get(wk, {"provider": "codex", "sessions": 0, "utilization_pct": 0.0}),
            "gemini": gemini.get(wk, {"provider": "gemini", "sessions": 0, "utilization_pct": 0.0}),
            "copilot": copilot.get(wk, {"provider": "copilot", "sessions": 0, "utilization_pct": 0.0}),
        }
        weekly_data[wk] = wk_data

        # Check for underutilization in the current week
        if wk == current_week:
            for provider, pdata in wk_data.items():
                util = pdata.get("utilization_pct", 0)
                if util < UNDERUTIL_THRESHOLD * 100:
                    alerts.append({
                        "provider": provider,
                        "utilization_pct": util,
                        "threshold_pct": UNDERUTIL_THRESHOLD * 100,
                        "message": f"{provider} at {util}% utilization (threshold: {UNDERUTIL_THRESHOLD*100}%)",
                        "subscription_cost": SUBSCRIPTIONS.get(provider, {}).get("cost_monthly", 0),
                    })

    report = {
        "generated_at": now.isoformat() + "Z",
        "report_weeks": weeks_back,
        "current_week": current_week,
        "subscriptions": SUBSCRIPTIONS,
        "total_monthly_spend": TOTAL_MONTHLY,
        "weekly_data": weekly_data,
        "underutilization_alerts": alerts,
    }
    return report


def render_markdown(report: dict) -> str:
    """Render report as markdown."""
    lines = [
        f"# AI Credit Utilization Report",
        f"",
        f"Generated: {report['generated_at']}",
        f"Current week: {report['current_week']}",
        f"Total monthly spend: ${report['total_monthly_spend']}/mo (fixed subscriptions)",
        f"",
        f"## Subscriptions",
        f"",
        f"| Provider | Monthly Cost | Plan |",
        f"|----------|-------------|------|",
    ]
    for prov, info in report["subscriptions"].items():
        lines.append(f"| {prov} | ${info['cost_monthly']}/mo | {info['plan']} |")
    lines.append(f"| **Total** | **${report['total_monthly_spend']}/mo** | |")
    lines.append("")

    lines.append("## Weekly Utilization")
    lines.append("")

    for wk in sorted(report["weekly_data"].keys(), reverse=True):
        wk_data = report["weekly_data"][wk]
        marker = " **(current)**" if wk == report["current_week"] else ""
        lines.append(f"### {wk}{marker}")
        lines.append("")
        lines.append("| Provider | Sessions | Utilization | Notes |")
        lines.append("|----------|----------|-------------|-------|")
        for prov in ["claude", "codex", "gemini", "copilot"]:
            pd = wk_data.get(prov, {})
            sess = pd.get("sessions", 0)
            util = pd.get("utilization_pct", 0)
            note = pd.get("note", "")
            bar = "█" * int(util / 10) + "░" * (10 - int(util / 10))
            flag = " ⚠️" if util < UNDERUTIL_THRESHOLD * 100 else ""
            lines.append(f"| {prov} | {sess} | {bar} {util}%{flag} | {note} |")
        lines.append("")

    if report["underutilization_alerts"]:
        lines.append("## ⚠️ Underutilization Alerts")
        lines.append("")
        for alert in report["underutilization_alerts"]:
            lines.append(f"- **{alert['provider']}**: {alert['message']} — ${alert['subscription_cost']}/mo at risk")
        lines.append("")

    return "\n".join(lines)


def render_dashboard(report: dict) -> str:
    """Compact terminal dashboard for current week."""
    wk = report["current_week"]
    wk_data = report["weekly_data"].get(wk, {})

    lines = [
        f"╔══════════════════════════════════════════════════╗",
        f"║  AI Credit Utilization Dashboard — {wk}      ║",
        f"║  Total: ${report['total_monthly_spend']}/mo fixed                       ║",
        f"╠══════════════════════════════════════════════════╣",
        f"║ Provider   │ $/mo │ Sessions │ Utilization      ║",
        f"╟────────────┼──────┼──────────┼──────────────────╢",
    ]
    for prov in ["claude", "codex", "gemini", "copilot"]:
        pd = wk_data.get(prov, {})
        sess = pd.get("sessions", 0)
        util = pd.get("utilization_pct", 0)
        cost = SUBSCRIPTIONS.get(prov, {}).get("cost_monthly", 0)
        bar = "█" * int(util / 10) + "░" * (10 - int(util / 10))
        flag = "⚠" if util < UNDERUTIL_THRESHOLD * 100 else " "
        lines.append(
            f"║ {prov:<10} │ {cost:>4.0f} │ {sess:>8} │ {bar} {util:>5.1f}%{flag}║"
        )
    lines.append(f"╚══════════════════════════════════════════════════╝")

    if report["underutilization_alerts"]:
        lines.append("")
        lines.append("ALERTS:")
        for alert in report["underutilization_alerts"]:
            lines.append(f"  ⚠ {alert['message']}")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AI credit utilization tracker — weekly snapshots across all providers"
    )
    parser.add_argument("--weeks", type=int, default=5, help="Weeks of history (default: 5)")
    parser.add_argument("--output-json", default=DEFAULT_JSON_OUT, help="JSON output path")
    parser.add_argument("--output-md", default=DEFAULT_MD_OUT, help="Markdown output path")
    parser.add_argument("--dashboard", action="store_true", help="Print compact terminal dashboard")
    parser.add_argument("--json-only", action="store_true", help="Only output JSON, no markdown")
    args = parser.parse_args()

    report = build_report(args.weeks)

    if args.dashboard:
        print(render_dashboard(report))
        return

    # Write JSON
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"JSON → {args.output_json}")

    # Write markdown
    if not args.json_only:
        os.makedirs(os.path.dirname(args.output_md), exist_ok=True)
        md = render_markdown(report)
        with open(args.output_md, "w") as f:
            f.write(md)
        print(f"Markdown → {args.output_md}")

    # Print alerts
    if report["underutilization_alerts"]:
        print(f"\n⚠️  {len(report['underutilization_alerts'])} underutilization alert(s):")
        for alert in report["underutilization_alerts"]:
            print(f"  - {alert['message']}")


if __name__ == "__main__":
    main()
