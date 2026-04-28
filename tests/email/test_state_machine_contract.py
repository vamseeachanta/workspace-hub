import importlib

import pytest


def require_queue_state():
    try:
        return importlib.import_module("scripts.email.queue_state")
    except ModuleNotFoundError as exc:
        pytest.fail(f"pending #2026 storage module: {exc}")


@pytest.mark.xfail(reason="pending #2026 storage impl")
def test_transition_inbound_to_extracted_writes_log(tmp_path):
    queue_state = require_queue_state()
    log = tmp_path / "queue-state.jsonl"

    queue_state.transition(
        log,
        account_id="user@example.com",
        thread_id="thread-1",
        from_state="inbound",
        to_state="extracted",
        ts_utc="2026-04-20T00:00:00Z",
    )

    assert queue_state.lookup(log, "user@example.com", "thread-1")["state"] == "extracted"


@pytest.mark.xfail(reason="pending #2026 storage impl")
def test_transition_retry_preserves_dedup_under_fresh_ts(tmp_path):
    queue_state = require_queue_state()
    log = tmp_path / "queue-state.jsonl"
    kwargs = {
        "account_id": "user@example.com",
        "thread_id": "thread-1",
        "from_state": "inbound",
        "to_state": "extracted",
    }

    queue_state.transition(log, ts_utc="2026-04-20T00:00:00Z", **kwargs)
    queue_state.transition(log, ts_utc="2026-04-20T00:01:00Z", **kwargs)

    assert queue_state.count_entries(log) == 1


@pytest.mark.xfail(reason="pending #2026 storage impl")
def test_purged_reactivates_on_reply_with_extraction_link(tmp_path):
    queue_state = require_queue_state()
    log = tmp_path / "queue-state.jsonl"
    extraction = tmp_path / "extraction.yaml"
    extraction.write_text("thread_id: thread-1\n", encoding="utf-8")

    queue_state.reactivate_reply(
        log,
        account_id="user@example.com",
        thread_id="thread-1",
        prior_state="purged",
        linked_extraction=str(extraction),
        ts_utc="2026-04-28T00:00:00Z",
    )

    state = queue_state.lookup(log, "user@example.com", "thread-1")
    assert state["state"] == "extracted"
    assert state["linked_extraction"] == str(extraction)
