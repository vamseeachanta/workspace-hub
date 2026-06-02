"""File-backed rate limiter for live Deckhand write enforcement."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

READ_ACTION = "read"
WINDOW_SECONDS = 3600


def decide(
    operator_id: str,
    scope: str,
    action_class: str,
    fingerprint: str,
    *,
    policy: dict[str, Any],
    store_dir: str | Path,
    clock: Any,
) -> tuple[bool, str]:
    """Return whether the request is allowed, persisting allowed write events."""
    if action_class == READ_ACTION:
        return True, "reads are not rate limited"
    try:
        now = _parse_time(clock() if callable(clock) else clock)
        limits = _limits_for_scope(policy, scope)
        duplicate_window = int(limits.get("duplicate_request_window_seconds") or 0)
        root = Path(store_dir)
        operator_path = root / "operator" / f"{_path_part(operator_id)}.json"
        scope_path = root / "scope" / f"{_path_part(scope)}.json"
        dup_path = root / "dup" / f"{_path_part(fingerprint)}.json"

        operator_events = _fresh_events(_read_events(operator_path), now)
        scope_events = _fresh_events(_read_events(scope_path), now)
        duplicate_last_seen = _read_last_seen(dup_path)
        if (
            duplicate_window > 0
            and duplicate_last_seen is not None
            and now - duplicate_last_seen < timedelta(seconds=duplicate_window)
        ):
            return False, "duplicate request suppressed"

        operator_cap = _positive_int(limits.get("per_operator_writes_per_hour"))
        if operator_cap is not None and len(operator_events) >= operator_cap:
            return False, "rate limit exceeded: operator writes per hour"
        scope_cap = _positive_int(limits.get("per_scope_writes_per_hour"))
        if scope_cap is not None and len(scope_events) >= scope_cap:
            return False, "rate limit exceeded: scope writes per hour"

        stamp = _format_time(now)
        _write_json(operator_path, {"events": [*operator_events, stamp]})
        _write_json(scope_path, {"events": [*scope_events, stamp]})
        _write_json(dup_path, {"last_seen": stamp})
        return True, "rate limit ok"
    except Exception:  # noqa: BLE001 - writes must fail closed on any store/config error.
        return False, "rate-limit store error"


def _limits_for_scope(policy: dict[str, Any], scope: str) -> dict[str, Any]:
    policy_root = policy.get("policy") if isinstance(policy.get("policy"), dict) else policy
    defaults = dict(policy_root.get("rate_limits") or {}) if isinstance(policy_root, dict) else {}

    scopes_root = policy.get("scopes") if isinstance(policy.get("scopes"), dict) else {}
    scopes = scopes_root.get("scopes") if isinstance(scopes_root.get("scopes"), dict) else {}
    scope_config = scopes.get(scope) if isinstance(scopes, dict) else None
    override = scope_config.get("rate_limits") if isinstance(scope_config, dict) else None
    if isinstance(override, dict):
        defaults.update(override)
    return defaults


def _read_events(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("invalid rate-limit event store")
    return [str(item) for item in data["events"]]


def _read_last_seen(path: Path) -> datetime | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(data, dict) or "last_seen" not in data:
        raise ValueError("invalid duplicate store")
    return _parse_time(data["last_seen"])


def _fresh_events(events: list[str], now: datetime) -> list[str]:
    threshold = now - timedelta(seconds=WINDOW_SECONDS)
    return [_format_time(ts) for ts in (_parse_time(item) for item in events) if ts >= threshold]


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _parse_time(value: Any) -> datetime:
    text = str(value)
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _positive_int(value: Any) -> int | None:
    if value is None:
        return None
    parsed = int(value)
    return parsed if parsed > 0 else None


def _path_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value)) or "unknown"
