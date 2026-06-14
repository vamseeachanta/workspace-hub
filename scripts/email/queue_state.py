"""Public path-first API for email queue-state tracking."""

from scripts.email.state import (
    AccountMappingError,
    AccountScope,
    LABEL_TAXONOMY,
    QueueStateError,
    attention_notification_events,
    count_entries,
    ensure_labels,
    list_threads,
    load_account_scope,
    lookup,
    pending_work_report,
    reactivate_reply,
    resolve_log_path,
    sweep_grace,
    transition,
)

__all__ = [
    "AccountMappingError",
    "AccountScope",
    "LABEL_TAXONOMY",
    "QueueStateError",
    "attention_notification_events",
    "count_entries",
    "ensure_labels",
    "list_threads",
    "load_account_scope",
    "lookup",
    "pending_work_report",
    "reactivate_reply",
    "resolve_log_path",
    "sweep_grace",
    "transition",
]
