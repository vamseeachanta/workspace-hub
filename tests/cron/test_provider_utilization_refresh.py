from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "provider-utilization-refresh.sh"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def test_wrapper_exists_and_refreshes_quota_and_utilization_artifacts() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "bash scripts/ai/assessment/query-quota.sh --refresh --log" in text
    assert "uv run --no-project python scripts/ai/credit-utilization-tracker.py" in text
    assert "uv run --no-project python scripts/ai/provider-routing-scorecard.py" in text
    assert "uv run --no-project python scripts/ai/provider-work-queue.py" in text
    assert "uv run --no-project python scripts/ai/provider-autolabel.py" in text
    assert "config/ai-tools/provider-utilization-weekly.json" in text
    assert "docs/reports/provider-utilization-weekly.md" in text


def test_schedule_declares_provider_utilization_refresh_task() -> None:
    payload = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    task = next(item for item in tasks if item["id"] == "provider-utilization-refresh")

    assert task["schedule"] == "20 */4 * * *"
    assert task["log"] == "logs/quality/provider-utilization-refresh-*.log"
    assert "bash scripts/cron/provider-utilization-refresh.sh" in task["command"]
