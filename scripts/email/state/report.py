from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .accounts import AccountScope, load_account_scope
from .store import list_threads

PENDING_STATES = {"inbound"}


def pending_work_report(
    log_path: str | Path | None = None,
    *,
    account_scope: AccountScope | None = None,
    inbox_snapshot: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    scope = account_scope or load_account_scope()
    local = _classify_local_threads(list_threads(log_path), scope)
    snapshot_result = _classify_inbox_snapshot(inbox_snapshot, local["tracked"], scope)
    per_account = _merge_per_account(local["per_account"], snapshot_result["per_account"])
    tracked_pending = sum(row["pending_work_count"] for row in local["tracked"].values())
    return {
        "tracked_empty": tracked_pending == 0,
        "mailbox_empty": _mailbox_empty(tracked_pending == 0, snapshot_result),
        "unknown_status": snapshot_result["unknown_status"],
        "unknown_count": snapshot_result["unknown_count"],
        "out_of_scope_count": local["out_of_scope_count"] + snapshot_result["out_of_scope_count"],
        "config_missing_count": local["config_missing_count"] + snapshot_result["config_missing_count"],
        "newer_message_pending_count": snapshot_result["newer_message_pending_count"],
        "snapshot_comparison_missing_count": snapshot_result["snapshot_comparison_missing_count"],
        "per_account": per_account,
        "attention_routes": _attention_routes(per_account),
        "pending_count": tracked_pending + snapshot_result["pending_count"],
    }


def _classify_local_threads(
    threads: Iterable[Mapping[str, Any]],
    scope: AccountScope,
) -> dict[str, Any]:
    result = _empty_classification()
    for row in threads:
        normalized = scope.normalize(row["account_id"])
        if normalized.status != "enabled" or normalized.alias is None:
            result[f"{normalized.status}_count"] += 1
            continue
        tracked = dict(row)
        tracked["account_id"] = normalized.alias
        pending = _local_pending_count(tracked)
        tracked["pending_work_count"] = pending
        result["tracked"][_snapshot_key(normalized.alias, tracked["thread_id"])] = tracked
        account = result["per_account"].setdefault(
            normalized.alias,
            _account_counts(scope.accounts[normalized.alias]),
        )
        account["states"][tracked["state"]] = account["states"].get(tracked["state"], 0) + 1
        account["pending_count"] += pending
    return result


def _classify_inbox_snapshot(
    inbox_snapshot: Iterable[Mapping[str, Any]] | None,
    tracked: Mapping[str, Mapping[str, Any]],
    scope: AccountScope,
) -> dict[str, Any]:
    result = _empty_snapshot_result(inbox_snapshot is None)
    if inbox_snapshot is None:
        return result
    for item in inbox_snapshot:
        if _is_noise(item):
            continue
        normalized = scope.normalize(str(item["account_id"]))
        if normalized.status != "enabled" or normalized.alias is None:
            result[f"{normalized.status}_count"] += 1
            continue
        account = result["per_account"].setdefault(
            normalized.alias,
            _account_counts(scope.accounts[normalized.alias]),
        )
        key = _snapshot_key(normalized.alias, str(item["thread_id"]))
        current = tracked.get(key)
        if current is None:
            result["unknown_count"] += 1
            result["pending_count"] += 1
            account["pending_count"] += 1
            account["snapshot_unknown_count"] += 1
            continue
        _count_newer_message(result, account, current, item)
    return result


def _count_newer_message(
    result: dict[str, Any],
    account: dict[str, Any],
    current: Mapping[str, Any],
    item: Mapping[str, Any],
) -> None:
    msg_id = item.get("latest_message_id") or item.get("message_id")
    received = item.get("received_at_utc")
    if not msg_id or not received:
        result["snapshot_comparison_missing_count"] += 1
        result["pending_count"] += 1
        account["pending_count"] += 1
        account["snapshot_comparison_missing_count"] += 1
        return
    if msg_id != current.get("last_seen_message_id") and received > current.get(
        "last_seen_received_at_utc", ""
    ):
        result["newer_message_pending_count"] += 1
        result["pending_count"] += 1
        account["pending_count"] += 1
        account["newer_message_pending_count"] += 1


def _mailbox_empty(tracked_empty: bool, snapshot_result: Mapping[str, Any]) -> bool | None:
    if snapshot_result["unknown_status"] == "not_evaluated":
        return None
    blocking = sum(
        snapshot_result[name]
        for name in (
            "unknown_count",
            "config_missing_count",
            "newer_message_pending_count",
            "snapshot_comparison_missing_count",
        )
    )
    return tracked_empty and blocking == 0


def _empty_classification() -> dict[str, Any]:
    return {
        "tracked": {},
        "per_account": {},
        "out_of_scope_count": 0,
        "config_missing_count": 0,
    }


def _empty_snapshot_result(not_evaluated: bool) -> dict[str, Any]:
    return {
        "unknown_status": "not_evaluated" if not_evaluated else "evaluated",
        "unknown_count": 0,
        "out_of_scope_count": 0,
        "config_missing_count": 0,
        "per_account": {},
        "newer_message_pending_count": 0,
        "snapshot_comparison_missing_count": 0,
        "pending_count": 0,
    }


def _account_counts(account: Any) -> dict[str, Any]:
    return {
        "states": {},
        "pending_count": 0,
        "snapshot_unknown_count": 0,
        "newer_message_pending_count": 0,
        "snapshot_comparison_missing_count": 0,
        "cleanup_enabled": account.cleanup_enabled,
        "retention_policy": account.retention_policy,
        "attention_method": account.attention_method,
        "attention_channel": account.attention_channel,
    }


def _merge_per_account(
    local: Mapping[str, dict[str, Any]],
    snapshot: Mapping[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged = {alias: dict(counts) for alias, counts in local.items()}
    for alias, counts in snapshot.items():
        target = merged.setdefault(alias, dict(counts))
        if target == counts:
            continue
        for key in (
            "pending_count",
            "snapshot_unknown_count",
            "newer_message_pending_count",
            "snapshot_comparison_missing_count",
        ):
            target[key] = target.get(key, 0) + counts.get(key, 0)
    return merged


def _attention_routes(per_account: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "account_id": alias,
            "pending_count": counts["pending_count"],
            "attention_method": counts.get("attention_method"),
            "attention_channel": counts.get("attention_channel"),
        }
        for alias, counts in sorted(per_account.items())
        if counts["pending_count"]
        and (counts.get("attention_method") or counts.get("attention_channel"))
    ]


def _local_pending_count(row: Mapping[str, Any]) -> int:
    return int(
        row["state"] in PENDING_STATES
        or row.get("needs_schema")
        or row.get("needs_user_decision")
    )


def _snapshot_key(account_id: str, thread_id: str) -> str:
    return f"{account_id}::{thread_id}"


def _is_noise(item: Mapping[str, Any]) -> bool:
    labels = set(item.get("labels", []))
    return "wh-email/noise" in labels
