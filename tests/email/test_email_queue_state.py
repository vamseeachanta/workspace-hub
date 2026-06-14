import json

from tests.email.email_queue_helpers import load_queue_state, write_accounts


def test_path_first_api_derives_snapshot_and_learning_paths(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-1",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-1",
    )

    assert (tmp_path / "queue-state-snapshot.yaml").exists()
    assert (tmp_path / "queue-state-snapshot.meta.yaml").exists()
    assert (tmp_path / "queue-learning-log.jsonl").exists()


def test_custom_log_path_uses_isolated_sibling_names(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "custom.jsonl"

    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-1",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:00:00Z",
    )

    assert (tmp_path / "custom-snapshot.yaml").exists()
    assert (tmp_path / "custom-snapshot.meta.yaml").exists()
    assert (tmp_path / "custom-learning-log.jsonl").exists()
    assert not (tmp_path / "queue-state-snapshot.yaml").exists()


def test_account_scope_limits_enabled_accounts_and_marks_skestates_out_of_scope(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)

    scope = queue_state.load_account_scope(config)

    assert scope.enabled_aliases() == {"ace", "personal"}
    assert scope.normalize("vamsee.achanta@aceengineer.com").alias == "ace"
    assert scope.normalize("achantav@gmail.com").alias == "personal"
    assert scope.normalize("skestatesinc@gmail.com").status == "out_of_scope"


def test_account_scope_hard_disables_unapproved_config_aliases(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    config.write_text(
        "\n".join(
            [
                "accounts:",
                "  ace:",
                "    email: vamsee.achanta@aceengineer.com",
                "    enabled: true",
                "  personal:",
                "    email: achantav@gmail.com",
                "    enabled: true",
                "  skestates:",
                "    email: skestatesinc@gmail.com",
                "    enabled: true",
                "",
            ]
        ),
        encoding="utf-8",
    )

    scope = queue_state.load_account_scope(config)

    assert scope.enabled_aliases() == {"ace", "personal"}
    assert scope.normalize("skestates").status == "out_of_scope"
    assert scope.normalize("skestatesinc@gmail.com").status == "out_of_scope"


def test_pending_work_report_requires_inbox_snapshot_to_claim_mailbox_empty(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-1",
        from_state="inbound",
        to_state="completed",
        ts_utc="2026-06-14T00:00:00Z",
        completed_at="2026-06-14T00:00:00Z",
    )

    report = queue_state.pending_work_report(log)

    assert report["tracked_empty"] is True
    assert report["unknown_status"] == "not_evaluated"
    assert report["mailbox_empty"] is None


def test_pending_work_report_blocks_empty_for_unknown_in_scope_inbox_thread(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)
    log = tmp_path / "queue-state.jsonl"

    report = queue_state.pending_work_report(
        log,
        account_scope=queue_state.load_account_scope(config),
        inbox_snapshot=[
            {
                "account_id": "achantav@gmail.com",
                "thread_id": "new-thread",
                "message_id": "msg-new",
                "received_at_utc": "2026-06-14T00:00:00Z",
            }
        ],
    )

    assert report["unknown_status"] == "evaluated"
    assert report["unknown_count"] == 1
    assert report["mailbox_empty"] is False


def test_pending_work_report_ignores_disabled_account_for_two_account_cleanup(tmp_path):
    queue_state = load_queue_state()
    config = tmp_path / "accounts.yaml"
    write_accounts(config)
    log = tmp_path / "queue-state.jsonl"

    report = queue_state.pending_work_report(
        log,
        account_scope=queue_state.load_account_scope(config),
        inbox_snapshot=[
            {
                "account_id": "skestatesinc@gmail.com",
                "thread_id": "disabled-thread",
                "message_id": "msg-disabled",
            }
        ],
    )

    assert report["out_of_scope_count"] == 1
    assert report["unknown_count"] == 0
    assert report["mailbox_empty"] is True


def test_pending_work_report_counts_newer_reply_on_tracked_thread(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-1",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-1",
        received_at_utc="2026-06-14T00:00:00Z",
    )

    report = queue_state.pending_work_report(
        log,
        inbox_snapshot=[
            {
                "account_id": "ace",
                "thread_id": "thread-1",
                "message_id": "msg-2",
                "received_at_utc": "2026-06-14T00:05:00Z",
            }
        ],
    )

    assert report["newer_message_pending_count"] == 1
    assert report["mailbox_empty"] is False


def test_pending_work_report_counts_latest_message_id_alias(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-1",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-1",
        received_at_utc="2026-06-14T00:00:00Z",
    )

    report = queue_state.pending_work_report(
        log,
        inbox_snapshot=[
            {
                "account_id": "ace",
                "thread_id": "thread-1",
                "latest_message_id": "msg-2",
                "received_at_utc": "2026-06-14T00:05:00Z",
            }
        ],
    )

    assert report["newer_message_pending_count"] == 1
    assert report["snapshot_comparison_missing_count"] == 0


def test_awaiting_reply_is_not_pending_without_new_reply(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="personal",
        thread_id="thread-wait",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:00:00Z",
    )
    queue_state.transition(
        log,
        account_id="personal",
        thread_id="thread-wait",
        from_state="extracted",
        to_state="awaiting-reply",
        ts_utc="2026-06-14T00:01:00Z",
    )

    report = queue_state.pending_work_report(log, inbox_snapshot=[])

    assert report["tracked_empty"] is True
    assert report["pending_count"] == 0
    assert report["mailbox_empty"] is True


def test_reactivated_cycle_does_not_dedup_against_initial_cycle(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-cycle",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-01T00:00:00Z",
    )
    queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-cycle",
        from_state="extracted",
        to_state="completed",
        ts_utc="2026-06-02T00:00:00Z",
    )
    queue_state.reactivate_reply(
        log,
        account_id="ace",
        thread_id="thread-cycle",
        prior_state="completed",
        linked_extraction=None,
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-new",
    )

    state = queue_state.transition(
        log,
        account_id="ace",
        thread_id="thread-cycle",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-06-14T00:01:00Z",
    )

    assert state["state"] == "extracted"
    assert state["cycle_id"] == "msg:msg-new"


def test_missing_extraction_reactivation_writes_learning_log(tmp_path):
    queue_state = load_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.reactivate_reply(
        log,
        account_id="personal",
        thread_id="thread-2",
        prior_state="completed",
        linked_extraction=None,
        ts_utc="2026-06-14T00:00:00Z",
        triggering_message_id="msg-2",
    )

    assert queue_state.lookup(log, "personal", "thread-2")["state"] == "inbound"
    learning = tmp_path / "queue-learning-log.jsonl"
    entries = [json.loads(line) for line in learning.read_text().splitlines()]
    assert entries[0]["triggering_event"] == "extraction_missing_on_reactivation"
