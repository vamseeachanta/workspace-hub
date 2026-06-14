from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .accounts import AccountScope
from .durability import file_sha256

REQUIRED_COUNT_FIELDS = (
    "unknown_count",
    "config_missing_count",
    "newer_message_pending_count",
    "snapshot_comparison_missing_count",
)
REQUIRED_THREAD_LIST_FIELDS = (
    "pending_thread_ids",
    "baseline_missing_thread_ids",
    "unknown_thread_ids",
    "config_missing_thread_ids",
    "newer_message_thread_ids",
    "snapshot_comparison_missing_thread_ids",
)
REQUIRED_ATTESTATION_FIELDS = (
    "checked_accounts",
    "log_byte_offset",
    "log_sha256",
    "unknown_status",
)


class QueueStateError(ValueError):
    """Raised when a queue-state operation is invalid."""


def validate_reactivation_precheck(
    precheck: Mapping[str, Any] | None,
    scope: AccountScope,
    log: Path,
) -> None:
    if precheck is None:
        raise QueueStateError("sweep apply requires a clean reactivation precheck")
    missing = _missing_required_fields(precheck)
    blockers = _aggregate_blocker_count(precheck)
    stale = _is_stale_precheck(precheck, log)
    if (
        missing
        or set(precheck.get("checked_accounts", [])) != scope.enabled_aliases()
        or precheck.get("unknown_status") != "evaluated"
        or blockers
        or _thread_blocker_keys(precheck)
        or stale
    ):
        raise QueueStateError("reactivation precheck is incomplete or not clean")


def _aggregate_blocker_count(precheck: Mapping[str, Any]) -> int:
    for name in REQUIRED_COUNT_FIELDS:
        value = precheck.get(name)
        if type(value) is not int or value != 0:
            return 1
    return 0


def _thread_blocker_keys(precheck: Mapping[str, Any]) -> list[str]:
    blockers = [
        key for key in REQUIRED_THREAD_LIST_FIELDS
        if not isinstance(precheck.get(key), list) or precheck[key]
    ]
    blockers.extend(
        key for key, value in precheck.items()
        if key.endswith("_thread_ids")
        and key not in REQUIRED_THREAD_LIST_FIELDS
        and value
    )
    return blockers


def _missing_required_fields(precheck: Mapping[str, Any]) -> set[str]:
    required = (
        set(REQUIRED_ATTESTATION_FIELDS)
        | set(REQUIRED_COUNT_FIELDS)
        | set(REQUIRED_THREAD_LIST_FIELDS)
    )
    return required - set(precheck)


def _is_stale_precheck(precheck: Mapping[str, Any], log: Path) -> bool:
    return (
        precheck.get("log_byte_offset") != (log.stat().st_size if log.exists() else 0)
        or precheck.get("log_sha256") != file_sha256(log)
    )
