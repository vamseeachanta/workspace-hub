"""Attestation routing contract for every private Git operation."""
import pytest

from client_llm_wiki import bootstrap_finalizer


EXPECTED = {
    "object_format", "symbolic_head", "resolve_head", "index_list",
    "recovery_tree", "commit_read", "index_tree", "hash_object", "mktree",
    "commit_tree", "cas", "read_tree", "push", "api_query", "final_return",
}


def test_every_private_git_operation_has_a_named_seam():
    assert bootstrap_finalizer._ATTESTED_OPERATIONS == EXPECTED


@pytest.mark.parametrize("operation", sorted(EXPECTED))
def test_every_named_operation_attests_before_and_after_baseexception(monkeypatch, operation):
    events = []
    monkeypatch.setattr(
        bootstrap_finalizer, "_independent_attestation",
        lambda context: events.append(("attest", context)),
    )
    with pytest.raises(KeyboardInterrupt):
        bootstrap_finalizer._with_attestation(
            "context", operation,
            lambda: events.append(("call", "context")) or (_ for _ in ()).throw(KeyboardInterrupt()),
        )
    assert events == [("attest", "context"), ("call", "context"), ("attest", "context")]
