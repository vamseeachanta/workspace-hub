"""Exact object residue for malformed success and post-write failures."""
import re

import pytest

from client_llm_wiki import bootstrap_finalizer


def _member():
    return type("Member", (), {
        "data": b"payload", "path": "README.md", "mode": 0o100644,
    })()


@pytest.mark.parametrize("operation", ["hash_object", "mktree"])
def test_malformed_success_preserves_independently_expected_oid(monkeypatch, operation):
    context = type("Context", (), {"clone": object()})()
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_: None)
    monkeypatch.setattr(bootstrap_finalizer, "_git", lambda *_a, **_k: b"malformed\n")
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        if operation == "hash_object":
            bootstrap_finalizer._build_tree(context, (_member(),))
        else:
            bootstrap_finalizer._mktree(context, {}, "", [])
    assert caught.value.residue.object_oids
    assert all(re.fullmatch(r"[0-9a-f]{40}", oid) for oid in caught.value.residue.object_oids)


def test_post_write_attestation_failure_preserves_written_oid(monkeypatch):
    context = type("Context", (), {"clone": object()})()
    checks = iter((None, bootstrap_finalizer.BootstrapFinalizerError("post")))

    def attest(*_args):
        outcome = next(checks)
        if outcome:
            raise outcome

    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", attest)
    monkeypatch.setattr(
        bootstrap_finalizer, "_git", lambda *_a, **_k: ("a" * 40 + "\n").encode(),
    )
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._build_tree(context, (_member(),))
    assert caught.value.residue.kind == "git_objects_hash_object_failed"
    assert len(caught.value.residue.object_oids) == 1


@pytest.mark.parametrize("failure", [RuntimeError("callback"), TimeoutError("timeout")])
def test_blob_callback_failure_reports_potentially_created_oid(monkeypatch, failure):
    context = type("Context", (), {"clone": object()})()
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_: None)
    monkeypatch.setattr(bootstrap_finalizer, "_git", lambda *_a, **_k: (_ for _ in ()).throw(failure))

    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._build_tree(context, (_member(),))

    assert caught.value.residue.kind == "git_objects_hash_object_failed"
    assert caught.value.residue.object_oids == (
        bootstrap_finalizer.object_oid("sha1", "blob", b"payload"),
    )


@pytest.mark.parametrize("failure", [RuntimeError("callback"), TimeoutError("timeout")])
def test_nested_tree_callback_failure_reports_exact_attempted_oids(monkeypatch, failure):
    context = type("Context", (), {"clone": object()})()
    member = type("Member", (), {
        "data": b"payload", "path": "nested/README.md", "mode": 0o100644,
    })()
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_: None)
    calls = 0

    def git(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return (bootstrap_finalizer.object_oid("sha1", "blob", b"payload") + "\n").encode()
        raise failure

    monkeypatch.setattr(bootstrap_finalizer, "_git", git)
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._build_tree(context, (member,))

    residue = caught.value.residue
    assert residue.kind == "git_objects_mktree_failed"
    assert len(residue.object_oids) == 2
    assert residue.object_oids[0] == bootstrap_finalizer.object_oid("sha1", "blob", b"payload")


@pytest.mark.parametrize("failure", [RuntimeError("callback"), TimeoutError("timeout")])
def test_commit_callback_failure_reports_potentially_created_commit(monkeypatch, failure):
    context = type("Context", (), {"clone": object()})()
    entry = type("Entry", (), {"repo": "org/llm-wiki-client"})()
    monkeypatch.setattr(bootstrap_finalizer, "_remote_attested", lambda *_: ("absent", None))
    monkeypatch.setattr(bootstrap_finalizer, "_build_tree", lambda *_: ("b" * 40, "c" * 40))
    monkeypatch.setattr(bootstrap_finalizer, "_expected_commit", lambda *_: "d" * 40)
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_: None)

    def git(_bound, *args, **_kwargs):
        if args[0] == "ls-files":
            return b""
        raise failure

    monkeypatch.setattr(bootstrap_finalizer, "_git", git)
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._initial_commit(context, entry, object(), (), "c" * 40)

    assert caught.value.residue.kind == "git_objects_commit_tree_failed"
    assert caught.value.residue.object_oids == ("b" * 40, "c" * 40, "d" * 40)
