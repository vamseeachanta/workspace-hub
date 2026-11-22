"""Pure last-seen summaries of explicit, synthetic-compatible heartbeat records.

This module performs no discovery, I/O, clock reads or evidence publishing.
The supported logical roles (worker, reviewer, controller) are categories, not
an inventory. Each record must contain exactly ``role`` and ``observed_at``.
Timestamps use RFC3339 with explicit seconds and a known UTC offset; leap
seconds, sub-microsecond precision and unknown local offsets are unsupported
and remain unverified.

``summarize_heartbeats`` returns a mapping with role, last_seen (UTC ISO text or
None), state and stable reason_codes. Unknown requested roles are never echoed.
Records for other known roles are ignored after validation. Any malformed,
unknown-role or future record invalidates the collection's status, including
records that cannot safely be attributed to the requested role. A valid prior
last_seen is retained, but does not override an unverified state.

A valid elapsed time is fresh at or below freshness, stale above freshness and
below offline_after, and offline at or above offline_after. These boundaries
are this API's contract, not operational defaults. Offline describes missing
recent evidence; it does not establish actual reachability or readiness.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
import re
from typing import Any


KNOWN_ROLES = frozenset({"worker", "reviewer", "controller"})
# RFC3339 offset ranges: hours 00 through 23, minutes 00 through 59.
# Fractional seconds are limited to Python datetime microsecond precision.
# Calendar ranges are validated by datetime.
_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?"
    r"(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)",
    re.ASCII,
)


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        return None
    if value.endswith("-00:00"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except (ValueError, OverflowError):
        return None


def _known_role(value: Any) -> bool:
    return isinstance(value, str) and value in KNOWN_ROLES


def summarize_heartbeats(
    role: str,
    records: Sequence[Mapping[str, Any]],
    *,
    as_of: str,
    freshness: timedelta,
    offline_after: timedelta,
) -> dict[str, Any]:
    """Summarize supplied evidence without modifying it or accessing resources.

    Caller configuration errors raise ValueError: as_of must be a supported
    timestamp and durations must satisfy zero <= freshness < offline_after.
    Malformed evidence produces unverified rather than raising. There are no
    default thresholds and no wall-clock fallback. The accepted collection is
    a sequence (such as a list or tuple), not a file, mapping or lazy iterator.
    Reason codes are deduplicated and sorted when evidence is unverified.
    """
    now = _timestamp(as_of)
    if now is None:
        raise ValueError("as_of must be a timestamp with a known UTC offset")
    if (
        not isinstance(freshness, timedelta)
        or not isinstance(offline_after, timedelta)
        or not timedelta() <= freshness < offline_after
    ):
        raise ValueError("durations must satisfy zero <= freshness < offline_after")

    result: dict[str, Any] = {
        "role": role if _known_role(role) else None,
        "last_seen": None,
        "state": "unverified",
        "reason_codes": [],
    }
    if not _known_role(role):
        result["reason_codes"] = ["unknown_role"]
        return result
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        result["reason_codes"] = ["malformed_evidence"]
        return result

    latest = None
    reasons = set()
    for record in records:
        if not isinstance(record, Mapping) or set(record) != {"role", "observed_at"}:
            reasons.add("malformed_evidence")
            continue
        if not _known_role(record["role"]):
            reasons.add("unknown_role")
            continue
        observed = _timestamp(record["observed_at"])
        if observed is None:
            reasons.add("malformed_evidence")
        elif observed > now:
            reasons.add("future_evidence")
        elif record["role"] == role and (latest is None or observed > latest):
            latest = observed

    if latest is not None:
        result["last_seen"] = latest.isoformat()
    if reasons:
        result["reason_codes"] = sorted(reasons)
        return result
    if latest is None:
        result["reason_codes"] = ["missing_evidence"]
        return result

    elapsed = now - latest
    if elapsed <= freshness:
        result.update(state="fresh", reason_codes=["within_freshness"])
    elif elapsed < offline_after:
        result.update(state="stale", reason_codes=["freshness_exceeded"])
    else:
        result.update(state="offline", reason_codes=["offline_threshold_reached"])
    return result
