"""The lease has to leave the host (#3772).

## The defect

`dispatch_lease` writes leases under `refs/heads/dispatch/leases/`. `dispatch_pull`
fetched and pushed `refs/heads/dispatch-lease/`. Those two namespaces do not
overlap, so no lease ever crossed the network: every host CAS'd against refs only
it could see, and therefore won every lease it asked for. The lease core is
correct — CAS, monotonic generation, fencing token — and was wired to nothing.

## What is asserted here, and what deliberately is not

Grepping for the prefix would pin the NAME. The name is not the property; the
property is that the ref a host WRITES is the ref its peer READS. So these tests
run the real code against real git: two checkouts of one bare remote, a lease
acquired on one, the module's own sync path, and then the peer's view of it.

Rename the namespace and these still pass. Diverge the two ends by one character
and `test_a_lease_taken_on_one_host_blocks_the_other` fails, because host-b
acquires a lease host-a already holds — the exact production failure.

`test_without_the_sync_path_the_second_host_wins_too` is the control: it shows
the blocking assertion is load-bearing rather than trivially true.

Hermetic: a bare repo on disk plays the remote. No network, no origin, no gh.

Run: uv run --with pyyaml --with pytest pytest tests/operations/test_dispatch_lease_namespace.py
"""

from __future__ import annotations

import fnmatch
import importlib.util
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod] = m
    spec.loader.exec_module(m)
    return m


dl = _load("dispatch_lease", "scripts/operations/dispatch_lease.py")
grl = _load("git_ref_lease", "scripts/operations/git_ref_lease.py")
dp = _load("dispatch_pull", "scripts/operations/dispatch_pull.py")

ISSUE = "vamseeachanta/deckhand#33"
TTL = 900


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True, check=True)


def _fleet(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A bare remote and two independent checkouts pointed at it."""
    remote = tmp_path / "remote.git"
    _run("git", "init", "-q", "--bare", str(remote))
    hosts = []
    for name in ("host-a", "host-b"):
        repo = tmp_path / name
        _run("git", "init", "-q", str(repo))
        _run("git", "-C", str(repo), "config", "user.email", f"{name}@t")
        _run("git", "-C", str(repo), "config", "user.name", name)
        _run("git", "-C", str(repo), "remote", "add", "origin", str(remote))
        hosts.append(repo)
    return remote, hosts[0], hosts[1]


def _remote_lease_refs(remote: Path) -> list[str]:
    out = _run("git", "-C", str(remote), "for-each-ref", "--format=%(refname)").stdout
    return [ln for ln in out.splitlines() if ln]


# ── the headline: mutual exclusion actually crosses the wire ────────────────


def test_a_lease_taken_on_one_host_blocks_the_other(tmp_path):
    """host-a claims, syncs; host-b syncs and must be refused.

    This is the whole point of the lease. It fails the moment the namespace the
    writer uses and the namespace the sync moves stop being the same one.
    """
    remote, a, b = _fleet(tmp_path)
    name = dp.default_lease_name({"id": ISSUE})

    assert dl.acquire(grl.GitRefLease(a), name, "host-a",
                      ttl_s=TTL, now=1000.0, new_token="tok-a") is not None
    dp._push_lease_refs(a)
    dp._fetch_lease_refs(b)

    assert dl.acquire(grl.GitRefLease(b), name, "host-b",
                      ttl_s=TTL, now=1001.0, new_token="tok-b") is None


def test_without_the_sync_path_the_second_host_wins_too(tmp_path):
    """Control: with no sync, host-b acquires freely.

    Keeps the test above honest — it proves the refusal comes from the sync, not
    from something incidental in the fixture.
    """
    _remote, a, b = _fleet(tmp_path)
    name = dp.default_lease_name({"id": ISSUE})

    assert dl.acquire(grl.GitRefLease(a), name, "host-a",
                      ttl_s=TTL, now=1000.0, new_token="tok-a") is not None
    assert dl.acquire(grl.GitRefLease(b), name, "host-b",
                      ttl_s=TTL, now=1001.0, new_token="tok-b") is not None


def test_the_pushed_lease_is_readable_by_a_second_checkout(tmp_path):
    """The blob itself round-trips: holder and generation survive the hop."""
    _remote, a, b = _fleet(tmp_path)
    name = dp.default_lease_name({"id": ISSUE})

    dl.acquire(grl.GitRefLease(a), name, "host-a",
               ttl_s=TTL, now=1000.0, new_token="tok-a")
    dp._push_lease_refs(a)
    dp._fetch_lease_refs(b)

    seen = grl.GitRefLease(b).read_ref(dl.lease_ref(name))
    assert seen is not None
    _sha, blob = seen
    assert blob["holder"] == "host-a" and blob["generation"] == 1


def test_the_fencing_token_is_visible_across_hosts(tmp_path):
    """`verify_token` is the pre-side-effect gate; it must see the peer's grant."""
    _remote, a, b = _fleet(tmp_path)
    name = dp.default_lease_name({"id": ISSUE})

    dl.acquire(grl.GitRefLease(a), name, "host-a",
               ttl_s=TTL, now=1000.0, new_token="tok-a")
    dp._push_lease_refs(a)
    dp._fetch_lease_refs(b)

    assert dl.verify_token(grl.GitRefLease(b), name, "tok-a") is True
    assert dl.verify_token(grl.GitRefLease(b), name, "tok-b") is False


def test_the_push_actually_lands_on_the_remote(tmp_path):
    """A best-effort push that silently pushed nothing would pass a peer-less test."""
    remote, a, _b = _fleet(tmp_path)
    name = dp.default_lease_name({"id": ISSUE})

    dl.acquire(grl.GitRefLease(a), name, "host-a",
               ttl_s=TTL, now=1000.0, new_token="tok-a")
    dp._push_lease_refs(a)

    assert dl.lease_ref(name) in _remote_lease_refs(remote)


def test_a_renewal_fast_forwards_on_the_remote(tmp_path):
    """Non-forced pushes must keep working after the first grant.

    Each lease commit is parented on the prior one, so a renew advances the ref
    rather than diverging. If it did diverge, every night after the first would
    push-reject and the fleet would silently stop syncing.
    """
    remote, a, _b = _fleet(tmp_path)
    git_a = grl.GitRefLease(a)
    name = dp.default_lease_name({"id": ISSUE})

    dl.acquire(git_a, name, "host-a", ttl_s=TTL, now=1000.0, new_token="tok-a")
    dp._push_lease_refs(a)
    assert dl.renew(git_a, name, "host-a", now=1100.0, new_token="tok-a2") is not None
    push = dp._push_lease_refs(a)

    assert push.returncode == 0
    assert dl.lease_ref(name) in _remote_lease_refs(remote)


# ── one constant, not two agreeing literals ─────────────────────────────────


def test_sync_refspecs_are_derived_from_the_writer_namespace(tmp_path):
    """Whatever ref the writer produces must match what fetch and push move.

    Asserted by matching a REAL ref from the writer against the module's own
    refspecs, so it holds under any renaming of the namespace.
    """
    name = dp.default_lease_name({"id": ISSUE})
    ref = dl.lease_ref(name)

    fetch_src, _, fetch_dst = dp.lease_fetch_refspec().lstrip("+").partition(":")
    assert fnmatch.fnmatch(ref, fetch_src)
    assert fnmatch.fnmatch(ref, fetch_dst)
    assert fnmatch.fnmatch(ref, dp.lease_push_refspec())


def test_the_adapter_does_not_carry_its_own_copy_of_the_namespace(tmp_path):
    """`git_ref_lease` and `dispatch_lease` must agree by construction."""
    assert grl.lease_ref("task-x") == dl.lease_ref("task-x")
