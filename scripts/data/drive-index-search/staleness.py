from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def compute_index_status(indexes, defaults: dict[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
    current = now or datetime.now(timezone.utc)
    return [_status_for_index(index, defaults, current) for index in indexes]


def stale_warnings(statuses: list[dict[str, Any]]) -> list[str]:
    warnings = []
    for status in statuses:
        if status["last_refresh_status"] == "failed":
            warnings.append(
                f"WARNING: index {status['id']} last refresh FAILED at {status['as_of']} -- results may be stale"
            )
        elif status["stale"]:
            warnings.append(
                f"WARNING: index {status['id']} is {status['days_stale']} days stale "
                f"(threshold {status['threshold_days']})"
            )
    return warnings


def _status_for_index(index, defaults: dict[str, Any], now: datetime) -> dict[str, Any]:
    freshness = index.freshness or {}
    state = _read_state(freshness.get("state_file"))
    as_of = state.get("finished_at") or freshness.get("as_of") or freshness.get("built_at")
    parsed = _parse_date(as_of)
    threshold = freshness.get("staleness_days") or defaults.get("staleness_days")
    days_stale = (now.date() - parsed.date()).days if parsed else None
    stale = bool(days_stale is not None and threshold is not None and days_stale > threshold)
    return {
        "id": index.id,
        "as_of": as_of,
        "days_stale": days_stale,
        "threshold_days": threshold,
        "stale": stale,
        "last_refresh_status": state.get("status") or "unknown",
        "row_count": state.get("row_count", freshness.get("row_count")),
    }


def _read_state(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
