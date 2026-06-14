from __future__ import annotations

import hashlib
import os
import socket
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

from .accounts import AccountScope, load_account_scope
from .durability import (
    append_json,
    read_events,
    repair_learning_log,
    snapshot_meta,
    store_lock,
    write_yaml,
)
from .paths import resolve_log_path, sibling_paths
from .safety import QueueStateError, validate_reactivation_precheck

STATES = {"inbound", "extracted", "awaiting-reply", "completed", "purged"}
REACTIVATION_FROM = {"awaiting-reply", "completed", "purged"}
REACTIVATION_TO = {"inbound", "extracted"}
ALLOWED_TRANSITIONS = {
    ("inbound", "extracted"),
    ("inbound", "completed"),
    ("extracted", "awaiting-reply"),
    ("extracted", "completed"),
    ("awaiting-reply", "extracted"),
    ("awaiting-reply", "completed"),
    ("awaiting-reply", "inbound"),
    ("completed", "purged"),
    ("completed", "extracted"),
    ("completed", "inbound"),
    ("purged", "extracted"),
    ("purged", "inbound"),
}


def transition(
    log_path: str | Path | None = None,
    *,
    account_id: str,
    thread_id: str,
    from_state: str,
    to_state: str,
    ts_utc: str,
    **metadata: Any,
) -> dict[str, Any]:
    log = resolve_log_path(log_path)
    with store_lock(log):
        _validate_transition(from_state, to_state, metadata.get("reason"))
        _parse_utc(ts_utc)
        events = read_events(log)
        snapshot = _snapshot_from_events(events)
        current = snapshot.get(_snapshot_key(account_id, thread_id))
        event = _build_event(
            account_id, thread_id, from_state, to_state, ts_utc, metadata, current
        )

        if _dedup_key(event) in {_dedup_key(row) for row in events}:
            return current or _materialize_event(event, None)

        if current and current["state"] != from_state:
            raise QueueStateError(
                f"stale transition for {account_id}/{thread_id}: "
                f"current={current['state']} from_state={from_state}"
            )

        append_json(log, event)
        learning = event.get("paired_learning_event")
        if learning:
            append_json(sibling_paths(log)["learning"], learning)
        snapshot = _rebuild_snapshot_unlocked(log)
        return snapshot.get(_snapshot_key(account_id, thread_id))


def lookup(
    log_path: str | Path | None,
    account_id: str,
    thread_id: str,
) -> dict[str, Any] | None:
    log = resolve_log_path(log_path)
    with store_lock(log):
        snapshot = _rebuild_snapshot_unlocked(log)
    return snapshot.get(_snapshot_key(account_id, thread_id))


def list_threads(
    log_path: str | Path | None = None,
    *,
    write_snapshot: bool = True,
) -> list[dict[str, Any]]:
    log = resolve_log_path(log_path)
    if write_snapshot:
        with store_lock(log):
            snapshot = _rebuild_snapshot_unlocked(log)
    else:
        snapshot = _snapshot_from_events(read_events(log))
    return sorted(snapshot.values(), key=lambda row: (row["account_id"], row["thread_id"]))


def count_entries(log_path: str | Path | None = None) -> int:
    return len(read_events(resolve_log_path(log_path)))


def reactivate_reply(
    log_path: str | Path | None = None,
    *,
    account_id: str,
    thread_id: str,
    prior_state: str,
    linked_extraction: str | None,
    ts_utc: str,
    **metadata: Any,
) -> dict[str, Any]:
    if prior_state not in REACTIVATION_FROM:
        raise QueueStateError(f"state '{prior_state}' cannot reactivate on reply")
    if linked_extraction:
        return transition(
            log_path,
            account_id=account_id,
            thread_id=thread_id,
            from_state=prior_state,
            to_state="extracted",
            ts_utc=ts_utc,
            linked_extraction=linked_extraction,
            **metadata,
        )
    return transition(
        log_path,
        account_id=account_id,
        thread_id=thread_id,
        from_state=prior_state,
        to_state="inbound",
        ts_utc=ts_utc,
        reason="missing-extraction",
        **metadata,
    )


def sweep_grace(
    log_path: str | Path | None = None,
    *,
    now_utc: str,
    grace_days: int = 7,
    dry_run: bool = True,
    account_scope: AccountScope | None = None,
    reactivation_precheck: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    log = resolve_log_path(log_path)
    scope = account_scope or load_account_scope()
    cutoff = _parse_utc(now_utc) - timedelta(days=grace_days)

    if dry_run:
        snapshot = _snapshot_from_events(read_events(log))
        candidates = _sweep_candidates(snapshot, scope, cutoff)
        return {"dry_run": True, "candidate_count": len(candidates), "candidates": candidates}

    with store_lock(log):
        validate_reactivation_precheck(reactivation_precheck, scope, log)
        events = read_events(log)
        snapshot = _snapshot_from_events(events)
        candidates = _sweep_candidates(snapshot, scope, cutoff)
        for row in candidates:
            event = _build_event(
                row["account_id"],
                row["thread_id"],
                "completed",
                "purged",
                now_utc,
                {"reason": "grace-elapsed"},
                row,
            )
            append_json(log, event)
        _rebuild_snapshot_unlocked(log)
    return {"dry_run": False, "purged_count": len(candidates), "candidates": candidates}


def _sweep_candidates(
    snapshot: Mapping[str, dict[str, Any]],
    scope: AccountScope,
    cutoff: datetime,
) -> list[dict[str, Any]]:
    return [
        row for row in snapshot.values()
        if row["state"] == "completed"
        and scope.cleanup_enabled(row["account_id"])
        and row.get("completed_at")
        and _parse_utc(row["completed_at"]) <= cutoff
    ]


def rebuild_snapshot(log_path: str | Path) -> dict[str, dict[str, Any]]:
    log = Path(log_path)
    with store_lock(log):
        return _rebuild_snapshot_unlocked(log)


def _rebuild_snapshot_unlocked(log_path: str | Path) -> dict[str, dict[str, Any]]:
    log = Path(log_path)
    events = read_events(log)
    snapshot = _snapshot_from_events(events)
    paths = sibling_paths(log)
    paths["snapshot"].parent.mkdir(parents=True, exist_ok=True)
    write_yaml(paths["snapshot"], snapshot)
    write_yaml(paths["meta"], snapshot_meta(log, paths["snapshot"]))
    paths["learning"].touch(exist_ok=True)
    repair_learning_log(paths["learning"], events)
    return snapshot


def _snapshot_from_events(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for event in events:
        key = _snapshot_key(event["account_id"], event["thread_id"])
        snapshot[key] = _materialize_event(event, snapshot.get(key))
    return snapshot


def _build_event(
    account_id: str,
    thread_id: str,
    from_state: str,
    to_state: str,
    ts_utc: str,
    metadata: Mapping[str, Any],
    current: Mapping[str, Any] | None,
) -> dict[str, Any]:
    trigger = metadata.get("triggering_message_id")
    cycle_id = metadata.get("cycle_id") or _cycle_id(
        from_state, to_state, trigger, metadata, current
    )
    dedup_event_id = metadata.get("dedup_event_id") or (
        f"msg:{trigger}" if trigger else "legacy:no-trigger"
    )
    transaction_id = _stable_id(account_id, thread_id, from_state, to_state, cycle_id, dedup_event_id)
    event = {
        "account_id": account_id,
        "thread_id": thread_id,
        "from_state": from_state,
        "to_state": to_state,
        "ts_utc": ts_utc,
        "cycle_id": cycle_id,
        "dedup_event_id": dedup_event_id,
        "transaction_id": transaction_id,
        "warning_no_triggering_message_id": trigger is None,
        "writer_identity": _writer_identity(),
    }
    _copy_metadata(event, metadata)
    if event.get("reason") == "missing-extraction":
        learning = _learning_event(event)
        event["paired_learning_event_id"] = learning["learning_event_id"]
        event["paired_learning_event"] = learning
    return event


def _copy_metadata(event: dict[str, Any], metadata: Mapping[str, Any]) -> None:
    fields = {
        "reason", "linked_extraction", "primary_classification",
        "secondary_classification", "completed_at", "needs_schema",
        "needs_user_decision", "triggering_message_id", "received_at_utc",
    }
    for field in fields:
        if metadata.get(field) is not None:
            event[field] = metadata[field]


def _materialize_event(
    event: Mapping[str, Any],
    prior: Mapping[str, Any] | None,
) -> dict[str, Any]:
    row = dict(prior or {})
    row.update({
        "account_id": event["account_id"],
        "thread_id": event["thread_id"],
        "state": event["to_state"],
        "ts_utc": event["ts_utc"],
        "cycle_id": event["cycle_id"],
        "needs_schema": bool(event.get("needs_schema", False)),
        "needs_user_decision": bool(event.get("needs_user_decision", False)),
    })
    _materialize_completion(row, event)
    _materialize_message_baseline(row, event)
    for field in ("linked_extraction", "primary_classification", "secondary_classification"):
        if field in event:
            row[field] = event[field]
    return row


def _materialize_completion(row: dict[str, Any], event: Mapping[str, Any]) -> None:
    if event["to_state"] == "completed":
        row["completed_at"] = event.get("completed_at", event["ts_utc"])
    else:
        row.pop("completed_at", None)


def _materialize_message_baseline(row: dict[str, Any], event: Mapping[str, Any]) -> None:
    if event.get("triggering_message_id"):
        row["last_seen_message_id"] = event["triggering_message_id"]
        row["last_seen_received_at_utc"] = event.get("received_at_utc", event["ts_utc"])
    if event["from_state"] in REACTIVATION_FROM and event["to_state"] in REACTIVATION_TO:
        row["cycle_started_at"] = event["ts_utc"]


def _validate_transition(from_state: str, to_state: str, reason: str | None) -> None:
    if from_state not in STATES or to_state not in STATES:
        raise QueueStateError(f"unknown state transition {from_state}->{to_state}")
    if (from_state, to_state) not in ALLOWED_TRANSITIONS:
        raise QueueStateError(f"transition {from_state}->{to_state} is not allowed")
    if to_state == "inbound" and reason != "missing-extraction":
        raise QueueStateError("reactivation to inbound requires missing-extraction reason")


def _cycle_id(
    from_state: str,
    to_state: str,
    trigger: str | None,
    metadata: Mapping[str, Any],
    current: Mapping[str, Any] | None,
) -> str:
    if from_state in REACTIVATION_FROM and to_state in REACTIVATION_TO:
        if trigger:
            return f"msg:{trigger}"
        source = metadata.get("linked_extraction") or metadata.get("reason", "reactivation")
        return "reactivation:" + hashlib.sha256(str(source).encode()).hexdigest()[:16]
    if current and current.get("cycle_id"):
        return str(current["cycle_id"])
    return "initial"


def _learning_event(event: Mapping[str, Any]) -> dict[str, Any]:
    event_id = _stable_id(
        event["account_id"],
        event["thread_id"],
        event["ts_utc"],
        "extraction_missing_on_reactivation",
    )
    return {
        "learning_event_id": event_id,
        "transaction_id": event["transaction_id"],
        "account_id": event["account_id"],
        "thread_id": event["thread_id"],
        "ts_utc": event["ts_utc"],
        "triggering_event": "extraction_missing_on_reactivation",
        "from_state": event["from_state"],
        "to_state": event["to_state"],
        "writer_identity": event["writer_identity"],
    }


def _writer_identity() -> dict[str, Any]:
    return {
        "process_name": "queue_state",
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "boot_id": _boot_id(),
    }


def _boot_id() -> str:
    return os.environ.get("EMAIL_QUEUE_BOOT_ID", "unknown")


def _dedup_key(event: Mapping[str, Any]) -> tuple[str, str, str, str, str, str]:
    return (
        event["account_id"],
        event["thread_id"],
        event["from_state"],
        event["to_state"],
        event.get("cycle_id", "initial"),
        event.get("dedup_event_id", "legacy:no-trigger"),
    )


def _snapshot_key(account_id: str, thread_id: str) -> str:
    return f"{account_id}::{thread_id}"


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise QueueStateError(f"timestamp must be UTC Z format: {value}")
    return datetime.fromisoformat(value[:-1] + "+00:00")
