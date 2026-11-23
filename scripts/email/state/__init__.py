"""Email queue-state implementation package."""

from .accounts import AccountMappingError, AccountScope, load_account_scope
from .labels import LABEL_TAXONOMY, ensure_labels
from .notifications import attention_notification_events
from .paths import resolve_log_path
from .report import pending_work_report
from .safety import QueueStateError
from .store import (
    count_entries,
    list_threads,
    lookup,
    reactivate_reply,
    sweep_grace,
    transition,
)

__all__ = [
    "AccountMappingError",
    "AccountScope",
    "LABEL_TAXONOMY",
    "QueueStateError",
    "count_entries",
    "ensure_labels",
    "attention_notification_events",
    "list_threads",
    "load_account_scope",
    "lookup",
    "pending_work_report",
    "reactivate_reply",
    "resolve_log_path",
    "sweep_grace",
    "transition",
]
