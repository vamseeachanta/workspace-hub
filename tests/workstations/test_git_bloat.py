"""Read-only diagnostics; every numeric fixture is synthetic, not a policy limit."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/workstations/git_bloat.py"


@pytest.fixture
def mod(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("git_bloat", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args, data=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], input=data, capture_output=True,
        check=True, env=env,
    ).stdout


def repository(tmp_path):
    """Construct temporary history without changing any checkout under review."""
    repo = tmp_path / "fixture"
    repo.mkdir()
    git(repo, "init", "-q", "--initial-branch=main")
    stream = (
        b"blob\nmark :1\ndata 3\none\n"
        b"commit refs/heads/main\nmark :2\n"
        b"committer Fixture <fixture> 0 +0000\ndata 4\nbase\n"
        b'M 100644 :1 "archived notes.txt"\n'
        b'M 100644 :1 "tab\\tname.txt"\n\n'
        b"commit refs/heads/main\nmark :3\n"
        b"committer Fixture <fixture> 1 +0000\ndata 4\nlive\nfrom :2\n"
        b'D "archived notes.txt"\nM 100644 :1 keep/current.txt\n\n'
        b"reset refs/heads/retained\nfrom :2\n\n"
        b"done\n"
    )
    git(repo, "fast-import", "--quiet", data=stream)
    return repo


def files_snapshot(repo):
    return {
        str(path.relative_to(repo)): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in repo.rglob("*") if path.is_file()
    }


def test_storage_worked_example(mod, tmp_path):
    """Hand calculation: 7 + 11 + 13 + 5 = 36; non-objects = 29 bytes.

    File lengths are explicit synthetic inputs. Filesystem allocation is not
    asserted to equal logical lengths. No reclaim quantity can be derived.
    """
    for name, content in {
        "objects/pack/fixture.pack": b"o" * 7,
        "lfs/objects/payload": b"l" * 11,
        "recovery-backups/fixture.patch": b"b" * 13,
        "config": b"c" * 5,
    }.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    result = mod.storage_observation(tmp_path)
    assert result["status"] == "EVALUATED"
    assert result["logical_file_bytes"] == 36
    assert result["non_object_logical_file_bytes"] == 29
    assert {key: value["logical_bytes"] for key, value in result["categories"].items()} == {
        "objects": 7, "lfs": 11, "recovery_backups": 13, "other": 5,
    }


def test_other_ref_and_descendants_block_candidates(mod, tmp_path):
    repo = repository(tmp_path)
    result = mod.inspect(repo, timeout_seconds=30, candidates=[
        "archived notes.txt", "keep", "keep/", "keepish", "missing", "tab\tname.txt",
    ])
    # The tab-containing candidate is rejected; Git path enumeration still uses
    # NUL delimiting so it cannot fabricate a second candidate or split names.
    assert result["candidates"][0]["status"] == "BLOCKED_LIVE_PATH"
    assert result["candidates"][1]["status"] == "BLOCKED_LIVE_PATH"
    assert result["candidates"][2]["status"] == "BLOCKED_LIVE_PATH"
    assert result["candidates"][3]["status"] == "ABSENT_FROM_TIPS"
    assert result["candidates"][4]["status"] == "ABSENT_FROM_TIPS"
    assert result["candidates"][5]["status"] == "NOT_EVALUATED"
    assert result["reclaimable_bytes"]["status"] == "NOT_EVALUATED"


def test_index_and_head_both_protect_live_paths(mod, tmp_path):
    repo = repository(tmp_path)
    # read-tree populates a disposable index; HEAD and every ref stay untouched.
    git(repo, "read-tree", "retained")
    git(repo, "update-ref", "-d", "refs/heads/retained")
    result = mod.inspect(repo, timeout_seconds=30, candidates=["archived notes.txt", "keep"])
    assert [row["status"] for row in result["candidates"]] == [
        "BLOCKED_LIVE_PATH", "BLOCKED_LIVE_PATH",
    ]


def test_subdirectory_candidates_match_root_index_paths(mod, tmp_path):
    repo = repository(tmp_path)
    nested = repo / "nested"
    nested.mkdir()
    git(repo, "read-tree", "HEAD")
    oid = git(repo, "hash-object", "-w", "--stdin", data=b"staged").strip().decode()
    for path in ("staged-only.txt", "nested/inside.txt"):
        git(repo, "update-index", "--add", "--cacheinfo", "100644", oid, path)
    candidates = ["staged-only.txt", "nested/inside.txt", "nested", "inside.txt"]
    before = files_snapshot(repo)
    root = mod.inspect(repo, timeout_seconds=30, candidates=candidates)
    selected = mod.inspect(nested, timeout_seconds=30, candidates=candidates)
    assert root["status"] == selected["status"] == "EVALUATED"
    assert [row["status"] for row in root["candidates"]] == [
        "BLOCKED_LIVE_PATH", "BLOCKED_LIVE_PATH", "BLOCKED_LIVE_PATH", "ABSENT_FROM_TIPS",
    ]
    assert selected["candidates"] == root["candidates"]
    assert before == files_snapshot(repo)


def test_annotated_tag_and_gitlink_are_protected(mod, tmp_path):
    repo = repository(tmp_path)
    oid = git(repo, "rev-parse", "retained").strip()
    tag = (b"object " + oid + b"\ntype commit\ntag retained\n"
           b"tagger Fixture <fixture> 0 +0000\n\nfixture\n")
    tag_oid = git(repo, "hash-object", "-t", "tag", "-w", "--stdin", data=tag).strip()
    git(repo, "update-ref", "refs/tags/retained", tag_oid.decode())
    git(repo, "update-ref", "-d", "refs/heads/retained")
    git(repo, "read-tree", "HEAD")
    git(repo, "update-index", "--add", "--cacheinfo", "160000", oid.decode(), "submodule")
    result = mod.inspect(repo, timeout_seconds=30, candidates=["archived notes.txt", "submodule"])
    assert all(row["status"] == "BLOCKED_LIVE_PATH" for row in result["candidates"])


def test_empty_tree_entry_is_a_live_path(mod, tmp_path):
    repo = repository(tmp_path)
    empty = git(repo, "mktree", data=b"").strip()
    tree = git(repo, "mktree", data=b"040000 tree " + empty + b"\tempty-dir\n").strip()
    git(repo, "update-ref", "refs/tags/tree-fixture", tree.decode())
    result = mod.inspect(repo, timeout_seconds=30, candidates=["empty-dir"])
    assert result["candidates"][0]["status"] == "BLOCKED_LIVE_PATH"


def test_index_content_change_with_identical_paths_is_detected(mod, tmp_path, monkeypatch):
    repo = repository(tmp_path)
    git(repo, "read-tree", "HEAD")
    original = mod.storage_observation

    def change(common):
        value = original(common)
        oid = git(repo, "hash-object", "-w", "--stdin", data=b"new index contents").strip()
        git(repo, "update-index", "--cacheinfo", "100644", oid.decode(), "keep/current.txt")
        return value

    monkeypatch.setattr(mod, "storage_observation", change)
    result = mod.inspect(repo, timeout_seconds=30, candidates=["absent"])
    assert result["status"] == "NOT_EVALUATED"
    assert "refs_or_index_changed" in result["issue_codes"]


@pytest.mark.parametrize("candidate", ["", ".", "..", "../escape", "/absolute", "a/../b", "a//b", "a\\b", "a\nname", "a/*"])
def test_invalid_candidate_is_not_treated_as_absent(mod, tmp_path, candidate):
    repo = repository(tmp_path)
    result = mod.inspect(repo, timeout_seconds=30, candidates=[candidate])
    assert result["status"] == "NOT_EVALUATED"
    assert result["candidates"][0]["status"] == "NOT_EVALUATED"


def test_readonly_and_inherited_git_environment(mod, tmp_path, monkeypatch):
    repo = repository(tmp_path)
    before = files_snapshot(repo)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "wrong"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path))
    result = mod.inspect(repo, timeout_seconds=30, reachable=True, candidates=["keep"])
    assert result["status"] == "EVALUATED"
    assert result["reachable"]["status"] == "EVALUATED"
    assert result["reachable"]["disk_bytes"] > 0
    assert before == files_snapshot(repo)
    assert str(repo) not in json.dumps(result)


def test_linked_worktree_measures_common_storage(mod, tmp_path):
    repo = repository(tmp_path)
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "--quiet", "--detach", str(linked), "HEAD")
    (repo / ".git/recovery-backups").mkdir()
    (repo / ".git/recovery-backups/fixture.patch").write_bytes(b"backup")
    result = mod.inspect(linked, timeout_seconds=30)
    assert result["storage"]["categories"]["recovery_backups"]["logical_bytes"] == len(b"backup")
    assert result["storage"]["scope"] == "common_git_directory"


@pytest.mark.parametrize("kind", ["shallow", "promisor", "promisor-marker", "partial", "alternates"])
def test_incomplete_object_graph_is_not_zero_or_reclaim(mod, tmp_path, kind):
    repo = repository(tmp_path)
    if kind == "shallow":
        (repo / ".git/shallow").write_bytes(git(repo, "rev-parse", "HEAD"))
    elif kind == "promisor":
        git(repo, "config", "remote.fixture.promisor", "true")
    elif kind == "partial":
        git(repo, "config", "extensions.partialclone", "fixture")
    elif kind == "promisor-marker":
        (repo / ".git/objects/pack/fixture.promisor").touch()
    else:
        (repo / ".git/objects/info/alternates").write_text(str(tmp_path / "missing-store"), encoding="utf-8", newline="\n")
    result = mod.inspect(repo, timeout_seconds=30, reachable=True, candidates=["absent"])
    assert result["status"] == "NOT_EVALUATED"
    assert result["reachable"]["status"] == "NOT_EVALUATED"
    assert result["reachable"]["disk_bytes"] is None
    assert result["candidates"][0]["status"] == "NOT_EVALUATED"


def test_symlink_storage_never_followed(mod, tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    (external / "private").write_bytes(b"x" * 100)
    common = tmp_path / "common"
    common.mkdir()
    (common / "objects").symlink_to(external, target_is_directory=True)
    result = mod.storage_observation(common)
    assert result["status"] == "NOT_EVALUATED"
    assert result["logical_file_bytes"] is None
    assert "symlink_target_excluded" in result["issue_codes"]


def test_missing_repo_and_empty_head_are_explicit(mod, tmp_path):
    assert mod.inspect(tmp_path / "missing", timeout_seconds=30)["status"] == "NOT_EVALUATED"
    git(tmp_path, "init", "--quiet")
    result = mod.inspect(tmp_path, timeout_seconds=30, candidates=["absent"])
    assert result["candidates"][0]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("kind", ["timeout", "failure", "malformed"])
def test_reachable_command_failure_is_not_measured_zero(mod, tmp_path, monkeypatch, kind):
    repo = repository(tmp_path)
    original = mod._git

    def fail(repo, args, timeout_seconds, **kwargs):
        if "rev-list" in args:
            if kind == "timeout":
                raise subprocess.TimeoutExpired("git", timeout_seconds)
            if kind == "failure":
                raise OSError("unreported private location")
            return b"unexpected output\n"
        return original(repo, args, timeout_seconds, **kwargs)

    monkeypatch.setattr(mod, "_git", fail)
    result = mod.inspect(repo, timeout_seconds=30, reachable=True)
    assert result["status"] == "NOT_EVALUATED"
    assert result["reachable"]["disk_bytes"] is None
    assert "unreported" not in json.dumps(result)


def test_changed_refs_invalidate_candidate_observation(mod, tmp_path, monkeypatch):
    repo = repository(tmp_path)
    original = mod._snapshot
    count = 0

    def change(*args, **kwargs):
        nonlocal count
        value = original(*args, **kwargs)
        count += 1
        return value if count == 1 else (value[0], value[1] + b"changed", value[2])

    monkeypatch.setattr(mod, "_snapshot", change)
    result = mod.inspect(repo, timeout_seconds=30, candidates=["absent"])
    assert result["candidates"][0]["status"] == "NOT_EVALUATED"
    assert "refs_or_index_changed" in result["issue_codes"]


def test_blob_ref_does_not_allow_absence_claim(mod, tmp_path):
    repo = repository(tmp_path)
    blob = git(repo, "rev-parse", "HEAD:keep/current.txt").strip().decode()
    git(repo, "update-ref", "refs/tags/blob-fixture", blob)
    result = mod.inspect(repo, timeout_seconds=30, candidates=["absent"])
    assert result["candidates"][0]["status"] == "NOT_EVALUATED"


def test_git_failure_suppresses_stderr_and_disables_fetch(mod, tmp_path, monkeypatch):
    def failure(command, **kwargs):
        assert "protocol.allow=never" in command
        assert "core.fsmonitor=false" in command
        assert kwargs["env"]["GIT_NO_LAZY_FETCH"] == "1"
        assert kwargs["env"]["GIT_OPTIONAL_LOCKS"] == "0"
        assert "GIT_DIR" not in kwargs["env"]
        assert kwargs["timeout"] == 30
        return subprocess.CompletedProcess(command, 128, b"", b"unreported private text")

    monkeypatch.setenv("GIT_DIR", str(tmp_path / "wrong"))
    monkeypatch.setattr(mod.subprocess, "run", failure)
    with pytest.raises(ValueError, match="git_observation_failed"):
        mod._git(tmp_path, ["ls-files"], 30)


def test_cli_json_and_exit_status(tmp_path):
    repo = repository(tmp_path)
    command = [sys.executable, "-B", str(SCRIPT), "--repo", str(repo), "--timeout-seconds", "30"]
    good = subprocess.run(command + ["--candidate", "keep"], capture_output=True, text=True, check=False)
    assert good.returncode == 0, good.stderr
    assert json.loads(good.stdout)["candidates"][0]["status"] == "BLOCKED_LIVE_PATH"
    invalid = subprocess.run(command + ["--candidate", "../bad"], capture_output=True, text=True, check=False)
    assert invalid.returncode == 1
    assert json.loads(invalid.stdout)["status"] == "NOT_EVALUATED"
    usage = subprocess.run(command[:-1] + ["0"], capture_output=True, text=True, check=False)
    assert usage.returncode == 2
