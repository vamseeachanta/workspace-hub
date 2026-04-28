from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_PATH = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
DOCS_PATH = REPO_ROOT / "docs" / "ops" / "scheduled-tasks.md"


def _cron_to_daily_time(cron_expr: str) -> str:
    minute, hour, day_of_month, month, day_of_week = cron_expr.split()
    assert day_of_month == month == day_of_week == "*"
    return f"{int(hour):02d}:{int(minute):02d} daily"


def test_ace_linux_2_harness_update_docs_match_schedule_source() -> None:
    schedule = yaml.safe_load(SCHEDULE_PATH.read_text(encoding="utf-8"))
    harness_update = next(
        task for task in schedule["tasks"] if task["id"] == "harness-update"
    )
    expected = _cron_to_daily_time(
        harness_update["schedule_by_machine"]["ace-linux-2"]
    )

    docs = DOCS_PATH.read_text(encoding="utf-8")
    section = docs.split(
        "## Task Schedule (ace-linux-2 / dev-secondary — contribute variant)", 1
    )[1].split("\n## ", 1)[0]
    row = re.search(r"^\| (?P<time>[^|]+) \| harness-update \|", section, re.M)

    assert row is not None
    assert row.group("time").strip() == expected
