from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = REPO_ROOT / "docs" / "ops" / "cron-process-response.md"
INVENTORY = REPO_ROOT / "docs" / "ops" / "scheduled-tasks.md"


def test_process_response_runbook_has_bounded_snapshot_and_group_guards():
    assert RUNBOOK.exists()
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "ps -eo pid,ppid,pgid,sid,etimes,stat,wchan:24,args" in text
    assert "Never signal the cron daemon's shared process group" in text
    assert "kill -TERM -- -<PGID>" in text
    assert "fresh snapshot" in text
    assert "separate user approval" in text


def test_process_response_runbook_requires_exact_import_timing_evidence():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "python -X importtime" in text
    assert "import-timing" in text
    assert "Do not infer" in text


def test_process_response_runbook_forbids_automatic_escalation():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "No automated SIGKILL" in text
    assert "kill -KILL -- -<PGID>" not in text


def test_scheduled_task_inventory_documents_runtime_contract():
    text = INVENTORY.read_text(encoding="utf-8")
    assert "logs/repository-sync-*.log" in text
    assert "04:25" in text
    assert "bridge-hermes-claude.sh --commit" in text
    for state in (
        "active_within_budget",
        "completed_success",
        "completed_failure",
        "overlap",
        "filesystem_wait",
        "excessive_runtime",
        "stale_or_reused_pid",
    ):
        assert state in text
