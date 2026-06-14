import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tests.email.email_queue_helpers import (
    clean_precheck,
    load_queue_state,
    write_accounts,
)


def test_sweep_grace_dry_run_then_apply_transitions_completed_threads(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )

    dry_run = queue_state.sweep_grace(
        log,
        now_utc="2026-06-14T00:00:00Z",
        dry_run=True,
    )
    assert dry_run["candidate_count"] == 1
    assert queue_state.lookup(log, "ace", "old-thread")["state"] == "completed"

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
        )

    applied = queue_state.sweep_grace(
        log,
        now_utc="2026-06-14T00:00:00Z",
        dry_run=False,
        reactivation_precheck=clean_precheck(log),
    )
    assert applied["purged_count"] == 1
    assert queue_state.lookup(log, "ace", "old-thread")["state"] == "purged"


def test_sweep_grace_dry_run_does_not_write_snapshot_files(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    log.write_text(
        json.dumps(
            {
                "account_id": "ace",
                "thread_id": "old-thread",
                "from_state": "inbound",
                "to_state": "completed",
                "ts_utc": "2026-06-01T00:00:00Z",
                "completed_at": "2026-06-01T00:00:00Z",
                "cycle_id": "initial",
                "dedup_event_id": "manual:test",
                "writer_identity": {
                    "process_name": "test",
                    "pid": 1,
                    "hostname": "test",
                    "boot_id": "test",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = queue_state.sweep_grace(
        log,
        now_utc="2026-06-14T00:00:00Z",
        dry_run=True,
    )

    assert result["candidate_count"] == 1
    assert not (tmp_path / "queue-state-snapshot.yaml").exists()
    assert not (tmp_path / "queue-state-snapshot.meta.yaml").exists()
    assert not (tmp_path / "queue-learning-log.jsonl").exists()


def test_sweep_grace_keeps_assist_only_accounts_forever(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)
    scope = queue_state.load_account_scope(config)
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="skestates",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )

    applied = queue_state.sweep_grace(
        log,
        now_utc="2026-06-14T00:00:00Z",
        dry_run=False,
        account_scope=scope,
        reactivation_precheck=clean_precheck(log),
    )

    assert applied["purged_count"] == 0
    assert queue_state.lookup(log, "skestates", "old-thread")["state"] == "completed"


def test_sweep_grace_precheck_scope_is_cleanup_accounts_only(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)
    scope = queue_state.load_account_scope(config)
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    precheck = clean_precheck(log)
    precheck["checked_accounts"] = ["ace", "personal", "skestates"]

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
            account_scope=scope,
            reactivation_precheck=precheck,
        )


def test_sweep_grace_rejects_thread_level_precheck_blockers(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    precheck = clean_precheck(log)
    precheck["pending_thread_ids"] = ["old-thread"]
    precheck["baseline_missing_thread_ids"] = ["old-thread"]

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
            reactivation_precheck=precheck,
        )


def test_sweep_grace_rejects_incomplete_precheck_fields(tmp_path):
    queue_state = load_queue_state()
    from scripts.email.state import safety

    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    required_keys = (
        safety.REQUIRED_ATTESTATION_FIELDS
        + safety.REQUIRED_COUNT_FIELDS
        + safety.REQUIRED_THREAD_LIST_FIELDS
    )
    for missing_key in required_keys:
        precheck = clean_precheck(log)
        precheck.pop(missing_key)
        with pytest.raises(queue_state.QueueStateError):
            queue_state.sweep_grace(
                log,
                now_utc="2026-06-14T00:00:00Z",
                dry_run=False,
                reactivation_precheck=precheck,
            )


@pytest.mark.parametrize("bad_value", [None, "", 0, False])
def test_sweep_grace_rejects_malformed_precheck_thread_lists(tmp_path, bad_value):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    precheck = clean_precheck(log)
    precheck["pending_thread_ids"] = bad_value

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
            reactivation_precheck=precheck,
        )


@pytest.mark.parametrize("bad_value", [None, "", False, -1, 1])
def test_sweep_grace_rejects_nonzero_or_malformed_precheck_counts(
    tmp_path,
    bad_value,
):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    precheck = clean_precheck(log)
    precheck["unknown_count"] = bad_value

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
            reactivation_precheck=precheck,
        )


def test_sweep_grace_rejects_stale_precheck_attestation(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )
    precheck = clean_precheck(log)
    queue_state.transition(
        log,
        account_id="personal",
        thread_id="new-thread",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-02T00:00:00Z",
    )

    with pytest.raises(queue_state.QueueStateError):
        queue_state.sweep_grace(
            log,
            now_utc="2026-06-14T00:00:00Z",
            dry_run=False,
            reactivation_precheck=precheck,
        )


def test_sweep_grace_apply_locks_precheck_through_purge(tmp_path, monkeypatch):
    queue_state = load_queue_state()
    from scripts.email.state import store as store_module

    log = tmp_path / "queue-state.jsonl"
    marker = tmp_path / "race-started"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="old-thread",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-01T00:00:00Z",
        completed_at="2026-06-01T00:00:00Z",
    )

    original_validate = store_module.validate_reactivation_precheck
    racer = None

    def racing_precheck(precheck, scope, current_log):
        nonlocal racer
        original_validate(precheck, scope, current_log)
        script = "\n".join(
            [
                "from pathlib import Path",
                "from scripts.email.queue_state import transition",
                f"Path({str(marker)!r}).write_text('started', encoding='utf-8')",
                "transition(",
                f"    {str(log)!r},",
                "    account_id='personal',",
                "    thread_id='race-thread',",
                "    from_state='inbound',",
                "    to_state='extracted',",
                "    ts_utc='2026-06-03T00:00:00Z',",
                ")",
            ]
        )
        racer = subprocess.Popen([sys.executable, "-c", script], cwd=Path.cwd())
        deadline = time.monotonic() + 5
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert marker.exists()
        try:
            racer.wait(timeout=0.25)
        except subprocess.TimeoutExpired:
            pass

    monkeypatch.setattr(store_module, "validate_reactivation_precheck", racing_precheck)
    queue_state.sweep_grace(
        log,
        now_utc="2026-06-14T00:00:00Z",
        dry_run=False,
        reactivation_precheck=clean_precheck(log),
    )
    assert racer is not None
    assert racer.wait(timeout=5) == 0

    events = [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    purge_index = next(
        index for index, event in enumerate(events)
        if event["thread_id"] == "old-thread" and event["to_state"] == "purged"
    )
    race_index = next(
        index for index, event in enumerate(events)
        if event["thread_id"] == "race-thread"
    )
    assert purge_index < race_index
