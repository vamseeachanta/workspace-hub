"""Transport reconciliation matrix for descriptor-bound finalization."""
import subprocess

import pytest

from client_llm_wiki import bootstrap_finalizer


@pytest.mark.parametrize(("push_outcome", "final_state", "error_kind"), [
    ("success", "equal", None),
    ("nonzero", "equal", None),
    ("timeout", "equal", None),
    ("exception", "equal", None),
    ("credential-unavailable", "unknown", "remote_unknown"),
    ("success", "different", "pushed_remote_advanced"),
    ("success", "absent", "remote_unknown"),
    ("success", "unknown", "remote_unknown"),
])
def test_transport_reconciles_every_push_outcome(
    monkeypatch, push_outcome, final_state, error_kind,
):
    commit, tree = "c" * 40, "t" * 40
    states = iter((("absent", None), (final_state, None)))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_head", lambda *_args: commit)
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: None)
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    context = type("Context", (), {"clone": object()})()
    entry = type("Entry", (), {"repo": "org/llm-wiki-client"})()
    if error_kind is None:
        bootstrap_finalizer._transport(context, entry, object(), commit, tree)
    else:
        with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
            bootstrap_finalizer._transport(context, entry, object(), commit, tree)
        assert caught.value.residue.kind == error_kind


@pytest.mark.parametrize("outcome", ["success", "nonzero", "timeout", "exception"])
def test_push_returns_for_every_bounded_transport_outcome(monkeypatch, outcome):
    def run(*_args, **_kwargs):
        if outcome == "timeout":
            raise subprocess.TimeoutExpired("git push", 5)
        if outcome == "exception":
            raise OSError("credential unavailable")
        return subprocess.CompletedProcess([], 0 if outcome == "success" else 1, b"", b"")

    monkeypatch.setattr(bootstrap_finalizer, "_run", run)
    clone = type("Clone", (), {"git_fd": 9})()
    context = type("Context", (), {"clone": clone})()
    bootstrap_finalizer._push(context, "org/llm-wiki-client", "c" * 40)
