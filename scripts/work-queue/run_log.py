"""run_log.py — Event-sourced run log for WRK stage crash recovery.

ABOUTME: Append-only JSONL run log per WRK item. Each completed stage writes
one event. On resume, the orchestrator reads the log and skips stages already
marked done (optionally checking content-addressed hashes for cache invalidation).

WRK-1187 Enhancement 1.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional


def append_stage_event(
    log_path: str,
    stage: int,
    status: str,
    entry_hash: str = "",
) -> None:
    """Append a stage completion event to the run log.

    Args:
        log_path: Path to run-log.jsonl file.
        stage: Stage number (1-20).
        status: "done", "failed", or "skipped".
        entry_hash: Optional SHA-256 hash of entry_reads files.
    """
    event = {
        "stage": stage,
        "status": status,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if entry_hash:
        event["entry_hash"] = entry_hash

    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def read_completed_stages(log_path: str) -> set[int]:
    """Return the set of stage numbers marked 'done' in the run log."""
    completed: set[int] = set()
    if not os.path.exists(log_path):
        return completed
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("status") == "done":
                    completed.add(event["stage"])
            except (json.JSONDecodeError, KeyError):
                continue
    return completed


def _get_last_event_for_stage(log_path: str, stage: int) -> Optional[dict]:
    """Return the last event for a given stage, or None."""
    last: Optional[dict] = None
    if not os.path.exists(log_path):
        return None
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("stage") == stage:
                    last = event
            except (json.JSONDecodeError, KeyError):
                continue
    return last


def should_skip_stage(
    log_path: str,
    stage: int,
    current_hash: str = "",
) -> bool:
    """Check if a stage can be skipped (already completed, inputs unchanged).

    Args:
        log_path: Path to run-log.jsonl.
        stage: Stage number to check.
        current_hash: SHA-256 of current entry_reads files. If empty,
            only checks completion status (no content-addressed skip).

    Returns:
        True if stage should be skipped (already done with matching inputs).
    """
    event = _get_last_event_for_stage(log_path, stage)
    if event is None or event.get("status") != "done":
        return False

    # Stage is done. If caller provided a hash, check it matches.
    if current_hash and event.get("entry_hash"):
        return current_hash == event["entry_hash"]

    # No hash comparison needed — stage is done, skip it.
    return True


def hash_entry_files(file_paths: list[str]) -> str:
    """Compute a deterministic SHA-256 hash over the contents of files.

    Missing files are silently skipped. Returns empty string for empty list.
    """
    if not file_paths:
        return ""
    h = hashlib.sha256()
    for path in sorted(file_paths):
        try:
            with open(path, "rb") as f:
                h.update(f.read())
        except OSError:
            continue
    return h.hexdigest()
