from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "provider-session-ecosystem-audit.sh"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def test_wrapper_exists_and_uses_uv_no_project_python() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py" in text
    assert "analysis/provider-session-ecosystem-audit.json" in text
    assert "docs/reports/provider-session-ecosystem-audit.md" in text


def test_schedule_declares_provider_session_ecosystem_audit_task() -> None:
    payload = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    task = next(item for item in tasks if item["id"] == "provider-session-ecosystem-audit")

    assert task["schedule"] == "15 4 * * 1"
    assert task["log"] == "logs/quality/provider-session-ecosystem-audit-*.log"
    assert "bash scripts/cron/provider-session-ecosystem-audit.sh" in task["command"]
