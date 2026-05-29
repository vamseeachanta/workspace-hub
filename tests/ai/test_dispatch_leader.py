"""Tests for scripts/ai/dispatch_leader.py (#2847 Phase 1).

Phase 1 = git-committed heartbeat + the SELF-FENCING invariant (lease writes
require a confirmed push) + detect-and-alert. NO auto-promotion (that is Phase 2).
The LeaderStateStore is injected so these unit tests never touch real git.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "dispatch_leader.py"
spec = importlib.util.spec_from_file_location("dispatch_leader", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["dispatch_leader"] = module
spec.loader.exec_module(module)

LeaderState = module.LeaderState
ClaimResult = module.ClaimResult
Status = module.Status
StoreUnavailable = module.StoreUnavailable
may_write_leases = module.may_write_leases
check = module.check


T0 = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)


def _state(leader="ace-linux-1", term=5, hb=T0, pid=111):
    return LeaderState(
        leader=leader, term=term, heartbeat_utc=hb.isoformat(), heartbeat_pid=pid
    )


class FakeStore:
    """Scripted store: read() returns `state` (or raises `read_exc`); claim()
    records the attempt and returns `claim_result`."""

    def __init__(self, state=None, claim_result=None, read_exc=None):
        self._state = state
        self._claim_result = claim_result
        self._read_exc = read_exc
        self.claims = []

    def read(self):
        if self._read_exc is not None:
            raise self._read_exc
        return self._state

    def claim(self, state):
        self.claims.append(state)
        return self._claim_result


class Alerts:
    def __init__(self):
        self.msgs = []

    def __call__(self, msg):
        self.msgs.append(msg)


# ── self-fence: may_write_leases ────────────────────────────────────────────

def test_may_write_requires_confirmed_push():
    store = FakeStore(state=_state(), claim_result=ClaimResult.PUSHED)
    assert may_write_leases(store, "ace-linux-1", 5, now=T0) is True
    assert len(store.claims) == 1  # heartbeat refreshed


def test_may_write_false_when_push_rejected():
    store = FakeStore(state=_state(), claim_result=ClaimResult.REJECTED)
    assert may_write_leases(store, "ace-linux-1", 5, now=T0) is False


def test_may_write_false_when_push_failed_self_fence():
    # The load-bearing BLOCKER-2 invariant: cannot prove reachable -> stand down.
    store = FakeStore(state=_state(), claim_result=ClaimResult.PUSH_FAILED)
    assert may_write_leases(store, "ace-linux-1", 5, now=T0) is False


def test_may_write_false_when_superseded_by_higher_term():
    store = FakeStore(state=_state(term=6), claim_result=ClaimResult.PUSHED)
    # my_term=5 but committed term=6 -> someone else took over -> demote, no claim
    assert may_write_leases(store, "ace-linux-1", 5, now=T0) is False
    assert store.claims == []


def test_may_write_false_when_not_leader():
    store = FakeStore(state=_state(leader="ace-linux-2"), claim_result=ClaimResult.PUSHED)
    assert may_write_leases(store, "ace-linux-1", 5, now=T0) is False
    assert store.claims == []


# ── detect-and-alert: check ─────────────────────────────────────────────────

def test_check_returns_leader_for_self():
    store = FakeStore(state=_state(leader="ace-linux-1"))
    assert check(store, "ace-linux-1", now=T0) is Status.LEADER


def test_check_fresh_heartbeat_ok():
    store = FakeStore(state=_state(leader="ace-linux-1", hb=T0))
    now = T0 + timedelta(seconds=module.HEARTBEAT_PERIOD_S)  # within threshold
    assert check(store, "ace-linux-2", now=now) is Status.OK


def test_check_stale_heartbeat_alerts_no_promotion():
    alerts = Alerts()
    store = FakeStore(state=_state(leader="ace-linux-1", hb=T0))
    now = T0 + timedelta(seconds=module.STALE_THRESHOLD_S + 60)
    assert check(store, "ace-linux-2", now=now, alert=alerts) is Status.STALE
    assert alerts.msgs  # alerted
    assert store.claims == []  # Phase 1: NEVER attempts to claim/promote


def test_check_store_unavailable_is_undetermined_never_acts():
    alerts = Alerts()
    store = FakeStore(read_exc=StoreUnavailable("git pull failed"))
    assert check(store, "ace-linux-2", now=T0, alert=alerts) is Status.UNDETERMINED
    assert alerts.msgs
    assert store.claims == []  # inconclusive -> never promote


def test_check_term_regression_is_undetermined():
    alerts = Alerts()
    store = FakeStore(state=_state(leader="ace-linux-1", term=3))
    # last_known_term=5 but committed term=3 -> corruption/rollback
    assert check(store, "ace-linux-2", now=T0, last_known_term=5, alert=alerts) is Status.UNDETERMINED
    assert alerts.msgs


# ── leader_can_originate (Phase 1b gate entrypoint) ─────────────────────────

def test_can_originate_true_when_leader_and_push_confirmed():
    store = FakeStore(state=_state(leader="ace-linux-1", term=5), claim_result=ClaimResult.PUSHED)
    assert module.leader_can_originate(store, "ace-linux-1", now=T0) is True


def test_can_originate_false_when_not_leader():
    store = FakeStore(state=_state(leader="ace-linux-1"), claim_result=ClaimResult.PUSHED)
    assert module.leader_can_originate(store, "ace-linux-2", now=T0) is False
    assert store.claims == []  # not leader -> never heartbeats


def test_can_originate_false_when_push_cannot_be_confirmed():
    store = FakeStore(state=_state(leader="ace-linux-1", term=5), claim_result=ClaimResult.PUSH_FAILED)
    assert module.leader_can_originate(store, "ace-linux-1", now=T0) is False  # self-fence


def test_can_originate_false_when_store_unavailable():
    store = FakeStore(read_exc=StoreUnavailable("uninitialized"))
    assert module.leader_can_originate(store, "ace-linux-1", now=T0) is False


# ── invariants ──────────────────────────────────────────────────────────────

def test_threshold_coherence_invariant():
    # STALE must exceed the heartbeat period (so a single missed beat isn't "dead")
    # and stay well under the lease TTL (so failover reasons within a lease window).
    assert module.HEARTBEAT_PERIOD_S < module.STALE_THRESHOLD_S < module.LEASE_TTL_S


def test_leaderstate_roundtrips_through_dict():
    st = _state()
    assert LeaderState.from_dict(st.to_dict()) == st


# ── GitLeaderStateStore — real git integration (no network; local bare origin) ──

import subprocess


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)


def _make_origin_and_clone(tmp_path):
    """A bare origin + a clone with a seeded main (the dedicated leadership ref is
    created lazily by the first claim, so main only needs a base commit)."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    _git(work, "config", "user.email", "t@t"); _git(work, "config", "user.name", "t")
    (work / "seed.txt").write_text("seed\n")
    _git(work, "add", "-A"); _git(work, "commit", "-q", "-m", "seed")
    _git(work, "push", "-q", "origin", "main")
    return origin, work


def _clone(origin, dest):
    subprocess.run(["git", "clone", str(origin), str(dest)], check=True, capture_output=True)
    _git(dest, "config", "user.email", "t@t"); _git(dest, "config", "user.name", "t")
    return dest


def test_gitstore_claim_bootstrap_then_read_roundtrip(tmp_path):
    GitLeaderStateStore = module.GitLeaderStateStore
    _, work = _make_origin_and_clone(tmp_path)
    store = GitLeaderStateStore(work)
    assert store.claim(_state(leader="ace-linux-1", term=1)) is ClaimResult.PUSHED  # bootstrap
    got = GitLeaderStateStore(work).read()
    assert got.leader == "ace-linux-1" and got.term == 1


def test_gitstore_read_uninitialized_ref_is_unavailable(tmp_path):
    GitLeaderStateStore = module.GitLeaderStateStore
    _, work = _make_origin_and_clone(tmp_path)
    with pytest.raises(StoreUnavailable):
        GitLeaderStateStore(work).read()  # dedicated ref doesn't exist yet


def test_gitstore_claim_writes_nothing_to_main_working_tree(tmp_path):
    # The dedicated-ref design must NOT create a commit on main or dirty the tree.
    GitLeaderStateStore = module.GitLeaderStateStore
    _, work = _make_origin_and_clone(tmp_path)
    head_before = _git(work, "rev-parse", "HEAD").stdout.strip()
    GitLeaderStateStore(work).claim(_state(term=1))
    head_after = _git(work, "rev-parse", "HEAD").stdout.strip()
    assert head_before == head_after  # main HEAD unmoved
    status = _git(work, "status", "--porcelain").stdout.strip()
    assert status == ""  # working tree clean


def test_gitstore_push_race_exactly_one_winner(tmp_path):
    """Two clones claim term 2 from the same parent — exactly one PUSHED, the
    other REJECTED (stale --force-with-lease). The atomic CAS Phase 2 builds on."""
    GitLeaderStateStore = module.GitLeaderStateStore
    origin, work_a = _make_origin_and_clone(tmp_path)
    GitLeaderStateStore(work_a).claim(_state(term=1))  # bootstrap term 1
    work_b = _clone(origin, tmp_path / "work_b")
    # Two processes both READ the same parent (term 1) before either claims.
    sa = GitLeaderStateStore(work_a); sa.read()
    sb = GitLeaderStateStore(work_b); sb.read()
    res_a = sa.claim(_state(leader="ace-linux-1", term=2))  # CAS vs term1 -> wins
    res_b = sb.claim(_state(leader="ace-linux-2", term=2))  # CAS vs term1 (now stale) -> loses
    assert {res_a, res_b} == {ClaimResult.PUSHED, ClaimResult.REJECTED}


def test_gitstore_rejected_claim_does_not_brick_reads(tmp_path):
    """BLOCKER-1 regression: a lost race must NOT brick subsequent reads. With the
    dedicated-ref/plumbing design there is no divergent commit on main, so read()
    keeps returning the winner's state."""
    GitLeaderStateStore = module.GitLeaderStateStore
    origin, work_a = _make_origin_and_clone(tmp_path)
    GitLeaderStateStore(work_a).claim(_state(leader="ace-linux-1", term=1))
    work_b = _clone(origin, tmp_path / "work_b")
    sb = GitLeaderStateStore(work_b); sb.read()                          # B observes term 1
    GitLeaderStateStore(work_a).claim(_state(leader="ace-linux-1", term=2))  # A advances origin
    loser = sb.claim(_state(leader="ace-linux-2", term=2))               # CAS vs term1 -> REJECTED
    assert loser is ClaimResult.REJECTED
    # The loser can STILL read the authoritative state (no brick), and main is clean.
    got = GitLeaderStateStore(work_b).read()
    assert got.leader == "ace-linux-1" and got.term == 2
    assert _git(work_b, "status", "--porcelain").stdout.strip() == ""


def test_gitstore_fetch_failure_is_unavailable_not_bootstrap(tmp_path):
    """A network/auth failure must be distinguished from a missing ref (review #2):
    read() raises StoreUnavailable (UNDETERMINED), never silently treats it as
    bootstrap (which would let a secondary mis-read absence)."""
    GitLeaderStateStore = module.GitLeaderStateStore
    _, work = _make_origin_and_clone(tmp_path)
    # point the remote at a non-existent path -> ls-remote/fetch hard-fail (not rc=2)
    _git(work, "remote", "set-url", "origin", str(tmp_path / "does-not-exist.git"))
    with pytest.raises(StoreUnavailable):
        GitLeaderStateStore(work).read()


def test_gitstore_claim_network_failure_returns_push_failed(tmp_path):
    """claim() honors its ClaimResult contract on a network failure (review #1) —
    returns PUSH_FAILED, never leaks StoreUnavailable."""
    GitLeaderStateStore = module.GitLeaderStateStore
    _, work = _make_origin_and_clone(tmp_path)
    _git(work, "remote", "set-url", "origin", str(tmp_path / "does-not-exist.git"))
    # no prior read() -> claim() must fetch, which fails -> PUSH_FAILED (not raise)
    assert GitLeaderStateStore(work).claim(_state(term=1)) is ClaimResult.PUSH_FAILED
