"""Tests for the equivalence-state publisher push path (#3500).

The publish push targets the dedicated ``equivalence-state`` ref — a
disconnected plumbing-built chain. Without the audited pre-push bypass the
hook's new-branch guard runs the FULL tier-1 suite (60+ min) on every cron
cycle and the push never lands (see #3500 / #3198). These tests pin that the
push subprocess env carries ``GIT_PRE_PUSH_SKIP=1`` (and nothing else does).
"""
import importlib.util
import json
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


# ── #3516: machine-keyed blobs — same-role boxes must not clobber each other ──

class TreeRecorder(GitRecorder):
    """Recorder with a scripted existing ref tree (name -> content json str)."""

    def __init__(self, tree):
        super().__init__(parent_exists=True)
        self.tree = tree  # {"full.json": '{"hostname": "ace-linux-1", ...}'}
        self._sha_to_name = {f"sha{i}": n for i, n in enumerate(sorted(tree))}

    def __call__(self, argv, input=None, capture_output=None, text=None, env=None):
        sub = argv[3]
        if sub == "ls-tree":
            self.calls.append((argv, env))
            out = "".join(f"100644 blob {sha}\t{name}\n"
                          for sha, name in self._sha_to_name.items())
            return types.SimpleNamespace(returncode=0, stdout=out, stderr="")
        if sub == "cat-file" and argv[4] == "-p":
            self.calls.append((argv, env))
            name = self._sha_to_name.get(argv[5], "")
            return types.SimpleNamespace(returncode=0, stdout=self.tree.get(name, ""), stderr="")
        return super().__call__(argv, input=input, capture_output=capture_output,
                                text=text, env=env)

    def mktree_input(self):
        for argv, _ in self.calls:
            pass
        return None


def _mktree_inputs(rec):
    return [argv for argv, _ in rec.calls if argv[3] == "mktree"]


def test_publish_keys_blob_by_machine_id(monkeypatch):
    rec = GitRecorder(parent_exists=False)
    captured = {}
    real_run = rec.__call__

    def spy(argv, input=None, **kw):
        if argv[3] == "mktree":
            captured["mktree_in"] = input
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", spy)
    assert es.publish("/fake/repo", "gpu-claw", '{"hostname": "gpu-claw"}') is True
    assert "gpu-claw.json" in captured["mktree_in"]


def test_publish_self_cleans_own_legacy_role_blob(monkeypatch):
    """A box republishing under its machine-id must drop ITS old role-named blob
    (migration is self-cleaning), while leaving other boxes' legacy blobs alone."""
    rec = TreeRecorder({
        "full.json": '{"hostname": "ace-linux-1"}',
        "contribute.json": '{"hostname": "ace-linux-2"}',
    })
    captured = {}
    real_run = rec.__call__

    def spy(argv, input=None, **kw):
        if argv[3] == "mktree":
            captured["mktree_in"] = input
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", spy)
    assert es.publish("/fake/repo", "dev-primary", '{"hostname": "ace-linux-1"}') is True
    tree_in = captured["mktree_in"]
    assert "dev-primary.json" in tree_in          # new machine-keyed blob
    assert "full.json" not in tree_in             # own legacy blob dropped
    assert "contribute.json" in tree_in           # other box's legacy blob kept


def test_resolve_identity_from_registry(tmp_path):
    reg = tmp_path / "registry.yaml"
    reg.write_text(
        "machines:\n"
        "  dev-primary:\n    hostname: ace-linux-1\n    hostname_aliases: [vamsee-linux1]\n"
        "    schedule_variant: full\n"
        "  gpu-claw:\n    hostname: gpu-claw\n    schedule_variant: contribute-minimal\n"
    )
    assert es.resolve_identity(str(reg), "gpu-claw") == ("gpu-claw", "contribute-minimal")
    assert es.resolve_identity(str(reg), "ace-linux-1") == ("dev-primary", "full")
    assert es.resolve_identity(str(reg), "VAMSEE-LINUX1") == ("dev-primary", "full")
    # unknown host: collision-safe fallback, never a shared name
    assert es.resolve_identity(str(reg), "mystery-box") == ("unknown-mystery-box", "unknown")
    assert es.resolve_identity(str(tmp_path / "nope.yaml"), "x") == ("unknown-x", "unknown")


def test_same_role_machines_do_not_clobber_end_to_end(tmp_path):
    """Integration (#3516 reproduction inverted): two machines, same role,
    publish machine-keyed -> collect sees BOTH."""
    import subprocess as sp
    origin = tmp_path / "origin.git"; work = tmp_path / "work"
    sp.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    sp.run(["git", "init", "-q", str(work)], check=True)
    sp.run(["git", "-C", str(work), "remote", "add", "origin", str(origin)], check=True)
    fp1 = json.dumps({"role": "contribute-minimal", "hostname": "acma-ansys05"})
    fp2 = json.dumps({"role": "contribute-minimal", "hostname": "acma-ws014"})
    assert es.publish(str(work), "ace-win-1", fp1) is True
    assert es.publish(str(work), "ace-win-2", fp2) is True
    boxes = es.collect(str(work))
    assert sorted(b["hostname"] for b in boxes) == ["acma-ansys05", "acma-ws014"]
