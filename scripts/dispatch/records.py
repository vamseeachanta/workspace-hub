#!/usr/bin/env python3
"""records.py — dispatch state as a durable record. workspace-hub#3740 slice 1.

867 issues sit at `dispatch:ready` and cannot advance: `SCHEMA.yaml:125`
documents `ready | active | done`, only `ready` was ever created, and nothing
reports back because the queue is drained by sessions that leave no trace.

**The record is the state. The label is a projection of it.**

Three reasons, each already demonstrated in this system:

1. A failed `gh issue edit` after the work finished destroys the completion.
   A committed record survives.
2. A label carries no evidence — not when, not which host, not what exit code —
   so deckhand#584 §4 ("finished but never published") has nothing to join on.
3. Two writers race, and labels have no compare-and-swap.

Point 3 was stated in the plan's first draft as *"…a git-backed record does"*.
**It does not.** Git offers no CAS across machines — only a push that may be
*rejected*, which is a retry signal, not a lock. Mutual exclusion is therefore
an explicit protocol (slice 2: create-only write → push → verify from the
remote → only then execute). This module's job is to make the record that
protocol operates on unambiguous.

This slice writes NO labels and creates none. `dispatch:active`/`dispatch:done`
land with the writer (plan D5): creating them earlier would turn every WALL in
chain.py into a clean-looking `0` while nothing wrote them.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 1

#: Mirrors SCHEMA.yaml:125. `blocked` is the quarantine terminal for a flapping
#: item — reverting forever is a loop nobody watches.
STATES = ("ready", "active", "done", "blocked")
TERMINAL = ("done", "blocked")

REQUIRED = ("schema", "issue", "state")

DEFAULT_TTL_MINUTES = 90
DEFAULT_MAX_ATTEMPTS = 3

#: How many beats fit inside one TTL. The interval is a FRACTION OF THE TTL, not
#: a constant, because every beat is a record write and `claim.py` commits AND
#: PUSHES every record write. A 30-second beat over a four-hour payload is ~480
#: commits pushed to `main` for one card; at `ttl/4` the same run costs eleven,
#: and raising the TTL — the very thing a long payload needs — lowers it further.
#:
#: Four, not two: after a beat lands at T the record is fresh until T+ttl, and
#: attempts fall at T+i … T+(N-1)i, so N-1 CONSECUTIVE beats may be lost to a
#: push race and the claim still survives. A beat is a push, and pushes lose
#: races to auto-sync routinely; an interval with no slack would turn an ordinary
#: lost race into an expired claim under a live job.
BEATS_PER_TTL = 4

#: Floor under the derived interval. `ttl/BEATS_PER_TTL` on a 20-second TTL is a
#: push every five seconds onto a branch several dispatch lanes and auto-sync are
#: already contending for — a beater that DoSes the thing it is protecting.
#: Configurations too tight for this floor are refused by `drain()`, not beaten
#: at slower than they need: silently under-beating is the original defect.
MIN_BEAT_SECONDS = 30

#: Hosts do not share a clock. A heartbeat this far ahead of the reader is
#: tolerated as ordinary drift; beyond it, it is reported as skew rather than
#: silently treated as either fresh or expired.
SKEW_GRACE_SECONDS = 120

_TS = "%Y-%m-%dT%H:%M:%SZ"


class RecordSchemaError(ValueError):
    """The record is not a shape this version understands.

    Refusing beats guessing: a half-read record from a future writer is how a
    migration silently corrupts history.
    """


class ClaimConflict(RuntimeError):
    """Another host holds a live claim on this issue."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(dt: datetime) -> str:
    return dt.strftime(_TS)


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, _TS).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# construction and transitions
# ---------------------------------------------------------------------------


def new_claim(issue: str, *, machine: str, host: str, job_id: str,
              queue_generation_id: str | None = None,
              ttl_minutes: int = DEFAULT_TTL_MINUTES,
              max_attempts: int = DEFAULT_MAX_ATTEMPTS, now=None) -> dict:
    """A claim on an issue. NOT a start — the work has not run yet.

    `claimed_at` is deliberately distinct from `started_at`: collapsing them
    makes "claimed but never started" — the split-brain symptom slice 2 exists
    to prevent — indistinguishable from a slow start.
    """
    ts = _stamp((now or _utcnow)())
    return {
        "schema": SCHEMA_VERSION,
        "issue": issue,
        "machine": machine,
        "state": "active",
        "previous_state": "ready",
        "reason": "claimed",
        "attempt": 1,
        "max_attempts": max_attempts,
        "host": host,
        "job_id": job_id,
        "queue_generation_id": queue_generation_id,
        "ttl_minutes": ttl_minutes,
        "claimed_at": ts,
        "heartbeat_at": ts,
        "started_at": None,
        "finished_at": None,
        "last_transition_at": ts,
        "returncode": None,
        "failure_category": None,
        "command_ref": None,
        "log_ref": None,
        "artifact_refs": [],
        "attempts": [{"attempt": 1, "host": host, "job_id": job_id,
                      "claimed_at": ts, "outcome": None}],
    }


def transition(record: dict, state: str, *, reason: str,
               returncode: int | None = None,
               failure_category: str | None = None, now=None) -> dict:
    """Move to a new state, keeping where it came from.

    `previous_state` and `last_transition_at` exist so a transition is auditable
    rather than only a current value — "it is done" and "it became done at T,
    from active" answer different questions, and §4 needs the second.
    """
    if state not in STATES:
        raise RecordSchemaError(f"state {state!r} not in {STATES}")
    ts = _stamp((now or _utcnow)())
    out = dict(record)
    out["previous_state"] = record.get("state")
    out["state"] = state
    out["reason"] = reason
    out["last_transition_at"] = ts
    if returncode is not None:
        out["returncode"] = returncode
    if failure_category is not None:
        out["failure_category"] = failure_category
    if state in TERMINAL:
        out["finished_at"] = ts
    attempts = [dict(a) for a in record.get("attempts") or []]
    if attempts:
        attempts[-1]["outcome"] = reason
    out["attempts"] = attempts
    return out


def reclaim(record: dict, *, host: str, job_id: str, now=None) -> dict:
    """A fresh attempt on an issue that was released or completed.

    Increments `attempt` and appends to `attempts` rather than overwriting: a
    record that forgets its own history cannot show that an item is flapping.
    """
    ts = _stamp((now or _utcnow)())
    out = dict(record)
    out["attempt"] = int(record.get("attempt") or 1) + 1
    out["previous_state"] = record.get("state")
    out["state"] = "active"
    out["reason"] = "reclaimed"
    out["host"] = host
    out["job_id"] = job_id
    out["claimed_at"] = ts
    out["heartbeat_at"] = ts
    out["started_at"] = None
    out["finished_at"] = None
    out["returncode"] = None
    out["last_transition_at"] = ts
    out["attempts"] = [dict(a) for a in record.get("attempts") or []] + [
        {"attempt": out["attempt"], "host": host, "job_id": job_id,
         "claimed_at": ts, "outcome": None}]
    return out


def heartbeat(record: dict, now=None) -> dict:
    """Refresh liveness.

    Beaten OUT-OF-BAND while the child process runs — a job blocked in a solver
    cannot beat for itself, and requiring it to would make every long run look
    dead. `drain.Heartbeat` is that out-of-band beater and `claim.beat` is the
    write; this function is PURE and decides nothing.

    In particular it does not check whether the record is still ours or still
    live, because at this level there is nothing to check it against. That check
    is `claim.beat`'s, and it is not optional: refreshing a record whose payload
    is dead strands the issue permanently, which is strictly worse than the
    expiry-under-a-live-job this function exists to prevent.
    """
    out = dict(record)
    out["heartbeat_at"] = _stamp((now or _utcnow)())
    return out


def beat_interval_seconds(ttl_minutes: int | None = None) -> int:
    """How often a held claim must be beaten, given its own TTL.

    Derived rather than configured so the two numbers cannot drift apart: an
    interval set independently of the TTL is one deploy away from exceeding it,
    and the symptom — a live job reclaimed by another host — appears nowhere near
    the setting that caused it.
    """
    ttl = int(ttl_minutes or DEFAULT_TTL_MINUTES) * 60
    return max(MIN_BEAT_SECONDS, ttl // BEATS_PER_TTL)


# ---------------------------------------------------------------------------
# liveness
# ---------------------------------------------------------------------------


def is_expired(record: dict, now=None) -> bool:
    """Past its OWN ttl. A future heartbeat is skew, never expiry.

    Treating a future timestamp as expiry would requeue live work whenever a
    host runs fast, and the symptom would present as random job loss.
    """
    beat = _parse(record.get("heartbeat_at"))
    if beat is None:
        return True                       # unknown liveness is not freshness
    current = (now or _utcnow)()
    # REDUNDANT BY ARITHMETIC, kept deliberately. A future heartbeat gives a
    # negative age, which can never exceed a positive TTL, so the comparison
    # below already returns False. Mutation-testing this branch to `if False`
    # leaves every test green — the guard is documentation, not logic.
    #
    # Retained because the next reader should not have to derive "negative
    # durations cannot exceed a positive TTL" to be sure live work is safe from
    # a fast clock, and because a future refactor to absolute-value or
    # clamped arithmetic would make it load-bearing without warning.
    if beat > current:
        return False
    ttl = int(record.get("ttl_minutes") or DEFAULT_TTL_MINUTES)
    return current - beat > timedelta(minutes=ttl)


def clock_skew_detected(record: dict, now=None) -> bool:
    beat = _parse(record.get("heartbeat_at"))
    if beat is None:
        return False
    return (beat - (now or _utcnow)()) > timedelta(seconds=SKEW_GRACE_SECONDS)


def should_quarantine(record: dict) -> bool:
    """Stop reverting once attempts are exhausted.

    An unbounded retry loop is this epic's defect wearing a helpful face: it
    looks like resilience and hides a job that can never succeed.
    """
    return int(record.get("attempt") or 1) >= int(
        record.get("max_attempts") or DEFAULT_MAX_ATTEMPTS)


def is_success(record: dict) -> bool:
    """`done` means ran to completion, NOT that it worked.

    Conflating them would let §4 count a failed run as delivered work — the
    chain would show completion where there is a failure to investigate.
    """
    return record.get("state") == "done" and record.get("returncode") == 0


# ---------------------------------------------------------------------------
# validation and persistence
# ---------------------------------------------------------------------------


def validate(record: dict) -> dict:
    if not isinstance(record, dict):
        raise RecordSchemaError("record must be a mapping")
    for field in REQUIRED:
        if field not in record:
            raise RecordSchemaError(f"missing required field {field!r}")
    if record["schema"] != SCHEMA_VERSION:
        raise RecordSchemaError(
            f"schema {record['schema']!r} != {SCHEMA_VERSION} — refusing to guess "
            "at an unknown shape; add an explicit migration"
        )
    if record["state"] not in STATES:
        raise RecordSchemaError(f"state {record['state']!r} not in {STATES}")
    return record


def record_path(root: Path, issue: str) -> Path:
    """One flat file per issue.

    `owner/repo#123` contains a path separator: left unescaped it would write
    into a nested directory and the record would be *unfindable* rather than
    wrong, which is the worse failure.
    """
    safe = re.sub(r"[^A-Za-z0-9._#-]", "-", issue)
    return Path(root) / f"{safe}.json"


def read_record(path: Path) -> dict:
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))


def write_record(root: Path, record: dict) -> Path:
    """Create-only against a LIVE claim held by someone else.

    Not sufficient on its own — git gives no cross-machine CAS, so slice 2 adds
    push-and-verify. But a local overwrite must not be what loses a claim before
    the protocol even runs.
    """
    validate(record)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = record_path(root, record["issue"])
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        live = existing.get("state") not in TERMINAL
        same_worker = (existing.get("host") == record.get("host")
                       and existing.get("job_id") == record.get("job_id"))
        newer_attempt = int(record.get("attempt") or 1) > int(existing.get("attempt") or 1)
        if live and not same_worker and not newer_attempt:
            raise ClaimConflict(
                f"{record['issue']} is held by {existing.get('host')}"
                f"/{existing.get('job_id')} in state {existing.get('state')!r}"
            )
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return path
