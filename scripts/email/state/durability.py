from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml


@contextmanager
def store_lock(log_path: Path):
    lock_path = log_path.with_suffix(f"{log_path.suffix}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        try:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except ImportError:
            pass
        try:
            yield
        finally:
            try:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except ImportError:
                pass


def read_events(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    events = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def append_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_yaml(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    with temp.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def snapshot_meta(log_path: Path, snapshot_path: Path) -> dict[str, Any]:
    return {
        "last_log_byte_offset": log_path.stat().st_size if log_path.exists() else 0,
        "last_log_sha256": file_sha256(log_path),
        "snapshot_sha256": file_sha256(snapshot_path),
        "written_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "log_generation": 1,
    }


def repair_learning_log(learning_path: Path, events: list[dict[str, Any]]) -> None:
    existing = learning_event_ids(learning_path)
    for event in events:
        learning = event.get("paired_learning_event")
        if learning and learning["learning_event_id"] not in existing:
            append_json(learning_path, learning)
            existing.add(learning["learning_event_id"])


def learning_event_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        json.loads(line)["learning_event_id"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def file_sha256(path: Path) -> str:
    if not path.exists():
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()
