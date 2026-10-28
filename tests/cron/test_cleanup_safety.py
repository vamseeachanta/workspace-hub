"""Synthetic fixtures only; counts and age boundaries are hand calculations.

Protocol version 1 is defined in docs/operations/cleanup-safety.html.
No fixture is an engineering input or a live cleanup target.
"""
import base64
import hashlib
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/lib"))


@pytest.fixture(autouse=True)
def isolate_git_bindings(monkeypatch):
    for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.delenv(variable, raising=False)


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/lib/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def evidence():
    return load("cleanup_evidence")


def test_sibling_layout_and_partial_coverage(tmp_path):
    """Hub plus two configured siblings: visited=2, expected=3, missing=1."""
    runtime = load("cleanup_runtime")
    hub = tmp_path / "hub"
    for repo in (hub, tmp_path / "alpha"):
        (repo / ".git").mkdir(parents=True)
    registry = tmp_path / "repos.txt"
    registry.write_text("alpha\nbeta\n")
    result = runtime.coverage(hub, tmp_path, registry)
    assert result == {"expected": ["workspace-hub", "alpha", "beta"],
                      "visited": ["workspace-hub", "alpha"], "missing": ["beta"]}
    (tmp_path / "beta").mkdir()
    (tmp_path / "beta" / ".git").write_text("gitdir: elsewhere")
    assert runtime.coverage(hub, tmp_path, registry)["missing"] == []


@pytest.mark.parametrize("slug", ["../escape", "/absolute", "alpha\nalpha"])
def test_bad_registry(tmp_path, slug):
    runtime = load("cleanup_runtime")
    registry = tmp_path / "repos"
    registry.write_text(slug)
    with pytest.raises(ValueError):
        runtime.coverage(tmp_path, tmp_path, registry)


@pytest.mark.parametrize("state, expected", [
    ({"configured": True, "gateway": True, "scheduler": True, "last_run": 95}, "recent"),
    ({"configured": True, "gateway": True, "scheduler": True, "last_run": 89}, "stale"),
    ({"configured": True, "gateway": False, "scheduler": True, "last_run": 95}, "automation unavailable"),
    ({"configured": True, "gateway": True, "scheduler": False, "last_run": 95}, "automation unavailable"),
    (None, "automation unavailable"),
])
def test_automation(tmp_path, state, expected):
    """At t=100 and bound=10, ages 5 and 11 are recent and stale."""
    runtime = load("cleanup_runtime")
    path = tmp_path / "state.json"
    if state is not None:
        path.write_text(json.dumps(state))
    result = runtime.automation(path, bound=10, now=100)
    assert result["liveness"] == expected
    assert "configured" in result and result["staleness_bound_seconds"] == 10


def staged(tmp_path):
    trash = tmp_path / "trash"
    target = trash / "old"
    target.mkdir(parents=True)
    (target / "payload").write_bytes(b"abc")
    return trash, target, tmp_path / "cleanup-verification.json"


def approval(evidence, trash, artifact):
    data = {"schema": 1, "delete_allowed": True,
            "target_paths": ["old"], "entries": evidence.snapshot(trash, ["old"])}
    artifact.write_text(json.dumps(data))
    return hashlib.sha256(artifact.read_bytes()).hexdigest()


def test_old_without_artifact_kept(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    os.utime(target, (0, 0))
    result = evidence.purge(trash, artifact, "", execute=True)
    assert target.exists() and not result["removed"]


def test_verified_directory_removed(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    result = evidence.purge(trash, artifact, digest, execute=True)
    assert result["removed"] == ["old"] and not target.exists()
    assert artifact.exists()


@pytest.mark.parametrize("change", ["artifact", "content", "mtime", "added", "symlink"])
def test_changed_evidence_kept(tmp_path, evidence, change):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    if change == "artifact":
        artifact.write_text(artifact.read_text() + " ")
    elif change == "content":
        stat = (target / "payload").stat()
        (target / "payload").write_bytes(b"xyz")
        os.utime(target / "payload", ns=(stat.st_atime_ns, stat.st_mtime_ns))
    elif change == "mtime":
        os.utime(target / "payload", ns=(0, 0))
    elif change == "added":
        (target / "new").touch()
    else:
        (target / "payload").unlink()
        (target / "payload").symlink_to(artifact)
    result = evidence.purge(trash, artifact, digest, execute=True)
    assert target.exists() and result["retained"] and result["reason"]


@pytest.mark.parametrize("name", ["cleanup-verification.json", "plan.html", "test_x.py", "review.json"])
def test_protected_artifacts_refused(tmp_path, evidence, name):
    trash, target, artifact = staged(tmp_path)
    (target / name).write_text("evidence")
    digest = approval(evidence, trash, artifact)
    assert not evidence.purge(trash, artifact, digest, execute=True)["removed"]
    assert (target / name).exists()


def test_artifact_inside_target_refused(tmp_path, evidence):
    trash, target, _ = staged(tmp_path)
    artifact = target / "permission.json"
    digest = approval(evidence, trash, artifact)
    assert not evidence.purge(trash, artifact, digest, execute=True)["removed"]


def test_dry_run_retains(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    assert not evidence.purge(trash, artifact, digest, execute=False)["removed"]
    assert target.exists()


def odd_tree(tmp_path):
    tree = tmp_path / "source"
    tree.mkdir()
    names = [b"tab\tx", b"line\nx", b"back\\x", b"-dash", b"raw\xff",
             "é".encode(), "e\u0301".encode()]
    for name in names:
        with open(os.fsencode(tree) + b"/" + name, "wb") as stream:
            stream.write(b"abc")
    (tree / "link").symlink_to("-dash")
    (tree / "broken").symlink_to("missing")
    return tree, names


def test_manifest_roundtrip_archive_and_sidecar(tmp_path):
    """Seven files contain abc (3 bytes each); two symlinks and root total ten records.

    SHA-256 abc vector: RFC 6234 section 8.5, SHA256 test case 1.
    Byte sorting is checked independently on the literal names.
    """
    archive = load("cleanup_archive")
    tree, names = odd_tree(tmp_path)
    out = tmp_path / "output"
    result = archive.create(tree, out)
    records = archive.read_manifest(result["manifest"])
    decoded = [base64.b64decode(row["path_b64"]) for row in records]
    assert decoded == sorted([b".", *names, b"link", b"broken"])
    assert len(records) == 10
    for row in records:
        if row["kind"] == "file":
            assert row["size"] == 3
            assert row["sha256"] == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert result["sidecar"].name == result["manifest_sha256"] + ".sha256"
    assert names[0] not in result["sidecar"].read_bytes()
    assert archive.verify(tree, result["archive"], result["manifest"], result["sidecar"])
    (tree / "-dash").write_bytes(b"xyz")
    with pytest.raises(ValueError):
        archive.verify(tree, result["archive"], result["manifest"], result["sidecar"])


@pytest.mark.parametrize("case", [
    "duplicate-decoded-names", "reversed-order", "invalid-base64",
    "unsupported-schema", "json-whitespace", "canonical-control",
])
def test_manifest_reader_rejects_noncanonical_records(tmp_path, case):
    """Protocol v1: docs/operations/cleanup-safety.html, Archive protocol.

    One record per entry requires unique decoded names in byte order; base64
    must decode, and JSON must use the specified compact serialization.
    Metadata, schema 1 and the abc digest below are the literal Worked example;
    schema 0 is unsupported because it differs from the specified version.
    Lg== decodes to b'.', and cGF5bG9hZA== to b'payload', independently of the
    manifest writer. Only the named rule is changed in each malformed case.
    """
    archive = load("cleanup_archive")
    header = b'{"path_encoding":"base64","schema":1}\n'
    directory = (
        b'{"device":1,"inode":10,"kind":"directory","mode":493,"mtime_ns":0,'
        b'"path_b64":"Lg==","size":32}\n'
    )
    payload = (
        b'{"device":1,"inode":11,"kind":"file","mode":420,"mtime_ns":0,'
        b'"path_b64":"cGF5bG9hZA==","sha256":'
        b'"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",'
        b'"size":3}\n'
    )
    canonical = header + directory + payload
    manifests = {
        "duplicate-decoded-names": header + directory + directory + payload,
        "reversed-order": header + payload + directory,
        "invalid-base64": header + directory.replace(b'Lg==', b'!!!!') + payload,
        "unsupported-schema": canonical.replace(b'"schema":1', b'"schema":0'),
        "json-whitespace": canonical.replace(b'"schema":1', b'"schema": 1'),
        "canonical-control": canonical,
    }
    source = tmp_path / "source"
    source.mkdir()
    (source / "payload").write_bytes(b"abc")
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_bytes(manifests[case])

    def recorded_bytes():
        return {path.relative_to(tmp_path): path.read_bytes() if path.is_file() else None
                for path in tmp_path.rglob("*")}

    before = recorded_bytes()
    try:
        if case == "canonical-control":
            rows = archive.read_manifest(manifest)
            assert [base64.b64decode(row["path_b64"], validate=True)
                    for row in rows] == [b".", b"payload"]
        else:
            with pytest.raises(ValueError):
                archive.read_manifest(manifest)
    finally:
        assert recorded_bytes() == before


def test_interrupted_manifest_has_no_final(tmp_path, monkeypatch):
    archive = load("cleanup_archive")
    tree, _ = odd_tree(tmp_path)
    def fail(*args):
        raise OSError("simulated failure before rename")
    monkeypatch.setattr(archive.os, "replace", fail)
    out = tmp_path / "output"
    with pytest.raises(OSError):
        archive.create(tree, out)
    assert not list(out.glob("*.jsonl"))
    assert list(out.glob("*.partial"))
    for path in out.glob("*.partial"):
        with pytest.raises(ValueError, match="partial"):
            archive.read_manifest(path)


def test_payload_ignored():
    for path in ("cleanup-output/payload.tar.gz", "cleanup-output/evidence.jsonl"):
        assert subprocess.run(["git", "check-ignore", "-q", path],
                              cwd=ROOT, check=False).returncode == 0


def test_shell_preflights_before_mutation():
    text = (ROOT / "scripts/cron/daily-cleanup.sh").read_text()
    assert text.index("cleanup_runtime.py\" coverage") < text.index("# === Lock acquisition")
    assert 'REPO_DIR="$SIBLING_ROOT/$repo"' in text
    assert "-exec rm -rf" not in text
    assert 'cleanup_evidence.py"' in text


def test_multiple_targets(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    (trash / "second").write_bytes(b"abc")
    data = {"schema": 1, "delete_allowed": True, "target_paths": ["old", "second"],
            "entries": evidence.snapshot(trash, ["old", "second"])}
    artifact.write_text(json.dumps(data))
    result = evidence.purge(trash, artifact, hashlib.sha256(artifact.read_bytes()).hexdigest(), True)
    assert result["removed"] == ["old", "second"] and not target.exists()


def test_last_moment_change_retained(tmp_path, evidence, monkeypatch):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    original = evidence.snapshot_fd
    calls = []
    def changed(fd, names):
        calls.append(True)
        if len(calls) == 2:  # Initial validation then the mandatory final re-hash.
            (target / "payload").write_bytes(b"changed")
        return original(fd, names)
    monkeypatch.setattr(evidence, "snapshot_fd", changed)
    assert not evidence.purge(trash, artifact, digest, True)["removed"]
    assert (target / "payload").read_bytes() == b"changed"


def test_exclusive_writer_lock(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    fd = os.open(trash, os.O_RDONLY)
    try:
        evidence.fcntl.flock(fd, evidence.fcntl.LOCK_EX)
        assert not evidence.purge(trash, artifact, digest, True)["removed"]
    finally:
        os.close(fd)
    assert target.exists()


@pytest.mark.parametrize("names", [["../escape"], ["old", "old"], [], ["/absolute"]])
def test_invalid_target_set(tmp_path, evidence, names):
    trash, target, artifact = staged(tmp_path)
    artifact.write_text(json.dumps({"schema": 1, "delete_allowed": True,
                                    "target_paths": names, "entries": []}))
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert not evidence.purge(trash, artifact, digest, True)["removed"]
    assert target.exists()


def test_tampered_archive_refused(tmp_path):
    archive = load("cleanup_archive")
    tree, _ = odd_tree(tmp_path)
    result = archive.create(tree, tmp_path / "output")
    result["archive"].write_bytes(b"damaged")
    with pytest.raises(ValueError, match="checksum"):
        archive.verify(tree, result["archive"], result["manifest"], result["sidecar"])


def test_bsd_tools_refused(monkeypatch):
    archive = load("cleanup_archive")
    monkeypatch.setattr(archive.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, stdout=b"BSD tool"))
    with pytest.raises(ValueError, match="NOT_EVALUATED"):
        archive.require_gnu()


def test_shell_only_temporary_targets(tmp_path):
    """Expected coverage is hub plus alpha (two); absent beta blocks all actions."""
    hub = tmp_path / "hub"
    for directory in (hub, tmp_path / "alpha"):
        (directory / ".git").mkdir(parents=True)
    registry = tmp_path / "repos"
    registry.write_text("alpha\n")
    tools = tmp_path / "bin"
    tools.mkdir()
    log = tmp_path / "calls"
    git = tools / "git"
    git.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n'
                   'case "$*" in *--show-toplevel*) printf "%s\\n" "$SCRIPT_ROOT";; esac\n')
    git.chmod(0o755)  # Fixture executable mode, POSIX shell script requirement.
    gh = tools / "gh"
    gh.write_text('#!/bin/sh\nprintf "[]\\n"\n')
    gh.chmod(0o755)
    env = {**os.environ, "PATH": str(tools) + os.pathsep + os.environ["PATH"],
           "CALLS": str(log), "SCRIPT_ROOT": str(ROOT), "TMPDIR": str(tmp_path),
           "CLEANUP_HUB_ROOT": str(hub), "CLEANUP_SIBLING_ROOT": str(tmp_path),
           "TIER1_REPOS_FILE": str(registry)}
    command = ["bash", str(ROOT / "scripts/cron/daily-cleanup.sh"), "--dry-run"]
    complete = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    assert complete.returncode == 0, complete.stderr
    assert '"visited": ["workspace-hub", "alpha"]' in complete.stdout
    assert "automation unavailable" in complete.stdout
    assert "fetch" not in log.read_text() and "worktree prune" not in log.read_text()
    assert not (tmp_path / ".daily-cleanup-lock").exists()

    registry.write_text("alpha\nbeta\n")
    partial = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    assert partial.returncode != 0 and '"missing": ["beta"]' in partial.stderr
    assert not (tmp_path / ".daily-cleanup-lock").exists()


@pytest.mark.parametrize("state", [[], {"last_run": True}, {"last_run": 101},
                                   {"last_run": "95"}, {"last_run": float("nan")}])
def test_malformed_automation_is_unavailable(tmp_path, state):
    runtime = load("cleanup_runtime")
    path = tmp_path / "state"
    path.write_text(json.dumps(state))
    assert runtime.automation(path, 10, 100)["liveness"] == "automation unavailable"


def test_registry_changed_after_configuration(tmp_path):
    runtime = load("cleanup_runtime")
    registry = tmp_path / "repos"
    registry.write_text("beta\n")
    with pytest.raises(ValueError, match="registry changed"):
        runtime.coverage(tmp_path, tmp_path, registry, ["workspace-hub", "alpha"])


@pytest.mark.parametrize("data", [[], {}, {"schema": 1, "target_paths": "old"},
                                  {"schema": True, "delete_allowed": True,
                                   "target_paths": ["old"], "entries": []}])
def test_malformed_approval_retained(tmp_path, evidence, data):
    trash, target, artifact = staged(tmp_path)
    artifact.write_text(json.dumps(data))
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert not evidence.purge(trash, artifact, digest, True)["removed"]
    assert target.exists()


def test_per_entry_final_rehash(tmp_path, evidence, monkeypatch):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    original = evidence.remove_tree
    def changed(fd, name, expected, relative):
        if name == b"payload":
            (target / "payload").write_bytes(b"changed")
        return original(fd, name, expected, relative)
    monkeypatch.setattr(evidence, "remove_tree", changed)
    result = evidence.purge(trash, artifact, digest, True)
    assert result["reason"] and not result["removed"]
    assert (target / "payload").read_bytes() == b"changed"


def test_symlink_trash_refused(tmp_path, evidence):
    trash, target, artifact = staged(tmp_path)
    digest = approval(evidence, trash, artifact)
    alias = tmp_path / "alias"
    alias.symlink_to(trash, target_is_directory=True)
    assert not evidence.purge(alias, artifact, digest, True)["removed"]
    assert target.exists()


def test_archive_hardlinks_and_resume(tmp_path, monkeypatch):
    archive = load("cleanup_archive")
    source = tmp_path / "source"
    source.mkdir()
    (source / "first").write_bytes(b"abc")
    os.link(source / "first", source / "second")
    result = archive.create(source, tmp_path / "output")
    assert archive.archive_records(result["archive"])[b"second"]["kind"] == "file"
    def no_recompute(*args):
        raise AssertionError("completed evidence must be reused")
    monkeypatch.setattr(archive, "archive_payload", no_recompute)
    assert archive.create(source, tmp_path / "output") == result


def test_worked_example_is_canonical(tmp_path):
    """Assigned metadata is illustrative; abc is three bytes and the RFC vector fixes its hash."""
    archive = load("cleanup_archive")
    page = (ROOT / "docs/operations/cleanup-safety.html").read_text()
    example = html.unescape(re.search(r'<pre id="manifest-example">(.*?)</pre>',
                                     page, re.DOTALL).group(1))
    path = tmp_path / "example.jsonl"
    path.write_text(example)
    rows = archive.read_manifest(path)
    assert [base64.b64decode(row["path_b64"]) for row in rows] == [b".", b"payload"]
    assert rows[1]["size"] == len(b"abc")
    assert rows[1]["sha256"] == hashlib.sha256(b"abc").hexdigest()
