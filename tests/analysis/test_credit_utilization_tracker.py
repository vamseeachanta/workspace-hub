from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "credit-utilization-tracker.py"
spec = importlib.util.spec_from_file_location("credit_utilization_tracker", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(__import__("json").dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_aggregate_provider_activity_counts_unique_sessions_and_post_records(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs" / "orchestrator"
    rows = [
        {"hook": "post", "ts": "2026-04-13T10:00:00Z", "session_id": "c1", "tool": "Bash"},
        {"hook": "post", "ts": "2026-04-13T10:05:00Z", "session_id": "c1", "tool": "Read"},
        {"hook": "post", "ts": "2026-04-14T09:00:00Z", "session_id": "c2", "tool": "Write"},
        {"hook": "pre", "ts": "2026-04-14T09:00:00Z", "session_id": "ignored", "tool": "Write"},
    ]
    write_jsonl(logs_root / "codex" / "session_20260414.jsonl", rows)

    weekly = module.aggregate_provider_activity(logs_root=logs_root, providers=("codex",))

    assert weekly["codex"]["2026-W16"]["sessions"] == 2
    assert weekly["codex"]["2026-W16"]["post_records"] == 3
    assert weekly["codex"]["2026-W16"]["top_tools"][0]["count"] == 1


def test_load_quota_weekly_uses_latest_snapshot_and_max_week_messages(tmp_path: Path) -> None:
    weekly_log = tmp_path / "weekly-log.jsonl"
    latest_quota = tmp_path / "agent-quota-latest.json"
    weekly_log.write_text(
        "\n".join(
            [
                '{"timestamp":"2026-04-13T01:00:00Z","agents":[{"provider":"codex","weekly_limit":1400,"week_messages":10,"pct_remaining":99,"source":"history.jsonl"}]}',
                '{"timestamp":"2026-04-13T05:00:00Z","agents":[{"provider":"codex","weekly_limit":1400,"week_messages":40,"pct_remaining":97,"source":"history.jsonl"}]}'
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    latest_quota.write_text(
        '{"timestamp":"2026-04-13T06:00:00Z","agents":[{"provider":"codex","weekly_limit":1400,"week_messages":42,"pct_remaining":97,"source":"history.jsonl"}]}\n',
        encoding="utf-8",
    )

    weekly = module.load_quota_weekly(weekly_log_path=weekly_log, latest_quota_path=latest_quota)
    codex = weekly["2026-W16"]["codex"]

    assert codex["week_messages"] == 42
    assert codex["snapshot_ts"] == "2026-04-13T06:00:00Z"


def test_build_report_prefers_quota_for_codex_and_activity_fallback_for_claude(tmp_path: Path) -> None:
    logs_root = tmp_path / "logs" / "orchestrator"
    write_jsonl(
        logs_root / "claude" / "session_20260413.jsonl",
        [
            {"hook": "post", "ts": "2026-04-13T08:00:00Z", "session_id": "claude-1", "tool": "Bash"},
            {"hook": "post", "ts": "2026-04-13T08:05:00Z", "session_id": "claude-1", "tool": "Read"},
        ],
    )
    write_jsonl(
        logs_root / "codex" / "session_20260413.jsonl",
        [{"hook": "post", "ts": "2026-04-13T09:00:00Z", "session_id": "codex-1", "tool": "Bash"}],
    )
    weekly_log = tmp_path / "weekly-log.jsonl"
    weekly_log.write_text(
        '{"timestamp":"2026-04-13T06:00:00Z","agents":[{"provider":"codex","weekly_limit":1400,"week_messages":140,"pct_remaining":90,"source":"history.jsonl"},{"provider":"claude","weekly_limit":20000,"pct_remaining":null,"source":"unavailable"}]}\n',
        encoding="utf-8",
    )
    latest_quota = tmp_path / "agent-quota-latest.json"
    latest_quota.write_text('{"timestamp":"2026-04-13T06:00:00Z","agents":[]}\n', encoding="utf-8")

    report = module.build_report(
        weeks_back=2,
        logs_root=logs_root,
        weekly_log_path=weekly_log,
        latest_quota_path=latest_quota,
    )
    week = report["weekly_data"]["2026-W16"]

    assert week["codex"]["utilization_basis"] == "quota"
    assert week["codex"]["reported_utilization_pct"] == 10.0
    assert week["claude"]["utilization_basis"] == "activity_vs_recent_peak"
    assert week["claude"]["reported_utilization_pct"] == 100.0
