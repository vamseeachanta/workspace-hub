"""TDD tests for the single-active-venue lease (#2971, F4).

Loads `scripts/operations/venue_lease.py` by file path (it is not an importable
package). Two git backends are exercised:

  * an in-memory FakeGit implementing the F3 injected interface
    (read_ref / create_ref / cas_update_ref) with create-only + CAS semantics
    and a monotonic sha counter, and
  * a real temp git repo via `git_ref_lease.GitRefLease` for one integration
    smoke test of the free-venue write path.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "operations" / "venue_lease.py"
spec = importlib.util.spec_from_file_location("venue_lease", MODULE_PATH)
assert spec is not None and spec.loader is not None
venue_lease = importlib.util.module_from_spec(spec)
sys.modules["venue_lease"] = venue_lease
spec.loader.exec_module(venue_lease)

dispatch_lease = venue_lease.dispatch_lease
git_ref_lease = venue_lease.git_ref_lease


# --- In-memory fake-git: dict name -> (sha, blob); create-only + CAS ----------
class FakeGit:
    def __init__(self) -> None:
        self.refs: dict[str, tuple[str, dict]] = {}
        self._counter = 0

    def _next_sha(self) -> str:
        self._counter += 1
        return f"sha{self._counter}"

    def read_ref(self, name: str):
        return self.refs.get(name)

    def create_ref(self, name: str, blob: dict):
        if name in self.refs:  # create fails if it already exists
            return None
        sha = self._next_sha()
        self.refs[name] = (sha, dict(blob))
        return sha

    def cas_update_ref(self, name: str, expected_sha: str, blob: dict):
        cur = self.refs.get(name)
        if cur is None or cur[0] != expected_sha:  # CAS only if tip unchanged
            return None
        sha = self._next_sha()
        self.refs[name] = (sha, dict(blob))
        return sha


# --- is_gated ------------------------------------------------------------------
def test_is_gated_write_capabilities_true():
    assert venue_lease.is_gated("escalation-sweep") is True
    assert venue_lease.is_gated("bot-send") is True


def test_is_gated_read_capabilities_false():
    assert venue_lease.is_gated("member-audit") is False
    assert venue_lease.is_gated("parity") is False


def test_is_gated_unknown_capability_raises():
    with pytest.raises(ValueError):
        venue_lease.is_gated("delete-everything")


# --- holds_venue: READ never gated, no lease acquired -------------------------
def test_holds_venue_read_allowed_without_lease():
    git = FakeGit()
    res = venue_lease.holds_venue(
        git, "member-audit", holder="hostA", ttl_s=60, now=100.0, new_token="t1"
    )
    assert res["allowed"] is True
    assert res["lease"] is None
    # No lease ref was created for a read.
    assert git.refs == {}


# --- holds_venue: WRITE on a free venue acquires generation 1 -----------------
def test_holds_venue_write_free_acquires_gen1():
    git = FakeGit()
    res = venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="t1"
    )
    assert res["allowed"] is True
    assert res["lease"]["holder"] == "hostA"
    assert res["lease"]["generation"] == 1
    assert res["lease"]["token"] == "t1"
    assert dispatch_lease.lease_ref(venue_lease.VENUE_LEASE_NAME) in git.refs


# --- holds_venue: WRITE blocked when another FRESH host holds it --------------
def test_holds_venue_write_blocked_by_other_fresh_host():
    git = FakeGit()
    a = venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="tA"
    )
    assert a["allowed"] is True
    # hostB tries while hostA's lease is still fresh (now within ttl).
    b = venue_lease.holds_venue(
        git, "bot-send", holder="hostB", ttl_s=60, now=110.0, new_token="tB"
    )
    assert b["allowed"] is False
    assert b["reason"] == "held by hostA"
    assert b["lease"] is None


# --- holds_venue: re-entrant (same holder) renews ----------------------------
def test_holds_venue_write_reentrant_renews():
    git = FakeGit()
    a1 = venue_lease.holds_venue(
        git, "escalation-sweep", holder="hostA", ttl_s=60, now=100.0, new_token="tA1"
    )
    assert a1["allowed"] is True
    a2 = venue_lease.holds_venue(
        git, "escalation-sweep", holder="hostA", ttl_s=60, now=130.0, new_token="tA2"
    )
    assert a2["allowed"] is True
    # renew keeps the same generation, refreshes renewed_at, rotates the token.
    assert a2["lease"]["generation"] == 1
    assert a2["lease"]["renewed_at"] == 130.0
    assert a2["lease"]["token"] == "tA2"


# --- holds_venue: reclaim path (expired + dead holder) -----------------------
def test_holds_venue_write_reclaims_expired_dead_holder():
    git = FakeGit()
    venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="tA"
    )
    # hostA's lease is expired (now-renewed_at > ttl) and hostA is dead.
    res = venue_lease.holds_venue(
        git,
        "bot-send",
        holder="hostB",
        ttl_s=60,
        now=200.0,
        new_token="tB",
        liveness_fn=lambda h: False,
    )
    assert res["allowed"] is True
    assert res["reason"] == "reclaimed"
    assert res["lease"]["holder"] == "hostB"
    assert res["lease"]["generation"] == 2  # fence bump
    assert res["lease"]["token"] == "tB"


def test_holds_venue_write_no_reclaim_when_holder_alive():
    git = FakeGit()
    venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="tA"
    )
    # Expired but holder still alive → refuse to steal.
    res = venue_lease.holds_venue(
        git,
        "bot-send",
        holder="hostB",
        ttl_s=60,
        now=200.0,
        new_token="tB",
        liveness_fn=lambda h: True,
    )
    assert res["allowed"] is False
    assert res["reason"] == "held by hostA"


# --- fence: token valid for holder, invalid after reclaim --------------------
def test_fence_holder_token_true_then_false_after_reclaim():
    git = FakeGit()
    a = venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="tA"
    )
    a_token = a["lease"]["token"]
    # hostA's write function fences just before its side effect → still valid.
    assert venue_lease.fence(git, a_token) is True

    # hostA stalls past ttl and dies; hostB reclaims, bumping the token.
    b = venue_lease.holds_venue(
        git,
        "bot-send",
        holder="hostB",
        ttl_s=60,
        now=200.0,
        new_token="tB",
        liveness_fn=lambda h: False,
    )
    assert b["allowed"] is True
    # hostA wakes up and fences with its STALE token → must abort.
    assert venue_lease.fence(git, a_token) is False
    # hostB's fresh token still passes.
    assert venue_lease.fence(git, b["lease"]["token"]) is True


def test_fence_absent_lease_false():
    git = FakeGit()
    assert venue_lease.fence(git, "anything") is False


# --- Real-git integration smoke test (GitRefLease) ----------------------------
def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)


def test_holds_venue_write_on_real_git_repo(tmp_path):
    _init_repo(tmp_path)
    git = git_ref_lease.GitRefLease(tmp_path)
    res = venue_lease.holds_venue(
        git, "bot-send", holder="hostA", ttl_s=60, now=100.0, new_token="t1"
    )
    assert res["allowed"] is True
    assert res["lease"]["generation"] == 1
    assert res["lease"]["holder"] == "hostA"
    # Fencing against the real ref works with the granted token.
    assert venue_lease.fence(git, res["lease"]["token"]) is True
    # A second host is blocked while the lease is fresh.
    res2 = venue_lease.holds_venue(
        git, "bot-send", holder="hostB", ttl_s=60, now=110.0, new_token="t2"
    )
    assert res2["allowed"] is False
    assert res2["reason"] == "held by hostA"


# ── #2971 code-review MAJOR fixes ────────────────────────────────────────────
def test_guarded_write_runs_only_when_held_and_fenced(tmp_path):
    import importlib.util as _u, sys as _s
    grl = _s.modules.get("git_ref_lease")
    if grl is None:
        spec = _u.spec_from_file_location("git_ref_lease", REPO_ROOT / "scripts" / "operations" / "git_ref_lease.py")
        grl = _u.module_from_spec(spec); _s.modules["git_ref_lease"] = grl; spec.loader.exec_module(grl)
    import subprocess
    subprocess.run(["git","init","-q",str(tmp_path)],check=True)
    subprocess.run(["git","-C",str(tmp_path),"config","user.email","t@t"],check=True)
    subprocess.run(["git","-C",str(tmp_path),"config","user.name","t"],check=True)
    git = grl.GitRefLease(str(tmp_path))
    ran = []
    res = venue_lease.guarded_write(git, "escalation-sweep", "host-a", 60, 1000.0, "tok-a",
                           side_effect_fn=lambda: ran.append(1) or "done")
    assert res["ran"] is True and res["result"] == "done" and ran == [1]


def test_guarded_write_skips_when_not_holder(tmp_path):
    import importlib.util as _u, sys as _s, subprocess
    grl = _s.modules["git_ref_lease"]
    subprocess.run(["git","init","-q",str(tmp_path)],check=True)
    subprocess.run(["git","-C",str(tmp_path),"config","user.email","t@t"],check=True)
    subprocess.run(["git","-C",str(tmp_path),"config","user.name","t"],check=True)
    git = grl.GitRefLease(str(tmp_path))
    venue_lease.holds_venue(git, "escalation-sweep", "host-a", 60, 1000.0, "tok-a")  # host-a holds
    ran = []
    res = venue_lease.guarded_write(git, "escalation-sweep", "host-b", 60, 1001.0, "tok-b",
                           side_effect_fn=lambda: ran.append(1))
    assert res["ran"] is False and ran == []   # host-b never runs the side effect


def test_is_our_lease_rejects_other_holder():
    assert venue_lease._is_our_lease({"holder": "me"}, "me") is True
    assert venue_lease._is_our_lease({"holder": "other"}, "me") is False
    assert venue_lease._is_our_lease(None, "me") is False
