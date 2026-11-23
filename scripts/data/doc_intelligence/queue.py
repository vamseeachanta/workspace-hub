"""Queue state management for batch document extraction."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_queue(path: Path) -> dict:
    """Parse a queue YAML file. Raises FileNotFoundError or ValueError."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Queue file not found: {path}")
    text = path.read_text()
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict) or "documents" not in data:
        raise ValueError(f"Invalid queue schema in {path}: missing 'documents' key")
    return data


def save_queue(queue: dict, path: Path) -> None:
    """Atomically write queue state via tmpfile + os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.dump(queue, default_flow_style=False, sort_keys=False))
    os.replace(tmp, path)


def get_pending(queue: dict) -> list[dict]:
    """Return documents with status == 'pending'."""
    return [d for d in queue.get("documents", []) if d.get("status") == "pending"]


def get_stats(queue: dict) -> dict[str, int]:
    """Return counts: pending, completed, failed, total."""
    docs = queue.get("documents", [])
    counts: dict[str, int] = {"pending": 0, "completed": 0, "failed": 0, "total": len(docs)}
    for d in docs:
        status = d.get("status", "pending")
        if status in counts:
            counts[status] += 1
    return counts


def mark_completed(doc: dict, manifest_path: str) -> None:
    """Mark a document as successfully processed."""
    doc["status"] = "completed"
    doc["manifest_path"] = manifest_path
    doc["processed_at"] = datetime.now(timezone.utc).isoformat()


def mark_failed(doc: dict, error: str) -> None:
    """Mark a document as failed with error message."""
    doc["status"] = "failed"
    doc["error"] = error
    doc["processed_at"] = datetime.now(timezone.utc).isoformat()
