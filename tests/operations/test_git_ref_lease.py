"""Integration test: the dispatch lease over REAL git (#2970, F3).

Drives dispatch_lease.acquire/renew/reclaim/verify_token through the GitRefLease
adapter against a real temporary git repo, proving the versioned-CAS + fencing
mechanism works on actual git refs (not just the in-memory fake).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


dl = _load("dispatch_lease", "scripts/operations/dispatch_lease.py")
grl = _load("git_ref_lease", "scripts/operations/git_ref_lease.py")


def _new_repo(tmp_path) -> str:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], check=True)
    return str(tmp_path)


def test_acquire_then_read_real_git(tmp_path):
    git = grl.GitRefLease(_new_repo(tmp_path))
    lease = dl.acquire(git, "task-x", "host-a", ttl_s=60, now=1000.0, new_token="tok-a")
    assert lease and lease["generation"] == 1 and lease["holder"] == "host-a"
    sha, blob = git.read_ref(dl.lease_ref("task-x"))
    assert blob["token"] == "tok-a"


def test_second_acquirer_loses_real_git(tmp_path):
    git = grl.GitRefLease(_new_repo(tmp_path))
    assert dl.acquire(git, "t", "host-a", 60, 1000.0, "tok-a")
    # host-b tries to acquire a fresh, held lease → None
    assert dl.acquire(git, "t", "host-b", 60, 1001.0, "tok-b") is None


def test_reclaim_cas_only_one_wins_real_git(tmp_path):
    git = grl.GitRefLease(_new_repo(tmp_path))
    dl.acquire(git, "t", "host-a", ttl_s=10, now=1000.0, new_token="tok-a")
    dead = lambda h: False  # host-a is dead
    # both reclaimers read the same ref state (expired: now 2000 > 1000+10)
    sha0, _ = git.read_ref(dl.lease_ref("t"))
    first = dl.reclaim(git, "t", "host-b", 10, now=2000.0, new_token="tok-b", liveness_fn=dead)
    assert first and first["generation"] == 2 and first["holder"] == "host-b"
    # host-c attempts reclaim using the now-stale sha → must fail (real CAS via git)
    second = git.cas_update_ref(dl.lease_ref("t"), sha0, {"holder": "host-c"})
    assert second is None  # git update-ref old-value mismatch → atomic CAS rejected


def test_fencing_old_token_rejected_real_git(tmp_path):
    git = grl.GitRefLease(_new_repo(tmp_path))
    dl.acquire(git, "t", "host-a", ttl_s=10, now=1000.0, new_token="tok-a")
    assert dl.verify_token(git, "t", "tok-a") is True
    dl.reclaim(git, "t", "host-b", 10, now=2000.0, new_token="tok-b", liveness_fn=lambda h: False)
    assert dl.verify_token(git, "t", "tok-a") is False   # superseded holder fenced out
    assert dl.verify_token(git, "t", "tok-b") is True


def test_renew_keeps_lease_real_git(tmp_path):
    git = grl.GitRefLease(_new_repo(tmp_path))
    dl.acquire(git, "t", "host-a", ttl_s=10, now=1000.0, new_token="tok-a")
    renewed = dl.renew(git, "t", "host-a", now=1005.0)
    assert renewed and renewed["renewed_at"] == 1005.0 and renewed["generation"] == 1
