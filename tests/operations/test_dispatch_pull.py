"""WF3 (#3000) — lease-arbitrated pull/claim core for no-SSH dispatch.

A no-SSH host claims work itself; the F3 git-ref lease (acquire + fencing token, NO release — the
lease lapses via TTL and is recovered by reclaim) guarantees that two hosts polling the same source
never run the same item concurrently. Fully deterministic: git (FakeGit), clock, token, liveness and
executor are all injected — mirrors test_dispatch_lease.py.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dispatch_lease = _load("dispatch_lease", "scripts/operations/dispatch_lease.py")
dp = _load("dispatch_pull", "scripts/operations/dispatch_pull.py")
lease_ref = dispatch_lease.lease_ref


class FakeGit:
    """Dict-backed git model (copied from test_dispatch_lease): name -> (sha, blob),
    fresh sha on each write so a stale-expected CAS fails like a moved ref tip."""

    def __init__(self):
        self.store: dict[str, tuple[str, dict]] = {}
        self._counter = 0

    def _next_sha(self) -> str:
        self._counter += 1
        return f"sha{self._counter:04d}"

    def read_ref(self, name):
        if name not in self.store:
            return None
        sha, blob = self.store[name]
        return sha, dict(blob)

    def create_ref(self, name, blob):
        if name in self.store:
            return None
        sha = self._next_sha()
        self.store[name] = (sha, dict(blob))
        return sha

    def cas_update_ref(self, name, expected_sha, blob):
        cur = self.store.get(name)
        if cur is None or cur[0] != expected_sha:
            return None
        sha = self._next_sha()
        self.store[name] = (sha, dict(blob))
        return sha


TTL = 30


def _tokens():
    n = {"i": 0}

    def fn():
        n["i"] += 1
        return f"tok{n['i']}"
    return fn


def alive(_h):
    return True


def dead(_h):
    return False


def test_single_item_claimed_run_and_marked_done():
    git = FakeGit()
    ran, done = [], []
    out = dp.claim_run(
        [{"id": "card-1"}], holder="m1", git=git, executor=lambda it: ran.append(it["id"]),
        ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens(), mark_done=lambda it: done.append(it["id"]),
    )
    assert [o["status"] for o in out] == ["ran"]
    assert ran == ["card-1"] and done == ["card-1"]


def test_two_holders_only_one_runs_no_double_run():
    """Headline: a shared lease ref → exactly one holder runs the item."""
    git = FakeGit()
    item = {"id": "card-x"}
    r1, r2 = [], []
    o1 = dp.claim_run([item], holder="m1", git=git, executor=lambda it: r1.append(1),
                      ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens())
    # m2 polls the same item while m1's lease is fresh:
    o2 = dp.claim_run([item], holder="m2", git=git, executor=lambda it: r2.append(1),
                      ttl_s=TTL, now_fn=lambda: 110.0, token_fn=_tokens())
    assert o1[0]["status"] == "ran"
    assert o2[0]["status"] == "skipped_held"
    assert r1 == [1] and r2 == []          # executor ran exactly once, on m1


def test_executor_failure_not_marked_done():
    git = FakeGit()
    done = []

    def boom(_it):
        raise RuntimeError("exec failed")
    out = dp.claim_run([{"id": "c"}], holder="m1", git=git, executor=boom,
                       ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens(),
                       mark_done=lambda it: done.append(it["id"]))
    assert out[0]["status"] == "failed"
    assert done == []                      # not completed → stays claimable after TTL


def test_held_fresh_by_other_is_skipped():
    git = FakeGit()
    dispatch_lease.acquire(git, "dispatch/c", holder="m1", ttl_s=TTL, now=100.0, new_token="t1")
    ran = []
    out = dp.claim_run([{"id": "c"}], holder="m2", git=git, executor=lambda it: ran.append(1),
                       ttl_s=TTL, now_fn=lambda: 105.0, token_fn=_tokens())
    assert out[0]["status"] == "skipped_held" and ran == []


def test_lost_fence_does_not_mark_done():
    """If our lease is superseded mid-run (token rotated), verify_token fails → no mark_done."""
    git = FakeGit()
    done = []

    def supersede(_it):
        # simulate another holder reclaiming us: overwrite the lease blob's token.
        ref = lease_ref("dispatch/c")
        sha, blob = git.store[ref]
        blob = dict(blob); blob["token"] = "stolen"; blob["holder"] = "m2"
        git.store[ref] = (git._next_sha(), blob)
    out = dp.claim_run([{"id": "c"}], holder="m1", git=git, executor=supersede,
                       ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens(),
                       mark_done=lambda it: done.append(it["id"]))
    assert out[0]["status"] == "lost_fence" and done == []


def test_crashed_holder_reclaimed_when_dead():
    git = FakeGit()
    dispatch_lease.acquire(git, "dispatch/c", holder="m1", ttl_s=TTL, now=100.0, new_token="t1")
    ran = []
    # now=200 → expired; liveness_fn dead → reclaim succeeds → we run it.
    out = dp.claim_run([{"id": "c"}], holder="m2", git=git, executor=lambda it: ran.append(1),
                       ttl_s=TTL, now_fn=lambda: 200.0, token_fn=_tokens(), liveness_fn=dead)
    assert out[0]["status"] == "ran" and ran == [1]


def test_expired_but_holder_alive_not_reclaimed():
    git = FakeGit()
    dispatch_lease.acquire(git, "dispatch/c", holder="m1", ttl_s=TTL, now=100.0, new_token="t1")
    ran = []
    out = dp.claim_run([{"id": "c"}], holder="m2", git=git, executor=lambda it: ran.append(1),
                       ttl_s=TTL, now_fn=lambda: 200.0, token_fn=_tokens(), liveness_fn=alive)
    assert out[0]["status"] == "skipped_held" and ran == []


def test_empty_items():
    assert dp.claim_run([], holder="m1", git=FakeGit(), executor=lambda it: None,
                        ttl_s=TTL, now_fn=lambda: 1.0, token_fn=_tokens()) == []
