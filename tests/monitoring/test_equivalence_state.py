"""Tests for the equivalence-state publisher push path (#3500).

The publish push targets the dedicated ``equivalence-state`` ref — a
disconnected plumbing-built chain. Without the audited pre-push bypass the
hook's new-branch guard runs the FULL tier-1 suite (60+ min) on every cron
cycle and the push never lands (see #3500 / #3198). These tests pin that the
push subprocess env carries ``GIT_PRE_PUSH_SKIP=1`` (and nothing else does).
"""
import importlib.util
import os
import types

_SPEC = importlib.util.spec_from_file_location(
    "equivalence_state",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "monitoring", "equivalence_state.py"),
)
es = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(es)

SHA_A = "a" * 40
SHA_B = "b" * 40


class GitRecorder:
    """subprocess.run stand-in scripted per git subcommand."""

    def __init__(self, parent_exists):
        self.parent_exists = parent_exists
        self.calls = []  # (args, env) tuples

    def __call__(self, argv, input=None, capture_output=None, text=None, env=None):
        sub = argv[3]  # ["git", "-C", repo, <subcommand>, ...]
        self.calls.append((argv, env))
        ok = types.SimpleNamespace(returncode=0, stdout="", stderr="")
        if sub == "ls-remote":
            if not self.parent_exists:
                return types.SimpleNamespace(returncode=2, stdout="", stderr="")
            return types.SimpleNamespace(returncode=0, stdout=f"{SHA_A}\trefs/heads/x\n", stderr="")
        if sub == "rev-parse":
            return types.SimpleNamespace(returncode=0, stdout=SHA_A + "\n", stderr="")
        if sub == "ls-tree":
            return ok
        if sub in ("hash-object", "mktree", "commit-tree"):
            return types.SimpleNamespace(returncode=0, stdout=SHA_B + "\n", stderr="")
        return ok  # fetch, push, ...

    def push_calls(self):
        return [(a, e) for a, e in self.calls if a[3] == "push"]

    def non_push_calls(self):
        return [(a, e) for a, e in self.calls if a[3] != "push"]


def _run_publish(monkeypatch, parent_exists):
    rec = GitRecorder(parent_exists)
    monkeypatch.setattr(es.subprocess, "run", rec)
    assert es.publish("/fake/repo", "full", "{}") is True
    return rec


def test_create_push_sets_prepush_bypass_env(monkeypatch):
    """Ref-creation push (remote ref absent) must carry GIT_PRE_PUSH_SKIP=1."""
    rec = _run_publish(monkeypatch, parent_exists=False)
    pushes = rec.push_calls()
    assert len(pushes) == 1
    _, env = pushes[0]
    assert env is not None
    assert env.get("GIT_PRE_PUSH_SKIP") == "1"


def test_update_push_sets_prepush_bypass_env(monkeypatch):
    """CAS update push (--force-with-lease) must also carry the bypass."""
    rec = _run_publish(monkeypatch, parent_exists=True)
    pushes = rec.push_calls()
    assert len(pushes) == 1
    argv, env = pushes[0]
    assert any(a.startswith("--force-with-lease") for a in argv)
    assert env is not None
    assert env.get("GIT_PRE_PUSH_SKIP") == "1"


def test_bypass_env_inherits_parent_environment(monkeypatch):
    """The push env must be an overlay on os.environ, not a bare dict —
    git needs PATH/HOME/credentials from the parent environment."""
    monkeypatch.setenv("EQ_TEST_SENTINEL", "present")
    rec = _run_publish(monkeypatch, parent_exists=False)
    _, env = rec.push_calls()[0]
    assert env.get("EQ_TEST_SENTINEL") == "present"


def test_non_push_git_calls_do_not_set_bypass(monkeypatch):
    """Only the push is exempted; plumbing calls keep the default env."""
    rec = _run_publish(monkeypatch, parent_exists=True)
    assert rec.non_push_calls()  # sanity: flow used plumbing
    for _, env in rec.non_push_calls():
        assert env is None
