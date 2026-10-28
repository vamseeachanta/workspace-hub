"""Exercise index-only inventory using independently staged fixture records.

Sources: https://git-scm.com/docs/git-ls-files (OUTPUT, -z, --stage),
https://git-scm.com/docs/git-update-index (USING --INDEX-INFO), and
https://git-scm.com/docs/git-fast-import (filemodify modes).
Expected modes below are literal fixture inputs, never filesystem inference.
"""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/maintenance/script_mode_inventory.py"
)


def git_environment():
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(repo, *args, data=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=data,
        capture_output=True,
        check=True,
        env=git_environment(),
    ).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repository with spaces"
    root.mkdir()
    git(root, "init", "--quiet", "--template=")
    return root


def stage_records(repo, entries):
    """Feed mode SP object SP stage TAB path NUL, per --index-info docs."""
    records = []
    for mode, stage, path, content in entries:
        oid = git(repo, "hash-object", "-w", "--stdin", data=content).strip()
        records.append(
            mode.encode() + b" " + oid + b" " + stage.encode()
            + b"\t" + os.fsencode(path) + b"\0"
        )
    git(repo, "update-index", "-z", "--index-info", data=b"".join(records))


def invoke(repo, *, cwd=None, env=None, extra=()):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), *extra],
        cwd=cwd,
        env=env,
        capture_output=True,
    )


def inventory(repo, **kwargs):
    result = invoke(repo, **kwargs)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert result.stderr == b""
    return json.loads(result.stdout)


def snapshot(repo):
    """Capture index, objects, config, worktree bytes, links and permission bits."""
    result = {}
    for path in repo.rglob("*"):
        permissions = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            payload = ("link", os.readlink(path))
        elif path.is_file():
            payload = ("file", path.read_bytes())
        else:
            payload = ("directory",)
        result[path.relative_to(repo).as_posix()] = (permissions, payload)
    return result


def test_inventory_has_literal_modes_and_candidate_flags(repo):
    # Modes and stage zero follow the cited Git documentation; order is deliberate.
    stage_records(repo, [
        ("100755", "0", "scripts/run", b"#!/bin/sh\nexit\n"),
        ("100644", "0", "scripts/library.sh", b"function_name() { :; }\n"),
        ("100644", "0", "scripts/check", b"#!/bin/sh\nexit\n"),
        ("100755", "0", "notes", b"No shebang\n"),
    ])
    assert inventory(repo) == [
        {"path": "notes", "indexed_mode": "100755", "script_candidate": False},
        {"path": "scripts/check", "indexed_mode": "100644", "script_candidate": True},
        {"path": "scripts/library.sh", "indexed_mode": "100644", "script_candidate": False},
        {"path": "scripts/run", "indexed_mode": "100755", "script_candidate": True},
    ]


@pytest.mark.parametrize("path", ["space name.sh", "line\nbreak.sh", "tab\tname.sh"])
def test_delimiter_bearing_names_round_trip_deterministically(repo, path):
    stage_records(repo, [("100644", "0", path, b"#!/bin/sh\n")])
    first = invoke(repo)
    second = invoke(repo)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert json.loads(first.stdout) == [
        {"path": path, "indexed_mode": "100644", "script_candidate": True}
    ]


def test_symlinks_are_reported_without_following_targets(repo):
    stage_records(repo, [
        ("100644", "0", "run", b"#!/bin/sh\n"),
        ("120000", "0", "link", b"run"),
        ("120000", "0", "looks-like-shebang", b"#!/bin/sh\n"),
    ])
    (repo / "run").write_bytes(b"#!/bin/sh\n")
    (repo / "link").symlink_to("run")
    before = snapshot(repo)
    assert inventory(repo) == [
        {"path": "link", "indexed_mode": "120000", "script_candidate": False},
        {"path": "looks-like-shebang", "indexed_mode": "120000", "script_candidate": False},
        {"path": "run", "indexed_mode": "100644", "script_candidate": True},
    ]
    assert snapshot(repo) == before


@pytest.mark.parametrize("mode", ["100644", "100755"])
def test_index_mode_survives_working_tree_permission_changes(repo, mode):
    stage_records(repo, [(mode, "0", "run", b"#!/bin/sh\n")])
    path = repo / "run"
    path.write_bytes(b"#!/bin/sh\n")
    initial = inventory(repo)
    # Toggle the platform's named execute bit, without deriving an indexed mode.
    path.chmod(stat.S_IMODE(path.stat().st_mode) ^ stat.S_IXUSR)
    before = snapshot(repo)
    assert inventory(repo) == initial == [
        {"path": "run", "indexed_mode": mode, "script_candidate": True}
    ]
    assert snapshot(repo) == before


def test_index_bytes_override_working_tree_content_and_missing_files(repo):
    stage_records(repo, [
        ("100644", "0", "run", b"#!/bin/sh\n"),
        ("100644", "0", "library.sh", b":\n"),
        ("100755", "0", "missing", b"#!/usr/bin/env python3\n"),
    ])
    (repo / "run").write_bytes(b"no shebang in working tree\n")
    (repo / "library.sh").write_bytes(b"#!/bin/sh\n")
    (repo / "untracked").write_bytes(b"#!/bin/sh\n")
    before = snapshot(repo)
    assert inventory(repo) == [
        {"path": "library.sh", "indexed_mode": "100644", "script_candidate": False},
        {"path": "missing", "indexed_mode": "100755", "script_candidate": True},
        {"path": "run", "indexed_mode": "100644", "script_candidate": True},
    ]
    assert snapshot(repo) == before


@pytest.mark.parametrize("stages", [("1", "2", "3"), ("2",)])
def test_unmerged_entries_are_rejected_without_partial_json(repo, stages):
    # Higher stages use the literal stages documented in git-ls-files OUTPUT.
    stage_records(repo, [("100644", "0", "ordinary", b"#!/bin/sh\n")])
    stage_records(repo, [
        ("100755", stage, "conflict\nname", b"#!/bin/sh\n") for stage in stages
    ])
    before = snapshot(repo)
    result = invoke(repo)
    assert result.returncode != 0
    assert result.stdout == b""
    assert b"unmerged index entries" in result.stderr.lower()
    assert b"conflict\\nname" in result.stderr
    assert snapshot(repo) == before


def test_explicit_repository_ignores_inherited_git_bindings(repo, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    git(other, "init", "--quiet", "--template=")
    stage_records(repo, [("100644", "0", "intended", b"#!/bin/sh\n")])
    stage_records(other, [("100755", "0", "unrelated", b":\n")])
    env = git_environment()
    env.update(
        GIT_DIR=str(other / ".git"),
        GIT_COMMON_DIR=str(other / ".git"),
        GIT_WORK_TREE=str(other),
        GIT_INDEX_FILE=str(other / ".git/index"),
        GIT_OBJECT_DIRECTORY=str(other / ".git/objects"),
    )
    before = snapshot(repo), snapshot(other)
    assert inventory(repo, cwd=other, env=env) == [
        {"path": "intended", "indexed_mode": "100644", "script_candidate": True}
    ]
    assert (snapshot(repo), snapshot(other)) == before


def test_subdirectory_argument_still_reports_repository_relative_paths(repo):
    stage_records(repo, [
        ("100644", "0", "root", b"#!/bin/sh\n"),
        ("100755", "0", "nested/run", b"#!/bin/sh\n"),
    ])
    nested = repo / "nested"
    nested.mkdir()
    assert inventory(nested) == inventory(repo)


def test_empty_index_is_an_empty_json_array(repo):
    assert inventory(repo) == []


def test_non_repository_is_a_clear_error(tmp_path):
    result = invoke(tmp_path)
    assert result.returncode != 0
    assert result.stdout == b""
    assert b"cannot read Git index" in result.stderr


def test_help_describes_read_only_review_candidates():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True
    )
    assert result.returncode == 0
    assert b"repository" in result.stdout
    assert b"review" in result.stdout.lower()
    assert b"read-only" in result.stdout.lower()


@pytest.mark.parametrize("inherited_restriction", [None, "0", "1"])
def test_missing_promisor_blob_fails_without_fetching(repo, tmp_path, inherited_restriction):
    # git-upload-pack allows an explicit object request in this local-only fixture.
    # The control proves the missing blob is fetchable, rather than unreachable.
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "--quiet", "--template=")
    git(source, "config", "uploadpack.allowAnySHA1InWant", "true")
    content = b"#!/bin/sh\nexit\n"
    oid = git(source, "hash-object", "-w", "--stdin", data=content).strip()
    stage_records(repo, [("100644", "0", "available", b":\n")])
    git(repo, "config", "remote.origin.url", source.as_posix())
    git(repo, "config", "remote.origin.promisor", "true")
    git(repo, "update-index", "--add", "--info-only", "--cacheinfo",
        "100644", oid.decode("ascii"), "missing")
    before = snapshot(repo), snapshot(source)
    env = git_environment()
    if inherited_restriction is not None:
        env["GIT_NO_LAZY_FETCH"] = inherited_restriction
    result = invoke(repo, env=env)
    after = snapshot(repo), snapshot(source)
    # Preserve the control even when the regression assertions fail on old code.
    control = git(repo, "cat-file", "blob", oid.decode("ascii"))
    assert control == content
    assert result.returncode != 0
    assert result.stdout == b""
    assert b"cannot read Git index or indexed blob" in result.stderr
    assert after == before
