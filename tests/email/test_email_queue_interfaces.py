import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.email.email_queue_helpers import load_queue_state, write_accounts


def test_label_plan_covers_read_assist_accounts_and_uses_separate_clients(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)

    class FakeClient:
        def __init__(self):
            self.labels = []

        def ensure_label(self, label):
            self.labels.append(label)

    clients = {"ace": FakeClient(), "personal": FakeClient(), "skestates": FakeClient()}
    result = queue_state.ensure_labels(
        account_scope=queue_state.load_account_scope(config),
        clients_by_account=clients,
        apply=True,
    )

    account_ids = {op["account_id"] for op in result["operations"]}
    labels = {op["label"] for op in result["operations"]}
    assert account_ids == {"ace", "personal", "skestates"}
    assert labels == {
        "wh-email/extracted",
        "wh-email/awaiting-reply",
        "wh-email/completed",
        "wh-email/noise",
    }
    assert clients["ace"].labels == clients["personal"].labels
    assert clients["skestates"].labels == clients["personal"].labels


def test_label_apply_fails_on_account_mapping_disagreement(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)

    with pytest.raises(queue_state.AccountMappingError):
        queue_state.ensure_labels(
            account_scope=queue_state.load_account_scope(config),
            clients_by_account={"ace": object(), "personal": object()},
            helper_account_map={"ace": "wrong@example.com"},
            apply=True,
        )


def test_cli_wrapper_dispatches_to_importable_main():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "email" / "email-queue-state.py"

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0
    assert "report" in result.stdout


def test_cli_rejects_apply_and_dry_run_together():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "email" / "email-queue-state.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "sweep",
            "--apply",
            "--dry-run",
            "--now-utc",
            "2026-06-14T00:00:00Z",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2


def test_cli_apply_requires_precheck_without_traceback(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "email" / "email-queue-state.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--state-dir",
            str(tmp_path),
            "sweep",
            "--apply",
            "--now-utc",
            "2026-06-14T00:00:00Z",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2
    assert "reactivation precheck" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_notify_attention_dry_run_outputs_skestates_event(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "email" / "email-queue-state.py"
    queue_state = load_queue_state()
    write_accounts(tmp_path / "accounts.yaml")
    queue_state.transition(
        tmp_path / "queue-state.jsonl",
        account_id="skestates",
        thread_id="family-finance-thread",
        from_state="completed",
        to_state="inbound",
        ts_utc="2026-06-14T00:00:00Z",
        reason="missing-extraction",
        triggering_message_id="msg-secret",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--state-dir",
            str(tmp_path),
            "notify-attention",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["applied"] is False
    assert payload["event_count"] == 1
    assert payload["events"][0]["source"] == "email"
    assert payload["events"][0]["job"] == "email-queue-attention"
    assert payload["events"][0]["status"] == "fail"
    assert json.loads(payload["events"][0]["details"]) == {
        "account": "skestates",
        "attention_channel": "Telegram: Family - Finance",
        "attention_method": "starred",
        "pending_count": 1,
    }
    assert "family-finance-thread" not in result.stdout
    assert "msg-secret" not in result.stdout


def test_cli_notify_attention_apply_invokes_notify_script(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "email" / "email-queue-state.py"
    notify_script = tmp_path / "notify.sh"
    notify_log = tmp_path / "notify-args.txt"
    notify_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f'printf "%s|%s|%s|%s\\n" "$1" "$2" "$3" "$4" >> "{notify_log}"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    queue_state = load_queue_state()
    write_accounts(tmp_path / "accounts.yaml")
    queue_state.transition(
        tmp_path / "queue-state.jsonl",
        account_id="skestates",
        thread_id="family-finance-thread",
        from_state="completed",
        to_state="inbound",
        ts_utc="2026-06-14T00:00:00Z",
        reason="missing-extraction",
        triggering_message_id="msg-secret",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--state-dir",
            str(tmp_path),
            "notify-attention",
            "--apply",
            "--notify-script",
            str(notify_script),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["applied"] is True
    assert payload["event_count"] == 1
    assert payload["emitted_count"] == 1
    source, job, status, details = notify_log.read_text(encoding="utf-8").split("|", 3)
    assert (source, job, status) == ("email", "email-queue-attention", "fail")
    assert json.loads(details) == {
        "account": "skestates",
        "attention_channel": "Telegram: Family - Finance",
        "attention_method": "starred",
        "pending_count": 1,
    }
    assert "family-finance-thread" not in details
    assert "msg-secret" not in details
    assert "skestatesinc@gmail.com" not in details


def test_missing_extraction_reactivation_links_state_and_learning_events(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.reactivate_reply(
        log,
        account_id="ace",
        thread_id="thread-3",
        prior_state="completed",
        linked_extraction=None,
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-3",
    )

    state_event = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
    learning_event = json.loads(
        (tmp_path / "queue-learning-log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    assert state_event["transaction_id"] == learning_event["transaction_id"]
    assert state_event["paired_learning_event_id"] == learning_event["learning_event_id"]


def test_snapshot_rebuild_repairs_missing_paired_learning_event(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.reactivate_reply(
        log,
        account_id="ace",
        thread_id="thread-4",
        prior_state="completed",
        linked_extraction=None,
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-4",
    )
    (tmp_path / "queue-learning-log.jsonl").unlink()

    queue_state.lookup(log, "ace", "thread-4")

    repaired = [
        json.loads(line)
        for line in (tmp_path / "queue-learning-log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert repaired[0]["triggering_event"] == "extraction_missing_on_reactivation"
