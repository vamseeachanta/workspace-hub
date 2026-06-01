"""Stateful Deckhand runtime orchestration."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, MutableMapping

import yaml

from . import audit, engine


Clock = Callable[[], str]
Executor = Callable[[dict[str, Any]], Any]
RateStore = MutableMapping[str, Any]


def handle(
    request: dict[str, Any],
    *,
    config: Any,
    executor: Executor,
    clock: Clock,
    rate_store: RateStore,
    audit_path: str | Path,
) -> dict[str, Any]:
    """Authorize, rate-limit, execute, and audit one Deckhand request."""
    decision = engine.decide(request, config=config)
    if not decision.get("allow"):
        persisted = audit.append_raw(
            _audit_record(decision, status="DENY"),
            path=audit_path,
            clock=clock,
        )
        return {
            "decision": decision,
            "executed": False,
            "decision_id": persisted["decision_id"],
        }

    checked_at = _parse_clock(clock())
    rate_decision = _rate_limit_decision(request, decision, config, rate_store, checked_at)
    if rate_decision is not None:
        persisted = audit.append_raw(
            _audit_record(rate_decision, status="DENY-rate"),
            path=audit_path,
            clock=clock,
        )
        return {
            "decision": rate_decision,
            "executed": False,
            "decision_id": persisted["decision_id"],
        }

    pending = audit.append_raw(
        _audit_record(decision, status="PENDING"),
        path=audit_path,
        clock=clock,
    )
    decision_id = pending["decision_id"]
    try:
        result = executor(request)
    except Exception as exc:  # noqa: BLE001 - runtime boundary must persist failures.
        error = {"type": type(exc).__name__}
        audit.append_raw(
            _audit_record(decision, status="FINAL", error=error),
            path=audit_path,
            clock=clock,
            decision_id=decision_id,
        )
        return {
            "decision": decision,
            "executed": False,
            "decision_id": decision_id,
            "error": error,
        }

    result_summary = _redacted_result(result)
    audit.append_raw(
        _audit_record(decision, status="FINAL", result=result_summary),
        path=audit_path,
        clock=clock,
        decision_id=decision_id,
    )
    return {
        "decision": decision,
        "executed": True,
        "decision_id": decision_id,
        "result": result_summary,
    }


def _audit_record(
    decision: dict[str, Any],
    *,
    status: str,
    result: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = dict(decision.get("audit") or {})
    record["status"] = status
    if result is not None:
        record["result"] = result
    if error is not None:
        record["error"] = error
    return record


def _rate_limit_decision(
    request: dict[str, Any],
    decision: dict[str, Any],
    config: Any,
    rate_store: RateStore,
    now: datetime,
) -> dict[str, Any] | None:
    if request.get("action_class") == engine.READ_ACTION:
        return None

    limits = _rate_limits(config, decision.get("scope_resolved"))
    duplicate_window = _positive_int(limits.get("duplicate_request_window_seconds"))
    if duplicate_window and _is_duplicate_request(request, rate_store, now, duplicate_window):
        return _deny_rate(decision, "duplicate request suppressed")

    operator_limit = _positive_int(limits.get("per_operator_writes_per_hour"))
    operator_bucket = f"operator:{request.get('operator_id')}"
    if operator_limit and _limit_exceeded(rate_store, operator_bucket, now, operator_limit):
        return _deny_rate(decision, "rate limit exceeded: operator writes per hour")

    scope_limit = _positive_int(limits.get("per_scope_writes_per_hour"))
    scope = decision.get("scope_resolved")
    scope_bucket = f"scope:{scope}"
    if scope_limit and _limit_exceeded(rate_store, scope_bucket, now, scope_limit):
        return _deny_rate(decision, "rate limit exceeded: scope writes per hour")

    _record_duplicate_request(request, rate_store, now, duplicate_window)
    _record_write_event(rate_store, operator_bucket, now)
    _record_write_event(rate_store, scope_bucket, now)
    return None


def _deny_rate(decision: dict[str, Any], reason: str) -> dict[str, Any]:
    denied = dict(decision)
    denied["allow"] = False
    denied["reason"] = reason
    denied["audit"] = dict(decision.get("audit") or {})
    denied["audit"]["decision"] = "DENY"
    denied["audit"]["reason"] = reason
    return denied


def _rate_limits(config: Any, scope_name: Any) -> dict[str, Any]:
    loaded = _load_config(config)
    if loaded is None:
        return {}
    policy, scopes_config = loaded
    merged = dict(policy.get("rate_limits") or {})
    scope = (scopes_config.get("scopes") or {}).get(scope_name) or {}
    if isinstance(scope, dict):
        merged.update(scope.get("rate_limits") or {})
    return merged


def _load_config(config: Any) -> tuple[dict[str, Any], dict[str, Any]] | None:
    try:
        if isinstance(config, (str, Path)):
            config_dir = Path(config)
            policy = yaml.safe_load((config_dir / "policy.yml").read_text(encoding="utf-8"))
            scopes = yaml.safe_load((config_dir / "scopes.yml").read_text(encoding="utf-8"))
            if isinstance(policy, dict) and isinstance(scopes, dict):
                return policy, scopes
            return None
        if isinstance(config, dict):
            policy = config.get("policy")
            scopes = config.get("scopes")
            if isinstance(policy, dict) and isinstance(scopes, dict):
                return policy, scopes
    except (OSError, yaml.YAMLError):
        return None
    return None


def _is_duplicate_request(
    request: dict[str, Any],
    rate_store: RateStore,
    now: datetime,
    window_seconds: int,
) -> bool:
    duplicate_requests = rate_store.setdefault("duplicate_requests", {})
    if not isinstance(duplicate_requests, dict):
        duplicate_requests = {}
        rate_store["duplicate_requests"] = duplicate_requests

    request_key = _request_key(request)
    previous = _parse_stored_ts(duplicate_requests.get(request_key))
    return previous is not None and now - previous <= timedelta(seconds=window_seconds)


def _record_duplicate_request(
    request: dict[str, Any],
    rate_store: RateStore,
    now: datetime,
    window_seconds: int | None,
) -> None:
    if not window_seconds:
        return
    duplicate_requests = rate_store.setdefault("duplicate_requests", {})
    if isinstance(duplicate_requests, dict):
        duplicate_requests[_request_key(request)] = _format_ts(now)


def _limit_exceeded(rate_store: RateStore, bucket: str, now: datetime, limit: int) -> bool:
    write_events = rate_store.setdefault("write_events", {})
    if not isinstance(write_events, dict):
        write_events = {}
        rate_store["write_events"] = write_events

    kept = _recent_events(write_events.get(bucket), now)
    write_events[bucket] = [_format_ts(event) for event in kept]
    return len(kept) >= limit


def _record_write_event(rate_store: RateStore, bucket: str, now: datetime) -> None:
    write_events = rate_store.setdefault("write_events", {})
    if not isinstance(write_events, dict):
        write_events = {}
        rate_store["write_events"] = write_events
    events = _recent_events(write_events.get(bucket), now)
    events.append(now)
    write_events[bucket] = [_format_ts(event) for event in events]


def _recent_events(value: Any, now: datetime) -> list[datetime]:
    if not isinstance(value, list):
        return []
    cutoff = now - timedelta(hours=1)
    return [
        event
        for item in value
        if (event := _parse_stored_ts(item)) is not None and event > cutoff
    ]


def _request_key(request: dict[str, Any]) -> str:
    encoded = json.dumps(request, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _redacted_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"ok": True}
    summary: dict[str, Any] = {}
    for key, item in value.items():
        key_text = str(key)
        if _sensitive_key(key_text):
            continue
        if isinstance(item, bool) or isinstance(item, (int, float)):
            summary[key_text] = item
        elif isinstance(item, dict):
            nested = _redacted_result(item)
            if nested:
                summary[key_text] = nested
    return summary or {"ok": True}


def _sensitive_key(key: str) -> bool:
    lowered = key.lower()
    sensitive_fragments = (
        "operator",
        "repo",
        "url",
        "branch",
        "error",
        "secret",
        "token",
        "path",
        "trace",
    )
    return any(fragment in lowered for fragment in sensitive_fragments)


def _positive_int(value: Any) -> int | None:
    return value if isinstance(value, int) and value > 0 else None


def _parse_clock(value: str) -> datetime:
    parsed = _parse_stored_ts(value)
    if parsed is None:
        raise ValueError(f"clock returned invalid ISO-8601 timestamp: {value!r}")
    return parsed


def _parse_stored_ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_ts(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
