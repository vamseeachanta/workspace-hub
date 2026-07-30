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

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "equivalence_state",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "monitoring", "equivalence_state.py"),
)
es = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(es)

SHA_A = "a" * 40
SHA_B = "b" * 40


def _fingerprint(**overrides):
    data = {
        "fingerprint_version": 1,
        "role": "contribute-minimal",
        "hostname": "acma-ws014",
        "machine_id": "ace-win-2",
        "ts": "2026-07-14T10:00:00+00:00",
        "clone_head": "abcdef1",
        "behind_origin": 0,
        "ahead_origin": 0,
        "harness_version": "1.2.3",
        "harness_install": "other",
        "registry_sha256": "a" * 64,
        "learning_cron_ages_h": {
            "comprehensive-learning-nightly": None,
            "session-analysis": None,
        },
        "provider_soul_hashes": {
            "hermes": None,
            "claude": None,
            "codex": None,
            "codex_agents": None,
            "gemini": None,
        },
        "on_main": False,
        "index_lock_stale_min": None,
        "last_publish_duration_s": None,
    }
    data.update(overrides)
    return json.dumps(data)


def test_validate_cli_accepts_exact_v1_without_git(tmp_path, monkeypatch):
    fp = tmp_path / "fingerprint.json"
    fp.write_text(_fingerprint())

    def git_must_not_run(*_args, **_kwargs):
        raise AssertionError("validation must not invoke git")

    monkeypatch.setattr(es.subprocess, "run", git_must_not_run)
    assert es.main(["validate", "--file", str(fp)]) == 0


def test_publish_rejects_invalid_fingerprint_before_git(monkeypatch):
    def git_must_not_run(*_args, **_kwargs):
        raise AssertionError("invalid fingerprints must be rejected before git")

    monkeypatch.setattr(es.subprocess, "run", git_must_not_run)
    with pytest.raises(es.FingerprintValidationError):
        es.publish("/fake/repo", "ace-win-2", "{}")


def test_schema_rejects_wrong_types_versions_keys_and_nonfinite_values():
    base = json.loads(_fingerprint())
    bad_payloads = []
    for field, value in (
        ("fingerprint_version", True),
        ("fingerprint_version", 2),
        ("role", []),
        ("ts", "2026-07-14T10:00:00"),
        ("ts", "2026-07-14 10:00:00+00:00"),
        ("behind_origin", True),
        ("last_publish_duration_s", -1),
    ):
        candidate = dict(base)
        candidate[field] = value
        bad_payloads.append(json.dumps(candidate))
    extra = dict(base)
    extra["unexpected"] = None
    bad_payloads.append(json.dumps(extra))
    providers = dict(base)
    providers["provider_soul_hashes"] = {"claude": None}
    bad_payloads.append(json.dumps(providers))
    bad_payloads.append(_fingerprint().replace('"last_publish_duration_s": null',
                                               '"last_publish_duration_s": NaN'))

    for payload in bad_payloads:
        with pytest.raises(es.FingerprintValidationError):
            es.validate_fingerprint(payload)


def test_publish_rejects_machine_mismatch_before_git(monkeypatch):
    def git_must_not_run(*_args, **_kwargs):
        raise AssertionError("mismatched machine must be rejected before git")

    monkeypatch.setattr(es.subprocess, "run", git_must_not_run)
    with pytest.raises(es.FingerprintValidationError, match="does not match"):
        es.publish("/fake/repo", "ace-win-1", _fingerprint())


def test_prepare_fingerprint_uses_only_publish_phase_health(tmp_path):
    fp = tmp_path / "fingerprint.json"
    health = tmp_path / "publish-health.json"
    fp.write_text(_fingerprint())
    health.write_text(json.dumps({
        "schema_version": 1,
        "ts": "2026-07-14T10:00:00+00:00",
        "phase": "fingerprint",
        "duration_s": 900,
        "rc": 3,
    }))

    es.prepare_fingerprint(str(fp), str(health))
    assert json.loads(fp.read_text())["last_publish_duration_s"] is None

    health.write_text(json.dumps({
        "schema_version": 1,
        "ts": "2026-07-14T10:01:00+00:00",
        "phase": "publish",
        "duration_s": 4.5,
        "rc": 0,
    }))
    es.prepare_fingerprint(str(fp), str(health))
    assert json.loads(fp.read_text())["last_publish_duration_s"] == 4.5


def test_prepare_failure_preserves_generated_fingerprint(tmp_path, monkeypatch):
    fp = tmp_path / "fingerprint.json"
    health = tmp_path / "publish-health.json"
    original = _fingerprint()
    fp.write_text(original)
    health.write_text(json.dumps({
        "schema_version": 1,
        "ts": "2026-07-14T10:01:00+00:00",
        "phase": "publish",
        "duration_s": 4.5,
        "rc": 0,
    }))
    monkeypatch.setattr(es.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("stop")))

    with pytest.raises(OSError, match="stop"):
        es.prepare_fingerprint(str(fp), str(health))
    assert fp.read_text() == original


def test_write_health_replace_failure_preserves_prior_record(tmp_path, monkeypatch):
    health = tmp_path / "publish-health.json"
    prior = '{"prior":"complete"}\n'
    health.write_text(prior)
    monkeypatch.setattr(es.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("stop")))

    with pytest.raises(OSError, match="stop"):
        es.write_publish_health(str(health), "publish", 2.0, 0)
    assert health.read_text() == prior


@pytest.mark.parametrize("field,value", [
    ("schema_version", True),
    ("ts", "2026-07-14T10:00:00"),
    ("phase", "compare"),
    ("phase", []),
    ("duration_s", True),
    ("duration_s", -1),
    ("rc", True),
    ("rc", 5),
])
def test_publish_health_schema_fails_closed(field, value):
    data = {
        "schema_version": 1,
        "ts": "2026-07-14T10:00:00+00:00",
        "phase": "publish",
        "duration_s": 1.5,
        "rc": 0,
    }
    data[field] = value
    with pytest.raises(es.PublishHealthValidationError):
        es.validate_publish_health(json.dumps(data))


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
    assert es.publish("/fake/repo", "ace-win-2", _fingerprint()) is True
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


def test_publish_retries_bounded_cas_race(monkeypatch):
    rec = GitRecorder(parent_exists=True)
    real_run = rec.__call__
    attempts = 0

    def race_once(argv, input=None, **kw):
        nonlocal attempts
        if argv[3] == "push":
            attempts += 1
            rec.calls.append((argv, kw.get("env")))
            if attempts == 1:
                return types.SimpleNamespace(returncode=1, stdout="", stderr="rejected stale info")
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", race_once)
    assert es.publish("/fake/repo", "ace-win-2", _fingerprint(), retries=2) is True
    assert attempts == 2


def test_publish_reports_exhausted_cas_race(monkeypatch):
    rec = GitRecorder(parent_exists=True)
    real_run = rec.__call__

    def always_race(argv, input=None, **kw):
        if argv[3] == "push":
            rec.calls.append((argv, kw.get("env")))
            return types.SimpleNamespace(returncode=1, stdout="", stderr="rejected stale info")
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", always_race)
    assert es.publish("/fake/repo", "ace-win-2", _fingerprint(), retries=2) is False
    assert len(rec.push_calls()) == 2


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
            out = "".join(f"100644 blob {sha}\t{name}\0"
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
    assert es.publish(
        "/fake/repo", "gpu-claw",
        _fingerprint(machine_id="gpu-claw", hostname="gpu-claw"),
    ) is True
    assert b"gpu-claw.json\0" in captured["mktree_in"]


def test_publish_preserves_unrelated_and_cr_suffixed_entries(monkeypatch):
    rec = TreeRecorder({
        "notes.txt": "operator note",
        "ace-win-1.json\r": '{"hostname": "malformed-name"}',
    })
    captured = {}
    real_run = rec.__call__

    def spy(argv, input=None, **kw):
        if argv[3] == "mktree":
            captured["mktree_in"] = input
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", spy)
    assert es.publish("/fake/repo", "ace-win-2", _fingerprint()) is True
    assert b"notes.txt\0" in captured["mktree_in"]
    assert b"ace-win-1.json\r\0" in captured["mktree_in"]


def test_publish_preserves_modes_subtrees_and_symlinks(monkeypatch):
    rec = GitRecorder(parent_exists=True)
    captured = {}
    real_run = rec.__call__

    def spy(argv, input=None, **kw):
        if argv[3] == "ls-tree":
            rec.calls.append((argv, kw.get("env")))
            tree = (b"100755 blob " + b"c" * 40 + b"\tnotes.sh\0"
                    b"120000 blob " + b"d" * 40 + b"\tlink\0"
                    b"040000 tree " + b"e" * 40 + b"\tdir\0")
            return types.SimpleNamespace(returncode=0, stdout=tree, stderr=b"")
        if argv[3] == "mktree":
            captured["mktree_in"] = input
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", spy)
    assert es.publish("/fake/repo", "ace-win-2", _fingerprint()) is True
    assert b"100755 blob " + b"c" * 40 + b"\tnotes.sh\0" in captured["mktree_in"]
    assert b"120000 blob " + b"d" * 40 + b"\tlink\0" in captured["mktree_in"]
    assert b"040000 tree " + b"e" * 40 + b"\tdir\0" in captured["mktree_in"]


def test_ls_tree_failure_blocks_all_mutating_git_plumbing(monkeypatch):
    rec = GitRecorder(parent_exists=True)
    real_run = rec.__call__

    def fail_tree(argv, input=None, **kw):
        if argv[3] == "ls-tree":
            rec.calls.append((argv, kw.get("env")))
            return types.SimpleNamespace(returncode=1, stdout=b"", stderr=b"read failed")
        return real_run(argv, input=input, **kw)

    monkeypatch.setattr(es.subprocess, "run", fail_tree)
    with pytest.raises(es.StoreUnavailable, match="ls-tree"):
        es.publish("/fake/repo", "ace-win-2", _fingerprint())
    assert not any(call[0][3] in {"hash-object", "mktree", "commit-tree", "push"}
                   for call in rec.calls)


def test_collect_rejects_poisoned_json_entry(monkeypatch):
    rec = TreeRecorder({"ace-win-1.json": "[]"})
    monkeypatch.setattr(es.subprocess, "run", rec)
    with pytest.raises(es.StoreUnavailable, match="invalid fingerprint entry"):
        es.collect("/fake/repo")


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
    assert es.publish(
        "/fake/repo", "dev-primary",
        _fingerprint(machine_id="dev-primary", hostname="ace-linux-1", role="full"),
    ) is True
    tree_in = captured["mktree_in"]
    assert b"dev-primary.json\0" in tree_in       # new machine-keyed blob
    assert b"full.json\0" not in tree_in          # own legacy blob dropped
    assert b"contribute.json\0" in tree_in        # other box's legacy blob kept


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
    fp1 = _fingerprint(machine_id="ace-win-1", hostname="acma-ansys05")
    fp2 = _fingerprint(machine_id="ace-win-2", hostname="acma-ws014")
    assert es.publish(str(work), "ace-win-1", fp1) is True
    assert es.publish(str(work), "ace-win-2", fp2) is True
    boxes = es.collect(str(work))
    assert sorted(b["hostname"] for b in boxes) == ["acma-ansys05", "acma-ws014"]
