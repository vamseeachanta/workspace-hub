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
