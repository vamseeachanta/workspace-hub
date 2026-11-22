"""Remote arbitration before execution, extending the namespace tests (#3772).

The fixtures are synthetic protocol inputs, not operational acceptance limits:
TTL=30, grant at t=100, rival at t=101, expiry at t=131. Hand calculation:
101-100=1 <= 30 (fresh); 131-100=31 > 30 (expired). Creation gives generation
1; one reclaim gives 1+1=2, per dispatch_lease.acquire/reclaim. Counts follow
from the explicit call sequence, independently of the implementation.

Git's documented branch fast-forward rule rejects sibling commits and unrelated
roots: https://git-scm.com/docs/git-push#_note_about_fast_forwards (2026).
All repositories and subprocess mutations are confined to temporary fixtures.
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
TTL = 30  # Synthetic input; boundary arithmetic is written out above.


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


@pytest.fixture
def repos(tmp_path, monkeypatch):
    # An inherited repository binding must not redirect fixture writes.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        monkeypatch.delenv(key, raising=False)
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "-q", "--bare")
    checkouts = []
    for name in ("first", "second"):
        repo = tmp_path / name
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.name", "Test")
        _git(repo, "config", "user.email", "test" + chr(64) + "invalid")
        _git(repo, "remote", "add", "origin", str(remote))
        checkouts.append(repo)
    return remote, *checkouts


def _adapter(repo):
    return grl.RemoteGitRefLease(repo)


def _run(adapter, holder, executor, **kwargs):
    return dp.claim_run([ITEM], holder=holder, git=adapter, executor=executor,
                        ttl_s=TTL, now_fn=lambda: 100, token_fn=lambda: holder,
                        **kwargs)


def _remote_blob(remote):
    return json.loads(_git(remote, "show", "-s", "--format=%B", REF).stdout)


def test_grant_is_published_before_execution(repos):
    """One call publishes one grant before its executor observes the remote."""
    remote, first, _ = repos
    seen = []
    out = _run(_adapter(first), "first", lambda _: seen.append(_remote_blob(remote)))
    assert out == [{"id": "task", "status": "ran"}]
    assert [blob["holder"] for blob in seen] == ["first"]


def test_second_checkout_cannot_execute_without_manual_sync(repos):
    """First grant wins; a second fresh acquisition implies zero extra calls."""
    _, first, second = repos
    calls = []
    _run(_adapter(first), "first", lambda _: calls.append("first"))
    out = _run(_adapter(second), "second", lambda _: calls.append("second"))
    assert out == [{"id": "task", "status": "skipped_held"}]
    assert calls == ["first"]


def test_simultaneous_absent_reads_have_one_execution(repos, monkeypatch):
    """Both read absence; first publishes while second prepares its creation.

    The roots differ because their fencing tokens differ. Neither root descends
    from the other, so Git must reject the later push; executor count is one.
    """
    remote, first, second = repos
    rival = _adapter(second)
    create = rival.create_ref
    calls = []

    def race(ref, blob):
        _run(_adapter(first), "first", lambda _: calls.append("first"))
        return create(ref, blob)

    monkeypatch.setattr(rival, "create_ref", race)
    out = _run(rival, "second", lambda _: calls.append("second"))
    assert out[0]["status"] == "skipped_held"
    assert calls == ["first"]
    assert _remote_blob(remote)["holder"] == "first"


def test_stale_renewal_cannot_replace_remote_successor(repos):
    """Two updates parented on P are siblings; only the first can advance P."""
    remote, first, second = repos
    a, b = _adapter(first), _adapter(second)
    dl.acquire(a, NAME, "first", TTL, 100, "original")
    sha, blob = b.read_ref(REF)
    assert dl.renew(a, NAME, "first", 101, new_token="renewed")
    assert b.cas_update_ref(REF, sha, {**blob, "token": "stale"}) is None
    assert _remote_blob(remote)["token"] == "renewed"


def test_reclaim_is_remote_and_fences_previous_token(repos):
    """131-100=31 > 30; dead holder permits generation 1+1=2."""
    _, first, second = repos
    a, b = _adapter(first), _adapter(second)
    dl.acquire(a, NAME, "first", TTL, 100, "original")
    reclaimed = dl.reclaim(b, NAME, "second", TTL, 131, "replacement", lambda _: False)
    assert reclaimed["generation"] == 2
    assert dl.verify_token(a, NAME, "original") is False
    assert dl.verify_token(a, NAME, "replacement") is True


def test_stale_reclaim_cannot_replace_remote_successor(repos):
    """Both contenders see generation 1; one sibling advances it to 2."""
    remote, first, second = repos
    a, b = _adapter(first), _adapter(second)
    dl.acquire(a, NAME, "first", TTL, 100, "original")
    sha, blob = a.read_ref(REF)
    assert dl.reclaim(b, NAME, "second", TTL, 131, "replacement", lambda _: False)
    assert a.cas_update_ref(REF, sha, {**blob, "token": "stale"}) is None
    assert _remote_blob(remote)["token"] == "replacement"


def test_unreachable_remote_does_not_use_local_grant(repos):
    """A local grant supplies no evidence about an inaccessible remote."""
    _, first, _ = repos
    dl.acquire(grl.GitRefLease(first), NAME, "first", TTL, 100, "local")
    _git(first, "remote", "set-url", "origin", str(first / "missing.git"))
    with pytest.raises(grl.LeaseSyncError):
        _adapter(first).read_ref(REF)
    calls = []
    out = _run(_adapter(first), "first", lambda _: calls.append("called"))
    assert out[0]["status"] == "failed"
    assert calls == []


def test_rejected_publication_never_executes_or_leaves_local_ref(repos, monkeypatch):
    """A failed publication leaves zero grants available for later bulk push."""
    remote, first, _ = repos
    adapter = _adapter(first)
    run_git = adapter._git

    def reject(*args, **kwargs):
        if args[0] == "push":
            return subprocess.CompletedProcess(args, 1, "", "publication refused")
        return run_git(*args, **kwargs)

    monkeypatch.setattr(adapter, "_git", reject)
    calls = []
    out = _run(adapter, "first", lambda _: calls.append("called"))
    assert out[0]["status"] == "skipped_held"
    assert calls == []
    assert _git(first, "for-each-ref", "--format=%(refname)").stdout == ""
    assert _git(remote, "for-each-ref", "--format=%(refname)").stdout == ""
    assert adapter.push_rc != 0


def test_fetch_failure_is_not_read_as_absence(repos, monkeypatch):
    """An advertised grant with unavailable objects must deny acquisition."""
    _, first, second = repos
    dl.acquire(_adapter(first), NAME, "first", TTL, 100, "original")
    adapter = _adapter(second)
    run_git = adapter._git

    def fail_fetch(*args, **kwargs):
        if args[0] == "fetch":
            return subprocess.CompletedProcess(args, 1, "", "fetch refused")
        return run_git(*args, **kwargs)

    monkeypatch.setattr(adapter, "_git", fail_fetch)
    with pytest.raises(grl.LeaseSyncError):
        adapter.read_ref(REF)
    assert adapter.fetch_rc != 0


def test_pre_execution_fence_denies_superseded_grant(repos, monkeypatch):
    """A reclaim after grant but before executor yields zero executor calls."""
    _, first, second = repos
    acquire = dp.acquire

    def superseded(*args):
        grant = acquire(*args)
        assert dl.reclaim(_adapter(second), NAME, "second", TTL, 131,
                          "replacement", lambda _: False)
        return grant

    monkeypatch.setattr(dp, "acquire", superseded)
    calls = []
    out = _run(_adapter(first), "first", lambda _: calls.append("called"))
    assert out == [{"id": "task", "status": "lost_fence"}]
    assert calls == []


def test_completion_fence_reads_remote_and_denies_old_token(repos):
    """Reclaim during execution yields one execution and zero completions."""
    _, first, second = repos
    done = []

    def supersede(_):
        assert dl.reclaim(_adapter(second), NAME, "second", TTL, 131,
                          "replacement", lambda _: False)

    out = _run(_adapter(first), "first", supersede, mark_done=done.append)
    assert out == [{"id": "task", "status": "lost_fence"}]
    assert done == []


def test_main_uses_remote_arbitration(repos, monkeypatch, tmp_path):
    """Two normal entry-point calls share the remote; executor count stays one."""
    remote, first, second = repos
    calls = []
    monkeypatch.setenv(dp.APPLY_FLAG, "1")
    monkeypatch.setattr(dp, "_resolve_machine", lambda *_: "primary")
    monkeypatch.setattr(dp, "_read_ready_cards", lambda *_: [ITEM])
    monkeypatch.setattr(dp, "load_command_bindings", lambda *_: {"task": "true"})

    def make_executor(**kwargs):
        def execute(_):
            assert _remote_blob(remote)["holder"]
            calls.append("called")
        return execute

    monkeypatch.setattr(dp, "make_drain_executor", make_executor)
    for repo in (first, second):
        assert dp.main(["--repo", str(repo), "--machine", "primary", "--apply",
                        "--delay", "0", "--log-dir", str(tmp_path / "logs")]) == 0
    assert calls == ["called"]


def test_main_reports_unreachable_remote_as_failure(repos, monkeypatch, tmp_path):
    """Read failure prevents all execution and produces a nonzero result."""
    _, first, _ = repos
    _git(first, "remote", "set-url", "origin", str(first / "missing.git"))
    monkeypatch.setattr(dp, "_resolve_machine", lambda *_: "primary")
    monkeypatch.setattr(dp, "_read_ready_cards", lambda *_: [ITEM])
    monkeypatch.setattr(dp, "load_command_bindings", lambda *_: {"task": "true"})
    calls = []
    monkeypatch.setattr(dp, "make_drain_executor", lambda **_: calls.append)
    assert dp.main(["--repo", str(first), "--machine", "primary", "--delay", "0",
                    "--log-dir", str(tmp_path / "logs")]) != 0
    assert calls == []


def test_unrelated_local_leases_are_not_published(repos):
    """Publishing one candidate creates exactly that ref, not a local wildcard."""
    remote, first, _ = repos
    dl.acquire(grl.GitRefLease(first), "local-only", "first", TTL, 100, "local")
    assert dl.acquire(_adapter(first), NAME, "first", TTL, 100, "remote")
    refs = _git(remote, "for-each-ref", "--format=%(refname)").stdout.splitlines()
    assert refs == [REF]


def test_read_uses_advertised_commit_when_fetch_sees_newer_descendant(repos, monkeypatch):
    """Renew between advertisement and fetch; the fetched parent remains readable."""
    _, first, second = repos
    a, b = _adapter(first), _adapter(second)
    dl.acquire(a, NAME, "first", TTL, 100, "original")
    run_git = b._git

    def race(*args, **kwargs):
        if args[0] == "fetch":
            assert dl.renew(a, NAME, "first", 101, new_token="renewed")
        return run_git(*args, **kwargs)

    monkeypatch.setattr(b, "_git", race)
    _, blob = b.read_ref(REF)
    assert blob["token"] == "original"
    monkeypatch.setattr(b, "_git", run_git)
    assert dl.verify_token(b, NAME, "original") is False


def test_main_reports_rejected_publication_as_failure(repos, monkeypatch, tmp_path):
    """Zero published grants and zero executor calls imply an unsuccessful run."""
    remote, first, _ = repos
    run_git = grl.RemoteGitRefLease._git

    def reject(self, *args, **kwargs):
        if args[0] == "push":
            return subprocess.CompletedProcess(args, 1, "", "publication refused")
        return run_git(self, *args, **kwargs)

    monkeypatch.setattr(grl.RemoteGitRefLease, "_git", reject)
    monkeypatch.setattr(dp, "_load", lambda *_: grl)
    monkeypatch.setattr(dp, "_resolve_machine", lambda *_: "primary")
    monkeypatch.setattr(dp, "_read_ready_cards", lambda *_: [ITEM])
    monkeypatch.setattr(dp, "load_command_bindings", lambda *_: {"task": "true"})
    calls = []
    monkeypatch.setattr(dp, "make_drain_executor", lambda **_: calls.append)
    assert dp.main(["--repo", str(first), "--machine", "primary", "--delay", "0",
                    "--log-dir", str(tmp_path / "logs")]) != 0
    assert calls == []
    assert _git(remote, "for-each-ref", "--format=%(refname)").stdout == ""
    records = [json.loads(line) for path in (tmp_path / "logs").glob("*.jsonl")
               for line in path.read_text().splitlines()]
    assert records[-1]["push_rc"] != 0
