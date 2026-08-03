#!/usr/bin/env python3
"""Claim protocol — mutual exclusion built from a push, not assumed from git.

workspace-hub#3740 slice 2.

## What this exists to prevent

Split-brain execution: two hosts with stale queue files both drain the same
card, both start work, and the first record to land silently wins while the
second job runs unrecorded.

That is not theoretical here. There is **one floating Orcina `Flex` seat
fleet-wide** (wh#3721): two concurrent dispatches fail on licence checkout,
wherever they land. A race does not merely duplicate work — it wastes both
attempts and produces two confusing failures.

## Why a protocol rather than a property

The plan's first draft argued the record beats the label because *"labels have
no compare-and-swap; a git-backed record does."* **Git provides no CAS across
machines.** It provides a push that may be **rejected**, which is a retry
signal. Two hosts can each write a record locally and each believe they hold
the item.

So exclusion is an ordering, and the order is the whole design:

    1. write claim (create-only)
    2. push
    3. REJECTED  -> someone else claimed it. Pull, re-read, DO NOT EXECUTE.
    4. accepted  -> re-read FROM THE REMOTE, confirm the claim is ours
    5. only then -> execute

Steps 3 and 4 are load-bearing. Step 4 exists because an accepted push proves
the *write* landed, not that *our* claim is the one that survived a concurrent
merge — the remote is the only authority on that.

## Fail-closed here, unlike #580

If push or verify fails, **the job does not run**. That is the opposite of the
notification-channel decision in deckhand#580, and deliberately so: there, a
wrong DENY converted a delivery outage into a submission outage. Here a wrong
ALLOW means two hosts executing the same work against a one-seat licence. The
asymmetry points the other way, so the answer does too.

Hermetic: the git surface is injected. No network, no real repo.

Run: uv run --with pyyaml pytest tests/dispatch/test_claim_protocol.py
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAIM_PY = REPO_ROOT / "scripts" / "dispatch" / "claim.py"


def _load():
    pkg = str(CLAIM_PY.parent)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location("dispatch_claim", CLAIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_claim"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
ISSUE = "vamseeachanta/digitalmodel#1885"


class FakeGit:
    """Injected git surface. Records the call order so the ORDER can be asserted.

    The protocol's correctness is entirely in the ordering, so a test that only
    checks the outcome would pass on an implementation that executed first and
    pushed afterwards.
    """

    def __init__(self, push_ok=True, remote_record=None):
        self.push_ok = push_ok
        self.remote_record = remote_record
        self.calls: list[str] = []

    def commit(self, path, message):
        self.calls.append("commit")
        return True

    def push(self):
        self.calls.append("push")
        return self.push_ok

    def pull(self):
        self.calls.append("pull")
        return True

    def read_remote(self, issue):
        self.calls.append("read_remote")
        return self.remote_record


def _ours(**kw):
    base = {"schema": 1, "issue": ISSUE, "state": "active",
            "host": "ace-linux-1", "job_id": "j1", "attempt": 1}
    base.update(kw)
    return base


# --------------------------------------------------------------------------
# the dangerous cases first
# --------------------------------------------------------------------------


def test_rejected_push_means_DO_NOT_EXECUTE(tmp_path):
    """Someone else claimed it between our read and our push."""
    git = FakeGit(push_ok=False)
    got = C.acquire(tmp_path, _ours(), git=git)
    assert got.ok is False
    assert "rejected" in got.reason.lower()


def test_a_rejected_push_still_pulls_so_the_next_read_is_current(tmp_path):
    """Leaving the clone behind guarantees the next attempt races again."""
    git = FakeGit(push_ok=False)
    C.acquire(tmp_path, _ours(), git=git)
    assert "pull" in git.calls


def test_an_accepted_push_is_NOT_sufficient(tmp_path):
    """The core subtlety.

    A push proves OUR WRITE landed, not that OUR CLAIM survived. A concurrent
    merge can accept the push while the remote holds someone else's claim.
    """
    git = FakeGit(push_ok=True,
                  remote_record=_ours(host="ace-linux-2", job_id="OTHER"))
    got = C.acquire(tmp_path, _ours(), git=git)
    assert got.ok is False, "an accepted push must not be read as ownership"
    assert "not ours" in got.reason.lower() or "other" in got.reason.lower()


def test_verify_reads_from_the_REMOTE_not_the_working_tree(tmp_path):
    """A local file is what we just wrote; it can only ever agree with us."""
    git = FakeGit(push_ok=True, remote_record=_ours())
    C.acquire(tmp_path, _ours(), git=git)
    assert "read_remote" in git.calls


def test_the_order_is_write_push_verify(tmp_path):
    git = FakeGit(push_ok=True, remote_record=_ours())
    C.acquire(tmp_path, _ours(), git=git)
    assert git.calls.index("commit") < git.calls.index("push") < git.calls.index("read_remote")


def test_a_clean_acquire_succeeds(tmp_path):
    git = FakeGit(push_ok=True, remote_record=_ours())
    got = C.acquire(tmp_path, _ours(), git=git)
    assert got.ok is True and got.record["job_id"] == "j1"


# --------------------------------------------------------------------------
# fail closed on anything unknown
# --------------------------------------------------------------------------


def test_an_unreadable_remote_refuses_rather_than_assuming(tmp_path):
    """Cannot-verify is not verified.

    Treating an unreachable remote as success is precisely the failure this
    whole epic keeps meeting: absence of a negative signal read as a positive.
    """
    git = FakeGit(push_ok=True, remote_record=None)
    got = C.acquire(tmp_path, _ours(), git=git)
    assert got.ok is False


def test_a_git_error_refuses(tmp_path):
    class Boom(FakeGit):
        def push(self):
            raise OSError("network gone")

    got = C.acquire(tmp_path, _ours(), git=Boom())
    assert got.ok is False
    assert got.record is None


def test_refusal_never_leaves_the_caller_thinking_it_holds_the_claim(tmp_path):
    """`ok is False` must come with no usable record.

    Returning a record on failure invites `if result.record:` — which reads as
    success and would execute.
    """
    for git in (FakeGit(push_ok=False), FakeGit(push_ok=True, remote_record=None)):
        got = C.acquire(tmp_path, _ours(), git=git)
        assert got.ok is False and got.record is None


# --------------------------------------------------------------------------
# stale queue generation
# --------------------------------------------------------------------------


def test_a_claim_from_a_stale_queue_generation_is_refused(tmp_path):
    """A host draining last week's queue file must not claim today's work.

    Without this, a stale clone quietly competes with a current one and the
    older queue can win the race.
    """
    got = C.acquire(tmp_path, _ours(queue_generation_id="q-OLD"),
                    git=FakeGit(push_ok=True, remote_record=_ours()),
                    current_generation="q-NEW")
    assert got.ok is False
    assert "generation" in got.reason.lower()


def test_a_matching_generation_is_allowed(tmp_path):
    rec = _ours(queue_generation_id="q-NEW")
    got = C.acquire(tmp_path, rec, git=FakeGit(push_ok=True, remote_record=rec),
                    current_generation="q-NEW")
    assert got.ok is True


def test_no_generation_declared_is_allowed_but_reported(tmp_path):
    """Back-compat with queue files predating generation ids — visible, not fatal."""
    got = C.acquire(tmp_path, _ours(), git=FakeGit(push_ok=True, remote_record=_ours()),
                    current_generation="q-NEW")
    assert got.ok is True
    assert got.warnings, "an unverifiable generation must be reported"


# --------------------------------------------------------------------------
# release
# --------------------------------------------------------------------------


def test_release_records_the_outcome_and_pushes(tmp_path):
    git = FakeGit(push_ok=True, remote_record=_ours())
    rec = C.acquire(tmp_path, _ours(), git=git).record
    out = C.release(tmp_path, rec, state="done", reason="completed",
                    returncode=0, git=git)
    assert out.ok is True
    assert out.record["state"] == "done"
    assert git.calls.count("push") == 2


def test_a_failed_release_push_is_reported_not_swallowed(tmp_path):
    """A completion that never reaches the remote is invisible to everyone else.

    Silently dropping it recreates the original defect one layer up: work that
    finished with nothing recording it.
    """
    git = FakeGit(push_ok=True, remote_record=_ours())
    rec = C.acquire(tmp_path, _ours(), git=git).record
    git.push_ok = False
    out = C.release(tmp_path, rec, state="done", reason="completed",
                    returncode=0, git=git)
    assert out.ok is False and out.reason
