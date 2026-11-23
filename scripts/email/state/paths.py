from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .accounts import resolve_state_dir


def resolve_log_path(
    log_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    if log_path is not None:
        return Path(log_path).expanduser()
    return resolve_state_dir(env) / "queue-state.jsonl"


def sibling_paths(log_path: str | Path) -> dict[str, Path]:
    log = Path(log_path)
    if log.name == "queue-state.jsonl":
        return {
            "snapshot": log.with_name("queue-state-snapshot.yaml"),
            "meta": log.with_name("queue-state-snapshot.meta.yaml"),
            "learning": log.with_name("queue-learning-log.jsonl"),
        }
    return {
        "snapshot": log.with_name(f"{log.stem}-snapshot.yaml"),
        "meta": log.with_name(f"{log.stem}-snapshot.meta.yaml"),
        "learning": log.with_name(f"{log.stem}-learning-log.jsonl"),
    }
