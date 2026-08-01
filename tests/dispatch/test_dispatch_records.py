#!/usr/bin/env python3
"""Dispatch records — the state is a record, the label is a projection. #3740 slice 1.

867 issues sit at `dispatch:ready` and cannot advance: `SCHEMA.yaml:125` documents
`ready | active | done`, and only `ready` was ever created. Nothing writes a later
state because nothing reports back — the queue is drained by sessions, and a
session that finishes leaves no trace.

## Why the record is authoritative and the label derived

Three reasons, each of which has already bitten this system:

1. **A failed API call loses the fact.** `gh issue edit` failing after the work
   finished destroys the completion. A committed record survives.
2. **A label carries no evidence.** `dispatch:done` cannot say *when*, *which
   host*, *what exit code* — so §4 ("finished but never published") has nothing
   to join on.
3. **Two writers race.** Labels have no compare-and-swap.

Point 3 needed correcting during review, and the correction is the reason this
module exists in the shape it does. The plan's first draft finished it with
*"…a git-backed record does."* **It does not.** Git offers no CAS across
machines — only a push that may be *rejected*, which is a retry signal, not a
lock. So mutual exclusion is an explicit protocol (slice 2), and this module's
job is to make the record it operates on unambiguous: create-only semantics,
schema-checked, with a claim distinct from a start.

## What this slice is NOT

No labels are written and none are created. `dispatch:active`/`dispatch:done`
land last, with the writer (plan D5) — creating them now would turn every WALL
in `chain.py` into a clean-looking `0` while nothing wrote them.

Hermetic: pure functions, injected clock, tmp_path. No gh, no git, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_dispatch_records.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_PY = REPO_ROOT / "scripts" / "dispatch" / "records.py"


def _load():
    spec = importlib.util.spec_from_file_location("dispatch_records", RECORDS_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_records"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
ISSUE = "vamseeachanta/digitalmodel#1885"


def _clock(dt=NOW):
    return lambda: dt


# --------------------------------------------------------------------------
# shape and schema
# --------------------------------------------------------------------------


def test_a_new_claim_records_who_and_when():
    rec = R.new_claim(ISSUE, machine="dev-primary", host="ace-linux-1",
                      job_id="j1", queue_generation_id="q1", now=_clock())
    assert rec["issue"] == ISSUE
    assert rec["state"] == "active"
    assert rec["attempt"] == 1
    assert rec["claimed_at"] == "2026-08-01T12:00:00Z"
    assert rec["host"] == "ace-linux-1" and rec["job_id"] == "j1"


def test_claimed_at_is_distinct_from_started_at():
    """A claim precedes the work.

    Collapsing them would make 'claimed but never started' — the split-brain
    symptom slice 2 exists to prevent — indistinguishable from a slow start.
    """
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    assert rec["claimed_at"] is not None
    assert rec.get("started_at") is None


def test_unknown_schema_version_refuses_rather_than_guessing():
    """A record from a future writer must not be half-read.

    Guessing at an unknown shape is how a migration silently corrupts history.
    """
    with pytest.raises(R.RecordSchemaError):
        R.validate({"schema": 999, "issue": ISSUE, "state": "done"})


def test_missing_required_field_refuses():
    with pytest.raises(R.RecordSchemaError):
        R.validate({"schema": 1, "state": "done"})     # no issue


def test_state_must_be_from_the_declared_lifecycle():
    with pytest.raises(R.RecordSchemaError):
        R.validate(dict(R.new_claim(ISSUE, machine="m", host="h", job_id="j",
                                    now=_clock()), state="finished-ish"))


# --------------------------------------------------------------------------
# transitions are auditable, not just current values
# --------------------------------------------------------------------------


def test_transition_records_where_it_came_from():
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    done = R.transition(rec, "done", reason="completed", returncode=0,
                        now=_clock(NOW + timedelta(minutes=5)))
    assert done["state"] == "done"
    assert done["previous_state"] == "active"
    assert done["last_transition_at"] == "2026-08-01T12:05:00Z"


def test_a_done_with_a_nonzero_returncode_is_a_RESULT_not_a_success():
    """`done` means "ran to completion", not "worked".

    Conflating them would let §4 count a failed run as delivered work — the
    chain would show completion where there is a failure to investigate.
    """
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    done = R.transition(rec, "done", reason="completed", returncode=2,
                        failure_category="solver-error", now=_clock())
    assert done["state"] == "done"
    assert done["returncode"] == 2
    assert done["failure_category"] == "solver-error"
    assert R.is_success(done) is False


def test_is_success_requires_done_AND_zero():
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    assert R.is_success(R.transition(rec, "done", reason="c", returncode=0,
                                     now=_clock())) is True
    assert R.is_success(rec) is False          # still active


def test_attempts_accumulate_rather_than_overwrite():
    """Flapping must be countable. An overwritten record hides its own history."""
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j1", now=_clock())
    rec = R.transition(rec, "ready", reason="heartbeat expired", now=_clock())
    rec2 = R.reclaim(rec, host="h2", job_id="j2",
                     now=_clock(NOW + timedelta(hours=2)))
    assert rec2["attempt"] == 2
    assert len(rec2["attempts"]) == 2
    assert rec2["attempts"][0]["outcome"] == "heartbeat expired"


# --------------------------------------------------------------------------
# heartbeat, TTL, skew, quarantine
# --------------------------------------------------------------------------


def _active(ttl=90, beat=NOW):
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", ttl_minutes=ttl,
                      now=_clock())
    return R.heartbeat(rec, now=_clock(beat))


def test_fresh_heartbeat_is_not_expired():
    assert R.is_expired(_active(), now=_clock(NOW + timedelta(minutes=30))) is False


def test_expired_past_its_own_ttl():
    assert R.is_expired(_active(ttl=30), now=_clock(NOW + timedelta(minutes=45))) is True


def test_ttl_is_per_job_not_global():
    """A ~57-sim OrcaFlex batch is not a 20-second smoke test.

    A single global TTL requeues legitimate long runs, which is worse than not
    expiring at all — it interrupts work that was fine.
    """
    long_job = _active(ttl=600)
    assert R.is_expired(long_job, now=_clock(NOW + timedelta(hours=5))) is False


def test_a_future_heartbeat_is_SKEW_not_expiry():
    """Hosts do not share a clock.

    Treating a future timestamp as expiry would requeue live work whenever a
    host runs fast — and the symptom would look like random job loss.
    """
    rec = _active(beat=NOW + timedelta(hours=3))
    assert R.is_expired(rec, now=_clock(NOW)) is False
    assert R.clock_skew_detected(rec, now=_clock(NOW)) is True


def test_small_skew_is_tolerated_not_flagged():
    rec = _active(beat=NOW + timedelta(seconds=20))
    assert R.clock_skew_detected(rec, now=_clock(NOW)) is False


def test_quarantine_after_max_attempts():
    """An unbounded retry loop is this epic's defect wearing a helpful face."""
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", max_attempts=2,
                      now=_clock())
    rec = R.transition(rec, "ready", reason="heartbeat expired", now=_clock())
    rec = R.reclaim(rec, host="h", job_id="j2", now=_clock())
    rec = R.transition(rec, "ready", reason="heartbeat expired", now=_clock())
    assert R.should_quarantine(rec) is True


def test_below_the_limit_does_not_quarantine():
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", max_attempts=3,
                      now=_clock())
    assert R.should_quarantine(rec) is False


# --------------------------------------------------------------------------
# persistence is create-only
# --------------------------------------------------------------------------


def test_write_then_read_roundtrips(tmp_path):
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    p = R.write_record(tmp_path, rec)
    assert R.read_record(p)["issue"] == ISSUE


def test_write_refuses_to_clobber_a_live_claim_from_another_host(tmp_path):
    """The record-level half of the claim protocol.

    Not sufficient on its own — git gives no cross-machine CAS, so slice 2 adds
    push-and-verify. But a local overwrite must not be the thing that loses a
    claim before the protocol even runs.
    """
    first = R.new_claim(ISSUE, machine="m", host="h1", job_id="j1", now=_clock())
    R.write_record(tmp_path, first)
    other = R.new_claim(ISSUE, machine="m", host="h2", job_id="j2", now=_clock())
    with pytest.raises(R.ClaimConflict):
        R.write_record(tmp_path, other)


def test_the_same_host_and_job_may_update_its_own_record(tmp_path):
    rec = R.new_claim(ISSUE, machine="m", host="h1", job_id="j1", now=_clock())
    R.write_record(tmp_path, rec)
    R.write_record(tmp_path, R.heartbeat(rec, now=_clock(NOW + timedelta(minutes=5))))
    assert R.read_record(R.record_path(tmp_path, ISSUE))["state"] == "active"


def test_a_terminal_record_may_be_reclaimed(tmp_path):
    """A finished item can legitimately be re-run later; a live one cannot."""
    rec = R.transition(R.new_claim(ISSUE, machine="m", host="h1", job_id="j1",
                                   now=_clock()), "done", reason="c",
                       returncode=0, now=_clock())
    R.write_record(tmp_path, rec)
    again = R.reclaim(rec, host="h2", job_id="j2", now=_clock())
    R.write_record(tmp_path, again)          # must not raise
    assert R.read_record(R.record_path(tmp_path, ISSUE))["attempt"] == 2


def test_record_filename_is_filesystem_safe(tmp_path):
    """`owner/repo#123` contains a path separator.

    Left unescaped it would silently write into a nested directory, and the
    record would be unfindable rather than wrong — the worst failure shape.
    """
    p = R.record_path(tmp_path, ISSUE)
    assert p.parent == tmp_path, f"record escaped into {p.parent}"
    assert "#" in p.name or "-" in p.name


def test_written_record_is_valid_json_with_schema(tmp_path):
    rec = R.new_claim(ISSUE, machine="m", host="h", job_id="j", now=_clock())
    p = R.write_record(tmp_path, rec)
    assert json.loads(p.read_text())["schema"] == R.SCHEMA_VERSION
