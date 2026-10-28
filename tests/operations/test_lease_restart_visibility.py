"""Lease publication and restart regression coverage for issue #3772.

Basis: tests/operations/test_dispatch_remote_lease.py uses synthetic TTL=30
and grant time=100. Here renewal=120 and peer observation=140 are synthetic
inputs, not operational limits. Hand calculation: 140-100=40 > 30, but
140-120=20 <= 30, so only the renewal keeps the lease fresh. Creation gives
one generation; renewal adds zero, leaving generation=1, as declared by
scripts/operations/dispatch_lease.py:acquire and :renew. The freshness rule
comes from :_is_expired; execution refusal comes from dispatch_pull.py:claim_run.
One item produces zero executor/completion calls when held; without publication,
that same item produces one of each. These counts follow from the fixture.

The local bare-remote pattern follows test_dispatch_remote_lease.py:repos.
All Git mutations use temporary repositories; existing Git identity configuration
is required and is never changed. No real executor or hosted remote is used.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dl = _load("dispatch_lease", "scripts/operations/dispatch_lease.py")
grl = _load("git_ref_lease", "scripts/operations/git_ref_lease.py")
dp = _load("dispatch_pull", "scripts/operations/dispatch_pull.py")

ITEM = {"id": "task", "card": {"gh": "task", "wip_eligible": True}}
NAME = dp.default_lease_name(ITEM)
REF = dl.lease_ref(NAME)
# Synthetic values and independent arithmetic are documented above.
TTL = 30
GRANTED_AT = 100
RENEWED_AT = 120
OBSERVED_AT = 140
EXPECTED_RENEWAL = {
    "holder": "first",
    "generation": 1,
    "token": "renewed",
    "ttl_s": TTL,
    "renewed_at": RENEWED_AT,
}


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def repos(tmp_path, monkeypatch):
    # Repository bindings inherited from a caller must not redirect fixture writes.
    for key in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    ):
        monkeypatch.delenv(key, raising=False)
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "-q", "--bare")
    first = tmp_path / "first"
    first.mkdir()
    _git(first, "init", "-q")
    _git(first, "remote", "add", "origin", str(remote))
    # Construct the peer only after the initial holder has finished its writes.
    return remote, first, tmp_path / "second"


def _fresh_checkout(remote, second):
    second.mkdir()
    _git(second, "init", "-q")
    _git(second, "remote", "add", "origin", str(remote))
    assert grl.GitRefLease(second).read_ref(REF) is None
    return second


def _renew_locally(first, *, publish):
    adapter = grl.GitRefLease(first)
    grant = dl.acquire(adapter, NAME, "first", TTL, GRANTED_AT, "original")
    assert grant == {
        "holder": "first", "generation": 1, "token": "original",
        "ttl_s": TTL, "renewed_at": GRANTED_AT,
    }
    if publish:
        assert dp._push_lease_refs(first).returncode == 0
    assert dl.renew(adapter, NAME, "first", RENEWED_AT, new_token="renewed") == EXPECTED_RENEWAL
    if publish:
        assert dp._push_lease_refs(first).returncode == 0
    return adapter.read_ref(REF)


def _compete(adapter, calls, completed, **kwargs):
    return dp.claim_run(
        [ITEM], holder="second", git=adapter, executor=calls.append,
        mark_done=completed.append, ttl_s=TTL, now_fn=lambda: OBSERVED_AT,
        token_fn=lambda: "competitor", **kwargs,
    )


def test_reopened_adapter_observes_published_renewal(repos):
    """A new checkout and adapter recover the renewed fence from published refs."""
    remote, first, second = repos
    published_sha, local_blob = _renew_locally(first, publish=True)
    assert local_blob == EXPECTED_RENEWAL
    assert json.loads(_git(remote, "show", "-s", "--format=%B", REF).stdout) == EXPECTED_RENEWAL

    _fresh_checkout(remote, second)
    assert dp._fetch_lease_refs(second).returncode == 0
    # Reopening has no access to the original adapter's in-memory state.
    reopened = grl.GitRefLease(second)
    assert reopened.read_ref(REF) == (published_sha, EXPECTED_RENEWAL)
    remote_reader = grl.RemoteGitRefLease(second)
    assert remote_reader.read_ref(REF) == (published_sha, EXPECTED_RENEWAL)
    assert dl.verify_token(remote_reader, NAME, "renewed") is True
    assert dl.verify_token(remote_reader, NAME, "original") is False


def test_fresh_competitor_after_restart_cannot_execute(repos):
    """Renewal freshness blocks reclaim even when the holder is reported dead."""
    remote, first, second = repos
    published_sha, _ = _renew_locally(first, publish=True)
    _fresh_checkout(remote, second)
    # Use the normal remote adapter without a manual fetch on this restart.
    reopened = grl.RemoteGitRefLease(second)
    assert reopened.read_ref(REF) == (published_sha, EXPECTED_RENEWAL)
    calls, completed, liveness_checks = [], [], []

    def dead(holder):
        liveness_checks.append(holder)
        return False

    assert _compete(reopened, calls, completed, liveness_fn=dead) == [
        {"id": "task", "status": "skipped_held"},
    ]
    assert calls == []
    assert completed == []
    assert liveness_checks == []
    assert grl.RemoteGitRefLease(second).read_ref(REF) == (published_sha, EXPECTED_RENEWAL)


def test_unpublished_renewal_is_not_restart_evidence(repos):
    """Control: local acquire and renew alone cannot exclude a fresh peer."""
    remote, first, second = repos
    _, local_blob = _renew_locally(first, publish=False)
    assert local_blob == EXPECTED_RENEWAL
    assert dl.verify_token(grl.GitRefLease(first), NAME, "renewed") is True
    assert _git(remote, "for-each-ref", "--format=%(refname)").stdout == ""

    _fresh_checkout(remote, second)
    assert dp._fetch_lease_refs(second).returncode == 0
    assert grl.GitRefLease(second).read_ref(REF) is None
    reopened = grl.RemoteGitRefLease(second)
    assert reopened.read_ref(REF) is None
    assert dl.verify_token(reopened, NAME, "renewed") is False
    calls, completed = [], []
    assert _compete(reopened, calls, completed) == [{"id": "task", "status": "ran"}]
    assert calls == [ITEM]
    assert completed == [ITEM]
    # A still-valid local fence does not describe the authoritative remote grant.
    assert dl.verify_token(grl.GitRefLease(first), NAME, "renewed") is True
    assert json.loads(_git(remote, "show", "-s", "--format=%B", REF).stdout) == {
        "holder": "second", "generation": 1, "token": "competitor",
        "ttl_s": TTL, "renewed_at": OBSERVED_AT,
    }
